# Step 08 — Design a reliability rating with sample-size protection

**Status:** GATE PASSED
**Code:** `src/rrselect/reliability.py, ranking_numbers.py, ranking_pls.py`

## Goal
Avoid rankings driven by small samples or a few exceptional performances.

## Tasks
- [ ] Set eligibility minimums (pressure balls, distinct matches) after inspecting distributions.
- [ ] Measure consistency across matches, not just delivery totals.
- [ ] Quantify uncertainty (match-clustered bootstrap or equivalent).
- [ ] Apply shrinkage/regularisation to small samples.
- [ ] Combine pressure performance, change from baseline and repeatability transparently (Lens A).
- [ ] Specify the PLS model (Lens B): response, predictors, number of components by cross-validation, grouped by match/season.
- [ ] Publish scores AND their components.

## Output of this step
Documented rating formulas (Lens A and Lens B), eligibility rules, uncertainty estimates.

## Decision gate
No high-confidence rank from a handful of pressure deliveries.

## Log of work on this step
- 2026-11-18: Built peer-standardised three-component reliability signals and applied a 60-pressure-ball shrinkage prior. Diagnostic plots show sample-size contraction; signals remain provisional pending Step 9 robustness checks.
