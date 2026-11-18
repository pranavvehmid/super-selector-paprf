"""Step 7 ordinary-context baselines and pressure-versus-baseline deltas."""

from __future__ import annotations


MIN_OPPORTUNITIES = 60
MIN_MATCHES = 6
PRESSURE_BANDS = frozenset({"elevated", "high"})


def rate(numerator: int, denominator: int) -> float:
    """Return a zero-safe per-opportunity rate."""
    return numerator / denominator if denominator else 0.0


def eligible(
    ordinary_opportunities: int,
    pressure_opportunities: int,
    ordinary_matches: int,
    pressure_matches: int,
) -> bool:
    """Require meaningful evidence in both the baseline and pressure context."""
    return (
        ordinary_opportunities >= MIN_OPPORTUNITIES
        and pressure_opportunities >= MIN_OPPORTUNITIES
        and ordinary_matches >= MIN_MATCHES
        and pressure_matches >= MIN_MATCHES
    )
