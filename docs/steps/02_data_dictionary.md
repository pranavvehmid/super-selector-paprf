# Step 02 — Build the data dictionary and relationship map

**Status:** GATE PASSED
**Code:** `src/rrselect/io.py`

## Goal
Understand what every relevant field means and how the files connect.

## Tasks
- [ ] Document every column in each file: meaning, type, key/identifier/context/outcome.
- [ ] Confirm joins: ball_by_ball.match_id→matches.match_id; matches.comp_id→competitions.comp_id; playing_eleven.match_id→matches.match_id; player mapping links competition, team and player IDs.
- [ ] Use IDs, not names, as join keys. Check whether player IDs are stable across competitions; check ID/name inconsistencies.
- [ ] Mark explicitly where the source does not define a field's semantics.

## Output of this step
Data dictionary (docs/data_dictionary.md), relationship map, join specification.

## Decision gate
Every field used in the model has a clear interpretation and traceable source.

## Log of work on this step
- 2026-11-18: Added and ran `scripts/profile_schema.py`, a dependency-free structural profiler. Its output is retained in `work/schema-profile.json` and records observed types, blank counts, and sample values for every column. No player-performance analysis was performed.
- 2026-11-18: Added and ran `scripts/profile_field_domains.py`, recording observed value domains and numeric ranges in `work/field-domain-profile.json`. Completed `docs/data_dictionary.md` with all 77 fields, the ID-based join specification, and explicit prohibitions on using undefined delivery-accounting fields before Step 4 validation.
