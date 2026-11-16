"""Knee-replacement recovery simulator.

Plays out the first six weeks at home for five patients, one recovery day
per tick, posting a daily reading for each patient to the telemetry
service. Three patients recover normally. Two drift off trajectory so the
dashboard has something to flag:

* Tom Murphy (id 3) plateaus on steps from day 15, the pattern of a stiff
  knee that needs more intensive physiotherapy.
* Mark Ryan (id 5) develops a rising resting heart rate from day 18, the
  pattern that warrants a check for infection or thrombosis.
* Sarah Smith (id 2) has a pain flare with poor sleep on days 24 to 28.

Step targets follow the published recovery curve used by the alert
service's expected band, scaled by each patient's pre-operative walking
ability.

Configuration (environment variables override the defaults, command-line
flags override both):
  TELEMETRY_SERVICE_URL  where readings go        default http://localhost:8002
  ALERT_SERVICE_URL      where flags are read from default http://localhost:8003
  SIM_INTERVAL           seconds per recovery day  default 2
  SIM_DAYS               days to replay            default 42
  SIM_LOOP               restart after the last day (true/false)
"""

import argparse
import os
import random
import time

import requests

TELEMETRY_URL = os.getenv("TELEMETRY_SERVICE_URL", "http://localhost:8002").rstrip("/")
ALERT_URL = os.getenv("ALERT_SERVICE_URL", "http://localhost:8003").rstrip("/")

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
    scale = ABILITY_FACTOR[ability] * effort
    target = STEP_TARGET_BY_WEEK[week] * scale
    nxt = STEP_TARGET_BY_WEEK.get(week + 1, STEP_TARGET_BY_WEEK[week]) * scale
    frac = ((day - 1) % 7) / 7
    return target + (nxt - target) * frac


def base_pain(day: int) -> float:
    # Starts around 6 and settles near 2 by week six.
    return max(1.5, 6.3 - day * 0.11)


def reading_for(pid: int, ability: str, hr_base: int, effort: float, day: int) -> dict:
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


def wait_for(url: str, name: str, attempts: int = 30) -> None:
    for _ in range(attempts):
        try:
            requests.get(f"{url}/health", timeout=3).raise_for_status()
            print(f"{name} service ready at {url}")
            return
        except requests.RequestException:
            time.sleep(2)
    raise SystemExit(f"{name} service not reachable at {url}")


def flagged_names() -> dict[str, list[str]]:
    try:
        summaries = requests.get(f"{ALERT_URL}/patients", timeout=3).json()
    except (requests.RequestException, ValueError):
        return {}
    return {s["patient"]["name"]: [f["name"] for f in s["flags"] if f["status"] == "flagged"]
            for s in summaries if s["flag_count"]}


def env_bool(name: str) -> bool:
    return os.getenv(name, "false").lower() in ("1", "true", "yes")


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay six weeks of knee recovery.")
    parser.add_argument("--interval", type=float, default=float(os.getenv("SIM_INTERVAL", "2")),
                        help="seconds per recovery day")
    parser.add_argument("--days", type=int, default=int(os.getenv("SIM_DAYS", "42")))
    parser.add_argument("--loop", action="store_true", default=env_bool("SIM_LOOP"),
                        help="restart from day 1 after the last day")
    args = parser.parse_args()

    wait_for(TELEMETRY_URL, "telemetry")
    requests.put(f"{TELEMETRY_URL}/simulation",
                 json={"seconds_per_day": args.interval, "total_days": args.days}, timeout=5)

    while True:
        requests.delete(f"{TELEMETRY_URL}/readings", timeout=5)
        print(f"Replaying {args.days} days for {len(PROFILES)} patients, {args.interval}s per day")
        for day in range(1, args.days + 1):
            for pid, name, ability, hr_base, effort in PROFILES:
                payload = reading_for(pid, ability, hr_base, effort, day)
                requests.post(f"{TELEMETRY_URL}/readings", json=payload, timeout=5)
                print(f"day {day:2d}  {name:12s} steps {payload['steps']:5d}  hr {payload['resting_hr']:3d}  "
                      f"sleep {payload['sleep_hours']:4.1f}  pain {payload['pain']}")
            flags = flagged_names()
            if flags:
                print("         FLAGS: " + "; ".join(f"{n}: {', '.join(f)}" for n, f in flags.items()))
            time.sleep(args.interval)
        if not args.loop:
            print("Replay complete. Telemetry keeps the data until restarted.")
            break


if __name__ == "__main__":
    main()
