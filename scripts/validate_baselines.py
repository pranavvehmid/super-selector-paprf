"""Validate Step 7 baseline formulas and eligibility flags."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rrselect.baselines import MIN_MATCHES, MIN_OPPORTUNITIES, eligible, rate


FILES = (
    ("batter", ROOT / "outputs" / "tables" / "batter_pressure_baselines.csv"),
    ("bowler", ROOT / "outputs" / "tables" / "bowler_pressure_baselines.csv"),
)
OUTPUT_PATH = ROOT / "work" / "baseline-validation.json"


def close(actual: str, expected: float) -> bool:
    return abs(float(actual) - expected) < 1e-6


def main() -> None:
    errors: list[dict[str, str]] = []
    counts: dict[str, int] = {}
    for role, path in FILES:
        row_count = 0
        with path.open("r", encoding="utf-8", newline="") as source:
            for row in csv.DictReader(source):
                row_count += 1
                if role == "batter":
                    ordinary_balls = int(row["ordinary_balls"])
                    pressure_balls = int(row["pressure_balls"])
                    expected_ordinary_rate = rate(int(row["ordinary_runs"]), ordinary_balls)
                    expected_pressure_rate = rate(int(row["pressure_runs"]), pressure_balls)
                    if not close(row["ordinary_runs_per_ball"], expected_ordinary_rate):
                        errors.append({"type": "batter_ordinary_rate", "player_id": row["player_id"]})
                    if not close(row["pressure_runs_per_ball"], expected_pressure_rate):
                        errors.append({"type": "batter_pressure_rate", "player_id": row["player_id"]})
                    expected_eligible = eligible(
                        ordinary_balls, pressure_balls,
                        int(row["ordinary_matches"]), int(row["pressure_matches"]),
                    )
                else:
                    ordinary_balls = int(row["ordinary_legal_balls"])
                    pressure_balls = int(row["pressure_legal_balls"])
                    expected_ordinary_economy = 6 * rate(int(row["ordinary_runs_conceded"]), ordinary_balls)
                    expected_pressure_economy = 6 * rate(int(row["pressure_runs_conceded"]), pressure_balls)
                    if not close(row["ordinary_economy"], expected_ordinary_economy):
                        errors.append({"type": "bowler_ordinary_economy", "player_id": row["player_id"]})
                    if not close(row["pressure_economy"], expected_pressure_economy):
                        errors.append({"type": "bowler_pressure_economy", "player_id": row["player_id"]})
                    expected_eligible = eligible(
                        ordinary_balls, pressure_balls,
                        int(row["ordinary_matches"]), int(row["pressure_matches"]),
                    )
                if (row["eligible"] == "true") != expected_eligible:
                    errors.append({"type": "eligibility_mismatch", "player_id": row["player_id"]})
        counts[role] = row_count
    report = {
        "rows_checked": counts,
        "minimum_opportunities": MIN_OPPORTUNITIES,
        "minimum_matches": MIN_MATCHES,
        "validation_error_count": len(errors),
        "errors": errors[:100],
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
