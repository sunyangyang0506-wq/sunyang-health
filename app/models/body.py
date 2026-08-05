from datetime import date
from pydantic import BaseModel


class BodyMetrics(BaseModel):
    record_date: date
    weight_kg: float
    bmi: float | None = None
    body_fat_percent: float | None = None
    muscle_mass_kg: float | None = None
    basal_metabolic_rate: float | None = None
    source: str = "unknown"
    confidence: str = "B"
