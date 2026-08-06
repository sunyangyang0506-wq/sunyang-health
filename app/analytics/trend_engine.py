from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from statistics import mean
from typing import Iterable, Sequence


@dataclass
class TrendWindow:
    days: int
    values: list[float]
    average: float | None
    first: float | None
    last: float | None
    change: float | None
    direction: str


def _direction(change: float | None, tolerance: float = 0.0) -> str:
    if change is None:
        return "insufficient_data"
    if change > tolerance:
        return "up"
    if change < -tolerance:
        return "down"
    return "stable"


def summarize_window(values: Sequence[float], days: int, tolerance: float = 0.0) -> TrendWindow:
    clean = [float(v) for v in values if v is not None]
    if not clean:
        return TrendWindow(days, [], None, None, None, None, "insufficient_data")
    first = clean[0]
    last = clean[-1]
    change = last - first if len(clean) >= 2 else 0.0
    return TrendWindow(
        days=days,
        values=clean,
        average=mean(clean),
        first=first,
        last=last,
        change=change,
        direction=_direction(change, tolerance=tolerance),
    )


def build_7_14_30_trends(daily_values: Sequence[float], tolerance: float = 0.0) -> dict[int, TrendWindow]:
    return {
        7: summarize_window(daily_values[-7:], 7, tolerance),
        14: summarize_window(daily_values[-14:], 14, tolerance),
        30: summarize_window(daily_values[-30:], 30, tolerance),
    }


def compare_recent_vs_prior(daily_values: Sequence[float], window: int = 7) -> dict[str, float | str | None]:
    values = [float(v) for v in daily_values if v is not None]
    if len(values) < window * 2:
        return {"recent_avg": None, "prior_avg": None, "delta": None, "direction": "insufficient_data"}

    prior = values[-window * 2:-window]
    recent = values[-window:]
    prior_avg = mean(prior)
    recent_avg = mean(recent)
    delta = recent_avg - prior_avg
    return {
        "recent_avg": recent_avg,
        "prior_avg": prior_avg,
        "delta": delta,
        "direction": _direction(delta),
    }
