PulseGuard Documentation
Overview
PulseGuard is a Remote Patient Monitoring (RPM) platform developed as part of a fourth-year DevOps project.

The platform monitors patient biometric telemetry, classifies health risks using predefined rules, and presents information through a clinician dashboard.

The project currently consists of:

Synthetic patient telemetry generation
FastAPI backend services
Alert classification engine
React frontend dashboard
Risk analysis and patient monitoring

Project Goals
The primary goals of PulseGuard are:

Monitor patient health remotely
Detect potential deterioration through telemetry analysis
Support clinician decision-making
Demonstrate modern DevOps practices
Showcase Infrastructure as Code, CI/CD and cloud deployment strategies
Technology Stack
Frontend
React
Vite
JavaScript
Backend
Python
FastAPI
Pydantic
Simulation
Python
Requests


Future Technologies
PostgreSQL
Docker
Kubernetes
Terraform
GitHub Actions
Prometheus
Grafana
Argo CD
Documentation Structure
The following documentation is available:

Architecture
Describes the system design and component interactions.

See:

architecture.md
Setup Guide
Instructions for running PulseGuard locally.

See:

setup.md

API Documentation
Details of backend endpoints and request/response formats.

See:

api.md
Testing Documentation
Testing strategy and validation procedures.

See:

testing.md
Operations Runbook
System startup and troubleshooting procedures.

See:

runbook.md
Changelog
Project history and feature progression.

See:

changelog.md

Current Status
The current prototype successfully demonstrates:

Telemetry generation
Telemetry ingestion
Risk classification
Alert processing
Dashboard visualisation
Real-time updates
Future Work
Planned enhancements include:

PostgreSQL integration
Authentication and authorisation
Historical telemetry storage
Heart rate trend visualisations
Docker containerisation
CI/CD automation
Observability and monitoring
Kubernetes deployment