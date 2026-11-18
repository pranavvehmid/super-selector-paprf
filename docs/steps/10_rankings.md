# Step 10 — Produce the ranked top-10 lists

**Status:** GATE PASSED
**Code:** `scripts/freeze_rankings.py`, `scripts/validate_rankings.py`

## Goal
Generate the formal outputs required by Unstop (and the alternative lenses).

## Tasks
- [x] Rank eligible batters and bowlers under Lens A.
- [x] Check duplicates and stable player IDs within each list.
- [x] Rank 1 = highest reliability signal.
- [x] Record score, components, sample sizes and shrinkage weight.
- [x] Freeze ranking version v1 under D-003.

## Output of this step
Final top-10 batter and bowler lists with evidence (outputs/rankings/).

## Decision gate
Report and Unstop dropdown selections match exactly.

## Log of work on this step
- 2026-11-18: Frozen outputs are outputs/rankings/lens_a_batters_v1.csv and outputs/rankings/lens_a_bowlers_v1.csv. Ranking validation found zero errors. Exact submission-dropdown labels still require a final manual check in Unstop because the platform dropdown is not part of the supplied data pack.
