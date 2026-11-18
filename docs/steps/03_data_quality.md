# Step 03 — Complete the data-quality and coverage audit

**Status:** GATE PASSED
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
- 2026-11-18: Added and ran scripts/audit_data_quality.py, a dependency-free audit that checks exact duplicates, coverage, player display-name consistency, candidate delivery ordering, special matches, and provisional exclusions. Its full result is stored in work/data-quality-audit.json; the human-readable policy is in docs/data_quality_report.md.
