"""Volatility-adaptive exit distances.

The legacy exits compare against margin ROI, so a "3% stop" at 10x leverage is really a
0.3% price move — well inside normal noise. These helpers express the stop as a multiple of
recent ATR in *price* terms, then convert to ROI only where the existing checks need it.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from src.config_loader import CONFIG

logger = logging.getLogger(__name__)


@dataclass
class ExitPlan:
    """Stop and target distances for a single position."""

    stop_price_pct: float       # Stop distance as % of entry price
    target_price_pct: float     # Target distance as % of entry price
    stop_roi_pct: float         # Same stop, expressed as % of margin
    target_roi_pct: float       # Same target, expressed as % of margin
    atr_pct: Optional[float]    # ATR% used to derive it (None = fell back to fixed)
    source: str                 # "atr" or "fixed"

    def stop_price(self, entry_price: float, is_long: bool) -> float:
        delta = entry_price * (self.stop_price_pct / 100.0)
        return entry_price - delta if is_long else entry_price + delta

    def target_price(self, entry_price: float, is_long: bool) -> float:
        delta = entry_price * (self.target_price_pct / 100.0)
        return entry_price + delta if is_long else entry_price - delta


def calculate_atr_percent(candles: Sequence[Sequence[Any]], period: int = 14) -> Optional[float]:
    """ATR over `period` candles, expressed as a percentage of the latest close.

    Accepts OHLCV rows in the common exchange layout where index 2/3/4 are high/low/close.
    """
    if not candles or len(candles) < period + 1:
        return None

    true_ranges: List[float] = []
    for i in range(len(candles) - period, len(candles)):
        if i <= 0:
            continue
        try:
            high = float(candles[i][2])
            low = float(candles[i][3])
            prev_close = float(candles[i - 1][4])
        except (IndexError, TypeError, ValueError):
            return None
        true_ranges.append(max(high - low, abs(high - prev_close), abs(low - prev_close)))

    if not true_ranges:
        return None

    atr = sum(true_ranges) / len(true_ranges)
    try:
        last_close = float(candles[-1][4])
    except (IndexError, TypeError, ValueError):
        return None

    if last_close <= 0:
        return None
    return (atr / last_close) * 100.0


def build_exit_plan(
    trading_settings: Dict[str, Any],
    leverage: float,
    atr_pct: Optional[float] = None,
) -> ExitPlan:
    """Resolve stop/target distances for a trade.

    In ``atr`` mode the stop is ``sl_atr_mult x atr_pct`` of price, clamped to the configured
    floor and ceiling, and the target is ``tp_rr_ratio`` times that distance. In ``fixed`` mode
    the legacy ROI percentages are used unchanged so existing deployments keep their behaviour.
    """
    leverage = max(float(leverage or 1.0), 1.0)
    mode = str(trading_settings.get("exit_mode") or CONFIG.get("exit_mode", "fixed")).lower()

    fixed_sl_roi = float(trading_settings.get("stop_loss_percent") or CONFIG.get("stop_loss_percent", 8) or 8)
    fixed_tp_roi = float(trading_settings.get("take_profit_percent") or CONFIG.get("take_profit_percent", 7) or 7)

    if mode != "atr" or atr_pct is None or atr_pct <= 0:
        if mode == "atr":
            logger.debug("ATR exit mode requested but no usable ATR; falling back to fixed percentages")
        return ExitPlan(
            stop_price_pct=fixed_sl_roi / leverage,
            target_price_pct=fixed_tp_roi / leverage,
            stop_roi_pct=fixed_sl_roi,
            target_roi_pct=fixed_tp_roi,
            atr_pct=atr_pct,
            source="fixed",
        )

    sl_mult = float(trading_settings.get("sl_atr_mult") or CONFIG.get("sl_atr_mult", 2.0) or 2.0)
    rr = float(trading_settings.get("tp_rr_ratio") or CONFIG.get("tp_rr_ratio", 2.5) or 2.5)
    min_stop = float(trading_settings.get("min_stop_price_pct") or CONFIG.get("min_stop_price_pct", 0.6) or 0.6)
    max_stop = float(trading_settings.get("max_stop_price_pct") or CONFIG.get("max_stop_price_pct", 4.0) or 4.0)

    stop_price_pct = min(max(atr_pct * sl_mult, min_stop), max_stop)
    target_price_pct = stop_price_pct * rr

    return ExitPlan(
        stop_price_pct=stop_price_pct,
        target_price_pct=target_price_pct,
        stop_roi_pct=stop_price_pct * leverage,
        target_roi_pct=target_price_pct * leverage,
        atr_pct=atr_pct,
        source="atr",
    )


def max_safe_leverage(stop_price_pct: float, buffer_multiple: float = 3.0) -> float:
    """Largest leverage that keeps liquidation at least `buffer_multiple` stops away.

    Liquidation sits roughly ``100 / leverage`` percent away before maintenance margin, so a
    stop of ``s`` percent needs ``leverage <= 100 / (s * buffer_multiple)``.
    """
    if stop_price_pct <= 0:
        return 1.0
    return max(1.0, 100.0 / (stop_price_pct * max(buffer_multiple, 1.0)))
