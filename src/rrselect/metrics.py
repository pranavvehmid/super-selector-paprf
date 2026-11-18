"""Step 6 delivery attribution rules for batter and bowler metrics."""

from __future__ import annotations

from typing import Mapping

from rrselect.state import is_legal_ball, team_runs


AMBIGUOUS_EXTRAS = frozenset({"other", "Penalty"})
NON_BATTER_RUN_EXTRAS = frozenset({"wide", "byes", "legbyes", "other", "Penalty"})
NON_BOWLER_WICKET_TYPES = frozenset(
    {"RunOut", "Retire Out", "Obstracting the field", "Obstructing the field"}
)


def is_metric_eligible(row: Mapping[str, str]) -> bool:
    """Return whether a delivery has unambiguous player attribution."""
    extras_type = row["extras_type"]
    if extras_type in AMBIGUOUS_EXTRAS:
        return False
    if extras_type == "None" and (
        int(row["extras1_runs"]) != 0 or int(row["extras_2_runs"]) != 0
    ):
        return False
    if extras_type in {"byes", "legbyes"} and int(row["runs"]) != 0:
        return False
    return True


def batter_runs(row: Mapping[str, str]) -> int:
    """Return runs credited to the striker under the Step 6 mapping."""
    if row["extras_type"] in NON_BATTER_RUN_EXTRAS:
        return 0
    return int(row["runs"])


def batter_ball_faced(row: Mapping[str, str]) -> bool:
    """Count a striker delivery opportunity; wides and ambiguous events are excluded."""
    return is_metric_eligible(row) and row["extras_type"] != "wide"


def bowler_runs_conceded(row: Mapping[str, str]) -> int:
    """Return attributed bowler runs, excluding byes and leg-byes."""
    runs = batter_runs(row)
    if row["extras_type"] in {"wide", "Overstep"}:
        runs += int(row["extras1_runs"]) + int(row["extras_2_runs"])
    return runs


def bowler_legal_ball(row: Mapping[str, str]) -> bool:
    """Return a legal delivery eligible for bowler-rate metrics."""
    return is_metric_eligible(row) and is_legal_ball(row)


def bowler_wicket(row: Mapping[str, str]) -> bool:
    """Return whether the source dismissal is credited to the bowler."""
    return (
        is_metric_eligible(row)
        and row["is_wicket"] == "true"
        and row["dismissal_type"] not in NON_BOWLER_WICKET_TYPES
    )


def batter_dot(row: Mapping[str, str]) -> bool:
    """Return a zero-batter-run delivery opportunity."""
    return batter_ball_faced(row) and batter_runs(row) == 0


def bowler_dot(row: Mapping[str, str]) -> bool:
    """Return a legal, team-scoreless delivery for bowler dot-rate metrics."""
    return bowler_legal_ball(row) and team_runs(row) == 0
