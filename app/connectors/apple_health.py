from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


APPLE_HEALTH_METRIC_MAP = {
    "bodyMass": "weight_kg",
    "bodyMassIndex": "bmi",
    "bodyFatPercentage": "body_fat_percent",
    "leanBodyMass": "lean_body_mass_kg",
    "stepCount": "steps",
    "activeEnergyBurned": "active_calories",
    "appleExerciseTime": "exercise_minutes",
    "distanceWalkingRunning": "distance_km",
    "heartRateVariabilitySDNN": "hrv_ms",
    "restingHeartRate": "resting_heart_rate",
    "vo2Max": "vo2max",
    "sleepAnalysis": "sleep_hours",
}


@dataclass
class NormalizedHealthRecord:
    recorded_at: datetime
    metric: str
    value: float
    source: str = "Apple Health"
    confidence: str = "B"
    unit: str | None = None
    raw_metric: str | None = None


def _lb_to_kg(value: float) -> float:
    return value * 0.45359237


def _mi_to_km(value: float) -> float:
    return value * 1.609344


def normalize_metric(metric: str, value: float, unit: str | None = None) -> tuple[str, float, str | None]:
    canonical = APPLE_HEALTH_METRIC_MAP.get(metric, metric)

    if metric in {"bodyMass", "leanBodyMass"} and unit in {"lb", "lbs"}:
        return canonical, _lb_to_kg(value), "kg"

    if metric == "distanceWalkingRunning" and unit in {"mi", "mile", "miles"}:
        return canonical, _mi_to_km(value), "km"

    if metric == "sleepAnalysis" and unit in {"min", "minute", "minutes"}:
        return canonical, value / 60.0, "h"

    return canonical, value, unit


def normalize_sample(sample: dict[str, Any]) -> NormalizedHealthRecord:
    metric = sample["metric"]
    value = float(sample["value"])
    unit = sample.get("unit")
    canonical, normalized_value, normalized_unit = normalize_metric(metric, value, unit)
    recorded_at = sample["recorded_at"]
    if isinstance(recorded_at, str):
        recorded_at = datetime.fromisoformat(recorded_at.replace("Z", "+00:00"))

    return NormalizedHealthRecord(
        recorded_at=recorded_at,
        metric=canonical,
        value=normalized_value,
        source=sample.get("source", "Apple Health"),
        confidence=sample.get("confidence", "B"),
        unit=normalized_unit,
        raw_metric=metric,
    )
