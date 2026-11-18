"""Validate proposed Step 4 team-run and legal-ball rules against source structure."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
AUDIT_PATH = ROOT / "work" / "data-quality-audit.json"
OUTPUT_PATH = ROOT / "work" / "state-rule-validation.json"
RUN_MARGIN_RE = re.compile(r"won by (\d+) runs?$", re.IGNORECASE)
WICKET_MARGIN_RE = re.compile(r"won by (\d+) wickets?$", re.IGNORECASE)


def load_rows(name: str) -> list[dict[str, str]]:
    with (RAW_DIR / name).open("r", encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def total_runs(row: dict[str, str]) -> int:
    return int(row["runs"]) + int(row["extras1_runs"]) + int(row["extras_2_runs"])


def is_legal_ball(row: dict[str, str]) -> bool:
    return row["extras_type"] not in {"wide", "Overstep", "other"}


def main() -> None:
    quality_audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    excluded_matches = set(quality_audit["provisional_primary_population"]["exclude_match_ids"])
    matches = {
        row["match_id"]: row
        for row in load_rows("matches.csv")
        if row["match_id"] not in excluded_matches
    }
    balls = [
        row
        for row in load_rows("ball_by_ball.csv")
        if row["match_id"] in matches and row["innings"] in {"1", "2"}
    ]

    innings_rows: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    over_rows: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in balls:
        innings_rows[(row["match_id"], row["innings"])].append(row)
        over_rows[(row["match_id"], row["innings"], row["overid"])].append(row)

    nonfinal_over_failures = []
    for innings_key, rows in innings_rows.items():
        over_ids = sorted({int(row["overid"]) for row in rows})
        final_over_id = max(over_ids)
        for over_id in over_ids:
            if over_id == final_over_id:
                continue
            records = over_rows[(innings_key[0], innings_key[1], str(over_id))]
            legal_count = sum(is_legal_ball(row) for row in records)
            if legal_count != 6:
                nonfinal_over_failures.append(
                    {
                        "match_id": innings_key[0],
                        "innings": innings_key[1],
                        "overid": over_id,
                        "legal_ball_count": legal_count,
                        "delivery_count": len(records),
                    }
                )

    innings_totals = {
        key: {
            "runs": sum(total_runs(row) for row in rows),
            "wickets": sum(row["is_wicket"] == "true" for row in rows),
            "legal_balls": sum(is_legal_ball(row) for row in rows),
        }
        for key, rows in innings_rows.items()
    }

    margin_checks = {
        "run_margin_matches_checked": 0,
        "run_margin_matches_matched": 0,
        "run_margin_mismatches": [],
        "wicket_margin_matches_checked": 0,
        "wicket_margin_matches_matched": 0,
        "wicket_margin_mismatches": [],
    }
    for match_id, match in matches.items():
        first = innings_totals.get((match_id, "1"))
        second = innings_totals.get((match_id, "2"))
        if first is None or second is None:
            continue
        result = match["result"].strip()
        run_match = RUN_MARGIN_RE.search(result)
        wicket_match = WICKET_MARGIN_RE.search(result)
        if run_match:
            expected = int(run_match.group(1))
            observed = first["runs"] - second["runs"]
            margin_checks["run_margin_matches_checked"] += 1
            if observed == expected:
                margin_checks["run_margin_matches_matched"] += 1
            else:
                margin_checks["run_margin_mismatches"].append(
                    {"match_id": match_id, "result": result, "expected": expected, "observed": observed}
                )
        if wicket_match:
            expected = int(wicket_match.group(1))
            observed = 10 - second["wickets"]
            margin_checks["wicket_margin_matches_checked"] += 1
            if observed == expected:
                margin_checks["wicket_margin_matches_matched"] += 1
            else:
                margin_checks["wicket_margin_mismatches"].append(
                    {"match_id": match_id, "result": result, "expected": expected, "observed": observed}
                )

    report = {
        "population": {
            "candidate_match_count": len(matches),
            "delivery_rows_in_innings_1_or_2": len(balls),
            "rules_tested": {
                "team_runs": "runs + extras1_runs + extras_2_runs",
                "legal_ball": "extras_type is neither wide, Overstep, nor other",
                "wickets_lost": "is_wicket == true",
            },
        },
        "complete_over_test": {
            "nonfinal_overs_checked": sum(
                1
                for key, rows in innings_rows.items()
                for over_id in {int(row["overid"]) for row in rows}
                if over_id != max(int(row["overid"]) for row in rows)
            ),
            "failure_count": len(nonfinal_over_failures),
            "failures": nonfinal_over_failures,
        },
        "state_reconstruction_holdout": {
            "match_ids": sorted(
                {failure["match_id"] for failure in nonfinal_over_failures}, key=int
            ),
            "reason": "At least one nonfinal over does not contain six inferred legal balls.",
        },
        "match_margin_checks": margin_checks,
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
