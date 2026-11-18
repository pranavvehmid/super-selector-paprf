# Step 01 — Lock the challenge scope and submission rules

**Status:** GATE PASSED
**Code:** `src/rrselect/config.py`

## Goal
Translate the official challenge into a precise analysis target before touching player rankings.

## Tasks
- [x] Fix the required outputs: top-10 batters, top-10 bowlers, reproducible methodology report.
- [x] Keep batting and bowling as separate ranking problems.
- [x] Record that pressure must be compared with each player's usual performance and must work for batting and bowling.
- [x] Decide competition scope: IPL + T20I primary; the two additional T20 competitions are sensitivity-only (D-001).
- [x] Record PLS as a deferred working interpretation and set Lens A as the planned Unstop method (D-002, D-003).
- [x] Record the currently known Unstop requirement: rankings and methodology report must match exactly.

## Output of this step
One-page scope specification: deliverables, included/excluded competitions, open definitions.

## Decision gate
**Passed on 2026-11-18.** The primary population, required outputs, active ranking method, and separation from contextual recommendations are explicit. Proceed to Step 2; do not begin player scoring until the later state, pressure, metric, baseline, reliability, and validation gates pass.

## Log of work on this step
- 2026-11-18: The user fixed the project structure as exactly three workstreams: primary data-led top-10 shortlist, current RR squad-building needs, and RR-specific player fit. The primary shortlist remains separate from contextual recommendations. D-001, D-002, and D-003 remain open.
- 2026-11-18: D-001 resolved as IPL and T20I primary with the two additional T20 competitions reserved for a labelled sensitivity check. D-003 resolved as Lens A for the planned Unstop lists. D-002 is deferred; no PLS model is active.
