PulseGuard Setup Guide
Overview
This guide explains how to set up and run the PulseGuard prototype locally.

Prerequisites
The following software must be installed:

Python 3.x
Node.js
npm
Git

Clone Repository
git clone https://github.com/Ibukunn7/pulseguard-prototype.git
Navigate into the repository:

cd pulseguard-prototype

Backend Setup
Navigate to the backend directory:

cd backend
Install dependencies:

pip install -r requirements.txt
Start the FastAPI server:

uvicorn main:app --reload
The API will be available at:

http://127.0.0.1:8000

Simulator Setup
Open a second terminal.

Navigate to the simulator directory:

cd simulator
Run the telemetry simulator:

python patient_simulator.py
The simulator will continuously generate synthetic patient telemetry data.

Frontend Setup
Open a third terminal.

Navigate to the frontend directory:

cd frontend
Install dependencies:

npm install
Start the React application:

npm run dev
The dashboard will be available at:

http://localhost:5173

Running the Complete System
Three processes must be running simultaneously:

Terminal 1
uvicorn main:app --reload
Terminal 2
python patient_simulator.py
Terminal 3
npm run dev

Expected Behaviour
The simulator generates patient telemetry.

The FastAPI backend receives and classifies the data.

The React dashboard displays patient status and risk levels in real time.