"""Build Step 8 shrinkage-protected reliability signals; not final rankings."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rrselect.reliability import (
    SHRINKAGE_PRIOR_BALLS,
    mean,
    sample_standard_deviation,
    shrink_to_peer,
    z_score,
)


INPUTS = {
    "batter": ROOT / "outputs" / "tables" / "batter_pressure_baselines.csv",
    "bowler": ROOT / "outputs" / "tables" / "bowler_pressure_baselines.csv",
}
OUTPUTS = {
    "batter": ROOT / "outputs" / "tables" / "batter_reliability_signals.csv",
    "bowler": ROOT / "outputs" / "tables" / "bowler_reliability_signals.csv",
}


def load_eligible(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as source:
        return [row for row in csv.DictReader(source) if row["eligible"] == "true"]


def component_statistics(rows: list[dict[str, str]], fields: list[str]) -> dict[str, tuple[float, float]]:
    return {
        field: (
            mean(float(row[field]) for row in rows),
            sample_standard_deviation(float(row[field]) for row in rows),
        )
        for field in fields
    }


def build_batter(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    fields = ["runs_per_ball_delta", "dot_rate_delta", "dismissal_rate_delta"]
    stats = component_statistics(rows, fields)
    results = []
    for row in rows:
        rpb = z_score(float(row[fields[0]]), *stats[fields[0]])
        dot = -z_score(float(row[fields[1]]), *stats[fields[1]])
        dismissal = -z_score(float(row[fields[2]]), *stats[fields[2]])
        raw_signal = (rpb + dot + dismissal) / 3
        shrunk_signal, weight = shrink_to_peer(raw_signal, int(row["pressure_balls"]))
        results.append({
            "player_id": row["player_id"],
            "player_name": row["player_name"],
            "ordinary_balls": row["ordinary_balls"],
            "pressure_balls": row["pressure_balls"],
            "ordinary_matches": row["ordinary_matches"],
            "pressure_matches": row["pressure_matches"],
            "runs_per_ball_delta": row["runs_per_ball_delta"],
            "dot_rate_delta": row["dot_rate_delta"],
            "dismissal_rate_delta": row["dismissal_rate_delta"],
            "raw_signal": f"{raw_signal:.6f}",
            "shrinkage_weight": f"{weight:.6f}",
            "reliability_signal": f"{shrunk_signal:.6f}",
        })
    return results


def build_bowler(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    fields = ["economy_delta", "dot_rate_delta", "wicket_rate_delta"]
    stats = component_statistics(rows, fields)
    results = []
    for row in rows:
        economy = -z_score(float(row[fields[0]]), *stats[fields[0]])
        dot = z_score(float(row[fields[1]]), *stats[fields[1]])
        wicket = z_score(float(row[fields[2]]), *stats[fields[2]])
        raw_signal = (economy + dot + wicket) / 3
        shrunk_signal, weight = shrink_to_peer(raw_signal, int(row["pressure_legal_balls"]))
        results.append({
            "player_id": row["player_id"],
            "player_name": row["player_name"],
            "ordinary_legal_balls": row["ordinary_legal_balls"],
            "pressure_legal_balls": row["pressure_legal_balls"],
            "ordinary_matches": row["ordinary_matches"],
            "pressure_matches": row["pressure_matches"],
            "economy_delta": row["economy_delta"],
            "dot_rate_delta": row["dot_rate_delta"],
            "wicket_rate_delta": row["wicket_rate_delta"],
            "raw_signal": f"{raw_signal:.6f}",
            "shrinkage_weight": f"{weight:.6f}",
            "reliability_signal": f"{shrunk_signal:.6f}",
        })
    return results


def write(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    batters = build_batter(load_eligible(INPUTS["batter"]))
    bowlers = build_bowler(load_eligible(INPUTS["bowler"]))
    write(OUTPUTS["batter"], batters)
    write(OUTPUTS["bowler"], bowlers)
    print(f"Wrote {OUTPUTS['batter'].relative_to(ROOT)}")
    print(f"Wrote {OUTPUTS['bowler'].relative_to(ROOT)}")
    print(f"Shrinkage prior: {SHRINKAGE_PRIOR_BALLS} pressure balls.")


if __name__ == "__main__":
    main()
