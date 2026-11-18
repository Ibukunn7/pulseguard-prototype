"""Alert service API tests with the upstream services stubbed out."""

from datetime import date

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

import clients
import main
from models import DailyReading, Patient

client = TestClient(main.app)

PATIENTS = [
    Patient(id=1, name="On Track", age=65, surgery_date=date(2026, 10, 1), walking_ability="unaided"),
    Patient(id=2, name="Low Steps", age=70, surgery_date=date(2026, 10, 1), walking_ability="unaided"),
]


def readings(pid, n, steps):
    return [DailyReading(patient_id=pid, day=d, steps=steps, resting_hr=65, sleep_hours=7.0, pain=3)
            for d in range(1, n + 1)]


STORE = {1: readings(1, 10, 2800), 2: readings(2, 10, 500)}


@pytest.fixture(autouse=True)
def stub_upstreams(monkeypatch):
    monkeypatch.setattr(clients, "list_patients", lambda: list(PATIENTS))
    monkeypatch.setattr(clients, "get_patient",
                        lambda pid: next(p for p in PATIENTS if p.id == pid))
    monkeypatch.setattr(clients, "get_readings", lambda pid: list(STORE.get(pid, [])))
    monkeypatch.setattr(clients, "get_simulation",
                        lambda: {"seconds_per_day": 1.5, "total_days": 42})
    monkeypatch.setattr(clients, "upstream_status", lambda: {"patient": "up", "telemetry": "up"})


def test_health():
    assert client.get("/health").json()["service"] == "alert"


def test_status_reports_dependencies_and_simulation():
    body = client.get("/status").json()
    assert body["services"] == {"alert": "up", "patient": "up", "telemetry": "up"}
    assert body["simulation"]["seconds_per_day"] == 1.5


def test_patients_ranked_by_flag_count():
    ranked = client.get("/patients").json()
    assert ranked[0]["patient"]["id"] == 2
    assert ranked[0]["flag_count"] == 1
    assert ranked[1]["flag_count"] == 0


def test_detail_includes_history_and_band():
    detail = client.get("/patients/1").json()
    assert detail["day"] == 10
    assert len(detail["readings"]) == 10
    assert len(detail["band"]) == 10
    assert [f["name"] for f in detail["flags"]] == ["mobilisation", "complication", "pain"]


def test_upstream_failure_becomes_503(monkeypatch):
    def boom():
        raise HTTPException(status_code=503, detail="patient service unreachable")
    monkeypatch.setattr(clients, "list_patients", boom)
    r = client.get("/patients")
    assert r.status_code == 503
    assert "unreachable" in r.json()["detail"]
