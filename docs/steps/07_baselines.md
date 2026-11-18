# Step 07 — Establish each player's normal-performance baseline

**Status:** GATE PASSED
**Code:** `src/rrselect/baselines.py`

## Goal
Answer: how does the player perform under pressure compared with their usual level?

## Tasks
- [ ] Baseline in ordinary situations; performance in elevated/high pressure.
- [ ] Compare with the player's own baseline, adjusting for role, phase, competition, season where supported.
- [ ] Consider both absolute pressure performance and change from baseline.
- [ ] Keep IPL and T20I visible; test competition adjustment or separate comparisons.

## Output of this step
Player-level baseline and pressure tables with context definitions.

## Decision gate
Comparison is like-for-like enough to interpret fairly.

## Log of work on this step
- 2026-11-18: Built ordinary-versus-pressure player baselines. Eligibility requires 60 opportunities and six matches in each context; 176 batters and 219 bowlers qualify. Independent formula and eligibility checks reported zero errors.
