"""Build Step 7 ordinary-context baselines from delivery-level attribution."""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rrselect.baselines import MIN_MATCHES, MIN_OPPORTUNITIES, PRESSURE_BANDS, eligible, rate


INPUT_PATH = ROOT / "data" / "processed" / "metric_attribution_deliveries.csv"
BATTER_OUTPUT_PATH = ROOT / "outputs" / "tables" / "batter_pressure_baselines.csv"
BOWLER_OUTPUT_PATH = ROOT / "outputs" / "tables" / "bowler_pressure_baselines.csv"


def new_batter_group() -> dict[str, object]:
    return {"runs": 0, "balls": 0, "dots": 0, "dismissals": 0, "matches": set()}


def new_bowler_group() -> dict[str, object]:
    return {"runs": 0, "balls": 0, "dots": 0, "wickets": 0, "matches": set()}


def context(band: str) -> str:
    return "pressure" if band in PRESSURE_BANDS else "ordinary"


def main() -> None:
    batter_groups: dict[tuple[str, str], dict[str, object]] = {}
    bowler_groups: dict[tuple[str, str], dict[str, object]] = {}
    names: dict[str, str] = {}

    with INPUT_PATH.open("r", encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            bucket = context(row["pressure_band"])
            batter_key = (row["striker_id"], bucket)
            batter_group = batter_groups.setdefault(batter_key, new_batter_group())
            batter_group["runs"] += int(row["batter_runs_attributed"])
            batter_group["balls"] += int(row["batter_ball_faced"] == "true")
            batter_group["dots"] += int(row["batter_dot"] == "true")
            batter_group["matches"].add(row["match_id"])
            names[row["striker_id"]] = row["striker_name"]
            if row["is_wicket"] == "true" and row["dismissed_player_id"].strip():
                dismissed_key = (row["dismissed_player_id"], bucket)
                dismissed_group = batter_groups.setdefault(dismissed_key, new_batter_group())
                dismissed_group["dismissals"] += 1
                dismissed_group["matches"].add(row["match_id"])
                names.setdefault(row["dismissed_player_id"], row["dismissed_player_id"])

            bowler_key = (row["bowler_id"], bucket)
            bowler_group = bowler_groups.setdefault(bowler_key, new_bowler_group())
            bowler_group["runs"] += int(row["bowler_runs_conceded"])
            bowler_group["balls"] += int(row["bowler_legal_ball"] == "true")
            bowler_group["dots"] += int(row["bowler_dot"] == "true")
            bowler_group["wickets"] += int(row["bowler_wicket"] == "true")
            bowler_group["matches"].add(row["match_id"])
            names[row["bowler_id"]] = row["bowler_name"]

    BATTER_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    batter_fields = [
        "player_id", "player_name", "ordinary_runs", "ordinary_balls",
        "ordinary_matches", "ordinary_runs_per_ball", "ordinary_dot_rate",
        "ordinary_dismissal_rate", "pressure_runs", "pressure_balls",
        "pressure_matches", "pressure_runs_per_ball", "pressure_dot_rate",
        "pressure_dismissal_rate", "runs_per_ball_delta", "dot_rate_delta",
        "dismissal_rate_delta", "eligible",
    ]
    with BATTER_OUTPUT_PATH.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=batter_fields)
        writer.writeheader()
        player_ids = sorted({player_id for player_id, _ in batter_groups}, key=int)
        for player_id in player_ids:
            ordinary = batter_groups.get((player_id, "ordinary"), new_batter_group())
            pressure = batter_groups.get((player_id, "pressure"), new_batter_group())
            ordinary_rpb = rate(int(ordinary["runs"]), int(ordinary["balls"]))
            pressure_rpb = rate(int(pressure["runs"]), int(pressure["balls"]))
            ordinary_dot = rate(int(ordinary["dots"]), int(ordinary["balls"]))
            pressure_dot = rate(int(pressure["dots"]), int(pressure["balls"]))
            ordinary_dismissal = rate(int(ordinary["dismissals"]), int(ordinary["balls"]))
            pressure_dismissal = rate(int(pressure["dismissals"]), int(pressure["balls"]))
            writer.writerow({
                "player_id": player_id,
                "player_name": names[player_id],
                "ordinary_runs": ordinary["runs"],
                "ordinary_balls": ordinary["balls"],
                "ordinary_matches": len(ordinary["matches"]),
                "ordinary_runs_per_ball": f"{ordinary_rpb:.6f}",
                "ordinary_dot_rate": f"{ordinary_dot:.6f}",
                "ordinary_dismissal_rate": f"{ordinary_dismissal:.6f}",
                "pressure_runs": pressure["runs"],
                "pressure_balls": pressure["balls"],
                "pressure_matches": len(pressure["matches"]),
                "pressure_runs_per_ball": f"{pressure_rpb:.6f}",
                "pressure_dot_rate": f"{pressure_dot:.6f}",
                "pressure_dismissal_rate": f"{pressure_dismissal:.6f}",
                "runs_per_ball_delta": f"{pressure_rpb - ordinary_rpb:.6f}",
                "dot_rate_delta": f"{pressure_dot - ordinary_dot:.6f}",
                "dismissal_rate_delta": f"{pressure_dismissal - ordinary_dismissal:.6f}",
                "eligible": str(eligible(
                    int(ordinary["balls"]), int(pressure["balls"]),
                    len(ordinary["matches"]), len(pressure["matches"]),
                )).lower(),
            })

    bowler_fields = [
        "player_id", "player_name", "ordinary_runs_conceded", "ordinary_legal_balls",
        "ordinary_matches", "ordinary_economy", "ordinary_dot_rate",
        "ordinary_wicket_rate", "pressure_runs_conceded", "pressure_legal_balls",
        "pressure_matches", "pressure_economy", "pressure_dot_rate",
        "pressure_wicket_rate", "economy_delta", "dot_rate_delta",
        "wicket_rate_delta", "eligible",
    ]
    with BOWLER_OUTPUT_PATH.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=bowler_fields)
        writer.writeheader()
        player_ids = sorted({player_id for player_id, _ in bowler_groups}, key=int)
        for player_id in player_ids:
            ordinary = bowler_groups.get((player_id, "ordinary"), new_bowler_group())
            pressure = bowler_groups.get((player_id, "pressure"), new_bowler_group())
            ordinary_economy = 6 * rate(int(ordinary["runs"]), int(ordinary["balls"]))
            pressure_economy = 6 * rate(int(pressure["runs"]), int(pressure["balls"]))
            ordinary_dot = rate(int(ordinary["dots"]), int(ordinary["balls"]))
            pressure_dot = rate(int(pressure["dots"]), int(pressure["balls"]))
            ordinary_wicket = rate(int(ordinary["wickets"]), int(ordinary["balls"]))
            pressure_wicket = rate(int(pressure["wickets"]), int(pressure["balls"]))
            writer.writerow({
                "player_id": player_id,
                "player_name": names[player_id],
                "ordinary_runs_conceded": ordinary["runs"],
                "ordinary_legal_balls": ordinary["balls"],
                "ordinary_matches": len(ordinary["matches"]),
                "ordinary_economy": f"{ordinary_economy:.6f}",
                "ordinary_dot_rate": f"{ordinary_dot:.6f}",
                "ordinary_wicket_rate": f"{ordinary_wicket:.6f}",
                "pressure_runs_conceded": pressure["runs"],
                "pressure_legal_balls": pressure["balls"],
                "pressure_matches": len(pressure["matches"]),
                "pressure_economy": f"{pressure_economy:.6f}",
                "pressure_dot_rate": f"{pressure_dot:.6f}",
                "pressure_wicket_rate": f"{pressure_wicket:.6f}",
                "economy_delta": f"{pressure_economy - ordinary_economy:.6f}",
                "dot_rate_delta": f"{pressure_dot - ordinary_dot:.6f}",
                "wicket_rate_delta": f"{pressure_wicket - ordinary_wicket:.6f}",
                "eligible": str(eligible(
                    int(ordinary["balls"]), int(pressure["balls"]),
                    len(ordinary["matches"]), len(pressure["matches"]),
                )).lower(),
            })
    print(f"Wrote {BATTER_OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Wrote {BOWLER_OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Eligibility requires {MIN_OPPORTUNITIES} opportunities and {MIN_MATCHES} matches in each context.")


if __name__ == "__main__":
    main()
