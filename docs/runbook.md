PulseGuard Operations Runbook

Overview
This runbook provides instructions for operating and troubleshooting the PulseGuard prototype.

System Startup Procedure
The PulseGuard prototype consists of three components:

FastAPI Backend
Patient Simulator
React Dashboard
All three components must be running.


Start Backend
Navigate to:

cd backend
Run:

uvicorn main:app --reload
Expected Result:

INFO: Uvicorn running on http://127.0.0.1:8000

Start Simulator
Open a second terminal.

Navigate to:

cd simulator
Run:

python patient_simulator.py
Expected Result:

Patient telemetry data is generated every few seconds.

Start Dashboard
Open a third terminal.

Navigate to:

cd frontend
Run:

npm run dev
Expected Result:

http://localhost:5173


Verification Checks
Backend Check
Open:

http://127.0.0.1:8000
Expected Response:

{
  "message": "PulseGuard Backend Running"
}

Telemetry Check
Open:

http://127.0.0.1:8000/vitals
Expected Result:

Patient telemetry records should be displayed.

Dashboard Check
Open:

http://localhost:5173
Expected Result:

Patient cards and dashboard statistics should be visible.

Troubleshooting
Dashboard Not Loading Data
Possible Cause
Backend not running.

Solution
Restart FastAPI:

uvicorn main:app --reload

No Patient Data Appears
Possible Cause
Simulator not running.

Solution
Start:

python patient_simulator.py

CORS Error
Example Error
Access to fetch has been blocked by CORS policy
Solution
Verify CORSMiddleware is configured in the backend.

Port Already In Use
Solution
Terminate existing process using the port and restart the application.

Future Operational Features
Future versions of PulseGuard will include:

PostgreSQL database
Docker deployment
CI/CD pipelines
Logging and monitoring
Kubernetes deployment
Alert notifications