# Lens A — "By the numbers" (statistical rating)

**Status:** PROPOSED FRAMEWORK, not final. Nothing here has been computed. Finalise in Step 8.

## Idea
Rate a player by how well they perform under pressure **relative to their own ordinary baseline and to context-matched peers**, protected against small samples, and demonstrably repeatable across matches.

## Proposed components (separately for batters and bowlers)
1. **Pressure level** — role-appropriate metric in elevated/high-pressure balls, context-adjusted (phase, innings, competition, batting position) versus the peer expectation for the same context.
   - Batters: runs per ball, boundary rate, dot-ball rate, dismissal rate.
   - Bowlers: runs per legal ball, dot-ball rate, boundary-concession rate, bowler-credited wicket rate.
2. **Change from own baseline** — pressure metric minus (or ratio to) the player's ordinary-situation metric, like-for-like on context.
3. **Repeatability** — consistency across distinct matches (e.g., share of pressure-matches at or above baseline; split-half or season-to-season correlation; match-level variance).
4. **Sample-size protection** — empirical-Bayes shrinkage: `m_shrunk = (n·m + k·μ_peer) / (n + k)` with `k` chosen from the data; minimum eligibility on pressure balls and distinct matches.
5. **Uncertainty** — match-clustered bootstrap confidence intervals for the pressure-vs-baseline difference and for the composite; optionally rank by a conservative lower bound.

## Composite
Standardise components (z-scores within role and eligibility pool), combine with documented weights; show alternatives (equal weights, rank-average, lower-bound ranking) and report sensitivity. Publish every component beside the score.

## Outputs
`outputs/rankings/lens_a_batters.csv`, `outputs/rankings/lens_a_bowlers.csv` (score, components, n balls, n matches, CI).

## Code
`src/rrselect/ranking_numbers.py`
