# Step 04 — Reconstruct each innings and the pre-delivery match state

**Status:** GATE PASSED
**Code:** `src/rrselect/state.py`

## Goal
Turn delivery records into a trustworthy timeline of the match situation before each ball.

## Tasks
- [ ] Order deliveries using innings_ball_num / over fields (timestamps as a cross-check).
- [ ] Validate what `runs`, `extras1_runs`, `extras_2_runs` mean and how they combine into team runs vs. batter runs vs. bowler-conceded runs.
- [ ] Derive legal balls and balls remaining (do NOT assume over_ball_num is a legal-ball count).
- [ ] Derive cumulative score and wickets before each delivery.
- [ ] Second innings: derive target and runs required (handle revised targets/shortened matches where data supports it).
- [ ] Compute required run rate, wickets in hand, current run rate, other pre-delivery features.
- [ ] Cross-check reconstructed totals/wickets against match records.
- [ ] Treat first-innings and second-innings states separately.

## Output of this step
Validated ball-level table with reconstructed PRE-delivery match state.

## Decision gate
No pressure label until innings state and legal-ball logic pass validation.

## Log of work on this step
- 2026-11-18: Added and ran scripts/validate_delivery_accounting.py against the 813-match provisional population. It confirms candidate delivery ordering and documents unsafe shortcuts, but does not establish the required accounting semantics. See docs/delivery_accounting_validation.md and work/delivery-accounting-validation.json.
- 2026-11-18: Checked the supplied archive and project records for a data-provider codebook; none was present. The field-level accounting rule remains blocked pending a provider definition or authorised scorecard reconciliation.
- 2026-11-18: Reconciled the state rules against source structure and outcomes. Team runs match all 394 ordinary run-margin results; the inferred legal-ball rule passes all retained complete overs; independent reconstruction validation found zero row-level errors. Held out malformed-over matches 14130, 14164, and 41509. After restricting primary analysis to IPL and T20I, generated data/interim/pre_delivery_state.csv for 782 matches.

## Log of work on this step
_(append dated notes here and in PROJECT_LOG.md)_
