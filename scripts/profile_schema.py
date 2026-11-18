"""Profile raw CSV structure for the Step 2 data dictionary without player analysis."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


CSV_FILENAMES = (
    "ball_by_ball.csv",
    "matches.csv",
    "competitions.csv",
    "teams.csv",
    "playing_eleven.csv",
    "competition_team_player_mapping.csv",
)


def classify(value: str) -> str:
    """Return a conservative observed value class without coercing source data."""
    if not value:
        return "blank"
    try:
        int(value)
    except ValueError:
        try:
            float(value)
        except ValueError:
            return "text"
        return "decimal"
    return "integer"


def profile_csv(path: Path) -> dict[str, object]:
    """Return row count and per-column observed structure for one CSV."""
    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames:
            raise ValueError(f"{path.name} has no header row.")

        columns = {
            name: {"blank_count": 0, "observed_types": Counter(), "samples": []}
            for name in reader.fieldnames
        }
        row_count = 0
        for row in reader:
            row_count += 1
            for name in reader.fieldnames:
                value = (row[name] or "").strip()
                columns[name]["observed_types"][classify(value)] += 1
                if value and len(columns[name]["samples"]) < 3:
                    columns[name]["samples"].append(value)
                if not value:
                    columns[name]["blank_count"] += 1

    return {
        "file": path.name,
        "row_count": row_count,
        "columns": [
            {
                "name": name,
                "blank_count": stats["blank_count"],
                "observed_types": dict(stats["observed_types"]),
                "samples": stats["samples"],
            }
            for name, stats in columns.items()
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()

    report = {
        "data_directory": str(arguments.data_directory.resolve()),
        "files": [profile_csv(arguments.data_directory / name) for name in CSV_FILENAMES],
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
