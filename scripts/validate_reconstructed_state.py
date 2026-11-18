"""Independently validate the Step 4 pre-delivery state output."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rrselect.state import is_legal_ball, is_wicket, team_runs


INPUT_PATH = ROOT / "data" / "interim" / "pre_delivery_state.csv"
OUTPUT_PATH = ROOT / "work" / "state-reconstruction-validation.json"


def main() -> None:
    errors: list[dict[str, object]] = []
    expected_by_innings: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"runs": 0, "wickets": 0, "legal_balls": 0, "last_ball": 0}
    )
    first_innings_totals: dict[str, int] = {}
    row_count = 0

    with INPUT_PATH.open("r", encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            row_count += 1
            innings_key = (row["match_id"], row["innings"])
            expected = expected_by_innings[innings_key]
            observed = {
                "runs": int(row["pre_delivery_runs"]),
                "wickets": int(row["pre_delivery_wickets"]),
                "legal_balls": int(row["pre_delivery_legal_balls"]),
            }
            if observed != {
                "runs": expected["runs"],
                "wickets": expected["wickets"],
                "legal_balls": expected["legal_balls"],
            }:
                errors.append(
                    {
                        "type": "pre_delivery_state_mismatch",
                        "match_id": row["match_id"],
                        "innings": row["innings"],
                        "innings_ball_num": row["innings_ball_num"],
                    }
                )
            ball_number = int(row["innings_ball_num"])
            if ball_number <= expected["last_ball"]:
                errors.append(
                    {
                        "type": "nonincreasing_innings_ball_num",
                        "match_id": row["match_id"],
                        "innings": row["innings"],
                        "innings_ball_num": row["innings_ball_num"],
                    }
                )
            if int(row["pre_delivery_balls_remaining"]) != max(
                120 - expected["legal_balls"], 0
            ):
                errors.append(
                    {
                        "type": "balls_remaining_mismatch",
                        "match_id": row["match_id"],
                        "innings": row["innings"],
                        "innings_ball_num": row["innings_ball_num"],
                    }
                )
            if row["innings"] == "2":
                target = first_innings_totals.get(row["match_id"])
                if target is None or int(row["target"]) != target + 1:
                    errors.append(
                        {
                            "type": "target_mismatch",
                            "match_id": row["match_id"],
                            "innings_ball_num": row["innings_ball_num"],
                        }
                    )
                elif int(row["pre_delivery_runs_required"]) != max(
                    target + 1 - expected["runs"], 0
                ):
                    errors.append(
                        {
                            "type": "runs_required_mismatch",
                            "match_id": row["match_id"],
                            "innings_ball_num": row["innings_ball_num"],
                        }
                    )
            expected["runs"] += team_runs(row)
            expected["wickets"] += int(is_wicket(row))
            expected["legal_balls"] += int(is_legal_ball(row))
            expected["last_ball"] = ball_number
            if row["innings"] == "1":
                first_innings_totals[row["match_id"]] = expected["runs"]

    output = {
        "row_count": row_count,
        "validation_error_count": len(errors),
        "errors": errors[:100],
        "rules": {
            "team_runs": "runs + extras1_runs + extras_2_runs",
            "legal_ball": "extras_type not in {wide, Overstep, other}",
            "wickets_lost": "is_wicket == true",
        },
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
