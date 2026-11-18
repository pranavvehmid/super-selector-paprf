"""Freeze the Step 10 primary Lens A rankings from validated signals."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "batters": ROOT / "outputs" / "tables" / "batter_reliability_signals.csv",
    "bowlers": ROOT / "outputs" / "tables" / "bowler_reliability_signals.csv",
}
OUTPUTS = {
    "batters": ROOT / "outputs" / "rankings" / "lens_a_batters_v1.csv",
    "bowlers": ROOT / "outputs" / "rankings" / "lens_a_bowlers_v1.csv",
}
MANIFEST_PATH = ROOT / "outputs" / "rankings" / "ranking_manifest_v1.json"
TOP_N = 10


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))


def main() -> None:
    manifest: dict[str, object] = {
        "version": "v1",
        "method": "Lens A pressure-versus-ordinary reliability signal",
        "scope": "IPL and T20I only; 782 validated matches after documented exclusions",
        "ranking_rule": "Descending shrinkage-protected reliability_signal",
        "shrinkage_prior_pressure_balls": 60,
        "top_n": TOP_N,
        "files": {},
    }
    for role, path in INPUTS.items():
        rows = sorted(
            load_rows(path),
            key=lambda row: float(row["reliability_signal"]),
            reverse=True,
        )[:TOP_N]
        output_rows = [
            {
                "rank": index,
                **row,
                "ranking_version": "v1",
            }
            for index, row in enumerate(rows, start=1)
        ]
        output_path = OUTPUTS[role]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8", newline="") as destination:
            writer = csv.DictWriter(destination, fieldnames=list(output_rows[0]))
            writer.writeheader()
            writer.writerows(output_rows)
        manifest["files"][role] = {
            "path": str(output_path.relative_to(ROOT)).replace("\\", "/"),
            "player_ids_in_rank_order": [row["player_id"] for row in output_rows],
        }
        print(f"Wrote {output_path.relative_to(ROOT)}")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {MANIFEST_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
