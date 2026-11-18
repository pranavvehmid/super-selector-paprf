"""Validate frozen Step 10 ranking files."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = (
    ROOT / "outputs" / "rankings" / "lens_a_batters_v1.csv",
    ROOT / "outputs" / "rankings" / "lens_a_bowlers_v1.csv",
)
OUTPUT_PATH = ROOT / "work" / "ranking-validation.json"


def main() -> None:
    errors: list[dict[str, str]] = []
    for path in FILES:
        with path.open("r", encoding="utf-8", newline="") as source:
            rows = list(csv.DictReader(source))
        if len(rows) != 10:
            errors.append({"type": "row_count", "file": path.name})
        if [int(row["rank"]) for row in rows] != list(range(1, 11)):
            errors.append({"type": "rank_sequence", "file": path.name})
        if len({row["player_id"] for row in rows}) != len(rows):
            errors.append({"type": "duplicate_player_id", "file": path.name})
        signals = [float(row["reliability_signal"]) for row in rows]
        if signals != sorted(signals, reverse=True):
            errors.append({"type": "signal_order", "file": path.name})
        if any(row["ranking_version"] != "v1" for row in rows):
            errors.append({"type": "version", "file": path.name})
    report = {"validation_error_count": len(errors), "errors": errors}
    OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
