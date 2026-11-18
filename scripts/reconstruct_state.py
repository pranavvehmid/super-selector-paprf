"""Reconstruct leakage-free pre-delivery state for validated Step 4 matches."""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rrselect.state import is_legal_ball, is_wicket, team_runs


RAW_DIR = ROOT / "data" / "raw"
QUALITY_AUDIT_PATH = ROOT / "work" / "data-quality-audit.json"
RULE_VALIDATION_PATH = ROOT / "work" / "state-rule-validation.json"
OUTPUT_PATH = ROOT / "data" / "interim" / "pre_delivery_state.csv"
SUMMARY_PATH = ROOT / "work" / "state-reconstruction-summary.json"


def load_rows(name: str) -> list[dict[str, str]]:
    with (RAW_DIR / name).open("r", encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def main() -> None:
    quality_audit = json.loads(QUALITY_AUDIT_PATH.read_text(encoding="utf-8"))
    rule_validation = json.loads(RULE_VALIDATION_PATH.read_text(encoding="utf-8"))
    excluded_match_ids = set(
        quality_audit["provisional_primary_population"]["exclude_match_ids"]
    )
    excluded_match_ids.update(
        rule_validation["state_reconstruction_holdout"]["match_ids"]
    )

    matches = {
        row["match_id"]: row
        for row in load_rows("matches.csv")
        if row["match_id"] not in excluded_match_ids
    }
    rows_by_innings: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in load_rows("ball_by_ball.csv"):
        if row["match_id"] in matches and row["innings"] in {"1", "2"}:
            rows_by_innings[(row["match_id"], row["innings"])].append(row)

    reconstructed: list[dict[str, object]] = []
    innings_totals: dict[tuple[str, str], int] = {}
    for innings_key, rows in rows_by_innings.items():
        rows.sort(key=lambda row: int(row["innings_ball_num"]))
        cumulative_runs = 0
        cumulative_wickets = 0
        cumulative_legal_balls = 0
        for row in rows:
            reconstructed.append(
                {
                    **row,
                    "pre_delivery_runs": cumulative_runs,
                    "pre_delivery_wickets": cumulative_wickets,
                    "pre_delivery_legal_balls": cumulative_legal_balls,
                }
            )
            cumulative_runs += team_runs(row)
            cumulative_wickets += int(is_wicket(row))
            cumulative_legal_balls += int(is_legal_ball(row))
        innings_totals[innings_key] = cumulative_runs

    for row in reconstructed:
        match_id = str(row["match_id"])
        innings = str(row["innings"])
        row["pre_delivery_balls_remaining"] = max(
            120 - int(row["pre_delivery_legal_balls"]), 0
        )
        if innings == "2":
            target = innings_totals[(match_id, "1")] + 1
            row["target"] = target
            row["pre_delivery_runs_required"] = max(
                target - int(row["pre_delivery_runs"]), 0
            )
        else:
            row["target"] = ""
            row["pre_delivery_runs_required"] = ""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(reconstructed[0].keys())
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reconstructed)

    summary = {
        "included_match_count": len(matches),
        "excluded_match_ids": sorted(excluded_match_ids, key=int),
        "delivery_rows": len(reconstructed),
        "innings_count": len(rows_by_innings),
        "state_definition": {
            "team_runs": "runs + extras1_runs + extras_2_runs",
            "legal_ball": "extras_type not in {wide, Overstep, other}",
            "wickets_lost": "is_wicket == true",
            "ordering": "ascending innings_ball_num within match_id and innings",
            "second_innings_target": "first innings total + 1",
            "balls_per_innings": 120,
        },
        "limitations": [
            "Only Step 3 and Step 4 holdout matches are excluded.",
            "Revised-condition and innings 3/4 matches remain excluded.",
            "Wicket state uses the source is_wicket flag; dismissal attribution remains a later metric task.",
        ],
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Wrote {SUMMARY_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
