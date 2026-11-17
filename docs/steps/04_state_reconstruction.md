# Step 04 — Reconstruct each innings and the pre-delivery match state

**Status:** NOT STARTED  
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
_(append dated notes here and in PROJECT_LOG.md)_
