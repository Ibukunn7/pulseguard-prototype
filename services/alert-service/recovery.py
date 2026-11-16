"""Expected recovery trajectory and clinical flag rules.

The step band is a per-week lookup of the lower and upper daily step counts
expected after a primary total knee replacement. Values are derived from
published consumer-wearable cohorts (All of Us Fitbit cohort, AAOS 2026;
Apple Watch cohort, KSSTA 2025), which show a trough of roughly 3,700
steps/day in the first month recovering to about 5,300 by six months.

The three flag rules are the MVP rules: simple thresholds over history,
intended to be reviewed with a clinical partner before any pilot.
"""

from statistics import mean
from typing import Optional

from models import BandPoint, DailyReading, Flag

# Lower and upper daily steps per recovery week for a patient who walked
# unaided before surgery. Week 12 and beyond reuse the last row.
STEP_BAND_BY_WEEK: dict[int, tuple[int, int]] = {
    1: (1200, 2800),
    2: (1800, 3400),
    3: (2300, 3900),
    4: (2800, 4400),
    5: (3200, 4800),
    6: (3500, 5100),
    7: (3700, 5300),
    8: (3900, 5500),
    9: (4000, 5600),
    10: (4100, 5700),
    11: (4200, 5800),
    12: (4300, 5900),
}

# Scale the band down for patients who needed a walking aid before surgery.
ABILITY_FACTOR: dict[str, float] = {
    "unaided": 1.0,
    "stick": 0.85,
    "frame": 0.70,
}

BASELINE_DAYS = 3          # first days at home used for the resting HR baseline
HR_RISE_THRESHOLD = 10     # BPM above baseline that counts as a rise
CONSECUTIVE_DAYS = 3       # days in a row a condition must hold
PAIN_HIGH = 7
PAIN_MODERATE = 5
SLEEP_LOW_HOURS = 5.0
WINDOW = 7                 # rolling window for step averages


def week_of(day: int) -> int:
    return max(1, (day - 1) // 7 + 1)


def step_band(day: int, walking_ability: str) -> tuple[int, int]:
    week = min(week_of(day), max(STEP_BAND_BY_WEEK))
    low, high = STEP_BAND_BY_WEEK[week]
    factor = ABILITY_FACTOR.get(walking_ability, 1.0)
    return int(low * factor), int(high * factor)


def band_series(up_to_day: int, walking_ability: str) -> list[BandPoint]:
    points = []
    for d in range(1, up_to_day + 1):
        low, high = step_band(d, walking_ability)
        points.append(BandPoint(day=d, low=low, high=high))
    return points


def baseline_hr(readings: list[DailyReading]) -> Optional[float]:
    first = [r.resting_hr for r in readings if r.day <= BASELINE_DAYS]
    if len(first) < BASELINE_DAYS:
        return None
    return round(mean(first), 1)


def _sorted(readings: list[DailyReading]) -> list[DailyReading]:
    return sorted(readings, key=lambda r: r.day)


def mobilisation_flag(readings: list[DailyReading], walking_ability: str) -> Flag:
    rs = _sorted(readings)
    if len(rs) < WINDOW:
        return Flag(name="mobilisation", status="pending",
                    reason=f"Needs {WINDOW} days of step data")

    recent = rs[-WINDOW:]
    avg = mean(r.steps for r in recent)
    low, _ = step_band(recent[-1].day, walking_ability)
    if avg < low:
        return Flag(name="mobilisation", status="flagged",
                    reason=f"7-day average {avg:.0f} steps is below the expected {low}")

    if len(rs) >= 2 * WINDOW and recent[-1].day > 14:
        previous = rs[-2 * WINDOW:-WINDOW]
        prev_avg = mean(r.steps for r in previous)
        if avg <= prev_avg:
            return Flag(name="mobilisation", status="flagged",
                        reason=f"No increase: {avg:.0f} steps this week vs {prev_avg:.0f} last week")

    return Flag(name="mobilisation", status="clear",
                reason=f"7-day average {avg:.0f} steps, within expected range")


def complication_flag(readings: list[DailyReading]) -> Flag:
    rs = _sorted(readings)
    base = baseline_hr(rs)
    if base is None or len(rs) < BASELINE_DAYS + CONSECUTIVE_DAYS:
        return Flag(name="complication", status="pending",
                    reason="Establishing resting heart rate baseline")

    last = rs[-CONSECUTIVE_DAYS:]
    if all(r.resting_hr >= base + HR_RISE_THRESHOLD for r in last):
        rise = last[-1].resting_hr - base
        return Flag(name="complication", status="flagged",
                    reason=f"Resting HR {rise:+.0f} BPM above baseline for {CONSECUTIVE_DAYS} days")

    return Flag(name="complication", status="clear",
                reason=f"Resting HR within {HR_RISE_THRESHOLD} BPM of baseline {base:.0f}")


def pain_flag(readings: list[DailyReading]) -> Flag:
    rs = _sorted(readings)
    if len(rs) < CONSECUTIVE_DAYS:
        return Flag(name="pain", status="pending",
                    reason=f"Needs {CONSECUTIVE_DAYS} days of check-ins")

    last = rs[-CONSECUTIVE_DAYS:]
    if all(r.pain >= PAIN_HIGH for r in last):
        return Flag(name="pain", status="flagged",
                    reason=f"Pain {PAIN_HIGH}+ for {CONSECUTIVE_DAYS} consecutive days")

    if all(r.sleep_hours < SLEEP_LOW_HOURS and r.pain >= PAIN_MODERATE for r in last):
        return Flag(name="pain", status="flagged",
                    reason=f"Under {SLEEP_LOW_HOURS:.0f}h sleep with pain {PAIN_MODERATE}+ for {CONSECUTIVE_DAYS} nights")

    return Flag(name="pain", status="clear",
                reason=f"Pain {last[-1].pain}/10, sleep {last[-1].sleep_hours:.1f}h")


def evaluate(readings: list[DailyReading], walking_ability: str) -> list[Flag]:
    return [
        mobilisation_flag(readings, walking_ability),
        complication_flag(readings),
        pain_flag(readings),
    ]
