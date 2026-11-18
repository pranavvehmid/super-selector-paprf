"""Validate Step 6 aggregate tables against delivery-level attribution."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTION_PATH = ROOT / "data" / "processed" / "metric_attribution_deliveries.csv"
BATTER_PATH = ROOT / "outputs" / "tables" / "batter_context_metrics.csv"
BOWLER_PATH = ROOT / "outputs" / "tables" / "bowler_context_metrics.csv"
OUTPUT_PATH = ROOT / "work" / "player-metrics-validation.json"


def as_bool(value: str) -> int:
    return int(value == "true")


def new_group() -> dict[str, object]:
    return {
        "runs": 0,
        "balls_faced": 0,
        "dot_balls": 0,
        "fours": 0,
        "sixes": 0,
        "dismissals": 0,
        "runs_conceded": 0,
        "legal_balls": 0,
        "wickets": 0,
        "matches": set(),
    }


def aggregate_batters() -> dict[tuple[str, str], dict[str, int]]:
    groups: dict[tuple[str, str], dict[str, int]] = {}
    with ATTRIBUTION_PATH.open("r", encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            key = (row["striker_id"], row["pressure_band"])
            group = groups.setdefault(key, new_group())
            group["runs"] += int(row["batter_runs_attributed"])
            group["balls_faced"] += as_bool(row["batter_ball_faced"])
            group["dot_balls"] += as_bool(row["batter_dot"])
            group["fours"] += int(int(row["batter_runs_attributed"]) == 4)
            group["sixes"] += int(int(row["batter_runs_attributed"]) == 6)
            group["matches"].add(row["match_id"])
            if row["is_wicket"] == "true" and row["dismissed_player_id"].strip():
                dismissed_key = (row["dismissed_player_id"], row["pressure_band"])
                dismissed_group = groups.setdefault(dismissed_key, new_group())
                dismissed_group["dismissals"] += 1
                dismissed_group["matches"].add(row["match_id"])
    return groups


def aggregate_bowlers() -> dict[tuple[str, str], dict[str, int]]:
    groups: dict[tuple[str, str], dict[str, int]] = {}
    with ATTRIBUTION_PATH.open("r", encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            key = (row["bowler_id"], row["pressure_band"])
            group = groups.setdefault(key, new_group())
            group["runs_conceded"] += int(row["bowler_runs_conceded"])
            group["legal_balls"] += as_bool(row["bowler_legal_ball"])
            group["dot_balls"] += as_bool(row["bowler_dot"])
            group["wickets"] += as_bool(row["bowler_wicket"])
            group["matches"].add(row["match_id"])
    return groups


def validate(path: Path, expected: dict[tuple[str, str], dict[str, int]], fields: list[str]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    observed_keys = set()
    with path.open("r", encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            key = (row["player_id"], row["pressure_band"])
            observed_keys.add(key)
            group = expected.get(key, {})
            for field in fields:
                if int(row[field]) != group.get(field, 0):
                    errors.append({"type": "aggregate_mismatch", "field": field, "player_id": key[0], "band": key[1]})
            if int(row["distinct_matches"]) != len(group.get("matches", set())):
                errors.append({"type": "match_count_mismatch", "player_id": key[0], "band": key[1]})
    for key in set(expected) - observed_keys:
        errors.append({"type": "missing_aggregate", "player_id": key[0], "band": key[1]})
    return errors


def main() -> None:
    batter_groups = aggregate_batters()
    bowler_groups = aggregate_bowlers()
    errors = validate(
        BATTER_PATH,
        batter_groups,
        ["runs", "balls_faced", "dot_balls", "fours", "sixes", "dismissals"],
    )
    errors.extend(
        validate(
            BOWLER_PATH,
            bowler_groups,
            ["runs_conceded", "legal_balls", "dot_balls", "wickets"],
        )
    )
    report = {
        "batter_group_count": len(batter_groups),
        "bowler_group_count": len(bowler_groups),
        "validation_error_count": len(errors),
        "errors": errors[:100],
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
