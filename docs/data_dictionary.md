# Data Dictionary (Step 2)

## Evidence and use rules

This dictionary uses the supplied CSV headers, the file-level descriptions in `docs/original/RR_Super_Select_Hackathon_Project_Handoff.md`, `work/schema-profile.json`, and `work/field-domain-profile.json`. It does not infer cricket-accounting rules from a column name or value pattern.

- **Observed** means the field name, type, blankness, and listed values/ranges are directly present in the supplied CSV.
- **Verified join** means `work/relationship-check.json` found no unmatched IDs for that relationship on 18 November 2026.
- **Unresolved** means the supplied materials do not define the field semantics well enough to use it for a derived match-state or performance calculation. It must not be used for that purpose until Step 4 validates it.

## Relationship and join specification

| From | To | Key | Status and permitted use |
|---|---|---|---|
| `ball_by_ball` | `matches` | `match_id` | Verified join; attach match context to a delivery. |
| `playing_eleven` | `matches` | `match_id` | Verified join; attach match context to a participation record. |
| `matches` | `competitions` | `comp_id` | Verified join; attach competition context to a match. |
| `competition_team_player_mapping` | `competitions` | `comp_id` | Verified join; attach competition context to a mapping record. |
| `teams` | `competitions` | `comp_id` | Verified join; identify a team within a competition with `(comp_id, team_id)`. |
| `playing_eleven` | `competition_team_player_mapping` | `(comp_id, team_id, player_id)` after joining the match to its competition | Join specification; use IDs only. |

The relationship check also found no player ID with more than one display name within either the mapping or ball-by-ball file. This is name-consistency evidence, not proof that names are safe join keys.

## `ball_by_ball.csv` — 200,999 observed delivery records

| Field | Observed type / domain | Source-supported description and status | Role |
|---|---|---|---|
| `match_id` | integer; 867 values | Match identifier; verified to join `matches.match_id`. | key |
| `innings` | integer; 1–4 | Innings-sequence field; ordering and treatment of innings 3–4 are unresolved. | context |
| `overid` | integer; 1–20 | Over-labelled sequence field; exact ordering rule is unresolved. | context |
| `over_ball_num` | integer; 1–13 | Ball-labelled value within an over; values above 6 show it is not a legal-ball count by itself. | context |
| `innings_ball_num` | integer; 1–136 | Ball-labelled value within an innings; exact ordering and legal-ball semantics are unresolved. | context |
| `batting_team_id` | integer; 38 values | Team identifier on the delivery record. | context identifier |
| `bowling_team_id` | integer; 38 values | Team identifier on the delivery record. | context identifier |
| `striker_id` | integer; 888 values | Player identifier in the source's striker-labelled field. | participant identifier |
| `striker_name` | text; 885 values | Display name in the striker-labelled field; not a join key. | display context |
| `non_striker_id` | integer; 867 values | Player identifier in the non-striker-labelled field. | participant identifier |
| `non_striker_name` | text; 864 values | Display name in the non-striker-labelled field; not a join key. | display context |
| `bowler_id` | integer; 647 values | Player identifier in the source's bowler-labelled field. | participant identifier |
| `bowler_name` | text; 646 values | Display name in the bowler-labelled field; not a join key. | display context |
| `batting_type` | text; `RHB`, `LHB` | Source categorical field; its formal coding definition is not supplied. | context |
| `bowling_type` | text; 12 values | Source categorical field; its formal coding definition is not supplied. | context |
| `batting_order` | integer; 1–13 | Source order-labelled field; calculation and treatment of values above 11 are unresolved. | context |
| `runs` | integer; 0–6 | Delivery outcome field. Its attribution to batter or team, and relation to extras, are unresolved. | outcome — do not use for metrics yet |
| `is_four` | text boolean; `true`/`false` | Source flag; its relationship to `runs` is unresolved. | outcome — do not use for metrics yet |
| `is_six` | text boolean; `true`/`false` | Source flag; its relationship to `runs` is unresolved. | outcome — do not use for metrics yet |
| `is_wicket` | text boolean; `true`/`false` | Source flag; dismissal and bowler-credit treatment are unresolved. | outcome — do not use for metrics yet |
| `dismissal_type_id` | integer or blank; 8 values | Source dismissal-category identifier, populated on 10,881 records; codebook is not supplied. | outcome — unresolved |
| `dismissal_type` | text or blank; 9 labels | Source dismissal-category label, populated on 10,881 records; attribution treatment is unresolved. | outcome — unresolved |
| `dismissed_player_id` | integer or blank; 814 values | Source dismissed-player identifier, populated on 10,892 records; its relation to `is_wicket` needs validation. | outcome — unresolved |
| `extras_type` | text; 7 labels | Source extras category (`None`, `wide`, `legbyes`, `Overstep`, `byes`, `other`, `Penalty`); accounting and legal-ball treatment are unresolved. | outcome — unresolved |
| `extras1_runs` | integer; 0–5 | Source extras-labelled numeric field; exact attribution and combination rule are unresolved. | outcome — unresolved |
| `extras_2_runs` | integer; 0, 1, or 4 | Source extras-labelled numeric field; exact attribution and combination rule are unresolved. | outcome — unresolved |
| `pace_or_spin` | text; `Pace`/`Spin` | Source categorical field; formal classification rule is not supplied. | context |
| `bowl_speed` | numeric; -1–1456.1 | Source speed-labelled numeric field; unit and sentinel-value definition are not supplied. | context — unresolved |
| `stroke` | text or blank; 31 values | Source stroke-labelled categorical field; taxonomy is not supplied. | context |
| `delivery_style` | text or blank; 35 values | Source delivery-style-labelled categorical field; taxonomy is not supplied. | context |
| `over_or_around` | text or blank; `Over`/`Around` | Source categorical field; formal coding definition is not supplied. | context |
| `on_or_off` | text; `Off-side`/`On-side` | Source categorical field; formal coding definition is not supplied. | context |
| `delivery_ist_time` | text timestamp; 200,826 values | Header says IST but observed strings end in UTC; time interpretation needs validation before ordering use. | context — unresolved |

