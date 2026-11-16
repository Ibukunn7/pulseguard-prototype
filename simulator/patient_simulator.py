"""Knee-replacement recovery simulator.

Plays out the first six weeks at home for five patients, one recovery day
per tick, posting a daily reading for each patient to the backend. Three
patients recover normally. Two drift off trajectory so the dashboard has
something to flag:

* Tom Murphy (id 3) plateaus on steps from day 15, the pattern of a stiff
  knee that needs more intensive physiotherapy.
* Mark Ryan (id 5) develops a rising resting heart rate from day 18, the
  pattern that warrants a check for infection or thrombosis.
* Sarah Smith (id 2) has a pain flare with poor sleep on days 24 to 28.

Step targets follow the published recovery curve used by the backend's
expected band, scaled by each patient's pre-operative walking ability.
"""

import argparse
import random
import time

import requests

API = "http://localhost:8000"
TOTAL_DAYS = 42

# Mid-band daily step target per week for an unaided walker.
STEP_TARGET_BY_WEEK = {1: 2000, 2: 2600, 3: 3100, 4: 3600, 5: 4000, 6: 4300}
ABILITY_FACTOR = {"unaided": 1.0, "stick": 0.85, "frame": 0.70}

PROFILES = [
    # id, name, walking ability, resting HR baseline, personal effort factor
    (1, "John Doe", "unaided", 64, 1.05),
    (2, "Sarah Smith", "stick", 72, 0.95),
    (3, "Tom Murphy", "unaided", 68, 1.00),
    (4, "Jane Kelly", "unaided", 61, 1.10),
    (5, "Mark Ryan", "frame", 75, 0.90),
]


def week_of(day: int) -> int:
    return min((day - 1) // 7 + 1, max(STEP_TARGET_BY_WEEK))


def base_steps(day: int, ability: str, effort: float) -> float:
    week = week_of(day)
    target = STEP_TARGET_BY_WEEK[week] * ABILITY_FACTOR[ability] * effort
    # Smooth within-week ramp so the curve climbs daily rather than stepping.
    nxt = STEP_TARGET_BY_WEEK.get(week + 1, target / (ABILITY_FACTOR[ability] * effort))
    frac = ((day - 1) % 7) / 7
    return target + (nxt * ABILITY_FACTOR[ability] * effort - target) * frac


def base_pain(day: int) -> float:
    # Starts around 6 and settles near 2 by week six.
    return max(1.5, 6.3 - day * 0.11)


def reading_for(pid: int, name: str, ability: str, hr_base: int, effort: float, day: int) -> dict:
    steps = base_steps(day, ability, effort)
    pain = base_pain(day)
    hr = hr_base

    if pid == 3 and day >= 15:
        # Plateau then slow decline: stuck at the day-14 level.
        steps = base_steps(14, ability, effort) * (1 - 0.01 * (day - 14))
        pain += 1.0

    if pid == 5 and day >= 18:
        # Resting HR climbs 2 BPM a day to +14, then stays up.
        hr = hr_base + min(14, 2 * (day - 17))
        steps *= 0.93

    if pid == 2 and 24 <= day <= 28:
        pain = 7.5
        steps *= 0.8

    pain = min(10, max(0, round(pain + random.uniform(-0.6, 0.6))))
    sleep = 8.6 - 0.45 * pain + random.uniform(-0.5, 0.5)
    if pid == 2 and 24 <= day <= 28:
        sleep = 4.2 + random.uniform(-0.3, 0.3)

    return {
        "patient_id": pid,
        "day": day,
        "steps": int(max(0, steps * random.uniform(0.92, 1.08))),
        "resting_hr": int(round(hr + random.uniform(-2, 2))),
        "sleep_hours": round(max(2.0, min(10.0, sleep)), 1),
        "pain": int(pain),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay six weeks of knee recovery.")
    parser.add_argument("--interval", type=float, default=2.0, help="seconds per recovery day")
    parser.add_argument("--days", type=int, default=TOTAL_DAYS)
    parser.add_argument("--loop", action="store_true", help="restart from day 1 after the last day")
    args = parser.parse_args()

    requests.put(f"{API}/simulation",
                 json={"seconds_per_day": args.interval, "total_days": args.days}, timeout=5)

    while True:
        requests.delete(f"{API}/readings", timeout=5)
        print(f"Replaying {args.days} days for {len(PROFILES)} patients, {args.interval}s per day")
        for day in range(1, args.days + 1):
            for pid, name, ability, hr_base, effort in PROFILES:
                payload = reading_for(pid, name, ability, hr_base, effort, day)
                resp = requests.post(f"{API}/readings", json=payload, timeout=5)
                flagged = [f["name"] for f in resp.json().get("flags", []) if f["status"] == "flagged"]
                tag = f"  FLAG {','.join(flagged)}" if flagged else ""
                print(f"day {day:2d}  {name:12s} steps {payload['steps']:5d}  hr {payload['resting_hr']:3d}  "
                      f"sleep {payload['sleep_hours']:4.1f}  pain {payload['pain']}{tag}")
            time.sleep(args.interval)
        if not args.loop:
            print("Replay complete. Backend keeps the data until restarted.")
            break


if __name__ == "__main__":
    main()
