"""Step 8 sample-size protection for pressure-versus-baseline signals."""

from __future__ import annotations

import math
from collections.abc import Iterable


SHRINKAGE_PRIOR_BALLS = 60


def mean(values: Iterable[float]) -> float:
    """Return arithmetic mean for a non-empty iterable."""
    values = list(values)
    return sum(values) / len(values)


def sample_standard_deviation(values: Iterable[float]) -> float:
    """Return zero-safe sample standard deviation."""
    values = list(values)
    if len(values) < 2:
        return 0.0
    average = mean(values)
    return math.sqrt(sum((value - average) ** 2 for value in values) / (len(values) - 1))


def z_score(value: float, average: float, standard_deviation: float) -> float:
    """Return zero when the peer variation is absent."""
    return (value - average) / standard_deviation if standard_deviation else 0.0


def shrink_to_peer(raw_signal: float, pressure_balls: int) -> tuple[float, float]:
    """Shrink a player signal toward the eligible-peer mean of zero."""
    weight = pressure_balls / (pressure_balls + SHRINKAGE_PRIOR_BALLS)
    return raw_signal * weight, weight
