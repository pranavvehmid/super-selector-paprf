# Step 05 — Define pressure transparently (batting and bowling)

**Status:** NOT STARTED  
**Code:** `src/rrselect/pressure.py`

## Goal
Create a meaningful, reproducible pressure definition using only pre-delivery information.

## Tasks
- [ ] Second-innings candidates: required run rate vs. expectation, balls remaining, wickets in hand, runs required, phase, knockout context (not assumed to mean every ball is high pressure).
- [ ] First-innings candidates: balls/overs remaining, wickets in hand, current rate vs. competition/season/phase expectation, phase.
- [ ] Batting pressure = difficulty faced by the batting side; bowling pressure = context in which the bowler must restrict/take wickets; outcomes measured separately.
- [ ] Define an 'ordinary' comparison group. Test a continuous index and bands (ordinary/elevated/high).
- [ ] Justify each indicator and weight/threshold; test sensitivity.
- [ ] No outcome of the rated ball, no match result, no future information.

## Output of this step
Written pressure definition, formula/logic, bands and rationale for both innings and both disciplines.

## Decision gate
Interpretable, available from the data, and leakage-free.

## Log of work on this step
_(append dated notes here and in PROJECT_LOG.md)_
