from pydantic import BaseModel
from datetime import datetime


class VitalReading(BaseModel):
    patient_id: int
    patient_name: str
    heart_rate: int
    sleep_hours: float
    timestamp: datetime