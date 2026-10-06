"""Mechanical 5-minute trend-pullback scalp (no LLM).

Decision rules, all computed from OKX klines the loop already fetches:

* Regime: 15m EMA20 vs EMA50 direction, 15m ADX(14) above a floor, DI agreement,
  and 15m ATR% inside a window so hot alts that spike through a tight stop are skipped.
* Setup: a 5m candle tags the Bollinger (20, 2) pullback zone (basis to band) with the
  trend, then the next closed 5m candle closes back through the basis in that direction.
* Filters: RSI(14) not already extended, relative volume on the confirmation candle,
  funding + open-interest crowding, weekday session window.
* Risk: stop just beyond the pullback wick, position sized so that stop loses exactly
  ``risk_per_trade_usd``; target is the same distance (1:1).

Everything here is pure computation and bookkeeping. Order placement lives in main.py.
"""

from __future__ import annotations

import json
import logging
import math
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

Candle = Sequence[Any]  # [ts_ms, open, high, low, close, volume]

MECHANICAL_MODE = "mechanical"

# Defaults for every knob, overridable from trading_settings (DB) or CONFIG.
DEFAULTS: Dict[str, Any] = {
    "mech_cycle_seconds": 60,
    "mech_max_positions": 5,
    "mech_leverage": 10,
    "mech_margin_usd": 30.0,
    "mech_take_profit_usd": 1.0,
    "mech_stop_loss_usd": 1.0,
    # Margin-ROI exits (easier hits than a fixed $2 on quiet scalps).
    "mech_tp_mode": "roi_percent",
    "mech_take_profit_percent": 5.0,
    "mech_stop_loss_percent": 5.0,
    # Looser regime so demo can take several quality setups/day (not 0).
    "mech_adx_min": 15.0,
    "mech_ema_min_separation_pct": 0.02,
    "mech_atr_min_pct": 0.35,
    "mech_atr_max_pct": 2.5,
    "mech_rsi_max_long": 75.0,
    "mech_rsi_min_short": 25.0,
    "mech_rvol_full": 0.9,
    "mech_rvol_half": 0.5,
    "mech_funding_max": 0.001,
    "mech_oi_rising_pct": 2.0,
    "mech_oi_window_minutes": 30,
    "mech_session_start_utc": 0,
    "mech_session_end_utc": 24,
    "mech_trade_weekends": True,
    "mech_stop_buffer_pct": 0.05,
    "mech_min_stop_pct": 0.10,
    "mech_max_stop_pct": 2.5,
    "mech_max_spread_frac_of_stop": 0.40,
    "mech_entry_ttl_candles": 2,
    "mech_pullback_lookback": 5,
    "mech_win_cooldown_minutes": 2,
    "mech_loss_cooldown_minutes": 12,
    "mech_pair_refresh_minutes": 10,
    "mech_min_size_risk_tolerance": 1.25,
}


# --------------------------------------------------------------------------- settings
def is_mechanical_mode(settings: Optional[Dict[str, Any]]) -> bool:
    """True when the dashboard parked the AI and chose the mechanical book."""
    if not settings:
        return False
    model = str(settings.get("llm_model") or "").strip().lower()
    mode = str(settings.get("decision_mode") or "").strip().lower()
    return model == MECHANICAL_MODE or mode == MECHANICAL_MODE


