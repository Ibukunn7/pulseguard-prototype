import requests
import random
import time
from datetime import datetime

patients = [
    "John Doe",
    "Sarah Smith",
    "Tom Murphy",
    "Jane Kelly",
    "Mark Ryan"
]

while True:

    patient_id = random.randint(1, 5)

    payload = {
        "patient_id": patient_id,
        "patient_name": patients[patient_id - 1],
        "heart_rate": random.randint(60, 130),
        "sleep_hours": round(random.uniform(4, 10), 1),
        "timestamp": datetime.now().isoformat()
    }

    requests.post(
        "http://localhost:8000/vitals",
        json=payload
    )

    print(payload)

    time.sleep(5)
