# Data dictionary (Step 2 — to be completed)

Fill each table from the actual files. Mark any field whose meaning the source does not define as **UNDEFINED — needs validation**. Do not guess.

Files: `ball_by_ball.csv` (33 cols), `matches.csv` (22), `competitions.csv` (4), `teams.csv` (3), `playing_eleven.csv` (9), `competition_team_player_mapping.csv` (6). Column names are listed in `docs/original/RR_Super_Select_Hackathon_Project_Handoff.md` §3.2.

## Join map
```
ball_by_ball.match_id  → matches.match_id
matches.comp_id        → competitions.comp_id
playing_eleven.match_id→ matches.match_id
playing_eleven.player_id + team → competition_team_player_mapping (comp_id, team_id, player_id)
teams (comp_id, team_id) supplies team names
```

## Field tables
| File | Column | Meaning | Type | Role (key/context/outcome) | Validation status |
|---|---|---|---|---|---|
| _to fill_ | | | | | |
