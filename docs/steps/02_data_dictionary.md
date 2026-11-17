# Step 02 — Build the data dictionary and relationship map

**Status:** NOT STARTED  
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
_(append dated notes here and in PROJECT_LOG.md)_
