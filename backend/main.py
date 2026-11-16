"""PulseGuard backend: ingests daily readings and serves flags to the dashboard."""

from datetime import date, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from models import DailyReading, Patient, PatientDetail, PatientSummary
from recovery import band_series, baseline_hr, evaluate, week_of

app = FastAPI(title="PulseGuard API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory store. Replaced by a patient service and a telemetry service with
# PostgreSQL in the next architecture phase.
# ---------------------------------------------------------------------------

_today = date.today()

PATIENTS: dict[int, Patient] = {
    p.id: p
    for p in [
        Patient(id=1, name="John Doe", age=67, surgery_date=_today - timedelta(days=42), walking_ability="unaided"),
        Patient(id=2, name="Sarah Smith", age=72, surgery_date=_today - timedelta(days=42), walking_ability="stick"),
        Patient(id=3, name="Tom Murphy", age=64, surgery_date=_today - timedelta(days=42), walking_ability="unaided"),
        Patient(id=4, name="Jane Kelly", age=70, surgery_date=_today - timedelta(days=42), walking_ability="unaided"),
        Patient(id=5, name="Mark Ryan", age=75, surgery_date=_today - timedelta(days=42), walking_ability="frame"),
    ]
}

READINGS: dict[int, list[DailyReading]] = {pid: [] for pid in PATIENTS}

# Set by the simulator so the dashboard can say how fast demo time runs.
# Real readings arrive once a day; this is None when no simulator is attached.
SIMULATION: dict = {"seconds_per_day": None, "total_days": None}


class SimulationConfig(BaseModel):
    seconds_per_day: float = Field(gt=0)
    total_days: int = Field(gt=0)


def _summary(patient: Patient) -> PatientSummary:
    readings = READINGS[patient.id]
    latest = max(readings, key=lambda r: r.day) if readings else None
    day = latest.day if latest else 0
    flags = evaluate(readings, patient.walking_ability)
    return PatientSummary(
        patient=patient,
        day=day,
        week=week_of(day) if day else 0,
        latest=latest,
        baseline_hr=baseline_hr(readings),
        flags=flags,
        flag_count=sum(1 for f in flags if f.status == "flagged"),
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def home():
    return {"message": "PulseGuard Backend Running", "version": app.version}


@app.get("/health")
def health():
    return {"status": "ok", "patients": len(PATIENTS),
            "readings": sum(len(r) for r in READINGS.values()),
            "simulation": SIMULATION}


@app.put("/simulation")
def set_simulation(config: SimulationConfig):
    """Called by the simulator on start so the dashboard can label demo time."""
    SIMULATION.update(config.model_dump())
    return SIMULATION


@app.get("/patients", response_model=list[PatientSummary])
def list_patients():
    """Monitored patients, most flags first, then most recent day."""
    summaries = [_summary(p) for p in PATIENTS.values()]
    summaries.sort(key=lambda s: (-s.flag_count, -s.day, s.patient.name))
    return summaries


@app.get("/patients/{patient_id}", response_model=PatientDetail)
def get_patient(patient_id: int):
    patient = PATIENTS.get(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    summary = _summary(patient)
    readings = sorted(READINGS[patient_id], key=lambda r: r.day)
    return PatientDetail(
        **summary.model_dump(),
        readings=readings,
        band=band_series(max(summary.day, 1), patient.walking_ability),
    )


@app.post("/readings", status_code=201)
def add_reading(reading: DailyReading):
    """Submit one day of metrics. Called by the simulator today and by a
    patient app in a later phase. A repeated day replaces the earlier entry."""
    if reading.patient_id not in PATIENTS:
        raise HTTPException(status_code=404, detail="Patient not found")
    store = READINGS[reading.patient_id]
    store[:] = [r for r in store if r.day != reading.day]
    store.append(reading)
    patient = PATIENTS[reading.patient_id]
    return {"message": "Reading added", "flags": evaluate(store, patient.walking_ability)}


@app.delete("/readings", status_code=204)
def reset_readings():
    """Clear all readings so the simulator can replay from day 1."""
    for store in READINGS.values():
        store.clear()


# Legacy endpoint kept for one release so the old dashboard still loads.
@app.get("/vitals")
def get_vitals():
    return [
        {"reading": {"patient_id": s.patient.id, "patient_name": s.patient.name,
                     "heart_rate": s.latest.resting_hr if s.latest else None,
                     "sleep_hours": s.latest.sleep_hours if s.latest else None,
                     "timestamp": s.latest.recorded_at if s.latest else None},
         "alert": "HIGH RISK" if s.flag_count else "NORMAL"}
        for s in list_patients() if s.latest
    ]
