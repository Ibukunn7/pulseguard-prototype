from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "patient"


def test_list_patients_sorted_by_id():
    ids = [p["id"] for p in client.get("/patients").json()]
    assert ids == sorted(ids)
    assert len(ids) >= 5


def test_get_patient():
    r = client.get("/patients/1")
    assert r.status_code == 200
    assert r.json()["name"] == "John Doe"


def test_unknown_patient_404():
    assert client.get("/patients/999").status_code == 404


def test_create_patient_assigns_next_id():
    before = len(client.get("/patients").json())
    r = client.post("/patients", json={"name": "New Patient", "age": 60,
                                       "surgery_date": "2026-11-01", "walking_ability": "stick"})
    assert r.status_code == 201
    assert r.json()["id"] == before + 1


def test_invalid_walking_ability_rejected():
    r = client.post("/patients", json={"name": "X", "age": 60,
                                       "surgery_date": "2026-11-01", "walking_ability": "wheelchair"})
    assert r.status_code == 422
