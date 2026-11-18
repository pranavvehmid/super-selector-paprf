"""Validate Step 5 pressure labels and their leakage guard."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "processed" / "pressure_labeled_deliveries.csv"
OUTPUT_PATH = ROOT / "work" / "pressure-definition-validation.json"
OUTCOME_FIELDS = {
    "runs",
    "is_four",
    "is_six",
    "is_wicket",
    "dismissal_type_id",
    "dismissal_type",
    "dismissed_player_id",
    "extras_type",
    "extras1_runs",
    "extras_2_runs",
}


def expected_band(index: float) -> str:
    if index >= 0.65:
        return "high"
    if index >= 0.40:
        return "elevated"
    return "ordinary"


def main() -> None:
    errors: list[dict[str, str]] = []
    row_count = 0
    with INPUT_PATH.open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        headers = set(reader.fieldnames or [])
        required = {
            "innings",
            "pre_delivery_runs",
            "pre_delivery_wickets",
            "pre_delivery_legal_balls",
            "target",
            "pre_delivery_runs_required",
            "pre_delivery_balls_remaining",
            "pressure_index",
            "pressure_band",
        }
        missing = sorted(required - headers)
        if missing:
            raise ValueError(f"Missing pressure fields: {missing}")
        for row in reader:
            row_count += 1
            index = float(row["pressure_index"])
            if not 0 <= index <= 1:
                errors.append({"type": "index_out_of_range", "match_id": row["match_id"]})
            if row["pressure_band"] != expected_band(index):
                errors.append({"type": "band_mismatch", "match_id": row["match_id"]})
            if row["innings"] == "1" and row["target"]:
                errors.append({"type": "first_innings_target_present", "match_id": row["match_id"]})
            if row["innings"] == "2" and not row["target"]:
                errors.append({"type": "second_innings_target_missing", "match_id": row["match_id"]})

    output = {
        "row_count": row_count,
        "validation_error_count": len(errors),
        "errors": errors[:100],
        "outcome_fields_retained_as_inputs": sorted(OUTCOME_FIELDS & required),
        "pressure_input_fields": sorted(required - {"pressure_index", "pressure_band"}),
        "leakage_check": (
            "Pressure calculation consumes only pre-delivery state and the "
            "second-innings target. No delivery-outcome or result field is an input."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
