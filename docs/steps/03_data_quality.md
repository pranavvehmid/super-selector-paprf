# Step 03 — Complete the data-quality and coverage audit

**Status:** NOT STARTED  
**Code:** `src/rrselect/data_quality.py`

## Goal
Establish what data is reliable enough to use and identify exclusions.

## Tasks
- [ ] Check missing values, duplicates, impossible values, inconsistent IDs.
- [ ] Check match coverage across ball-by-ball, matches, competitions and playing-XI files.
- [ ] Identify abandoned, shortened, tied, super-over, incomplete and multi-innings (3rd/4th innings) matches.
- [ ] Review revised overs/targets and flag matches needing special handling.
- [ ] Validate chronology and ball ordering within each match and innings.
- [ ] Investigate player-mapping consistency, aliases, and incomplete metadata.
- [ ] Document inclusion/exclusion reasons.

## Output of this step
Data-quality report and reproducible inclusion/exclusion policy.

## Decision gate
Do not score records whose delivery, player or match context cannot be interpreted reliably.

## Log of work on this step
_(append dated notes here and in PROJECT_LOG.md)_
