"""Run the Step 3 structural, coverage, and ordering audit without pandas."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
OUTPUT_PATH = ROOT / "work" / "data-quality-audit.json"
FILES = (
    "ball_by_ball.csv",
    "matches.csv",
    "competitions.csv",
    "teams.csv",
    "playing_eleven.csv",
    "competition_team_player_mapping.csv",
)


def load_csv(name: str) -> tuple[list[str], list[dict[str, str]]]:
    with (RAW_DIR / name).open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames:
            raise ValueError(f"No header found in {name}")
        return reader.fieldnames, list(reader)


def file_quality(headers: list[str], rows: list[dict[str, str]]) -> dict[str, object]:
    tuple_rows = [tuple(row.get(header, "") for header in headers) for row in rows]
    blank_counts = {
        header: sum(not row.get(header, "").strip() for row in rows)
        for header in headers
    }
    return {
        "row_count": len(rows),
        "column_count": len(headers),
        "exact_duplicate_row_count": len(tuple_rows) - len(set(tuple_rows)),
        "blank_counts": blank_counts,
    }


def as_ids(rows: list[dict[str, str]], field: str) -> set[str]:
    return {row[field] for row in rows if row[field].strip()}


def player_name_variants(rows: list[dict[str, str]], id_field: str, name_field: str) -> dict[str, list[str]]:
    names_by_id: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        if row[id_field].strip() and row[name_field].strip():
            names_by_id[row[id_field]].add(row[name_field])
    return {player_id: sorted(names) for player_id, names in names_by_id.items() if len(names) > 1}


def ball_ordering(rows: list[dict[str, str]]) -> dict[str, int]:
    coordinates: Counter[tuple[str, str, str]] = Counter()
    previous: dict[tuple[str, str], int] = {}
    regressions = 0
    invalid_numbers = 0
    for row in rows:
        coordinate = (row["match_id"], row["innings"], row["innings_ball_num"])
        coordinates[coordinate] += 1
        try:
            ball_number = int(row["innings_ball_num"])
        except ValueError:
            invalid_numbers += 1
            continue
        group = coordinate[:2]
        if group in previous and ball_number < previous[group]:
            regressions += 1
        previous[group] = ball_number
    return {
        "duplicate_match_innings_ball_coordinates": sum(count - 1 for count in coordinates.values() if count > 1),
        "raw_file_order_regressions_by_innings_ball_num": regressions,
        "non_integer_innings_ball_num": invalid_numbers,
    }


def main() -> None:
    loaded = {name: load_csv(name) for name in FILES}
    rows = {name: content[1] for name, content in loaded.items()}
    report: dict[str, object] = {
        "source_directory": "data/raw",
        "file_quality": {
            name: file_quality(*loaded[name]) for name in FILES
        },
    }

    balls = rows["ball_by_ball.csv"]
    matches = rows["matches.csv"]
    competitions = rows["competitions.csv"]
    playing = rows["playing_eleven.csv"]
    mapping = rows["competition_team_player_mapping.csv"]

    ball_match_ids = as_ids(balls, "match_id")
    match_ids = as_ids(matches, "match_id")
    playing_match_ids = as_ids(playing, "match_id")
    report["coverage"] = {
        "ball_by_ball_match_ids": len(ball_match_ids),
        "matches_match_ids": len(match_ids),
        "playing_eleven_match_ids": len(playing_match_ids),
        "matches_without_ball_by_ball": sorted(match_ids - ball_match_ids, key=int),
        "matches_without_playing_eleven": sorted(match_ids - playing_match_ids, key=int),
        "playing_eleven_without_matches": sorted(playing_match_ids - match_ids, key=int),
        "ball_by_ball_without_matches": sorted(ball_match_ids - match_ids, key=int),
        "matches_without_competition": sorted(
            as_ids(matches, "comp_id") - as_ids(competitions, "comp_id"), key=int
        ),
    }

    special_matches = {
        "abandoned_or_no_result": [],
        "revised_overs_or_target": [],
    }
    for row in matches:
        result = row["result"].strip().lower()
        if "abandoned" in result or "no result" in result:
            special_matches["abandoned_or_no_result"].append(
                {"match_id": row["match_id"], "result": row["result"]}
            )
        if any(row[field].strip() for field in ("first_inn_revised_overs", "second_inn_revised_overs", "revised_target")):
            special_matches["revised_overs_or_target"].append(
                {
                    "match_id": row["match_id"],
                    "first_inn_revised_overs": row["first_inn_revised_overs"],
                    "second_inn_revised_overs": row["second_inn_revised_overs"],
                    "revised_target": row["revised_target"],
                }
            )
    report["special_matches"] = special_matches
    report["ball_by_ball_ordering"] = ball_ordering(balls)
    report["innings_coverage"] = dict(sorted(Counter(row["innings"] for row in balls).items(), key=lambda item: int(item[0])))
    extra_innings_match_ids = sorted(
        {row["match_id"] for row in balls if int(row["innings"]) > 2}, key=int
    )
    special_match_ids = {
        row["match_id"] for row in special_matches["abandoned_or_no_result"]
    }
    revised_match_ids = {
        row["match_id"] for row in special_matches["revised_overs_or_target"]
    }
    competition_by_id = {row["comp_id"]: row for row in competitions}
    primary_competition_ids = {
        row["comp_id"]
        for row in competitions
        if row["match_format"] == "T20I" or row["comp_name"].startswith("IPL ")
    }
    scope_excluded_match_ids = {
        row["match_id"]
        for row in matches
        if row["comp_id"] not in primary_competition_ids
    }
    provisional_exclusion_match_ids = (
        special_match_ids
        | revised_match_ids
        | set(extra_innings_match_ids)
        | scope_excluded_match_ids
    )
    report["provisional_primary_population"] = {
        "exclude_match_ids": sorted(provisional_exclusion_match_ids, key=int),
        "exclude_match_count": len(provisional_exclusion_match_ids),
        "candidate_match_count": len(ball_match_ids - provisional_exclusion_match_ids),
        "match_ids_with_innings_3_or_4": extra_innings_match_ids,
        "scope_excluded_match_ids": sorted(scope_excluded_match_ids, key=int),
        "scope_excluded_competitions": [
            {
                "comp_id": competition_id,
                "comp_name": competition_by_id[competition_id]["comp_name"],
            }
            for competition_id in sorted(
                {
                    row["comp_id"]
                    for row in matches
                    if row["match_id"] in scope_excluded_match_ids
                },
                key=int,
            )
        ],
        "reason": (
            "Special match conditions require Step 4 state-reconstruction validation "
            "before inclusion; non-IPL T20 competitions are sensitivity-only under D-001."
        ),
    }
    report["player_name_variants"] = {
        "mapping": player_name_variants(mapping, "player_id", "player_name"),
        "striker": player_name_variants(balls, "striker_id", "striker_name"),
        "non_striker": player_name_variants(balls, "non_striker_id", "non_striker_name"),
        "bowler": player_name_variants(balls, "bowler_id", "bowler_name"),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