## `matches.csv` — 883 observed match records

| Field | Observed type / domain | Source-supported description and status | Role |
|---|---|---|---|
| `match_id` | integer; 883 values | Match identifier; joins to ball-by-ball and playing-XI records. | key |
| `comp_id` | integer; 138 values | Competition identifier; verified to join `competitions.comp_id`. | foreign key |
| `match_number` | integer; 1–75 | Source match-number field; numbering scope is not supplied. | context |
| `match_date` | date-like text; 686 values | Source match-date field. | context |
| `stage` | text; 7 values | Source stage field. | context |
| `venue_id` | integer; 98 values | Source venue identifier; no venue lookup table is supplied. | context identifier |
| `venue_country` | text; 17 values | Source venue-country field. | context |
| `home_team_id` | integer; 36 values | Source home-team identifier. | context identifier |
| `home_team` | text; 36 values | Source home-team display name; not a join key. | display context |
| `away_team_id` | integer; 36 values | Source away-team identifier. | context identifier |
| `away_team` | text; 36 values | Source away-team display name; not a join key. | display context |
| `home_team_captain_id` | integer or blank | Source home-captain identifier; blank-value semantics are not supplied. | context identifier |
| `away_team_captain_id` | integer or blank | Source away-captain identifier; blank-value semantics are not supplied. | context identifier |
| `toss_win_team_id` | integer or blank | Source toss-winner team identifier; blank-value semantics are not supplied. | context identifier |
| `toss_opted` | text or blank; `Fielding`/`Batting` | Source toss-decision field. | context |
| `man_of_the_match` | integer; includes 0 | Source award-labelled identifier; the meaning of 0 is not supplied. | context — unresolved |
| `first_inn_revised_overs` | integer or blank; 30–114 | Source revised-overs field; unit and blank-value semantics are unresolved. | context — unresolved |
| `second_inn_revised_overs` | integer or blank; 30–114 | Source revised-overs field; unit and blank-value semantics are unresolved. | context — unresolved |
| `revised_target` | integer or blank; 33–213 | Source revised-target field; blank-value semantics are unresolved. | context — unresolved |
| `knock_out` | integer; 0/1 | Source knockout-labelled flag; formal coding definition is not supplied. | context |
| `win_team_id` | integer or blank | Source winning-team identifier; blank-value semantics are not supplied. | outcome context |
| `result` | text; 670 values | Source result text. It must not label pressure because it contains post-match information. | post-outcome — prohibited for pressure |

