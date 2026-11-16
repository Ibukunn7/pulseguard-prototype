"""Alert service: the clinical logic, and the only service the dashboard calls.

Stores nothing. On each request it fetches patients from the patient
service and readings from the telemetry service, then computes the
expected band, the resting heart rate baseline and the three flags.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import clients
from models import Patient, PatientDetail, PatientSummary
from recovery import band_series, baseline_hr, evaluate, week_of

app = FastAPI(title="PulseGuard Alert Service", version="0.3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _summary(patient: Patient) -> PatientSummary:
    readings = clients.get_readings(patient.id)
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


@app.get("/health")
def health():
    return {"status": "ok", "service": "alert"}


@app.get("/status")
def status():
    """Dependency health plus the simulator's time scale, for the dashboard header."""
    return {"services": {"alert": "up", **clients.upstream_status()},
            "simulation": clients.get_simulation()}


@app.get("/patients", response_model=list[PatientSummary])
def list_patients():
    """Monitored patients, most flags first, then most recent day."""
    summaries = [_summary(p) for p in clients.list_patients()]
    summaries.sort(key=lambda s: (-s.flag_count, -s.day, s.patient.name))
    return summaries


@app.get("/patients/{patient_id}", response_model=PatientDetail)
def get_patient(patient_id: int):
    patient = clients.get_patient(patient_id)
    summary = _summary(patient)
    readings = sorted(clients.get_readings(patient_id), key=lambda r: r.day)
    return PatientDetail(
        **summary.model_dump(),
        readings=readings,
        band=band_series(max(summary.day, 1), patient.walking_ability),
    )
