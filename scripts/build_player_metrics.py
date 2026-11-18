"""Create Step 6 attribution records and player-by-pressure aggregates."""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rrselect.metrics import (
    batter_ball_faced,
    batter_dot,
    batter_runs,
    bowler_dot,
    bowler_legal_ball,
    bowler_runs_conceded,
    bowler_wicket,
    is_metric_eligible,
)


INPUT_PATH = ROOT / "data" / "processed" / "pressure_labeled_deliveries.csv"
ATTRIBUTION_PATH = ROOT / "data" / "processed" / "metric_attribution_deliveries.csv"
BATTER_OUTPUT_PATH = ROOT / "outputs" / "tables" / "batter_context_metrics.csv"
BOWLER_OUTPUT_PATH = ROOT / "outputs" / "tables" / "bowler_context_metrics.csv"


def increment(group: dict[str, object], field: str, value: int) -> None:
    group[field] = int(group[field]) + value


def main() -> None:
    ATTRIBUTION_PATH.parent.mkdir(parents=True, exist_ok=True)
    BATTER_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    batter_groups: dict[tuple[str, str], dict[str, object]] = {}
    bowler_groups: dict[tuple[str, str], dict[str, object]] = {}
    player_names: dict[str, str] = {}
    dismissal_groups: dict[tuple[str, str], set[str]] = defaultdict(set)

    with INPUT_PATH.open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        with ATTRIBUTION_PATH.open("w", encoding="utf-8", newline="") as destination:
            writer: csv.DictWriter | None = None
            for row in reader:
                eligible = is_metric_eligible(row)
                batter_run_value = batter_runs(row) if eligible else 0
                batter_ball = batter_ball_faced(row)
                bowler_run_value = bowler_runs_conceded(row) if eligible else 0
                legal_ball = bowler_legal_ball(row)
                result = {
                    **row,
                    "metric_eligible": str(eligible).lower(),
                    "batter_runs_attributed": batter_run_value,
                    "batter_ball_faced": str(batter_ball).lower(),
                    "batter_dot": str(batter_dot(row)).lower(),
                    "bowler_runs_conceded": bowler_run_value,
                    "bowler_legal_ball": str(legal_ball).lower(),
                    "bowler_dot": str(bowler_dot(row)).lower(),
                    "bowler_wicket": str(bowler_wicket(row)).lower(),
                }
                if writer is None:
                    writer = csv.DictWriter(destination, fieldnames=list(result))
                    writer.writeheader()
                writer.writerow(result)

                player_names[row["striker_id"]] = row["striker_name"]
                player_names[row["non_striker_id"]] = row["non_striker_name"]
                player_names[row["bowler_id"]] = row["bowler_name"]
                band = row["pressure_band"]
                batter_key = (row["striker_id"], band)
                batter_group = batter_groups.setdefault(
                    batter_key,
                    {
                        "player_id": row["striker_id"],
                        "player_name": row["striker_name"],
                        "pressure_band": band,
                        "runs": 0,
                        "balls_faced": 0,
                        "dot_balls": 0,
                        "fours": 0,
                        "sixes": 0,
                        "matches": set(),
                    },
                )
                increment(batter_group, "runs", batter_run_value)
                increment(batter_group, "balls_faced", int(batter_ball))
                increment(batter_group, "dot_balls", int(batter_dot(row)))
                increment(batter_group, "fours", int(batter_run_value == 4))
                increment(batter_group, "sixes", int(batter_run_value == 6))
                batter_group["matches"].add(row["match_id"])

                bowler_key = (row["bowler_id"], band)
                bowler_group = bowler_groups.setdefault(
                    bowler_key,
                    {
                        "player_id": row["bowler_id"],
                        "player_name": row["bowler_name"],
                        "pressure_band": band,
                        "runs_conceded": 0,
                        "legal_balls": 0,
                        "dot_balls": 0,
                        "wickets": 0,
                        "matches": set(),
                    },
                )
                increment(bowler_group, "runs_conceded", bowler_run_value)
                increment(bowler_group, "legal_balls", int(legal_ball))
                increment(bowler_group, "dot_balls", int(bowler_dot(row)))
                increment(bowler_group, "wickets", int(bowler_wicket(row)))
                bowler_group["matches"].add(row["match_id"])

                if row["dismissed_player_id"].strip():
                    if row["is_wicket"] == "true":
                        dismissal_groups[(row["dismissed_player_id"], band)].add(
                            row["match_id"]
                        )

    for key, dismissal_matches in dismissal_groups.items():
        if key not in batter_groups:
            batter_groups[key] = {
                "player_id": key[0],
                "player_name": player_names.get(key[0], key[0]),
                "pressure_band": key[1],
                "runs": 0,
                "balls_faced": 0,
                "dot_balls": 0,
                "fours": 0,
                "sixes": 0,
                "matches": set(),
            }
        batter_groups[key]["dismissals"] = len(dismissal_matches)
        batter_groups[key]["matches"].update(dismissal_matches)

    def write_batters() -> None:
        fields = [
            "player_id",
            "player_name",
            "pressure_band",
            "runs",
            "balls_faced",
            "dot_balls",
            "fours",
            "sixes",
            "dismissals",
            "distinct_matches",
        ]
        with BATTER_OUTPUT_PATH.open("w", encoding="utf-8", newline="") as destination:
            writer = csv.DictWriter(destination, fieldnames=fields)
            writer.writeheader()
            for group in sorted(
                batter_groups.values(),
                key=lambda item: (str(item["player_id"]), str(item["pressure_band"])),
            ):
                writer.writerow(
                    {
                        **{field: group.get(field, 0) for field in fields},
                        "distinct_matches": len(group["matches"]),
                    }
                )

    def write_bowlers() -> None:
        fields = [
            "player_id",
            "player_name",
            "pressure_band",
            "runs_conceded",
            "legal_balls",
            "dot_balls",
            "wickets",
            "distinct_matches",
        ]
        with BOWLER_OUTPUT_PATH.open("w", encoding="utf-8", newline="") as destination:
            writer = csv.DictWriter(destination, fieldnames=fields)
            writer.writeheader()
            for group in sorted(
                bowler_groups.values(),
                key=lambda item: (str(item["player_id"]), str(item["pressure_band"])),
            ):
                writer.writerow(
                    {
                        **{field: group.get(field, 0) for field in fields},
                        "distinct_matches": len(group["matches"]),
                    }
                )

    write_batters()
    write_bowlers()
    print(f"Wrote {ATTRIBUTION_PATH.relative_to(ROOT)}")
    print(f"Wrote {BATTER_OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Wrote {BOWLER_OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
