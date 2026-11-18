# Changelog

All notable changes to the PulseGuard project are documented in this file.

---

## Version 0.3.0 - November 2026

### Microservices and Docker Compose

Split the backend into three independent services:

- Patient service (registry, port 8001)
- Telemetry service (ingestion and storage, port 8002)
- Alert service (flag evaluation, port 8003)

Each service has its own Dockerfile and health check.

Docker Compose wires the full stack with startup ordering via health checks. One command starts all five containers.

### Alert and Flag System

Implemented three clinical flag rules:

- Mobilisation: steps below expected band or no weekly gain after day 14
- Complication: resting heart rate 10+ above personal baseline for three consecutive days
- Pain: pain score 7+ for three days, or short sleep with elevated pain for three nights

Expected step band defined per recovery week, adjusted by walking ability.

Heart rate baseline computed from the first three days of readings.

### Recovery Simulator

Replaced random telemetry with realistic six-week recovery curves for five patients.

Two patients drift on purpose:

- Mark Ryan: heart rate rising from day 18 (complication flag)
- Sarah Smith: elevated pain and poor sleep around days 24–28 (pain flag)
- Tom Murphy: step plateau from day 15 (mobilisation flag)

### GP Dashboard

Rebuilt around flags:

- Patients ranked by flag count
- Flag status and reason displayed per patient
- Trend charts: steps vs expected band, heart rate vs baseline, pain and sleep
- Demo clock labelled on screen

### Testing

Added 33 automated tests across the three services:

- Patient service: 6 tests
- Telemetry service: 6 tests
- Alert service: 21 tests (flag logic and API)

---

## Version 0.1.0 - November 2026

### Initial Prototype

Implemented:

- FastAPI backend
- VitalReading data model
- Telemetry ingestion endpoint
- In-memory data storage
- Synthetic patient telemetry generator
- React dashboard
- Risk classification engine
- Statistics dashboard cards
- Patient monitoring interface

### Alert Classification

Added support for:

- NORMAL status
- MODERATE RISK status
- HIGH RISK status

Rules implemented:

- Heart Rate > 110 BPM → HIGH RISK
- Heart Rate > 95 BPM → MODERATE RISK
- Sleep Hours < 5 → MODERATE RISK

### Documentation

Created:

- Architecture documentation
- Setup guide
- API documentation
- Testing documentation
- Operational runbook
