# PulseGuard API Documentation

## Overview

PulseGuard exposes three backend services, each on its own port.

| Service           | Base URL                  |
|-------------------|---------------------------|
| Patient service   | http://localhost:8001     |
| Telemetry service | http://localhost:8002     |
| Alert service     | http://localhost:8003     |

---

## Patient Service

### GET /health

Returns the health status of the service.

Response:

```json
{ "status": "ok" }
```

### GET /patients

Returns all registered patients.

Response:

```json
[
  {
    "id": 1,
    "name": "John Doe",
    "age": 67,
    "surgery_date": "2026-10-07",
    "walking_ability": "unaided"
  }
]
```

Walking ability values: `unaided`, `stick`, `frame`.

### GET /patients/{id}

Returns a single patient by ID.

Returns `404` if the patient does not exist.

### POST /patients

Creates a new patient.

Request body:

```json
{
  "name": "string",
  "age": 18,
  "surgery_date": "YYYY-MM-DD",
  "walking_ability": "unaided"
}
```

---

## Telemetry Service

### GET /health

Returns the health status of the service.

### POST /readings

Stores a daily reading for a patient.

One reading per patient per day. A second POST for the same patient and day replaces the first.

Returns `201` on success.

Request body:

```json
{
  "patient_id": 1,
  "day": 7,
  "steps": 2400,
  "resting_hr": 72,
  "sleep_hours": 7.2,
  "pain": 3
}
```

### GET /readings/{patient_id}

Returns all readings for a patient, ordered by day.

Returns `[]` if no readings exist.

### DELETE /readings

Deletes all readings for all patients.

Returns `204`.

### GET /simulation

Returns the current simulator configuration.

Response:

```json
{
  "seconds_per_day": 1.5,
  "total_days": 42
}
```

### PUT /simulation

Updates the simulator configuration.

Request body:

```json
{
  "seconds_per_day": 1.5,
  "total_days": 42
}
```

---

## Alert Service

### GET /health

Returns the health status of the service.

### GET /status

Returns the health status of all three services and the current simulator configuration.

Response:

```json
{
  "services": {
    "alert": "ok",
    "patient": "ok",
    "telemetry": "ok"
  },
  "simulation": {
    "seconds_per_day": 1.5,
    "total_days": 42
  }
}
```

### GET /patients

Returns all patients ranked by flag count, then by recovery day.

Each patient includes:

- Current recovery day and week
- Latest reading
- Heart rate baseline
- Three flag evaluations (mobilisation, complication, pain)
- Total flag count

Flag status values: `clear`, `flagged`, `pending`.

### GET /patients/{id}

Returns full detail for a single patient.

Includes all fields from `GET /patients` plus:

- Full reading history
- Expected step band per week

Returns `404` if the patient does not exist.

---

## Future API Enhancements

Planned features include:

- Authentication
- GP controls: acknowledge, snooze, per-patient thresholds
- Alert history endpoints
- User roles and permissions
