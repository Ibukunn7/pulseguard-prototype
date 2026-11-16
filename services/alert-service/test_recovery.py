"""Unit tests for the expected band and the three flag rules.

Run from the backend folder:  python -m pytest -q
"""

from models import DailyReading
from recovery import (baseline_hr, complication_flag, evaluate, mobilisation_flag,
                      pain_flag, step_band, week_of)


def reading(day, steps=3000, hr=65, sleep=7.0, pain=3):
    return DailyReading(patient_id=1, day=day, steps=steps, resting_hr=hr,
                        sleep_hours=sleep, pain=pain)


def days(n, **kw):
    return [reading(d, **kw) for d in range(1, n + 1)]


# --- band ------------------------------------------------------------------

def test_week_of_boundaries():
    assert week_of(1) == 1
    assert week_of(7) == 1
    assert week_of(8) == 2
    assert week_of(42) == 6


def test_band_scales_with_walking_ability():
    unaided = step_band(10, "unaided")
    frame = step_band(10, "frame")
    assert frame[0] < unaided[0] and frame[1] < unaided[1]


def test_band_beyond_week_12_uses_last_row():
    assert step_band(100, "unaided") == step_band(84, "unaided")


# --- mobilisation ----------------------------------------------------------

def test_mobilisation_pending_before_seven_days():
    assert mobilisation_flag(days(6), "unaided").status == "pending"


def test_mobilisation_clear_when_within_band():
    rs = days(7, steps=2000)  # week 1 band is 1200 to 2800
    assert mobilisation_flag(rs, "unaided").status == "clear"


def test_mobilisation_flags_below_band():
    rs = days(7, steps=800)
    assert mobilisation_flag(rs, "unaided").status == "flagged"


def test_mobilisation_flags_plateau_after_week_two():
    rs = [reading(d, steps=3000) for d in range(1, 22)]  # flat for three weeks
    flag = mobilisation_flag(rs, "unaided")
    assert flag.status == "flagged"
    assert "No increase" in flag.reason


def test_mobilisation_clear_when_climbing():
    rs = [reading(d, steps=2000 + d * 100) for d in range(1, 22)]
    assert mobilisation_flag(rs, "unaided").status == "clear"


# --- complication ----------------------------------------------------------

def test_baseline_needs_three_days():
    assert baseline_hr(days(2)) is None
    assert baseline_hr(days(3, hr=66)) == 66


def test_complication_pending_until_six_days():
    assert complication_flag(days(5)).status == "pending"


def test_complication_flags_three_days_above_baseline():
    rs = days(5, hr=65) + [reading(d, hr=76) for d in (6, 7, 8)]
    flag = complication_flag(rs)
    assert flag.status == "flagged"


def test_complication_clear_for_two_day_rise():
    rs = days(6, hr=65) + [reading(7, hr=76), reading(8, hr=76)]
    assert complication_flag(rs).status == "clear"


# --- pain ------------------------------------------------------------------

def test_pain_flags_three_days_at_seven():
    rs = days(3, pain=7)
    assert pain_flag(rs).status == "flagged"


def test_pain_flags_short_sleep_with_moderate_pain():
    rs = days(3, sleep=4.5, pain=5)
    assert pain_flag(rs).status == "flagged"


def test_pain_clear_for_short_sleep_without_pain():
    rs = days(3, sleep=4.5, pain=2)
    assert pain_flag(rs).status == "clear"


# --- evaluate --------------------------------------------------------------

def test_evaluate_returns_all_three_in_order():
    names = [f.name for f in evaluate(days(10), "unaided")]
    assert names == ["mobilisation", "complication", "pain"]
