"""Data models for the PulseGuard knee-replacement recovery prototype."""

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

WalkingAbility = Literal["unaided", "stick", "frame"]
FlagStatus = Literal["clear", "flagged", "pending"]


class Patient(BaseModel):
    """A patient recovering at home after a primary total knee replacement."""

    id: int
    name: str
    age: int
    surgery_date: date
    walking_ability: WalkingAbility = "unaided"


class DailyReading(BaseModel):
    """One day of wearable metrics plus the patient's pain score."""

    patient_id: int
    day: int = Field(ge=1, description="Days since surgery, starting at 1")
    steps: int = Field(ge=0)
    resting_hr: int = Field(ge=30, le=200, description="Resting heart rate in BPM")
    sleep_hours: float = Field(ge=0, le=24)
    pain: int = Field(ge=0, le=10, description="Patient-reported pain, 0 to 10")
    recorded_at: datetime = Field(default_factory=datetime.now)


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
    """Detail view: everything in the summary plus history and the band."""

    readings: list[DailyReading]
    band: list[BandPoint]
