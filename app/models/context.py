from __future__ import annotations

from datetime import date
from pydantic import BaseModel, Field


class MedicationContext(BaseModel):
    record_date: date
    medication_name: str
    dose_text: str | None = None
    taken_time: str | None = None
    source: str = "user"


class LabResult(BaseModel):
    record_date: date
    test_name: str
    value: float | str
    unit: str | None = None
    reference_range: str | None = None
    clinician_target: str | None = None
    source: str = "medical"


class MenstrualContext(BaseModel):
    record_date: date
    cycle_day: int | None = None
    phase: str | None = None
    bleeding: str | None = None
    symptoms: list[str] = Field(default_factory=list)
    source: str = "user"


class SubjectiveContext(BaseModel):
    record_date: date
    fatigue: int | None = Field(default=None, ge=0, le=10)
    hunger: int | None = Field(default=None, ge=0, le=10)
    stress: int | None = Field(default=None, ge=0, le=10)
    mood: str | None = None
    edema: bool | None = None
    bowel_note: str | None = None
    symptoms: list[str] = Field(default_factory=list)
    source: str = "user"
