"""Partial take-profit ladder.

Closing the whole position at one target means any trade that runs to the target and
reverses before filling becomes a full loss. Scaling out banks part of the move as soon as
the trade has earned one unit of risk, which is what turns marginal trades into small wins
and lifts realised win rate without needing better entries.

The ladder is expressed in R multiples, where one R is the stop distance, so it adapts to
whatever volatility-derived stop the position was opened with.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from src.config_loader import CONFIG

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LadderRung:
    """One scale-out step: close `size_pct` of the original size at `r_multiple`."""

    r_multiple: float
    size_pct: float


@dataclass
class LadderState:
    """Fill progress for one open position."""

    original_size: float
    rungs_filled: List[int] = field(default_factory=list)
    breakeven_armed: bool = False

    def remaining_pct(self, rungs: List[LadderRung]) -> float:
        taken = sum(rungs[i].size_pct for i in self.rungs_filled if i < len(rungs))
        return max(0.0, 100.0 - taken)


# asset -> LadderState
_STATES: Dict[str, LadderState] = {}


def parse_ladder(spec: Any) -> List[LadderRung]:
    """Parse a ladder spec into rungs.

    Accepts ``"1.0:50,2.0:30"`` (R multiple : percent of original size) or an already
    structured list of dicts/pairs. Rungs are returned sorted by R multiple. An empty or
    unparseable spec yields no rungs, which disables scaling out.
    """
    if not spec:
        return []

    raw_pairs: List[Tuple[Any, Any]] = []
    if isinstance(spec, str):
        for chunk in spec.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            if ":" not in chunk:
                logger.warning(f"Ignoring malformed ladder rung '{chunk}' (expected R:size_pct)")
                continue
            r_raw, size_raw = chunk.split(":", 1)
            raw_pairs.append((r_raw, size_raw))
    elif isinstance(spec, (list, tuple)):
        for item in spec:
            if isinstance(item, dict):
                raw_pairs.append((item.get("r") or item.get("r_multiple"), item.get("size_pct") or item.get("size")))
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                raw_pairs.append((item[0], item[1]))
    else:
        logger.warning(f"Unsupported ladder spec type: {type(spec).__name__}")
        return []

    rungs: List[LadderRung] = []
    for r_raw, size_raw in raw_pairs:
        try:
            r_multiple = float(r_raw)
            size_pct = float(size_raw)
        except (TypeError, ValueError):
            logger.warning(f"Ignoring malformed ladder rung '{r_raw}:{size_raw}'")
            continue
        if r_multiple <= 0 or size_pct <= 0:
            continue
        rungs.append(LadderRung(r_multiple=r_multiple, size_pct=min(size_pct, 100.0)))

    rungs.sort(key=lambda x: x.r_multiple)

    total = sum(r.size_pct for r in rungs)
    if total > 100.0:
        logger.warning(f"Ladder rungs total {total:.0f}% of position; trimming to 100%")
        trimmed: List[LadderRung] = []
        budget = 100.0
        for rung in rungs:
            if budget <= 0:
                break
            take = min(rung.size_pct, budget)
            trimmed.append(LadderRung(rung.r_multiple, take))
            budget -= take
        rungs = trimmed

    return rungs


def get_ladder(trading_settings: Optional[Dict[str, Any]] = None) -> List[LadderRung]:
    settings = trading_settings or {}
    spec = settings.get("profit_ladder")
    if spec is None:
        spec = CONFIG.get("profit_ladder")
    return parse_ladder(spec)


def register_position(asset: str, original_size: float) -> None:
    """Record the size a position opened with, so rung sizes stay proportional."""
    key = (asset or "").upper()
    if original_size <= 0:
        return
    _STATES[key] = LadderState(original_size=float(original_size))


def next_fill(
    asset: str,
    r_multiple: float,
    current_size: float,
    trading_settings: Optional[Dict[str, Any]] = None,
) -> Optional[Tuple[float, LadderRung, float]]:
    """Return ``(size_to_close, rung, remaining_pct)`` if a rung is due, else None.

    Only the highest rung reached is filled per call, so a fast move through several rungs
    still closes them one at a time on successive monitor cycles.
    """
    key = (asset or "").upper()
    rungs = get_ladder(trading_settings)
    if not rungs or current_size <= 0:
        return None

    state = _STATES.get(key)
    if state is None:
        # Position opened before the ladder was registered — anchor on what we can see.
        state = LadderState(original_size=float(current_size))
        _STATES[key] = state

    due = [
        i for i, rung in enumerate(rungs)
        if i not in state.rungs_filled and r_multiple >= rung.r_multiple
    ]
    if not due:
        return None

    index = due[0]
    rung = rungs[index]
    size_to_close = min(state.original_size * (rung.size_pct / 100.0), current_size)
    if size_to_close <= 0:
        return None

    state.rungs_filled.append(index)
    remaining_pct = state.remaining_pct(rungs)
    return size_to_close, rung, remaining_pct


def mark_breakeven_armed(asset: str) -> None:
    state = _STATES.get((asset or "").upper())
    if state:
        state.breakeven_armed = True


def is_breakeven_armed(asset: str) -> bool:
    state = _STATES.get((asset or "").upper())
    return bool(state and state.breakeven_armed)


def has_taken_profit(asset: str) -> bool:
    """True once at least one rung has filled — used to arm the breakeven stop."""
    state = _STATES.get((asset or "").upper())
    return bool(state and state.rungs_filled)


def clear(asset: Optional[str] = None) -> None:
    if asset:
        _STATES.pop(asset.upper(), None)
    else:
        _STATES.clear()


def snapshot() -> Dict[str, Dict[str, Any]]:
    return {
        k: {
            "original_size": v.original_size,
            "rungs_filled": list(v.rungs_filled),
            "breakeven_armed": v.breakeven_armed,
        }
        for k, v in _STATES.items()
    }
