"""Step 5 pressure definition using only pre-delivery state."""

from __future__ import annotations

from typing import Mapping


def clamp(value: float) -> float:
    """Restrict a pressure component to the unit interval."""
    return max(0.0, min(1.0, value))


def phase(pre_delivery_legal_balls: int) -> str:
    """Return a reproducible T20 phase from pre-delivery legal balls."""
    if pre_delivery_legal_balls < 36:
        return "powerplay"
    if pre_delivery_legal_balls < 90:
        return "middle"
    return "death"


def pressure_components(row: Mapping[str, str]) -> dict[str, float]:
    """Calculate pressure components without using the rated-ball outcome."""
    legal_balls = int(row["pre_delivery_legal_balls"])
    wickets = int(row["pre_delivery_wickets"])
    progress = clamp(legal_balls / 120)
    wicket_stress = clamp(wickets / 10)

    if row["innings"] == "1":
        late_innings_stress = clamp((legal_balls - 72) / 48)
        return {
            "required_run_rate": 0.0,
            "progress": progress,
            "wicket_stress": wicket_stress,
            "run_rate_stress": 0.0,
            "late_innings_stress": late_innings_stress,
            "pressure_index": 0.70 * late_innings_stress + 0.30 * wicket_stress,
        }

    balls_remaining = int(row["pre_delivery_balls_remaining"])
    runs_required = int(row["pre_delivery_runs_required"])
    required_run_rate = 6 * runs_required / max(balls_remaining, 1)
    run_rate_stress = clamp((required_run_rate - 7) / 5)
    return {
        "required_run_rate": required_run_rate,
        "progress": progress,
        "wicket_stress": wicket_stress,
        "run_rate_stress": run_rate_stress,
        "late_innings_stress": 0.0,
        "pressure_index": (
            0.55 * run_rate_stress + 0.25 * wicket_stress + 0.20 * progress
        ),
    }


def pressure_band(index: float) -> str:
    """Classify continuous pressure for baseline and sensitivity work."""
    if index >= 0.65:
        return "high"
    if index >= 0.40:
        return "elevated"
    return "ordinary"
