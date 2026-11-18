# Step 09 — Validate the model and test ranking robustness

**Status:** GATE PASSED
**Code:** `scripts/validate_robustness.py`

## Goal
Check that rankings reflect repeatable pressure performance, not an artefact of the formula.

## Tasks
- [x] Alternative pressure-sample test: high-only versus elevated/high.
- [x] Shrinkage-prior test: 30, 60 and 90 pressure balls.
- [x] Record the stability results and limitations.
- [ ] Season/competition holdouts are deferred: small player samples would make them misleading rather than confirmatory.
- [ ] Lens B comparison is deferred because D-003 locks Lens A as the official submission method.

## Output of this step
Validation tables, sensitivity analysis, uncertainty notes, finalised rating specification.

## Decision gate
Final rankings remain defensible under sensible alternatives.

## Log of work on this step
- 2026-11-18: The base population requires 60 pressure opportunities and six pressure matches. Every batter top-10 remains in the top-10 under priors of 30, 60 and 90 balls. Bowler overlap is 9/10 at prior 30 and 10/10 at 60 and 90. High-only pressure tests retain 7/10 batters and 5/10 bowlers, which is expected because the eligibility population contracts from 176 to 105 batters and from 219 to 157 bowlers. The official elevated/high definition and 60-ball prior are therefore retained. See work/robustness-validation.json.
