"""Step 9 sensitivity checks for shrinkage and pressure-context choices."""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rrselect.baselines import MIN_MATCHES, MIN_OPPORTUNITIES, eligible, rate
from rrselect.reliability import mean, sample_standard_deviation, z_score


INPUT_PATH = ROOT / "data" / "processed" / "metric_attribution_deliveries.csv"
BASELINE_SIGNAL_PATHS = {
    "batter": ROOT / "outputs" / "tables" / "batter_reliability_signals.csv",
    "bowler": ROOT / "outputs" / "tables" / "bowler_reliability_signals.csv",
}
OUTPUT_PATH = ROOT / "work" / "robustness-validation.json"


def new_group() -> dict[str, object]:
    return {
        "runs": 0,
        "balls": 0,
        "dots": 0,
        "dismissals": 0,
        "wickets": 0,
        "matches": set(),
    }


def build_strict_rows(role: str) -> list[dict[str, object]]:
    groups: dict[tuple[str, str], dict[str, object]] = {}
    names: dict[str, str] = {}
    with INPUT_PATH.open("r", encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            if row["pressure_band"] == "ordinary":
                bucket = "ordinary"
            elif row["pressure_band"] == "high":
                bucket = "pressure"
            else:
                continue
            if role == "batter":
                key = (row["striker_id"], bucket)
                group = groups.setdefault(key, new_group())
                group["runs"] += int(row["batter_runs_attributed"])
                group["balls"] += int(row["batter_ball_faced"] == "true")
                group["dots"] += int(row["batter_dot"] == "true")
                group["matches"].add(row["match_id"])
                names[row["striker_id"]] = row["striker_name"]
                if row["is_wicket"] == "true" and row["dismissed_player_id"].strip():
                    dismissed_key = (row["dismissed_player_id"], bucket)
                    dismissed = groups.setdefault(dismissed_key, new_group())
                    dismissed["dismissals"] += 1
                    dismissed["matches"].add(row["match_id"])
                    names.setdefault(row["dismissed_player_id"], row["dismissed_player_id"])
            else:
                key = (row["bowler_id"], bucket)
                group = groups.setdefault(key, new_group())
                group["runs"] += int(row["bowler_runs_conceded"])
                group["balls"] += int(row["bowler_legal_ball"] == "true")
                group["dots"] += int(row["bowler_dot"] == "true")
                group["wickets"] += int(row["bowler_wicket"] == "true")
                group["matches"].add(row["match_id"])
                names[row["bowler_id"]] = row["bowler_name"]

    rows = []
    player_ids = {player_id for player_id, _ in groups}
    for player_id in player_ids:
        ordinary = groups.get((player_id, "ordinary"), new_group())
        pressure = groups.get((player_id, "pressure"), new_group())
        if not eligible(
            int(ordinary["balls"]), int(pressure["balls"]),
            len(ordinary["matches"]), len(pressure["matches"]),
        ):
            continue
        if role == "batter":
            values = (
                rate(int(pressure["runs"]), int(pressure["balls"])) - rate(int(ordinary["runs"]), int(ordinary["balls"])),
                rate(int(pressure["dots"]), int(pressure["balls"])) - rate(int(ordinary["dots"]), int(ordinary["balls"])),
                rate(int(pressure["dismissals"]), int(pressure["balls"])) - rate(int(ordinary["dismissals"]), int(ordinary["balls"])),
            )
        else:
            values = (
                6 * rate(int(pressure["runs"]), int(pressure["balls"])) - 6 * rate(int(ordinary["runs"]), int(ordinary["balls"])),
                rate(int(pressure["dots"]), int(pressure["balls"])) - rate(int(ordinary["dots"]), int(ordinary["balls"])),
                rate(int(pressure["wickets"]), int(pressure["balls"])) - rate(int(ordinary["wickets"]), int(ordinary["balls"])),
            )
        rows.append({
            "player_id": player_id,
            "player_name": names[player_id],
            "pressure_balls": int(pressure["balls"]),
            "deltas": values,
        })
    return rows


def strict_scores(role: str) -> dict[str, float]:
    rows = build_strict_rows(role)
    statistics = [
        (mean(row["deltas"][index] for row in rows), sample_standard_deviation(row["deltas"][index] for row in rows))
        for index in range(3)
    ]
    scores = {}
    for row in rows:
        first = z_score(row["deltas"][0], *statistics[0])
        second = z_score(row["deltas"][1], *statistics[1])
        third = z_score(row["deltas"][2], *statistics[2])
        if role == "batter":
            raw = (first - second - third) / 3
        else:
            raw = (-first + second + third) / 3
        scores[str(row["player_id"])] = raw * row["pressure_balls"] / (row["pressure_balls"] + 60)
    return scores


def load_base_scores(role: str) -> dict[str, tuple[float, float]]:
    with BASELINE_SIGNAL_PATHS[role].open("r", encoding="utf-8", newline="") as source:
        return {
            row["player_id"]: (float(row["raw_signal"]), float(row["pressure_balls"] if role == "batter" else row["pressure_legal_balls"]))
            for row in csv.DictReader(source)
        }


def top_ids(scores: dict[str, float], limit: int = 10) -> list[str]:
    return [player_id for player_id, _ in sorted(scores.items(), key=lambda item: item[1], reverse=True)[:limit]]


def main() -> None:
    report: dict[str, object] = {
        "minimum_opportunities": MIN_OPPORTUNITIES,
        "minimum_matches": MIN_MATCHES,
        "roles": {},
    }
    for role in ("batter", "bowler"):
        base = load_base_scores(role)
        prior_scores = {
            str(prior): {
                player_id: raw * pressure_balls / (pressure_balls + prior)
                for player_id, (raw, pressure_balls) in base.items()
            }
            for prior in (30, 60, 90)
        }
        reference_top = set(top_ids(prior_scores["60"]))
        strict = strict_scores(role)
        strict_top = set(top_ids(strict))
        report["roles"][role] = {
            "eligible_base_count": len(base),
            "eligible_high_only_count": len(strict),
            "prior_top10_overlap_with_60": {
                prior: len(reference_top & set(top_ids(scores)))
                for prior, scores in prior_scores.items()
            },
            "high_only_top10_overlap_with_base": len(reference_top & strict_top),
        }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
