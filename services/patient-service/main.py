"""Patient service: who is being monitored and when their surgery was.

Owns the patient registry. Knows nothing about readings or flags.
"""

from datetime import date, timedelta
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="PulseGuard Patient Service", version="0.3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

WalkingAbility = Literal["unaided", "stick", "frame"]


class Patient(BaseModel):
    id: int
    name: str
    age: int = Field(ge=18, le=110)
    surgery_date: date
    walking_ability: WalkingAbility = "unaided"


class NewPatient(BaseModel):
    name: str
    age: int = Field(ge=18, le=110)
    surgery_date: date
    walking_ability: WalkingAbility = "unaided"


# In-memory registry. Becomes a PostgreSQL table in the next phase.
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


@app.get("/health")
def health():
    return {"status": "ok", "service": "patient", "patients": len(PATIENTS)}


@app.get("/patients", response_model=list[Patient])
def list_patients():
    return sorted(PATIENTS.values(), key=lambda p: p.id)


@app.get("/patients/{patient_id}", response_model=Patient)
def get_patient(patient_id: int):
    patient = PATIENTS.get(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@app.post("/patients", response_model=Patient, status_code=201)
def create_patient(new: NewPatient):
    next_id = max(PATIENTS, default=0) + 1
    patient = Patient(id=next_id, **new.model_dump())
    PATIENTS[next_id] = patient
    return patient
