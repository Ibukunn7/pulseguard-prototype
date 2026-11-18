# PulseGuard Documentation

## Overview

PulseGuard is a Remote Patient Monitoring (RPM) platform developed as part of a fourth-year DevOps project.

The platform monitors knee replacement patients during the first six weeks of home recovery, flags patients who drift from their expected trajectory, and presents the information through a GP dashboard.

The project currently consists of:

- Patient registry service
- Telemetry ingestion service
- Alert and flag evaluation service
- React frontend dashboard
- Recovery simulator

## Project Goals

The primary goals of PulseGuard are:

- Monitor knee replacement recovery remotely
- Detect patients drifting from expected recovery trajectories
- Support GP decision-making with ranked, explained flags
- Demonstrate modern DevOps practices
- Showcase containerisation, CI/CD and cloud deployment strategies

## Technology Stack

### Frontend

- React
- Vite
- JavaScript

### Backend

- Python
- FastAPI
- Pydantic

### Infrastructure

- Docker
- Docker Compose
- Nginx

### Simulation

- Python
- Requests

## Future Technologies

- PostgreSQL
- Kubernetes
- Terraform
- GitHub Actions
- Prometheus
- Grafana
- Argo CD

## Documentation Structure

The following documentation is available:

**Architecture**
Describes the system design and component interactions.

See: [architecture.md](architecture.md)

**Setup Guide**
Instructions for running PulseGuard locally.

See: [setup.md](setup.md)

**API Documentation**
Details of backend endpoints and request/response formats.

See: [api.md](api.md)

**Testing Documentation**
Testing strategy and validation procedures.

See: [testing.md](testing.md)

**Operations Runbook**
System startup and troubleshooting procedures.

See: [runbook.md](runbook.md)

**Changelog**
Project history and feature progression.

See: [changelog.md](changelog.md)

## Current Status

The current prototype successfully demonstrates:

- Patient registry with five knee replacement patients
- Daily telemetry ingestion (steps, heart rate, sleep, pain)
- Three clinical flag rules evaluated against recovery history
- GP dashboard ranking patients by urgency
- Full stack containerised with Docker Compose
- Recovery simulator replaying six weeks in under a minute

## Future Work

Planned enhancements include:

- PostgreSQL integration
- Authentication and authorisation
- HealthKit and Health Connect wearable integration
- GP controls: acknowledge, snooze, per-patient thresholds
- CI/CD automation
- Observability and monitoring
- Kubernetes deployment
