"""Per-asset re-entry cooldown.

On net-mode exchanges an opposite-side order closes the open position, so a flip-flopping
signal turns into a churn of small losses plus fees. This guard records every close and
refuses new entries on that asset until the cooldown expires.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# asset -> {"until": datetime, "side": "long"|"short"|None, "was_loss": bool, "pnl": float}
_COOLDOWNS: Dict[str, Dict[str, Any]] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def record_close(
    asset: str,
    pnl_usd: float,
    was_long: bool,
    trading_settings: Optional[Dict[str, Any]] = None,
) -> None:
    """Start a cooldown for `asset` after a position closes."""
    settings = trading_settings or {}
    was_loss = float(pnl_usd or 0.0) < 0

    minutes = float(
        settings.get("loss_reentry_cooldown_minutes", 90.0) if was_loss
        else settings.get("reentry_cooldown_minutes", 45.0)
    )
    if minutes <= 0:
        return

    key = (asset or "").upper()
    _COOLDOWNS[key] = {
        "until": _now() + timedelta(minutes=minutes),
        "side": "long" if was_long else "short",
        "was_loss": was_loss,
        "pnl": float(pnl_usd or 0.0),
    }
    logger.info(
        f"⏳ Re-entry cooldown for {key}: {minutes:.0f}m "
        f"({'loss' if was_loss else 'win'} ${pnl_usd:.2f})"
    )


def check_entry(
    asset: str,
    is_long: bool,
    trading_settings: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, Optional[str]]:
    """Return ``(allowed, reason_if_blocked)`` for a proposed entry."""
    settings = trading_settings or {}
    key = (asset or "").upper()
    entry = _COOLDOWNS.get(key)
    if not entry:
        return True, None

    remaining = (entry["until"] - _now()).total_seconds()
    if remaining <= 0:
        _COOLDOWNS.pop(key, None)
        return True, None

    proposed_side = "long" if is_long else "short"
    block_flip = bool(settings.get("block_direction_flip", True))

    # A reversal right after a stop-out is the churn pattern we're guarding against.
    if block_flip and entry["side"] and proposed_side != entry["side"]:
        return False, (
            f"{key} direction flip blocked: last close was {entry['side']}, "
            f"{remaining / 60:.0f}m cooldown remaining"
        )

    return False, f"{key} in re-entry cooldown for another {remaining / 60:.0f}m"


def active_cooldowns() -> Dict[str, Dict[str, Any]]:
    """Snapshot of live cooldowns, pruned of anything expired."""
    now = _now()
    for key in [k for k, v in _COOLDOWNS.items() if v["until"] <= now]:
        _COOLDOWNS.pop(key, None)
    return {
        k: {
            "until": v["until"].isoformat(),
            "side": v["side"],
            "was_loss": v["was_loss"],
            "minutes_remaining": round((v["until"] - now).total_seconds() / 60, 1),
        }
        for k, v in _COOLDOWNS.items()
    }


def clear(asset: Optional[str] = None) -> None:
    """Clear one asset's cooldown, or all of them."""
    if asset:
        _COOLDOWNS.pop(asset.upper(), None)
    else:
        _COOLDOWNS.clear()
