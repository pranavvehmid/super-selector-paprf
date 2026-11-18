"""Profile delivery-accounting fields before innings reconstruction."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "ball_by_ball.csv"
AUDIT_PATH = ROOT / "work" / "data-quality-audit.json"
OUTPUT_PATH = ROOT / "work" / "delivery-accounting-validation.json"


def as_int(row: dict[str, str], field: str) -> int:
    return int(row[field])


def main() -> None:
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    excluded_matches = set(audit["provisional_primary_population"]["exclude_match_ids"])

    extras = Counter()
    extras_run_pairs = Counter()
    run_flag_mismatches = Counter()
    dismissal_consistency = Counter()
    delivery_counter_transitions = Counter()
    previous_by_innings: dict[tuple[str, str], dict[str, str]] = {}
    included_rows = 0

    with RAW_PATH.open("r", encoding="utf-8-sig", newline="") as source:
        for row in csv.DictReader(source):
            if row["match_id"] in excluded_matches:
                continue
            included_rows += 1
            extras_type = row["extras_type"]
            extras[extras_type] += 1
            extras_run_pairs[
                (extras_type, as_int(row, "runs"), as_int(row, "extras1_runs"), as_int(row, "extras_2_runs"))
            ] += 1

            if (row["is_four"] == "true") != (as_int(row, "runs") == 4):
                run_flag_mismatches["is_four_vs_runs"] += 1
            if (row["is_six"] == "true") != (as_int(row, "runs") == 6):
                run_flag_mismatches["is_six_vs_runs"] += 1
            if row["is_four"] == "true" and row["is_six"] == "true":
                run_flag_mismatches["both_boundary_flags_true"] += 1
            if (row["is_wicket"] == "true") != bool(row["dismissal_type"].strip()):
                dismissal_consistency["is_wicket_vs_dismissal_type"] += 1
            if (row["is_wicket"] == "true") != bool(row["dismissed_player_id"].strip()):
                dismissal_consistency["is_wicket_vs_dismissed_player_id"] += 1

            innings_key = (row["match_id"], row["innings"])
            previous = previous_by_innings.get(innings_key)
            if previous is not None:
                same_over = row["overid"] == previous["overid"]
                current_ball = as_int(row, "over_ball_num")
                previous_ball = as_int(previous, "over_ball_num")
                if same_over:
                    delivery_counter_transitions["same_over_rows"] += 1
                    if current_ball != previous_ball + 1:
                        delivery_counter_transitions["nonsequential_over_ball_num_within_over"] += 1
                else:
                    delivery_counter_transitions["new_over_rows"] += 1
                    if current_ball != 1:
                        delivery_counter_transitions["new_over_not_starting_at_one"] += 1
            previous_by_innings[innings_key] = row

    report = {
        "population": {
            "included_delivery_rows": included_rows,
            "excluded_match_count": len(excluded_matches),
            "rule": "Uses the provisional Step 3 population; no delivery accounting rule is inferred.",
        },
        "extras_type_counts": dict(sorted(extras.items())),
        "top_extras_run_combinations": [
            {
                "extras_type": key[0],
                "runs": key[1],
                "extras1_runs": key[2],
                "extras_2_runs": key[3],
                "row_count": count,
            }
            for key, count in extras_run_pairs.most_common(30)
        ],
        "run_flag_mismatches": dict(run_flag_mismatches),
        "dismissal_consistency_mismatches": dict(dismissal_consistency),
        "delivery_counter_transitions": dict(delivery_counter_transitions),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
