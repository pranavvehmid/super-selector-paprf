"""Profile observed CSV field domains for the Step 2 data dictionary."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
OUTPUT_PATH = ROOT / "work" / "field-domain-profile.json"
NUMBER_RE = re.compile(r"^-?\d+(?:\.\d+)?$")
MAX_VALUES = 20


def is_blank(value: str | None) -> bool:
    return value is None or value.strip() == ""


def profile_file(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames:
            raise ValueError(f"No header found in {path.name}")

        fields = {
            name: {"blank_count": 0, "values": Counter(), "numeric_values": []}
            for name in reader.fieldnames
        }
        row_count = 0
        for row in reader:
            row_count += 1
            for name, value in row.items():
                field = fields[name]
                if is_blank(value):
                    field["blank_count"] += 1
                    continue
                value = value.strip()
                field["values"][value] += 1
                if NUMBER_RE.fullmatch(value):
                    field["numeric_values"].append(float(value))

    field_profiles = []
    for name in reader.fieldnames:
        field = fields[name]
        values = field["values"]
        numeric_values = field["numeric_values"]
        profile: dict[str, object] = {
            "name": name,
            "blank_count": field["blank_count"],
            "nonblank_distinct_count": len(values),
            "most_common_values": values.most_common(MAX_VALUES),
        }
        if values and len(numeric_values) == sum(values.values()):
            profile["numeric_min"] = min(numeric_values)
            profile["numeric_max"] = max(numeric_values)
        field_profiles.append(profile)

    return {"file": path.name, "row_count": row_count, "fields": field_profiles}


def main() -> None:
    profiles = [profile_file(path) for path in sorted(RAW_DIR.glob("*.csv"))]
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(profiles, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
