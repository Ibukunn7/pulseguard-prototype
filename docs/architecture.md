PulseGuard Architecture
Overview
PulseGuard is a Remote Patient Monitoring (RPM) platform designed to monitor patient health after discharge from hospital.

The system collects biometric telemetry, processes patient readings, classifies risk levels and presents the information through a clinician dashboard.

System Architecture
Patient Simulator
        ↓
FastAPI Backend
        ↓
Alert Engine
        ↓
React Dashboard

Components
Patient Simulator
The patient simulator generates synthetic biometric telemetry data.

Example telemetry data includes:

Patient ID
Patient Name
Heart Rate
Sleep Hours
Timestamp
The telemetry is sent to the backend using HTTP POST requests.

FastAPI Backend
The backend receives telemetry from the simulator.

Responsibilities:

Data validation
Telemetry ingestion
Risk classification
API endpoint exposure
Current APIs:

GET /
GET /vitals
POST /vitals

Alert Engine
The alert engine evaluates incoming telemetry.

Current rules:

Heart Rate > 110 BPM = HIGH RISK
Heart Rate > 95 BPM = MODERATE RISK
Sleep Hours < 5 = MODERATE RISK
The generated risk level is attached to each reading.
React Dashboard
The dashboard retrieves telemetry using the GET /vitals endpoint.

Features:

Live telemetry updates
Latest reading per patient
Risk classification display
Dashboard statistics
Colour-coded patient status


Current Technology Stack
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

Future Architecture
Future development will include:

PostgreSQL database
Authentication
Role-Based Access Control (RBAC)
Docker containers
CI/CD pipeline
Kubernetes deployment
Monitoring and logging