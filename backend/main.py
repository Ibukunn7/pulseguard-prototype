from tkinter import NORMAL

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import VitalReading

app = FastAPI()

# Allow React frontend to access FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vitals = []


@app.get("/")
def home():
    return {
        "message": "PulseGuard Backend Running"
    }


@app.post("/vitals")
def add_vital(reading: VitalReading):

    alert = "NORMAL"

    if reading.heart_rate > 110:
        alert = "HIGH RISK"

    elif reading.heart_rate > 95:
        alert = "MODERATE RISK"

    elif reading.sleep_hours < 5:
        alert = "MODERATE RISK"

    vitals.append(
        {
            "reading": reading,
            "alert": alert
        }
    )

    return {
        "message": "Vital Added"
    }


@app.get("/vitals")
def get_vitals():
    return vitals