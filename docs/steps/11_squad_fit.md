# Step 11 — Add squad-context overlay (Lens C)

**Status:** BLOCKED — source inputs not supplied
**Code:** `src/rrselect/squadfit.py`

## Goal
Explain why data-derived picks could be useful to RR without distorting the statistical ranking.

## Tasks
- [ ] Load user-supplied/verified external data: IPL 2027 retention list, auction pool, current RR squad, RR historical picks, player hometown/heritage (data/external/).
- [ ] Flag each ranked player: retained elsewhere / in auction pool / already at RR / availability unknown.
- [ ] Assess RR squad composition and gaps by role (openers, middle order, finishers, pace, spin, death overs, overseas slots).
- [ ] Summarise RR's historical pick patterns (age, role, domestic team, hometown/region, price band) strictly from supplied data.
- [ ] Produce a recommendation shortlist with a stated, auditable rule for how fit is combined with pressure scores (never changing the underlying scores).
- [ ] Do not infer availability, price or likelihood of purchase without evidence.

## Output of this step
Squad-fit notes and shortlist per lens (outputs/rankings/ and docs/factors/).

## Decision gate
Statistical scores untouched; all external facts sourced and dated.

## Log of work on this step
- 2026-11-18: Kept deliberately separate from Lens A. The repository has no dated, source-backed current RR squad, retention, auction-pool, price, or availability dataset. No such facts have been inferred. The report documents the exact outstanding inputs and labels this workstream incomplete.
