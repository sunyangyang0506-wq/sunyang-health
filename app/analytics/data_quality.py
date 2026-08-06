from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable


@dataclass
class QualityResult:
    confidence: str
    usable: bool
    conflicts: list[str]
    notes: list[str]


def evaluate_coverage(days_with_data: int, window_days: int, minimum_ratio: float = 0.6) -> tuple[float, bool]:
    if window_days <= 0:
        return 0.0, False
    ratio = days_with_data / window_days
    return ratio, ratio >= minimum_ratio


def detect_same_day_conflicts(metric: str, values: Iterable[float]) -> list[str]:
    values = [float(v) for v in values]
    if len(values) < 2:
        return []

    spread = max(values) - min(values)
    thresholds = {
        "weight_kg": 2.0,
        "body_fat_percent": 3.0,
        "resting_heart_rate": 15.0,
        "hrv_ms": 40.0,
    }
    threshold = thresholds.get(metric)
    if threshold is not None and spread > threshold:
        return [f"{metric} same-day spread {spread:.2f} exceeds threshold {threshold:.2f}"]
    return []


def freshness_status(recorded_at: datetime, now: datetime | None = None, max_age_days: int = 7) -> str:
    now = now or datetime.now(recorded_at.tzinfo)
    age = now - recorded_at
    if age <= timedelta(days=max_age_days):
        return "current"
    if age <= timedelta(days=max_age_days * 4):
        return "recent_history"
    return "historical"


def assess_record(metric: str, values_same_day: Iterable[float], source: str, recorded_at: datetime) -> QualityResult:
    conflicts = detect_same_day_conflicts(metric, values_same_day)
    confidence = "B" if source.lower().startswith("apple") else "C"
    notes = [f"freshness={freshness_status(recorded_at)}", f"source={source}"]
    if conflicts:
        return QualityResult(confidence="E", usable=False, conflicts=conflicts, notes=notes)
    return QualityResult(confidence=confidence, usable=True, conflicts=[], notes=notes)
