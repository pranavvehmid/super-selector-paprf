# Unified player index v1

The index answers which players exceeded the expectations of their usual T20 deployment by the largest supported margin in the supplied sample. It integrates the seven [contextual role leaderboards](paprf_contextual_role_profiles.md). The archived submission and the pressure-only research ranks answer a different question.

## Ranking directory

| Leaderboard | Purpose and algorithm | Relationship and main limitation |
|---|---|---|
| Lens A v1 | Archived Round 1 batting and bowling top tens. Three equally weighted signed z-scores of pressure versus ordinary rates, multiplied by n/(n+60). [Formula ledger](lens_a_formula_ledger.md). | Historical pressure baseline. Pooled context can mix roles and competitions. |
| Pressure research v2–v4 | Match within contexts and rank by the tenth percentile of 500 match resamples. [v2](paprf_v2_uncertainty.md), [v3](paprf_v3_cell_granularity.md), [v4](paprf_v4_reanalysis.md). | Diagnostics for pressure lift, independent of the unified index. Rankings show weak temporal stability. |
| Contextual role profiles | Seven distinct deployments. Earlier-date expected outcomes give opposition and context adjustments. Role weights combine scoring, boundaries and dismissals or wickets. [Weights and definitions](paprf_contextual_role_profiles.md). | The unified index uses their component values. Run and boundary residuals have substantial overlap. |
| Unified player index | Common role-relative scale, opportunity-based role assignment and capped secondary credit. Equations below. | Relative demonstrated effectiveness. It is not a forecast, auction shortlist or replacement for the official pressure submission. |
| Experimental leaderboards | Equal weights, extra India weighting, residualised boundaries and alternative versatility. | Diagnostics show how assumptions affect rankings. No experimental setting was selected based on preferred names. |

## Equations

**(1) Role assignment.** Among a player's observed deployments, primary role is the one with most scored opportunities. If no opportunities fall after warm-up, use observed raw opportunities. Ties use scored match count, then the unshrunk role signal if available, then role ID. A primary needs at least 60 scored balls and six scored matches to receive an index. Players who do not qualify are recorded with a reason. More opportunities determine deployment and sample support, not raw run or wicket superiority.

**(2) Within-role scaling.** For each eligible player and role, recover the unshrunk contextual signal c = Σ wⱼzⱼ from the signed capped components and the published role weights. Compute μ and sample standard deviation σ over all eligible players in that role. Define Q = 100Φ[(c−μ)/σ], where Φ is the standard normal cumulative distribution function. A flat cohort uses Q = 50. Q is a smooth reference score in (0, 100), with 50 at the role mean. It is not the percentage of actual peers defeated and not a probability of future success. Unlike averaging rank positions, the transformation retains differences in component magnitudes. Normal reference scaling reduces units and scale incompatibilities, though skew and unequal role strength can still matter.

**(3) Evidence shrinkage.** Define R = n/(n+120) and S = 50 + R(Q−50). This uses the existing role prior and shrinks toward neutral exactly once. Applying reliability to the already shrunken published role score would count sample size twice. At n = 120, R = 0.5. With Q = 90, S = 70. S ranges from 0 to 100 and is a historical role-relative index.

**(4) Overall index.** Select at most one supported secondary role with the largest credit, where credit = 0.10 × min(1, nₛ/nₚ) × max(0, Sₛ−50). Here p and s identify primary and secondary roles. Other roles remain visible without accumulating credits. The index I = min(100, Sₚ + credit). For Sₚ = 70, Sₛ = 80 and nₛ/nₚ = 0.5, credit is 1.5 and I = 71.5. The bonus is at most 5 points before clipping. Rank by score at six decimal places and break ties by numeric player ID.

Opposition quality and pressure context are already included in the expected-outcome benchmark. Pressure lift, India support, annual/recency contrast and historical bootstrap membership are shown as evidence. They receive no separate automatic bonus. That avoids rewarding the same balls twice or assigning an unvalidated India or recency multiplier. The prior forward tests do not establish stable player ordering in every role. Consistency and forecast interpretation remain limitations. Age and pitch characteristics require further verified data.

## Sensitivity and reproducibility

Compare the primary index with three alternatives: no secondary credit, a 1.5× India source scenario, and a boundary-residualised source scenario. Role assignment and sample requirements are held fixed. The latter two recalculate role reference centres and scales. These are historical sensitivity tests rather than independent predictive validation. Run `python scripts/build_paprf_unified_ranking.py`. The evidence bundle records source hashes, role peer scales, every eligible component, all observed role assignments, and overlaps between alternatives.

## Results and worked trace

The index ranks 397 of 881 observed player IDs. The 484 unranked records record the primary evidence gate and stay searchable. Five of the top ten are openers, compared with 64 of the 397 eligible primary assignments. This concentration should be reviewed alongside differences in role opportunity counts, pool sizes, and tail shapes. No role quota is applied. The shared scale compares within-role evidence and does not guarantee equivalent difficulty or equal representation across roles.

Abhishek Sharma (ID 6281) has 1,753 opener balls across 102 scored matches, 78.4% of his scored opportunities. His capped signed components are approximately +2.506577 for runs, +2.241210 for boundaries and −0.105743 for dismissals. Applying 45%, 30% and 25% gives c = 1.773887. Against the opener mean −0.004546 and sample SD 0.716492, the reference z is 2.482139 and Q = 99.347018. Retention 1,753/1,873 = 0.935932 gives S = 96.185437. His supported secondary middle-bowling score is 26.603370, so it adds zero. His final index is 96.185437.

The primary-only and India-weighted alternatives each retain 10 of the 10 primary names. Residualising boundaries retains 9 of 10, with Yashasvi Jaiswal entering and Harry Brook leaving. The maximum absolute rank movements across the full cohort are 16, 71 and 179 places, respectively. Stable top-ten membership can coexist with substantial shifts elsewhere. The new index has no predecessor with the same criterion. Historical role or pressure ranks remain available as comparisons, while bootstrapped top-ten shares correspond to the source role profiles. They are not unified rank confidence intervals.

- [Unified top ten](../../outputs/rankings/paprf_unified_top10_v1.csv)
- [All player assignments](../../outputs/tables/paprf_unified_assignments.csv)
- [Four scenario score ledgers](../../outputs/tables/paprf_unified_score_ledger.csv)
- [Player-level components and input hashes](../../work/paprf_unified_ranking.json)

Next validation should test whether different roles have comparable score calibration in future windows. It should also recompute unified ranks inside a shared whole-match resample rather than transplanting source-role inclusion probabilities.
