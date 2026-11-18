"""Apply the Step 5 pressure definition to validated pre-delivery state."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rrselect.pressure import phase, pressure_band, pressure_components


INPUT_PATH = ROOT / "data" / "interim" / "pre_delivery_state.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "pressure_labeled_deliveries.csv"
SUMMARY_PATH = ROOT / "work" / "pressure-definition-summary.json"


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    index_sums = Counter()
    fieldnames: list[str] | None = None
    row_count = 0

    with INPUT_PATH.open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as destination:
            writer: csv.DictWriter | None = None
            for row in reader:
                components = pressure_components(row)
                band = pressure_band(components["pressure_index"])
                result = {
                    **row,
                    "innings_phase": phase(int(row["pre_delivery_legal_balls"])),
                    "required_run_rate": f"{components['required_run_rate']:.6f}",
                    "pressure_progress": f"{components['progress']:.6f}",
                    "pressure_wicket_stress": f"{components['wicket_stress']:.6f}",
                    "pressure_run_rate_stress": f"{components['run_rate_stress']:.6f}",
                    "pressure_late_innings_stress": f"{components['late_innings_stress']:.6f}",
                    "pressure_index": f"{components['pressure_index']:.6f}",
                    "pressure_band": band,
                }
                if writer is None:
                    fieldnames = list(result.keys())
                    writer = csv.DictWriter(destination, fieldnames=fieldnames)
                    writer.writeheader()
                writer.writerow(result)
                key = f"innings_{row['innings']}:{band}"
                counts[key] += 1
                index_sums[f"innings_{row['innings']}"] += components["pressure_index"]
                row_count += 1

    summary = {
        "row_count": row_count,
        "definition_version": "v1",
        "bands": dict(sorted(counts.items())),
        "mean_pressure_index": {
            innings: index_sums[innings] / sum(
                count for key, count in counts.items() if key.startswith(f"{innings}:")
            )
            for innings in sorted(index_sums)
        },
        "leakage_guard": (
            "Uses only pre_delivery_* fields, the second-innings target known before "
            "that innings begins, and the innings number. It does not use the rated "
            "delivery outcome, result, winner, or a future delivery."
        ),
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Wrote {SUMMARY_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
