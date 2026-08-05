from datetime import date
from pydantic import BaseModel


class ActivityMetrics(BaseModel):
    record_date: date
    steps: int
    active_calories: float
    exercise_minutes: int
    distance_km: float
    vo2max: float | None = None
    resting_heart_rate: int | None = None
    hrv_ms: float | None = None
    source: str = "Apple Health"
