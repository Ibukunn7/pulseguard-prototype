PulseGuard Testing Documentation

Overview 
Testing was performed throughout development to verify that telemetry data could successfully travel through the system and be displayed on the dashboard.

Testing Strategy
The current prototype uses manual testing to validate functionality.

Testing focuses on:

Telemetry generation
API communication
Alert classification
Dashboard updates

Test Case 1 - Backend Health Check
Objective
Verify that the FastAPI backend starts correctly.

Steps
Start the backend service.
Navigate to:
http://127.0.0.1:8000
Expected Result
{
  "message": "PulseGuard Backend Running"
}
Result
PASS

Test Case 2 - Telemetry Ingestion
Objective
Verify that the backend receives telemetry readings.

Steps
Start the simulator.
Monitor backend logs.
Expected Result
Successful POST requests appear in backend logs.

Result
PASS

Test Case 3 - Alert Classification
Objective
Verify that alert rules classify patient risk correctly.

Rules Tested
High Risk
Heart Rate > 110 BPM
Expected:

HIGH RISK
Moderate Risk
Heart Rate > 95 BPM
Expected:

MODERATE RISK
Moderate Risk
Sleep Hours < 5
Expected:

MODERATE RISK
Result
PASS

Test Case 4 - Dashboard Updates
Objective
Verify that the React dashboard displays incoming telemetry.

Steps
Start backend.
Start simulator.
Start frontend.
Expected Result
Patient information appears and updates automatically.

Result
PASS

Test Case 5 - Dashboard Statistics
Objective
Verify that summary cards display accurate patient counts.

Statistics Tested
Total Patients
Normal Patients
Moderate Risk Patients
High Risk Patients
Result
PASS

Future Testing
Future development will introduce:

Unit testing
Integration testing
Automated API testing
CI/CD testing pipelines
Security testing
Performance testing