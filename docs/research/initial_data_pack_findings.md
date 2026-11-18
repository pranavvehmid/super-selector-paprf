# Initial Data Pack Findings

**Purpose:** Preserve the structural findings documented before the current continuation. These findings are not player-performance analysis, pressure modelling, or player rankings.

**Source record:** `docs/original/RR_Super_Select_Hackathon_Project_Handoff.md`, section 3.  
**Current rule:** Reproduce the relevant check against `data/raw/` before relying on it in model code or the final report.

## Files supplied

| File | Previously recorded rows | Previously recorded columns | Intended use |
|---|---:|---:|---|
| `ball_by_ball.csv` | 200,999 | 33 | Delivery-level performance and match-state reconstruction |
| `matches.csv` | 883 | 22 | Match context, results, targets, revisions, and stage |
| `competitions.csv` | 141 | 4 | Competition and season context |
| `teams.csv` | 353 | 3 | Team identifiers and names within competition |
| `playing_eleven.csv` | 28,381 | 9 | Player participation, batting order, captain, wicketkeeper, and impact flags |
| `competition_team_player_mapping.csv` | 6,413 | 6 | Competition, team, and player mapping |
| Official Round 1 PDF | 2 pages | — | Formal challenge requirements |

The present local structural audit report, `work/data-audit.json`, confirms the six CSV row and column counts above and reports zero malformed row widths.

## Previously recorded coverage checks

The earlier handoff recorded the following findings. Re-verify when a later step needs them:

- Ball-by-ball records cover 867 distinct match IDs; `matches.csv` contains 883 match records.
- The 16 match records without ball-by-ball rows were recorded as `Match Abandoned`.
- `competitions.csv` has 141 records: 134 T20I and 7 T20.
- The seven T20 entries were recorded as IPL 2022, 2023, 2024, 2025, and 2026; Men's T20 Emerging Teams Asia Cup 2024; and Asia Cup Rising Stars 2025.
- Ball-by-ball data joined to 397 T20 matches and 470 T20I matches, totalling 867 matches.
- The competition-team-player mapping was recorded as 6,413 rows and 1,217 distinct player IDs.
- The playing-XI file was recorded as 28,381 rows, 880 distinct match IDs, and 1,082 distinct player IDs.
- Match dates and ball timestamps were recorded from 22 January 2022 through 1 November 2026.
- No exact duplicate rows were found in the six CSV files during the prior audit.
- Every ball-by-ball match ID matched a match record; every match competition ID and mapping competition ID matched `competitions.csv`.

## Join map

Use IDs as keys. Do not join on player names alone.

```text
ball_by_ball.match_id -> matches.match_id
matches.comp_id -> competitions.comp_id
playing_eleven.match_id -> matches.match_id
playing_eleven.player_id + team context -> competition_team_player_mapping
teams(comp_id, team_id) -> team names
```

## Important caveats to resolve before modelling

1. `runs`, `extras1_runs`, and `extras_2_runs` are separate. Validate their exact attribution before calculating team total, batter runs, bowler runs conceded, or performance metrics.
2. There is no explicit legal-delivery field. Derive legal balls carefully and validate the rule. `over_ball_num` may exceed six and cannot be assumed to be a legal-ball count.
3. `extras_type` is blank for most standard deliveries and has values including wide, legbyes, Overstep, byes, other, and Penalty. Validate treatment for each relevant metric.
4. Dismissal fields are blank for most non-wicket deliveries; inspect dismissal coding before wicket attribution.
5. Revised overs and revised targets are mostly blank. Do not assume every blank value means an ordinary, full-length match.
6. The data contains innings 1 and 2 predominantly, plus a small number of innings 3 and 4 records. Define their treatment explicitly.
7. The playing-XI file has some missing batting-order, captain, and wicketkeeper values. Use participation and impact flags only after field-level validation.
8. The player mapping is competition/team-specific. Confirm player-ID stability and name consistency before a multi-competition player analysis.
9. The two non-IPL T20 competitions must be explicitly included, excluded, or used only as a sensitivity check through D-001; do not let a simple `T20` filter choose the scope implicitly.

## What is not complete

- No field-level data dictionary has been completed.
- No full data-quality report or inclusion/exclusion policy has been approved.
- No innings reconstruction, legal-ball rule, or extras-attribution rule has been validated.
- No pressure definition, player metric, baseline, reliability model, validation result, recommendation, or ranking exists.
