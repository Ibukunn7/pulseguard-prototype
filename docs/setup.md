# PulseGuard Setup Guide

## Overview

This guide explains how to set up and run the PulseGuard prototype locally.

## Prerequisites

The following software must be installed:

- Docker
- Docker Compose
- Git

## Clone Repository

```bash
git clone https://github.com/Ibukunn7/pulseguard-prototype.git
```

Navigate into the repository:

```bash
cd pulseguard-prototype
```

## Running with Docker Compose

Build and start all services:

```bash
docker compose up --build
```

The following ports will be available:

| Service           | Port |
|-------------------|------|
| Patient service   | 8001 |
| Telemetry service | 8002 |
| Alert service     | 8003 |
| Dashboard         | 3000 |

The simulator starts automatically and begins replaying patient data.

Open the dashboard at `http://localhost:3000`.

## Stopping the Stack

```bash
docker compose down
```

## Running Without Docker

If Docker is not available, each service can be run manually.

### Manual Prerequisites

- Python 3.12
- Node.js 20
- npm

### Patient Service

```bash
cd services/patient-service
pip install -r requirements.txt
uvicorn main:app --port 8001
```

### Telemetry Service

```bash
cd services/telemetry-service
pip install -r requirements.txt
uvicorn main:app --port 8002
```

### Alert Service

```bash
cd services/alert-service
pip install -r requirements.txt
uvicorn main:app --port 8003
```

### Dashboard

```bash
cd frontend
npm install
npm run dev
```

The dashboard will be available at `http://localhost:5173`.

### Simulator

```bash
cd simulator
pip install -r requirements.txt
python patient_simulator.py
```

## Expected Behaviour

The simulator generates five patient recoveries over 42 days.

The alert service evaluates readings and flags patients who drift.

The dashboard displays patients ranked by flag count and updates every two seconds during the demo.
