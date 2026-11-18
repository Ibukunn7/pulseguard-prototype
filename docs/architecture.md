# PulseGuard Architecture

## Overview

PulseGuard is a microservices-based Remote Patient Monitoring platform for knee replacement recovery.

The system ingests daily patient readings, evaluates them against recovery rules, and presents the results through a GP dashboard.

## System Architecture

```
Simulator
   ↓
Patient Service   Telemetry Service
        ↘               ↙
         Alert Service
               ↓
           Dashboard
```

All five components run as containers under Docker Compose.

## Components

### Patient Service

Maintains the patient registry.

Responsibilities:

- Store patient records (name, age, surgery date, walking ability)
- Expose patient list and individual patient lookup
- Walking ability is used by the alert service to adjust step targets

Port: `8001`

### Telemetry Service

Stores daily readings. Has no knowledge of clinical meaning.

Responsibilities:

- Accept and store one reading per patient per day
- Expose readings by patient in day order
- Manage simulator configuration (seconds per day, total days)

A reading contains:

- Steps
- Resting heart rate
- Sleep hours
- Pain score (0–10)
- Recovery day

Port: `8002`

### Alert Service

Evaluates readings against recovery rules. Stores nothing.

Responsibilities:

- Fetch patients and readings from the other services on each request
- Compute the expected step band for each recovery week
- Calculate each patient's heart rate baseline (mean of first three days)
- Evaluate three flags per patient
- Return patients ranked by flag count

Port: `8003`

### Dashboard

React frontend served by Nginx.

Responsibilities:

- Display patients ranked by urgency
- Show flag status and reason per patient
- Render trend charts against the expected band and personal baseline
- Display demo clock when simulator is attached

Port: `3000`

### Simulator

Replays synthetic six-week recoveries for five patients.

Responsibilities:

- POST one reading per patient per day on each tick
- Drift two patients on purpose so all three flags fire
- Run as a container; does not expose an HTTP port

## Flag Rules

### Mobilisation

Steps below the expected weekly band for seven consecutive days, or no week-on-week increase after day 14.

The step target is adjusted by walking ability: unaided 1.0, stick 0.85, frame 0.70.

Status: `pending` until day 7.

### Complication

Resting heart rate 10 BPM or more above the personal baseline for three consecutive days.

Baseline is the mean resting heart rate from the first three days of readings.

Status: `pending` until day 3.

### Pain

Pain score 7 or above for three consecutive days, or sleep under five hours with pain 5 or above for three consecutive nights.

Status: `pending` until day 3.

## Technology Stack

### Frontend

- React
- Vite
- JavaScript
- Nginx

### Backend

- Python
- FastAPI
- Pydantic
- httpx

### Infrastructure

- Docker
- Docker Compose

### Simulation

- Python
- Requests

## Future Architecture

Future development will include:

- PostgreSQL per service, with migrations
- Authentication and role-based access control
- HealthKit and Health Connect wearable integration
- Kubernetes deployment
- CI/CD pipeline
- Monitoring and logging
