"""Create a factual supplied-data player universe for later discovery work.

This is an inventory, not a scouting score, role verdict, nationality record or
selection recommendation. It uses only the locked IPL/T20I primary scope.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUTPUT = ROOT / "outputs" / "tables" / "supplied_data_candidate_universe.csv"


def read_rows(name: str) -> list[dict[str, str]]:
    with (RAW / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    competitions = {row["comp_id"]: row for row in read_rows("competitions.csv")}
    matches = {row["match_id"]: row for row in read_rows("matches.csv")}
    primary_match_ids = {
        match_id
        for match_id, match in matches.items()
        if (competition := competitions[match["comp_id"]])["match_format"] == "T20I"
        or competition["comp_name"].startswith("IPL ")
    }
    players: dict[str, dict[str, object]] = defaultdict(lambda: {
        "player_name": "", "batting_delivery_count": 0, "bowling_delivery_count": 0,
        "batting_match_ids": set(), "bowling_match_ids": set(), "playing_xi_match_ids": set(),
        "competition_ids": set(),
    })

    for row in read_rows("ball_by_ball.csv"):
        if row["match_id"] not in primary_match_ids:
            continue
        comp_id = matches[row["match_id"]]["comp_id"]
        striker = players[row["striker_id"]]
        striker["player_name"] = row["striker_name"]
        striker["batting_delivery_count"] += 1
        striker["batting_match_ids"].add(row["match_id"])
        striker["competition_ids"].add(comp_id)
        bowler = players[row["bowler_id"]]
        bowler["player_name"] = row["bowler_name"]
        bowler["bowling_delivery_count"] += 1
        bowler["bowling_match_ids"].add(row["match_id"])
        bowler["competition_ids"].add(comp_id)

    for row in read_rows("playing_eleven.csv"):
        if row["match_id"] not in primary_match_ids:
            continue
        player = players[row["player_id"]]
        player["player_name"] = player["player_name"] or row["player_id"]
        player["playing_xi_match_ids"].add(row["match_id"])
        player["competition_ids"].add(matches[row["match_id"]]["comp_id"])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "player_id", "player_name", "batting_delivery_count", "batting_match_count",
        "bowling_delivery_count", "bowling_match_count", "playing_xi_match_count",
        "primary_competition_count", "inventory_note",
    ]
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for player_id, player in sorted(players.items(), key=lambda item: int(item[0])):
            writer.writerow({
                "player_id": player_id,
                "player_name": player["player_name"],
                "batting_delivery_count": player["batting_delivery_count"],
                "batting_match_count": len(player["batting_match_ids"]),
                "bowling_delivery_count": player["bowling_delivery_count"],
                "bowling_match_count": len(player["bowling_match_ids"]),
                "playing_xi_match_count": len(player["playing_xi_match_ids"]),
                "primary_competition_count": len(player["competition_ids"]),
                "inventory_note": "Supplied-data participation inventory only; not a role, quality or selection judgment.",
            })
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
