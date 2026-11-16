Changelog

All notable changes to the Pulseguard project are documented in this file.

Version 0.1.0 - November 2026
Initial prototype
Implemenetd:
- FastAPI backend
- VitalReading data model
- Telemetry ingestion endpoint
- In-memory data storage
- Synthetic patient telemetry generator
- React dashboard
- Risk classification engine
- Statistics dashboard cards
- Patient monitoring interface

Alert Classification
Added support for:

NORMAL status
MODERATE RISK status
HIGH RISK status
Rules implemented:

Heart Rate > 110 BPM → HIGH RISK
Heart Rate > 95 BPM → MODERATE RISK
Sleep Hours < 5 → MODERATE RISK

Dashboard Improvements
Implemented:

Latest reading per patient
Dashboard statistics
Risk-based patient cards
Status colour indicators
Patient telemetry display

Documentation
Created:

Architecture documentation
Setup guide
API documentation
Testing documentation
Operational runbook