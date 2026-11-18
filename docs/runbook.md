# PulseGuard Operations Runbook

## Overview

This runbook provides instructions for operating and troubleshooting the PulseGuard prototype.

## System Startup

Start the full stack:

```bash
docker compose up --build
```

Expected result: five containers start in order. The dashboard is available at `http://localhost:3000`.

## System Shutdown

```bash
docker compose down
```

## Viewing Logs

All services:

```bash
docker compose logs -f
```

One service:

```bash
docker compose logs -f alert-service
```

Service names: `patient-service`, `telemetry-service`, `alert-service`, `dashboard`, `simulator`.

## Verification Checks

### Patient Service

Open `http://localhost:8001/health`.

Expected response:

```json
{ "status": "ok" }
```

### Telemetry Service

Open `http://localhost:8002/health`.

### Alert Service

Open `http://localhost:8003/health`.

### Dashboard

Open `http://localhost:3000`.

Expected result: patient cards and service status pills are visible.

## Troubleshooting

### Dashboard Shows No Data

Possible cause: alert service not running.

Solution:

```bash
docker compose restart alert-service
```

### Service Shows as Down in Dashboard

Possible cause: container failed its health check.

Solution:

```bash
docker compose logs alert-service
docker compose restart alert-service
```

### Port Already in Use

Possible cause: another process is using one of the required ports (8001, 8002, 8003, 3000).

Solution: identify and stop the conflicting process, then restart the stack.

Windows:

```bash
netstat -ano | findstr :3000
taskkill /PID <pid> /F
```

### No Patient Data After Startup

Possible cause: simulator has not started yet or exited early.

Solution:

```bash
docker compose logs simulator
docker compose restart simulator
```

### Resetting All Data

Stop the stack, then start fresh:

```bash
docker compose down
docker compose up --build
```

All readings are stored in memory and are cleared on restart.

## Future Operational Features

Future versions of PulseGuard will include:

- PostgreSQL with persistent storage
- Structured logging with a request ID across services
- Prometheus and Grafana dashboards
- Alerting on service health
- Kubernetes deployment
