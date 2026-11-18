import pytest
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def reset():
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
    assert r.json()["service"] == "telemetry"


def test_store_and_read_in_day_order():
    post_day(1, 3)
    post_day(1, 1)
    post_day(1, 2)
    days = [r["day"] for r in client.get("/readings/1").json()]
    assert days == [1, 2, 3]


def test_repeated_day_replaces():
    post_day(1, 1, steps=1000)
    post_day(1, 1, steps=4000)
    readings = client.get("/readings/1").json()
    assert len(readings) == 1 and readings[0]["steps"] == 4000


def test_unknown_patient_returns_empty_list():
    assert client.get("/readings/42").json() == []


def test_invalid_reading_rejected():
    assert post_day(1, 1, pain=11).status_code == 422
    assert post_day(1, 0).status_code == 422


def test_simulation_config_roundtrip():
    r = client.put("/simulation", json={"seconds_per_day": 1.5, "total_days": 42})
    assert r.status_code == 200
    assert client.get("/simulation").json() == {"seconds_per_day": 1.5, "total_days": 42}
