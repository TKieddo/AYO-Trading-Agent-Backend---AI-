"""Higher-timeframe trend agreement filter.

Most of the churn came from taking longs and shorts on the same pair inside a range. A
single timeframe cannot distinguish a pullback from a reversal; requiring the entry
direction to agree with a slower timeframe removes the majority of counter-trend entries
at the cost of skipping some early reversals.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional, Tuple

from src.config_loader import CONFIG

logger = logging.getLogger(__name__)


def _setting(trading_settings: Optional[Dict[str, Any]], key: str, default: Any) -> Any:
    settings = trading_settings or {}
    value = settings.get(key)
    if value is None:
        value = CONFIG.get(key, default)
    return default if value is None else value


def check_trend_agreement(
    asset: str,
    is_long: bool,
    fetch_value: Callable[..., Optional[float]],
    trading_settings: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, str]:
    """Return ``(allowed, reason)`` for an entry based on the higher timeframe.

    Direction is taken from the fast/slow EMA relationship on the confirmation timeframe.
    If the indicator data is unavailable the trade is allowed — the filter should never be
    the reason a strategy stops trading entirely.
    """
    if not _setting(trading_settings, "enable_htf_trend_filter", True):
        return True, "htf filter disabled"

    timeframe = str(_setting(trading_settings, "htf_trend_timeframe", "1h"))
    fast_period = int(_setting(trading_settings, "htf_trend_fast_ema", 20) or 20)
    slow_period = int(_setting(trading_settings, "htf_trend_slow_ema", 50) or 50)
    min_separation_pct = float(_setting(trading_settings, "htf_trend_min_separation_pct", 0.0) or 0.0)

    asset_u = str(asset or "").replace("/", "").replace("_", "").upper()
    forex_ccy = ("USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD")
    if len(asset_u) >= 6 and asset_u[:3] in forex_ccy and asset_u[3:6] in forex_ccy:
        symbol = f"{asset_u[:3]}/{asset_u[3:6]}"
    else:
        symbol = f"{asset}/USDT"
    try:
        fast = fetch_value("ema", symbol, timeframe, params={"period": fast_period}, key="value")
        slow = fetch_value("ema", symbol, timeframe, params={"period": slow_period}, key="value")
    except Exception as e:
        logger.debug(f"HTF trend fetch failed for {asset}: {e}")
        return True, "htf data unavailable"

    if not fast or not slow or slow <= 0:
        return True, "htf data unavailable"

    separation_pct = ((fast - slow) / slow) * 100.0

    # A flat higher timeframe is a range, not a trend — treat it as no signal either way.
    if min_separation_pct > 0 and abs(separation_pct) < min_separation_pct:
        if _setting(trading_settings, "htf_block_when_flat", True):
            return False, (
                f"{asset} {timeframe} is flat (EMA{fast_period} within "
                f"{abs(separation_pct):.2f}% of EMA{slow_period}, need {min_separation_pct:.2f}%)"
            )
        return True, "htf flat but flat-blocking disabled"

    htf_is_up = separation_pct > 0
    if htf_is_up == is_long:
        return True, (
            f"{asset} {timeframe} trend {'up' if htf_is_up else 'down'} "
            f"({separation_pct:+.2f}%) agrees with {'long' if is_long else 'short'}"
        )

    return False, (
        f"{asset} counter-trend: {timeframe} is {'up' if htf_is_up else 'down'} "
        f"({separation_pct:+.2f}%) but signal is {'long' if is_long else 'short'}"
    )
