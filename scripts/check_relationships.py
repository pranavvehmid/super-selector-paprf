"""Validate documented ID relationships for Step 2 without player-performance analysis."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def values(path: Path, column: str) -> set[str]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return {row[column] for row in csv.DictReader(stream) if row[column]}


def id_name_variants(path: Path, id_column: str, name_column: str) -> dict[str, list[str]]:
    """Return IDs associated with more than one nonblank display name."""
    names_by_id: dict[str, set[str]] = {}
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            identifier = row[id_column]
            name = row[name_column]
            if identifier and name:
                names_by_id.setdefault(identifier, set()).add(name)
    return {
        identifier: sorted(names)
        for identifier, names in names_by_id.items()
        if len(names) > 1
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    source = arguments.data_directory

    match_ids = values(source / "matches.csv", "match_id")
    competition_ids = values(source / "competitions.csv", "comp_id")
    ball_match_ids = values(source / "ball_by_ball.csv", "match_id")
    playing_match_ids = values(source / "playing_eleven.csv", "match_id")
    match_competition_ids = values(source / "matches.csv", "comp_id")
    mapping_competition_ids = values(source / "competition_team_player_mapping.csv", "comp_id")
    team_competition_ids = values(source / "teams.csv", "comp_id")
    mapping_name_variants = id_name_variants(
        source / "competition_team_player_mapping.csv", "player_id", "player_name"
    )
    ball_name_variants = {}
    for id_column, name_column in (
        ("striker_id", "striker_name"),
        ("non_striker_id", "non_striker_name"),
        ("bowler_id", "bowler_name"),
    ):
        variants = id_name_variants(source / "ball_by_ball.csv", id_column, name_column)
        for identifier, names in variants.items():
            ball_name_variants.setdefault(identifier, set()).update(names)
    ball_name_variants = {
        identifier: sorted(names)
        for identifier, names in ball_name_variants.items()
        if len(names) > 1
    }

    checks = {
        "ball_by_ball.match_id_to_matches.match_id": sorted(ball_match_ids - match_ids),
        "playing_eleven.match_id_to_matches.match_id": sorted(playing_match_ids - match_ids),
        "matches.comp_id_to_competitions.comp_id": sorted(match_competition_ids - competition_ids),
        "mapping.comp_id_to_competitions.comp_id": sorted(mapping_competition_ids - competition_ids),
        "teams.comp_id_to_competitions.comp_id": sorted(team_competition_ids - competition_ids),
    }
    report = {
        "unmatched_ids": checks,
        "all_relationship_checks_pass": all(not missing for missing in checks.values()),
        "player_name_variants": {
            "mapping": mapping_name_variants,
            "ball_by_ball": ball_name_variants,
        },
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not report["all_relationship_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
