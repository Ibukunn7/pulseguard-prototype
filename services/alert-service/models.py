"""Models the alert service reads from the other services and serves to the dashboard."""

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

WalkingAbility = Literal["unaided", "stick", "frame"]
FlagStatus = Literal["clear", "flagged", "pending"]


class Patient(BaseModel):
    """As served by the patient service."""

    id: int
    name: str
    age: int
    surgery_date: date
    walking_ability: WalkingAbility = "unaided"


class DailyReading(BaseModel):
    """As served by the telemetry service."""

    patient_id: int
    day: int = Field(ge=1)
    steps: int = Field(ge=0)
    resting_hr: int
    sleep_hours: float
    pain: int = Field(ge=0, le=10)
    recorded_at: Optional[datetime] = None


class Flag(BaseModel):
    """Result of one clinical flag rule for one patient."""

    name: Literal["mobilisation", "complication", "pain"]
    status: FlagStatus
    reason: str


class PatientSummary(BaseModel):
    """List-view entry: patient, latest reading and current flags."""

    patient: Patient
    day: int
    week: int
    latest: Optional[DailyReading]
    baseline_hr: Optional[float]
    flags: list[Flag]
    flag_count: int


class BandPoint(BaseModel):
    """Expected step range for one recovery day."""

    day: int
    low: int
    high: int


class PatientDetail(PatientSummary):
    """Detail view: summary plus history and the expected band."""

    readings: list[DailyReading]
    band: list[BandPoint]
