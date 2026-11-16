"""HTTP clients for the patient and telemetry services.

Base URLs come from the environment so the same image runs under compose
(service names) and on a laptop (localhost ports). Every call has a short
timeout and turns a connection failure into a 503 with a clear message,
so the dashboard can say which dependency is down instead of hanging.
"""

import os

import httpx
from fastapi import HTTPException

from models import DailyReading, Patient

PATIENT_URL = os.getenv("PATIENT_SERVICE_URL", "http://127.0.0.1:8001").rstrip("/")
TELEMETRY_URL = os.getenv("TELEMETRY_SERVICE_URL", "http://127.0.0.1:8002").rstrip("/")
TIMEOUT = float(os.getenv("UPSTREAM_TIMEOUT_SECONDS", "3"))


def _get(base: str, path: str, service: str):
    try:
        response = httpx.get(f"{base}{path}", timeout=TIMEOUT)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503,
                            detail=f"{service} service unreachable at {base}: {type(exc).__name__}")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=response.json().get("detail", "Not found"))
    if response.is_error:
        raise HTTPException(status_code=502,
                            detail=f"{service} service returned {response.status_code}")
    return response.json()


def list_patients() -> list[Patient]:
    return [Patient(**p) for p in _get(PATIENT_URL, "/patients", "patient")]


def get_patient(patient_id: int) -> Patient:
    return Patient(**_get(PATIENT_URL, f"/patients/{patient_id}", "patient"))


def get_readings(patient_id: int) -> list[DailyReading]:
    return [DailyReading(**r) for r in _get(TELEMETRY_URL, f"/readings/{patient_id}", "telemetry")]


def get_simulation() -> dict:
    try:
        return _get(TELEMETRY_URL, "/simulation", "telemetry")
    except HTTPException:
        return {"seconds_per_day": None, "total_days": None}


def upstream_status() -> dict[str, str]:
    status = {}
    for name, base in (("patient", PATIENT_URL), ("telemetry", TELEMETRY_URL)):
        try:
            httpx.get(f"{base}/health", timeout=TIMEOUT).raise_for_status()
            status[name] = "up"
        except httpx.HTTPError:
            status[name] = "down"
    return status
