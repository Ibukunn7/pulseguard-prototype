"""API tests against the FastAPI app with the in-memory store.

Run from the backend folder:  python -m pytest -q
"""

import pytest
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def reset_store():
    client.delete("/readings")
    yield
    client.delete("/readings")


def post_day(patient_id, day, **kw):
    body = {"patient_id": patient_id, "day": day, "steps": 2500,
            "resting_hr": 65, "sleep_hours": 7.0, "pain": 3}
    body.update(kw)
    return client.post("/readings", json=body)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["patients"] == 5


def test_post_reading_returns_flags():
    r = post_day(1, 1)
    assert r.status_code == 201
    assert [f["name"] for f in r.json()["flags"]] == ["mobilisation", "complication", "pain"]


def test_unknown_patient_rejected():
    assert post_day(99, 1).status_code == 404


def test_invalid_pain_rejected():
    assert post_day(1, 1, pain=11).status_code == 422


def test_repeated_day_replaces_reading():
    post_day(1, 1, steps=1000)
    post_day(1, 1, steps=4000)
    detail = client.get("/patients/1").json()
    assert len(detail["readings"]) == 1
    assert detail["readings"][0]["steps"] == 4000


def test_patients_ranked_by_flag_count():
    for d in range(1, 8):
        post_day(2, d, steps=500)       # below band -> mobilisation flag
        post_day(1, d, steps=2500)      # within band
    ranked = client.get("/patients").json()
    assert ranked[0]["patient"]["id"] == 2
    assert ranked[0]["flag_count"] == 1


def test_detail_includes_band_up_to_latest_day():
    for d in range(1, 11):
        post_day(3, d)
    detail = client.get("/patients/3").json()
    assert detail["day"] == 10
    assert len(detail["band"]) == 10
    assert detail["band"][0]["low"] < detail["band"][-1]["low"]
