"""Step 4 helpers for leakage-free pre-delivery innings state."""

from __future__ import annotations

from typing import Mapping


NON_LEGAL_EXTRAS = frozenset({"wide", "Overstep", "other"})


def team_runs(row: Mapping[str, str]) -> int:
    """Return the validated additive delivery total."""
    return int(row["runs"]) + int(row["extras1_runs"]) + int(row["extras_2_runs"])


def is_legal_ball(row: Mapping[str, str]) -> bool:
    """Return the Step 4 validated legal-delivery classification."""
    return row["extras_type"] not in NON_LEGAL_EXTRAS


def is_wicket(row: Mapping[str, str]) -> bool:
    """Return the source wicket flag for innings-state wicket count."""
    return row["is_wicket"] == "true"