## `competitions.csv` — 141 observed competition records

| Field | Observed type / domain | Source-supported description and status | Role |
|---|---|---|---|
| `comp_id` | integer; 141 values | Competition identifier; join key. | key |
| `comp_name` | text; 141 values | Competition display name; not a join key. | display context |
| `match_format` | text; `T20I`/`T20` | Source match-format field. Scope decision D-001 controls its use. | context |
| `season` | text-like; 8 values | Source season field, including split-season labels such as `2022/23`. | context |

## `teams.csv` — 353 observed competition-team records

| Field | Observed type / domain | Source-supported description and status | Role |
|---|---|---|---|
| `comp_id` | integer; 141 values | Competition identifier; verified to join `competitions.comp_id`. | foreign key |
| `team_id` | integer; 38 values | Team identifier; combine with `comp_id` for this file's team identity. | key component |
| `team_name` | text; 38 values | Team display name; not a join key. | display context |

## `playing_eleven.csv` — 28,381 observed participation records

| Field | Observed type / domain | Source-supported description and status | Role |
|---|---|---|---|
| `match_id` | integer; 880 values | Match identifier; verified to join `matches.match_id`. | foreign key |
| `team_id` | integer; 38 values | Source team identifier. | key component |
| `player_id` | integer; 1,082 values | Source player identifier. | key component |
| `batting_order` | integer or blank; 1–13 | Source order-labelled field; blank-value and values-above-11 treatment are unresolved. | context — unresolved |
| `is_played` | text boolean; `true`/`false` | Source participation-labelled flag; formal coding definition is not supplied. | context |
| `is_captain` | text boolean or blank | Source captain-labelled flag; blank-value semantics are not supplied. | context — unresolved |
| `is_wk` | text boolean or blank | Source wicketkeeper-labelled flag; blank-value semantics are not supplied. | context — unresolved |
| `is_impact` | integer; 0/1 | Source impact-labelled flag; formal coding definition is not supplied. | context — unresolved |
| `is_impact_off` | integer; 0/1 | Source impact-off-labelled flag; formal coding definition is not supplied. | context — unresolved |

## `competition_team_player_mapping.csv` — 6,413 observed mapping records

| Field | Observed type / domain | Source-supported description and status | Role |
|---|---|---|---|
| `comp_id` | integer; 140 values | Competition identifier; verified to join `competitions.comp_id`. | key component |
| `comp_name` | text; 140 values | Competition display name; not a join key. | display context |
| `team_id` | integer; 38 values | Team identifier. | key component |
| `team_name` | text; 38 values | Team display name; not a join key. | display context |
| `player_id` | integer; 1,217 values | Player identifier. Use with competition and team identifiers for this mapping. | key component |
| `player_name` | text; 1,210 values | Player display name; not a join key. | display context |

## Step 2 gate decision

**Gate passed on 18 November 2026.** The repository now has a source-traceable dictionary for every supplied field, the documented joins are verified, and every unresolved delivery/accounting semantic is explicitly prohibited from metric or match-state use until Step 4 validation. No player analysis or ranking has been performed.

The next step is the Step 3 data-quality and coverage audit. That audit must define eligibility and exclusions before Step 4 attempts to validate delivery accounting.