def resolve_config(settings: Optional[Dict[str, Any]], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Merge DEFAULTS with CONFIG (env) and DB settings; DB wins."""
    out = dict(DEFAULTS)
    for source in (config or {}, settings or {}):
        for key in DEFAULTS:
            val = source.get(key)
            if val is None or val == "":
                continue
            default = DEFAULTS[key]
            try:
                if isinstance(default, bool):
                    out[key] = val if isinstance(val, bool) else str(val).strip().lower() in {"1", "true", "yes", "on"}
                elif isinstance(default, int):
                    out[key] = int(float(val))
                elif isinstance(default, float):
                    out[key] = float(val)
                else:
                    out[key] = val
            except (TypeError, ValueError):
                continue
    return out


def resolve_exit_targets(
    settings: Optional[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Resolve user TP/SL independently (any R:R) for mechanical exits.

    ``tp_mode`` (dashboard):
      * ``roi_percent`` — % of margin (TP and SL set separately → 1:1, 1:2, …)
      * ``price_percent`` — % of entry price (TP/SL independent)
      * ``usd`` — fixed dollars (TP/SL independent)

    Exchange algos are pinned to the resolved levels; exit watcher uses the same mode.
    """
    cfg = resolve_config(settings, config)
    settings = settings or {}
    try:
        margin = abs(float(
            settings.get("margin_per_position")
            or settings.get("mech_margin_usd")
            or cfg.get("mech_margin_usd")
            or 30.0
        ))
    except (TypeError, ValueError):
        margin = 30.0
    if margin <= 0:
        margin = 30.0
    try:
        lev = max(int(float(settings.get("leverage") or cfg.get("mech_leverage") or 10)), 1)
    except (TypeError, ValueError):
        lev = 10

    mode = str(
        settings.get("tp_mode") or cfg.get("mech_tp_mode") or "roi_percent"
    ).strip().lower()
    if mode not in ("usd", "roi_percent", "price_percent"):
        mode = "roi_percent"

    price_based = False
    if mode == "usd":
        try:
            tp_usd = abs(float(
                settings.get("take_profit_usd")
                or settings.get("mech_take_profit_usd")
                or cfg.get("mech_take_profit_usd")
                or 1.0
            ))
        except (TypeError, ValueError):
            tp_usd = 1.0
        if tp_usd <= 0:
            tp_usd = 1.0
        try:
            raw_sl = settings.get("stop_loss_usd")
            if raw_sl is None or raw_sl == "":
                raw_sl = settings.get("mech_stop_loss_usd") or cfg.get("mech_stop_loss_usd") or tp_usd
            sl_usd = abs(float(raw_sl))
        except (TypeError, ValueError):
            sl_usd = tp_usd
        if sl_usd <= 0:
            sl_usd = tp_usd
        tp_pct = (tp_usd / margin) * 100.0 if margin else 0.0
        sl_pct = (sl_usd / margin) * 100.0 if margin else 0.0
        rr = (tp_usd / sl_usd) if sl_usd else 0.0
        label = f"${tp_usd:.2f} TP / ${sl_usd:.2f} SL (R:R {rr:.2f})"
    else:
        try:
            tp_pct = abs(float(
                settings.get("take_profit_percent")
                or settings.get("mech_take_profit_percent")
                or cfg.get("mech_take_profit_percent")
                or 5.0
            ))
        except (TypeError, ValueError):
            tp_pct = 5.0
        if tp_pct <= 0:
            tp_pct = 5.0
        try:
            sl_pct = abs(float(
                settings.get("stop_loss_percent")
                or settings.get("mech_stop_loss_percent")
                or cfg.get("mech_stop_loss_percent")
                or tp_pct
            ))
        except (TypeError, ValueError):
            sl_pct = tp_pct
        if sl_pct <= 0:
            sl_pct = tp_pct
        # Keep % inside numeric(5,2) column limits used by Supabase.
        tp_pct = min(tp_pct, 99.99)
        sl_pct = min(sl_pct, 99.99)
        if mode == "price_percent":
            price_based = True
            notional = margin * lev
            tp_usd = notional * tp_pct / 100.0
            sl_usd = notional * sl_pct / 100.0
            rr = (tp_pct / sl_pct) if sl_pct else 0.0
            label = f"{tp_pct:g}%/{sl_pct:g}% price TP/SL (R:R {rr:.2f}, ≈${tp_usd:.2f}/${sl_usd:.2f})"
        else:
            tp_usd = margin * tp_pct / 100.0
            sl_usd = margin * sl_pct / 100.0
            rr = (tp_pct / sl_pct) if sl_pct else 0.0
            label = f"{tp_pct:g}%/{sl_pct:g}% margin ROI TP/SL (R:R {rr:.2f}, ≈${tp_usd:.2f}/${sl_usd:.2f} on ${margin:.0f})"

    return {
        "mode": mode,
        "margin_usd": margin,
        "leverage": lev,
        "tp_usd": tp_usd,
        "sl_usd": sl_usd,
        "tp_pct": tp_pct,
        "sl_pct": sl_pct,
        "price_based": price_based,
        "label": label,
    }


def apply_mechanical_overrides(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Margin sizing + user TP/SL levels when the mode is mechanical.

    Does **not** force 1:1 — TP and SL stay whatever you set (%, price %, or $).
    Trailing / ladder / BE are off so those levels stay respected.
    """
    if not is_mechanical_mode(settings):
        return settings
    cfg = resolve_config(settings)
    targets = resolve_exit_targets(settings, cfg)
    margin = float(targets["margin_usd"])
    mode = str(targets["mode"])
    tp_usd = float(targets["tp_usd"])
    sl_usd = float(targets["sl_usd"])
    tp_pct = float(targets["tp_pct"])
    sl_pct = float(targets["sl_pct"])

    settings["margin_per_position"] = margin
    settings["position_sizing_mode"] = "margin"
    settings["tp_mode"] = mode
    settings["take_profit_usd"] = tp_usd
    settings["stop_loss_usd"] = -sl_usd
    settings["risk_per_trade_usd"] = sl_usd
    settings["take_profit_percent"] = tp_pct
    settings["stop_loss_percent"] = sl_pct
    settings["agent_manage_exits"] = True
    settings["enable_stop_loss_orders"] = True
    settings["take_profit_strict_enforcement"] = True
    settings["enable_profit_ladder"] = False
    settings["enable_breakeven_stop"] = False
    settings["enable_trailing_stop"] = False
    settings["enable_drawdown_protection"] = False
    settings["reentry_cooldown_minutes"] = float(cfg["mech_win_cooldown_minutes"])
    settings["loss_reentry_cooldown_minutes"] = float(cfg["mech_loss_cooldown_minutes"])
    settings["block_direction_flip"] = True
    settings["max_positions"] = int(cfg["mech_max_positions"])
    settings["leverage"] = int(cfg["mech_leverage"])
    settings["asset_leverage_overrides"] = {}
    settings["interval"] = "5m"
    return settings


# --------------------------------------------------------------------------- indicators
def ema(values: Sequence[float], period: int) -> List[float]:
    if not values or period <= 0:
        return []
    k = 2.0 / (period + 1.0)
    out: List[float] = []
    prev = float(values[0])
    for v in values:
        prev = float(v) * k + prev * (1.0 - k)
        out.append(prev)
    return out


def sma(values: Sequence[float], period: int) -> List[Optional[float]]:
    out: List[Optional[float]] = []
    window: Deque[float] = deque(maxlen=period)
    total = 0.0
    for v in values:
        if len(window) == period:
            total -= window[0]
        window.append(float(v))
        total += float(v)
        out.append(total / period if len(window) == period else None)
    return out


def bollinger(closes: Sequence[float], period: int = 20, mult: float = 2.0) -> List[Optional[Tuple[float, float, float]]]:
    """Per-index (upper, basis, lower); None until the window fills."""
    out: List[Optional[Tuple[float, float, float]]] = []
    for i in range(len(closes)):
        if i + 1 < period:
            out.append(None)
            continue
        window = [float(c) for c in closes[i + 1 - period : i + 1]]
        basis = sum(window) / period
        var = sum((c - basis) ** 2 for c in window) / period
        sd = math.sqrt(var)
        out.append((basis + mult * sd, basis, basis - mult * sd))
    return out


def rsi(closes: Sequence[float], period: int = 14) -> Optional[float]:
    if len(closes) <= period:
        return None
    gains = 0.0
    losses = 0.0
    for i in range(1, period + 1):
        d = float(closes[i]) - float(closes[i - 1])
        if d >= 0:
            gains += d
        else:
            losses -= d
    avg_gain = gains / period
    avg_loss = losses / period
    for i in range(period + 1, len(closes)):
        d = float(closes[i]) - float(closes[i - 1])
        avg_gain = (avg_gain * (period - 1) + max(d, 0.0)) / period
        avg_loss = (avg_loss * (period - 1) + max(-d, 0.0)) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - 100.0 / (1.0 + rs)


def _true_ranges(highs: Sequence[float], lows: Sequence[float], closes: Sequence[float]) -> List[float]:
    out: List[float] = []
    for i in range(len(closes)):
        h, l = float(highs[i]), float(lows[i])
        if i == 0:
            out.append(h - l)
            continue
        pc = float(closes[i - 1])
        out.append(max(h - l, abs(h - pc), abs(l - pc)))
    return out


def atr(highs: Sequence[float], lows: Sequence[float], closes: Sequence[float], period: int = 14) -> Optional[float]:
    trs = _true_ranges(highs, lows, closes)
    if len(trs) < period + 1:
        return None
    value = sum(trs[1 : period + 1]) / period
    for tr in trs[period + 1 :]:
        value = (value * (period - 1) + tr) / period
    return value


def adx(highs: Sequence[float], lows: Sequence[float], closes: Sequence[float], period: int = 14) -> Optional[Tuple[float, float, float]]:
    """Wilder ADX. Returns (adx, +DI, -DI) or None when there is not enough data."""
    n = len(closes)
    if n < 2 * period + 1:
        return None
    trs = _true_ranges(highs, lows, closes)
    plus_dm: List[float] = [0.0]
    minus_dm: List[float] = [0.0]
    for i in range(1, n):
        up = float(highs[i]) - float(highs[i - 1])
        down = float(lows[i - 1]) - float(lows[i])
        plus_dm.append(up if (up > down and up > 0) else 0.0)
        minus_dm.append(down if (down > up and down > 0) else 0.0)

    tr_s = sum(trs[1 : period + 1])
    pdm_s = sum(plus_dm[1 : period + 1])
    mdm_s = sum(minus_dm[1 : period + 1])
    dxs: List[float] = []
    plus_di = minus_di = 0.0
    for i in range(period + 1, n):
        tr_s = tr_s - tr_s / period + trs[i]
        pdm_s = pdm_s - pdm_s / period + plus_dm[i]
        mdm_s = mdm_s - mdm_s / period + minus_dm[i]
        if tr_s <= 0:
            dxs.append(0.0)
            continue
        plus_di = 100.0 * pdm_s / tr_s
        minus_di = 100.0 * mdm_s / tr_s
        denom = plus_di + minus_di
        dxs.append(100.0 * abs(plus_di - minus_di) / denom if denom > 0 else 0.0)
    if len(dxs) < period:
        return None
    adx_val = sum(dxs[:period]) / period
    for dx in dxs[period:]:
        adx_val = (adx_val * (period - 1) + dx) / period
    return adx_val, plus_di, minus_di


# --------------------------------------------------------------------------- candles
def interval_ms(interval: str) -> int:
    s = (interval or "5m").strip().lower()
    unit = s[-1]
    qty = int(s[:-1] or 1)
    return qty * {"m": 60_000, "h": 3_600_000, "d": 86_400_000}.get(unit, 60_000)


def closed_candles(rows: Sequence[Candle], interval: str, now_ms: Optional[int] = None) -> List[Candle]:
    """Drop the still-forming last candle so every rule reads closed bars only."""
    if not rows:
        return []
    now_ms = now_ms or int(datetime.now(timezone.utc).timestamp() * 1000)
    out = [r for r in rows if r and len(r) >= 6]
    if out and int(out[-1][0]) + interval_ms(interval) > now_ms:
        out = out[:-1]
    return out


# --------------------------------------------------------------------------- session
def session_open(now: datetime, cfg: Dict[str, Any]) -> Tuple[bool, str]:
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    now = now.astimezone(timezone.utc)
    if not cfg.get("mech_trade_weekends") and now.weekday() >= 5:
        return False, "weekend — no new entries"
    start = int(cfg.get("mech_session_start_utc", 6))
    end = int(cfg.get("mech_session_end_utc", 24))
    hour = now.hour + now.minute / 60.0
    if start <= end:
        ok = start <= hour < end
    else:  # window wraps midnight
        ok = hour >= start or hour < end
    if not ok:
        return False, f"outside session window {start:02d}:00–{end:02d}:00 UTC"
    return True, ""


# --------------------------------------------------------------------------- OI memory
class OIHistory:
    """Rolling open-interest per asset so a crowding gate can see the recent change."""

    def __init__(self, maxlen: int = 240):
        self._hist: Dict[str, Deque[Tuple[float, float]]] = {}
        self._maxlen = maxlen

    def record(self, asset: str, oi: Optional[float], ts: Optional[float] = None) -> None:
        if oi is None:
            return
        key = asset.upper()
        ts = ts or datetime.now(timezone.utc).timestamp()
        self._hist.setdefault(key, deque(maxlen=self._maxlen)).append((ts, float(oi)))

    def change_pct(self, asset: str, minutes: float) -> Optional[float]:
        hist = self._hist.get(asset.upper())
        if not hist or len(hist) < 2:
            return None
        now_ts, now_oi = hist[-1]
        cutoff = now_ts - minutes * 60.0
        base = None
        for ts, oi in hist:
            if ts <= cutoff:
                base = oi
            else:
                break
        if base is None:
            base = hist[0][1]
        if base <= 0:
            return None
        return (now_oi - base) / base * 100.0


# --------------------------------------------------------------------------- signal
@dataclass
class ScalpSignal:
    asset: str
    side: str  # "buy" | "sell"
    entry_price: float
    stop_price: float
    target_price: float
    stop_distance_pct: float
    size_factor: float
    signal_ts: int
    confirm_ts: int
    metrics: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_long(self) -> bool:
        return self.side == "buy"


@dataclass
class ScalpSkip:
    asset: str
    reason: str
    metrics: Dict[str, Any] = field(default_factory=dict)


def evaluate(
    asset: str,
    candles_5m: Sequence[Candle],
    candles_15m: Sequence[Candle],
    *,
    funding: Optional[float],
    oi_change_pct: Optional[float],
    cfg: Dict[str, Any],
    now: Optional[datetime] = None,
    last_signal_ts: Optional[int] = None,
) -> ScalpSignal | ScalpSkip:
    """Return a signal or the first reason the asset was skipped this cycle."""
    now = now or datetime.now(timezone.utc)
    now_ms = int(now.timestamp() * 1000)
    c15 = closed_candles(candles_15m, "15m", now_ms)
    c5 = closed_candles(candles_5m, "5m", now_ms)
    metrics: Dict[str, Any] = {}

    if len(c15) < 60 or len(c5) < 40:
        return ScalpSkip(asset, f"not enough candles (15m={len(c15)}, 5m={len(c5)})", metrics)

    h15 = [float(r[2]) for r in c15]
    l15 = [float(r[3]) for r in c15]
    x15 = [float(r[4]) for r in c15]
    ema20 = ema(x15, 20)[-1]
    ema50 = ema(x15, 50)[-1]
    adx_pack = adx(h15, l15, x15, 14)
    atr15 = atr(h15, l15, x15, 14)
    last_px = x15[-1]
    if adx_pack is None or atr15 is None or last_px <= 0:
        return ScalpSkip(asset, "15m indicators unavailable", metrics)
    adx_val, plus_di, minus_di = adx_pack
    atr_pct = atr15 / last_px * 100.0
    sep_pct = (ema20 - ema50) / ema50 * 100.0 if ema50 else 0.0
    metrics.update({
        "ema20_15m": round(ema20, 8), "ema50_15m": round(ema50, 8), "ema_sep_pct": round(sep_pct, 4),
        "adx_15m": round(adx_val, 2), "plus_di": round(plus_di, 2), "minus_di": round(minus_di, 2),
        "atr_15m_pct": round(atr_pct, 3),
    })

    # Volatility window — the entry-spike guard.
    if atr_pct < float(cfg["mech_atr_min_pct"]):
        return ScalpSkip(asset, f"too quiet: 15m ATR {atr_pct:.2f}% < {cfg['mech_atr_min_pct']}%", metrics)
    if atr_pct > float(cfg["mech_atr_max_pct"]):
        return ScalpSkip(asset, f"too hot: 15m ATR {atr_pct:.2f}% > {cfg['mech_atr_max_pct']}%", metrics)

    # Regime.
    min_sep = float(cfg["mech_ema_min_separation_pct"])
    if adx_val < float(cfg["mech_adx_min"]):
        return ScalpSkip(asset, f"flat 15m: ADX {adx_val:.1f} < {cfg['mech_adx_min']}", metrics)
    if sep_pct >= min_sep and plus_di > minus_di:
        side = "buy"
    elif sep_pct <= -min_sep and minus_di > plus_di:
        side = "sell"
    else:
        return ScalpSkip(asset, f"no 15m direction (EMA sep {sep_pct:.3f}%, +DI {plus_di:.1f} / -DI {minus_di:.1f})", metrics)
    metrics["regime"] = "long" if side == "buy" else "short"

    # Crowding.
    fmax = float(cfg["mech_funding_max"])
    oi_rising = float(cfg["mech_oi_rising_pct"])
    metrics["funding"] = funding
    metrics["oi_change_pct"] = None if oi_change_pct is None else round(oi_change_pct, 2)
    if funding is not None and oi_change_pct is not None and oi_change_pct > oi_rising:
        if side == "buy" and funding > fmax:
            return ScalpSkip(asset, f"crowded long: funding {funding:.4%} with OI +{oi_change_pct:.1f}%", metrics)
        if side == "sell" and funding < -fmax:
            return ScalpSkip(asset, f"crowded short: funding {funding:.4%} with OI +{oi_change_pct:.1f}%", metrics)

    # 5m setup.
    o5 = [float(r[1]) for r in c5]
    h5 = [float(r[2]) for r in c5]
    l5 = [float(r[3]) for r in c5]
    x5 = [float(r[4]) for r in c5]
    v5 = [float(r[5]) for r in c5]
    bands = bollinger(x5, 20, 2.0)
    confirm_i = len(c5) - 1
    band_c = bands[confirm_i]
    if band_c is None:
        return ScalpSkip(asset, "5m Bollinger unavailable", metrics)
    upper_c, basis_c, lower_c = band_c
    confirm_close, confirm_open = x5[confirm_i], o5[confirm_i]
    confirm_ts = int(c5[confirm_i][0])
    metrics.update({"bb_basis_5m": round(basis_c, 8), "confirm_close": confirm_close})

    lookback = int(cfg["mech_pullback_lookback"])
    signal_i: Optional[int] = None
    for i in range(confirm_i - 1, max(confirm_i - 1 - lookback, 19), -1):
        b = bands[i]
        if b is None:
            continue
        _, basis_i, lower_i = b
        upper_i = b[0]
        if side == "buy" and l5[i] <= basis_i and x5[i] >= lower_i:
            signal_i = i
            break
        if side == "sell" and h5[i] >= basis_i and x5[i] <= upper_i:
            signal_i = i
            break
    if signal_i is None:
        return ScalpSkip(asset, "no pullback to 5m basis in the last candles", metrics)
    signal_ts = int(c5[signal_i][0])
    metrics["signal_ts"] = signal_ts
    if last_signal_ts is not None and signal_ts <= last_signal_ts:
        return ScalpSkip(asset, "same pullback already traded — waiting for a new one", metrics)

    # Confirmation: close back through the basis with the trend.
    if side == "buy" and not (confirm_close > basis_c and confirm_close > confirm_open):
        return ScalpSkip(asset, f"no bullish close back above basis ({confirm_close:.6g} vs {basis_c:.6g})", metrics)
    if side == "sell" and not (confirm_close < basis_c and confirm_close < confirm_open):
        return ScalpSkip(asset, f"no bearish close back below basis ({confirm_close:.6g} vs {basis_c:.6g})", metrics)

    # RSI chase filter.
    rsi14 = rsi(x5[-60:], 14)
    metrics["rsi_5m"] = None if rsi14 is None else round(rsi14, 1)
    if rsi14 is not None:
        if side == "buy" and rsi14 >= float(cfg["mech_rsi_max_long"]):
            return ScalpSkip(asset, f"extended: 5m RSI {rsi14:.0f} >= {cfg['mech_rsi_max_long']}", metrics)
        if side == "sell" and rsi14 <= float(cfg["mech_rsi_min_short"]):
            return ScalpSkip(asset, f"extended: 5m RSI {rsi14:.0f} <= {cfg['mech_rsi_min_short']}", metrics)

    # Relative volume on the confirmation candle.
    prior = v5[confirm_i - 20 : confirm_i]
    avg_vol = sum(prior) / len(prior) if prior else 0.0
    rvol = v5[confirm_i] / avg_vol if avg_vol > 0 else None
    metrics["rvol"] = None if rvol is None else round(rvol, 2)
    size_factor = 1.0
    if rvol is not None:
        if rvol < float(cfg["mech_rvol_half"]):
            return ScalpSkip(asset, f"thin confirmation: RVOL {rvol:.2f} < {cfg['mech_rvol_half']}", metrics)
        if rvol < float(cfg["mech_rvol_full"]):
            size_factor = 0.5

    # Stop beyond the pullback wick, target the same distance.
    buffer_pct = float(cfg["mech_stop_buffer_pct"]) / 100.0
    atr5 = atr(h5, l5, x5, 14)
    buffer_abs = max(confirm_close * buffer_pct, (atr5 or 0.0) * 0.1)
    entry = confirm_close
    if side == "buy":
        wick = min(l5[signal_i], l5[confirm_i])
        stop = wick - buffer_abs
        dist = entry - stop
        target = entry + dist
    else:
        wick = max(h5[signal_i], h5[confirm_i])
        stop = wick + buffer_abs
        dist = stop - entry
        target = entry - dist
    if dist <= 0 or entry <= 0:
        return ScalpSkip(asset, "degenerate stop geometry", metrics)
    stop_pct = dist / entry * 100.0
    metrics.update({"stop_pct": round(stop_pct, 3), "size_factor": size_factor})
    if stop_pct < float(cfg["mech_min_stop_pct"]):
        return ScalpSkip(asset, f"stop too tight: {stop_pct:.2f}% < {cfg['mech_min_stop_pct']}%", metrics)
    if stop_pct > float(cfg["mech_max_stop_pct"]):
        return ScalpSkip(asset, f"wick too long: stop {stop_pct:.2f}% > {cfg['mech_max_stop_pct']}%", metrics)

    return ScalpSignal(
        asset=asset,
        side=side,
        entry_price=entry,
        stop_price=stop,
        target_price=target,
        stop_distance_pct=stop_pct,
        size_factor=size_factor,
        signal_ts=signal_ts,
        confirm_ts=confirm_ts,
        metrics=metrics,
    )


# --------------------------------------------------------------------------- sizing
@dataclass
class SizedOrder:
    contracts: float
    coin_qty: float
    notional_usd: float
    margin_usd: float
    risk_usd: float
    reward_usd: float


def size_position(
    signal: ScalpSignal,
    *,
    risk_usd: float,
    leverage: int,
    ct_val: float,
    lot_sz: float,
    min_sz: float,
    available_balance: float,
    bid: Optional[float],
    ask: Optional[float],
    cfg: Dict[str, Any],
    margin_usd: Optional[float] = None,
    take_profit_usd: Optional[float] = None,
    stop_loss_usd: Optional[float] = None,
) -> SizedOrder | ScalpSkip:
    """Size by fixed margin (preferred) or legacy wick-risk. Always book fixed $ TP/SL when set."""
    if bid and ask and bid > 0 and ask > 0:
        spread_pct = (ask - bid) / signal.entry_price * 100.0
        max_frac = float(cfg["mech_max_spread_frac_of_stop"])
        if signal.stop_distance_pct > 0 and spread_pct > signal.stop_distance_pct * max_frac:
            return ScalpSkip(
                signal.asset,
                f"spread {spread_pct:.3f}% is more than {max_frac:.0%} of the {signal.stop_distance_pct:.2f}% stop",
            )

    ct_val = float(ct_val or 1.0) or 1.0
    lot_sz = float(lot_sz or 1.0) or 1.0
    min_sz = float(min_sz or lot_sz) or lot_sz
    lev = max(int(leverage or 1), 1)
    entry = float(signal.entry_price)
    if entry <= 0:
        return ScalpSkip(signal.asset, "invalid entry price")

    factor = float(signal.size_factor or 1.0)
    use_margin = margin_usd is not None and float(margin_usd) > 0
    if use_margin:
        margin_target = max(float(margin_usd), 0.0) * factor
        if margin_target <= 0:
            return ScalpSkip(signal.asset, "zero margin budget")
        notional = margin_target * lev
        coin_qty = notional / entry
        contracts = math.floor((coin_qty / ct_val) / lot_sz) * lot_sz
        if contracts < min_sz:
            contracts = min_sz
        coin_qty = contracts * ct_val
        notional = coin_qty * entry
        margin = notional / lev
        tp = abs(float(take_profit_usd if take_profit_usd is not None else cfg.get("mech_take_profit_usd") or 2.0))
        sl = abs(float(stop_loss_usd if stop_loss_usd is not None else cfg.get("mech_stop_loss_usd") or tp))
        if coin_qty <= 0:
            return ScalpSkip(signal.asset, "zero sized quantity")
        # Rewrite stop/target to fixed USD distances so exchange TP hits ~$2 every fill.
        dist_tp = tp / coin_qty
        dist_sl = sl / coin_qty
        if signal.side == "buy":
            signal.stop_price = entry - dist_sl
            signal.target_price = entry + dist_tp
        else:
            signal.stop_price = entry + dist_sl
            signal.target_price = entry - dist_tp
        signal.stop_distance_pct = dist_sl / entry * 100.0
        if margin > max(float(available_balance or 0.0), 0.0) * 0.9:
            return ScalpSkip(signal.asset, f"margin ${margin:.2f} exceeds 90% of available ${available_balance:.2f}")
        return SizedOrder(
            contracts=contracts,
            coin_qty=coin_qty,
            notional_usd=notional,
            margin_usd=margin,
            risk_usd=sl,
            reward_usd=tp,
        )

    # Legacy: contracts so the wick stop loses ``risk_usd``.
    risk_target = max(float(risk_usd), 0.0) * factor
    dist = abs(signal.entry_price - signal.stop_price)
    if risk_target <= 0 or dist <= 0:
        return ScalpSkip(signal.asset, "zero risk budget or stop distance")

    coin_qty = risk_target / dist
    contracts = math.floor((coin_qty / ct_val) / lot_sz) * lot_sz
    if contracts < min_sz:
        contracts = min_sz
    coin_qty = contracts * ct_val
    actual_risk = coin_qty * dist
    tolerance = float(cfg["mech_min_size_risk_tolerance"])
    if actual_risk > risk_target * tolerance + 1e-9:
        return ScalpSkip(
            signal.asset,
            f"exchange minimum size would risk ${actual_risk:.2f} (> ${risk_target:.2f}); coin too violent for this book",
        )
    notional = coin_qty * signal.entry_price
    margin = notional / lev
    if margin > max(float(available_balance or 0.0), 0.0) * 0.9:
        return ScalpSkip(signal.asset, f"margin ${margin:.2f} exceeds 90% of available ${available_balance:.2f}")
    return SizedOrder(
        contracts=contracts,
        coin_qty=coin_qty,
        notional_usd=notional,
        margin_usd=margin,
        risk_usd=actual_risk,
        reward_usd=actual_risk,
    )


# --------------------------------------------------------------------------- stats
class ScalpStats:
    """Fill / cancel / close tallies persisted so a redeploy keeps the demo scorecard."""

    def __init__(self, path: str | Path = "mechanical_stats.json"):
        self.path = Path(path)
        self.data: Dict[str, Any] = self._fresh()
        self._load()

    @staticmethod
    def _fresh() -> Dict[str, Any]:
        return {
            "placed": 0, "filled": 0, "cancelled": 0,
            "closes": 0, "wins": 0, "losses": 0, "scratches": 0,
            "gross_profit": 0.0, "gross_loss": 0.0, "fees": 0.0,
            "last_close": None, "started_at": datetime.now(timezone.utc).isoformat(),
        }

    def _load(self) -> None:
        try:
            if self.path.exists():
                loaded = json.loads(self.path.read_text())
                if isinstance(loaded, dict):
                    self.data.update(loaded)
        except Exception as e:  # pragma: no cover - best effort
            logger.debug(f"mechanical stats load failed: {e}")

    def _save(self) -> None:
        try:
            self.path.write_text(json.dumps(self.data))
        except Exception as e:  # pragma: no cover
            logger.debug(f"mechanical stats save failed: {e}")

    def record_placed(self) -> None:
        self.data["placed"] += 1
        self._save()

    def record_filled(self) -> None:
        self.data["filled"] += 1
        self._save()

    def record_cancelled(self) -> None:
        self.data["cancelled"] += 1
        self._save()

    def record_close(self, pnl_usd: float, fee_usd: float = 0.0) -> None:
        pnl = float(pnl_usd or 0.0)
        self.data["closes"] += 1
        if pnl >= 0.5:
            self.data["wins"] += 1
            self.data["gross_profit"] += pnl
        elif pnl <= -0.5:
            self.data["losses"] += 1
            self.data["gross_loss"] += abs(pnl)
        else:
            self.data["scratches"] += 1
            if pnl >= 0:
                self.data["gross_profit"] += pnl
            else:
                self.data["gross_loss"] += abs(pnl)
        self.data["fees"] += abs(float(fee_usd or 0.0))
        self.data["last_close"] = {"pnl": round(pnl, 4), "at": datetime.now(timezone.utc).isoformat()}
        self._save()

    def reset(self) -> None:
        self.data = self._fresh()
        self._save()

    def summary(self) -> Dict[str, Any]:
        d = dict(self.data)
        decided = d["wins"] + d["losses"]
        d["win_rate_pct"] = round(d["wins"] / decided * 100.0, 1) if decided else None
        d["profit_factor"] = round(d["gross_profit"] / d["gross_loss"], 2) if d["gross_loss"] > 0 else (None if d["gross_profit"] == 0 else float("inf"))
        if d["profit_factor"] == float("inf"):
            d["profit_factor"] = 99.0
        d["net_pnl"] = round(d["gross_profit"] - d["gross_loss"], 2)
        d["fill_rate_pct"] = round(d["filled"] / d["placed"] * 100.0, 1) if d["placed"] else None
        return d
