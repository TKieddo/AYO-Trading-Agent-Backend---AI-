"""Forex session helpers.

FX is closed from Friday ~22:00 UTC to Sunday ~22:00 UTC (5pm New York). When the
market is shut IG may still return a stale last price, but there are no new candles —
calling DeepSeek in that state burns credits for a guaranteed hold.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional


def is_forex_session_open(now: Optional[datetime] = None) -> bool:
    """Return True when the major FX session is open (Sun 22:00 UTC → Fri 22:00 UTC)."""
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    else:
        now = now.astimezone(timezone.utc)

    weekday = now.weekday()  # Mon=0 … Sun=6
    minutes = now.hour * 60 + now.minute

    # Saturday always closed
    if weekday == 5:
        return False
    # Friday after 22:00 UTC closed
    if weekday == 4 and minutes >= 22 * 60:
        return False
    # Sunday before 22:00 UTC closed
    if weekday == 6 and minutes < 22 * 60:
        return False
    return True


def looks_like_forex(asset: str) -> bool:
    base = (asset or "").replace("/", "").replace("_", "").replace("-", "").upper()
    metals = ("XAUUSD", "XAGUSD", "GOLD", "SILVER")
    if base in metals or base.startswith("XAU") or base.startswith("XAG"):
        return True
    ccy = ("USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD")
    return len(base) >= 6 and base[:3] in ccy and base[3:6] in ccy
