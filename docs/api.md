PulseGuard API Documentation

Overview
The PulseGuard backend exposes REST API endpoints used by the telemetry simulator and clinician dashboard.

Base URL:

http://127.0.0.1:8000

GET /
Returns the health status of the backend service.

Request
GET /
Response
{
  "message": "PulseGuard Backend Running"
}

GET /vitals
Returns stored patient telemetry readings.

Request
GET /vitals
Example Response
[
  {
    "reading": {
      "patient_id": 2,
      "patient_name": "Sarah Smith",
      "heart_rate": 124,
      "sleep_hours": 7.2,
      "timestamp": "2026-11-02T15:24:47.718907"
    },
    "alert": "HIGH RISK"
  }
]

POST /vitals
Receives telemetry from the patient simulator.

Request
POST /vitals
Example Request Body
{
  "patient_id": 2,
  "patient_name": "Sarah Smith",
  "heart_rate": 124,
  "sleep_hours": 7.2,
  "timestamp": "2026-11-02T15:24:47.718907"
}
Example Response
{
  "message": "Vital Added"
}

Alert Classification Rules
The backend automatically classifies patient risk levels.

High Risk
Heart Rate > 110 BPM
Result:

HIGH RISK

Moderate Risk
Heart Rate > 95 BPM
or

Sleep Hours < 5
Result:

MODERATE RISK

Normal
Patients not matching any alert condition are classified as:

NORMAL

Future API Enhancements
Planned API features include:

Authentication
Patient management endpoints
Historical telemetry endpoints
Alert management endpoints
User roles and permissions