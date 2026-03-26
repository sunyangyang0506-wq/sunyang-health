from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RecoveryLevel(str, Enum):
    PUSH = "适合冲"
    STEADY = "适合稳"
    RECOVER = "建议恢复"


class CommunicationStyle(str, Enum):
    RATIONAL = "理性直接型"
    COMPANION = "温和陪伴型"
    ENCOURAGING = "鼓励驱动型"
    AUTONOMOUS = "高自主型"


@dataclass(slots=True)
class UserProfile:
    user_id: str
    goal: str
    weekly_frequency: int
    preferred_style: CommunicationStyle | None = None


@dataclass(slots=True)
class DailySignals:
    sleep_hours: float
    sleep_trend_delta: float
    consecutive_training_days: int
    subjective_fatigue: int  # 1-10
    resting_heart_rate_delta: float  # vs baseline
    lower_body_load_high: bool = False
    meal_protein_gap_g: int = 0
    calorie_over_target: int = 0


@dataclass(slots=True)
class DailyDecision:
    recovery_level: RecoveryLevel
    reason: str
    training_action: str
    nutrition_action: str


@dataclass(slots=True)
class WeeklySummaryInput:
    training_completion_rate: float
    weight_delta_kg: float
    high_calorie_meals: int
    avg_sleep_hours: float


@dataclass(slots=True)
class WeeklySummary:
    progress: str
    blocker: str
    effective_behavior: str
    next_single_action: str
