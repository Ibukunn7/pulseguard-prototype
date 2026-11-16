"""Telemetry service: receives and stores daily readings.

Deliberately knows nothing about patients beyond their id, and nothing
about what a reading means. Today the simulator posts here; later a patient
app does. Today the store is in memory; later it is PostgreSQL.
"""

from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="PulseGuard Telemetry Service", version="0.3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class DailyReading(BaseModel):
    """One day of wearable metrics plus the patient's pain score."""

    patient_id: int
    day: int = Field(ge=1, description="Days since surgery, starting at 1")
    steps: int = Field(ge=0)
    resting_hr: int = Field(ge=30, le=200)
    sleep_hours: float = Field(ge=0, le=24)
    pain: int = Field(ge=0, le=10)
    recorded_at: datetime = Field(default_factory=datetime.now)


class SimulationConfig(BaseModel):
    seconds_per_day: float = Field(gt=0)
    total_days: int = Field(gt=0)


# patient_id -> day -> reading. A repeated day replaces the earlier entry.
READINGS: dict[int, dict[int, DailyReading]] = {}

# Set by the simulator so the dashboard can label demo time.
SIMULATION: dict[str, Optional[float]] = {"seconds_per_day": None, "total_days": None}


@app.get("/health")
def health():
    return {"status": "ok", "service": "telemetry",
            "patients_with_data": len(READINGS),
            "readings": sum(len(d) for d in READINGS.values())}


@app.post("/readings", status_code=201)
def add_reading(reading: DailyReading):
    READINGS.setdefault(reading.patient_id, {})[reading.day] = reading
    return {"message": "Reading stored", "patient_id": reading.patient_id,
            "day": reading.day, "days_recorded": len(READINGS[reading.patient_id])}


@app.get("/readings/{patient_id}", response_model=list[DailyReading])
def get_readings(patient_id: int):
    """All readings for a patient in day order. Empty list if none yet."""
    return [READINGS.get(patient_id, {})[d] for d in sorted(READINGS.get(patient_id, {}))]


@app.delete("/readings", status_code=204)
def reset_readings():
    """Clear everything so the simulator can replay from day 1."""
    READINGS.clear()


@app.get("/simulation")
def get_simulation():
    return SIMULATION


@app.put("/simulation")
def set_simulation(config: SimulationConfig):
    SIMULATION.update(config.model_dump())
    return SIMULATION
