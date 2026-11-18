# Supplied-Data Candidate Universe Inventory

**Generated:** 18 November 2026  
**Script:** scripts/build_candidate_universe.py  
**Output:** outputs/tables/supplied_data_candidate_universe.csv

## What this inventory is

This is a source-data coverage inventory for future player discovery. It is not a ranking, a role classification, a nationality table, an availability list, a scouting score or a selection recommendation.

## Population and calculation

The script selects every raw match whose joined competition is labelled T20I or whose competition name begins with IPL. This raw primary universe contains 853 matches in 136 competitions. It aggregates three direct indicators by player ID:

    batting_delivery_count = count of raw primary-scope deliveries where player_id = striker_id
    bowling_delivery_count = count of raw primary-scope deliveries where player_id = bowler_id
    playing_xi_match_count = distinct raw primary-scope matches where player_id appears in playing_eleven

It also records distinct batting matches, bowling matches and primary competitions. This is intentionally broader than the official ranking population: it includes raw primary matches before state-quality exclusions and therefore must not be used to quote Lens A eligibility or performance totals.

## Results

| Directly observed inventory measure | Count | Evidence meaning |
|---|---:|---|
| Unique player IDs in raw primary-scope inventory | 1,002 | Appears in playing XI and/or raw delivery participation. |
| IDs with at least one striker delivery | 824 | Direct batting-delivery evidence exists. |
| IDs with at least one bowler delivery | 596 | Direct bowling-delivery evidence exists. |
| IDs with at least one playing-XI record | 1,002 | Direct participation-record evidence exists. |
| Blank player names in generated inventory | 0 | Names are present for display only; IDs remain the key. |

## Limits and controls

- The source fields do not establish nationality, age, current team, availability, batting role, bowling role, technical quality, injury status, or scouting potential. Those columns are intentionally absent.
- A high delivery count measures recorded opportunity, not merit. It cannot be treated as a quality score.
- A player may be in the inventory but not qualify for the validated Lens A comparison, which separately uses 782 state-validated matches and 60-opportunity/six-match thresholds.
- Future discovery categorisation must be entered in docs/evidence/candidate_discovery_register.csv with a source reference and confidence note.
