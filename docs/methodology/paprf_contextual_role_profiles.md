# Contextual T20 role profiles

## Protocol

This research iteration measures effectiveness relative to expected delivered outcomes. The historical PAPRF v4 pressure ranks remain a distinct comparison. All role and opponent estimates use the supplied organiser data.

Batting roles are based on the source batting slot and first pre-delivery phase seen as striker or non-striker in that innings. Slots 1–2 are openers, 3–4 top order and 5+ middle/lower order, except players in slots 5+ first seen in the death phase, who are classified as late entrants. This is an observed deployment proxy, not a permanent finisher designation. Bowlers are evaluated separately in each phase. A player can qualify in multiple roles. Batting uses balls faced and bowling uses legal balls. Bowling model runs use legal-ball concessions. Wides and no-ball concessions remain in the conventional economy column, assigned to the same phase, and are outside the legal-ball residual model. A boundary must have the matching four or six flag and attributed runs. A batting dismissal must occur on a counted striker ball.

### Earlier-date baseline and opposition adjustment

Process whole match dates in order. Freeze all rates until the date's rows are scored, then update the rates. Keep the first 195 matches before 3 April 2023 as warm-up. For each role, define the observation vector Y = (runs, boundary indicator, dot indicator, dismissal or credited wicket indicator, six indicator). Coaching and recruitment interpretations are outside these metrics.

The context key includes innings, phase, competition family, batting deployment or bowling phase, India venue indicator, pressure band, and observed opposing style (pace/spin or batting hand). Let a historical group have outcome sum S and n opportunities. Calculate its mean as (S + k × parent mean)/(n + k). The hierarchy moves from discipline mean to deployment/phase/family parent with k = 120 and then to the full cell with k = 120. Before any role history exists, use fixed priors of 1 run, 0.15 boundaries, 0.35 dots, 0.04 dismissals or wickets and 0.05 sixes per opportunity. Priors are initialisation assumptions.

Compute earlier-date residuals as actual minus the unadjusted context expectation. Estimate a team residual mean with denominator n + 360 and an individual opponent residual mean with denominator n + 120. Use 25% team and 75% individual in the adjustment, independently on each outcome. Clip runs to [0, 6] for batting or [0, 8] for legal bowling and indicators to [0, 1]. The opponent is the delivering bowler for batting, and current striker for bowling. This is a historical proxy and does not separate individual skill, other opponents and scheduling effects. Quality tiers use the prior individual contextual run residual, oriented so harder opposition is positive. A tier requires 120 prior opportunities, with strong at +0.10 or above, weaker at −0.10 or below, average between, and unknown otherwise. Report an out-of-date prediction MSE comparison against the unadjusted model. Competition family adjustment controls observed baseline differences and is not a causal tournament-quality ranking.

### Scores and dimensions

Aggregate residuals per opportunity. In each eligible role pool, z-standardise runs, boundary and event residual rates using sample standard deviations. Orient scoring and boundaries up and dismissal risk down for batters, and orient run and boundary prevention up and credited wickets up for bowlers. Clip signed z-scores at ±3. Eligibility requires 60 scored balls and six scored matches. Multiply the weighted composite by n/(n+120), with n the unweighted role opportunity count. The primary score weights all locations equally. Stress-test India at 1.5× event weight, and compare the prespecified role weights with equal weights. No arbitrary age bonus is applied.

| Role | Runs or prevention | Boundaries or prevention | Dismissals or wickets |
|---|---:|---:|---:|
| Opener | 0.45 | 0.30 | 0.25 |
| Top order | 0.40 | 0.20 | 0.40 |
| Middle/lower order | 0.40 | 0.25 | 0.35 |
| Late entrant | 0.50 | 0.35 | 0.15 |
| Powerplay bowler | 0.35 | 0.20 | 0.45 |
| Middle bowler | 0.35 | 0.20 | 0.45 |
| Death bowler | 0.50 | 0.25 | 0.25 |

The batting Explosiveness Index is [0.60 z(runs) + 0.40 z(boundaries)] × n/(n+120). Sixes and dots remain available as diagnostics. Inspect rank correlation between scored components for redundancy. The role-conditioned pressure comparison is the difference between pressure and ordinary contextual residual means for each metric. Report a pressure difference only with at least 30 opportunities in both buckets. This overlay improves comparability without introducing a newly calibrated pressure label.

Annual and split tables contain raw opportunity counts, strike rate or economy, boundary and event rates, and mean contextual residuals. Publish the annual raw series for 2022–2026 when observations exist. Trend regression requires at least three years with 60 scored balls each. Let t be year, y annual run residual and n scored balls. The weighted slope is Σ n(t−t̄)(y−ȳ) / Σ n(t−t̄)², with ball-weighted means. The recency contrast uses weights n × 2⁻⁽²⁰²⁶⁻ᵗ⁾⁄². Negative raw conceded-run slopes favour bowlers. No age, origin, home advantage, physical pitch trait, ground dimensions or future potential is inferred from location or career appearance dates. Venue country measures India exposure. A schedule-side label is not a player's home ground.

### Follow-up redundancy test

The first run showed strong scoring–boundary correlation. Keep the original primary score as the declared reference. For the follow-up sensitivity case, let x be the role pool's run residual and y its boundary residual. Replace y with y − β(x − mean(x)), where β = Σ (x − mean(x))(y − mean(y)) / Σ (x − mean(x))². Re-standardise the transformed boundary component and keep the original weights. This strips linear dependence in the fitted role cohort. It does not make the components independent or establish predictive superiority.

## Results

The source audit found consistent batting positions across 12,630 observed player-innings. On batting opportunities, the four flag disagrees with a four-run attribution on 19 rows and the six flag disagrees with a six-run attribution on three. Requiring both signals prevents unverified boundary attributions. These are discrepancy counts across flag fields.

| Discipline | Scored balls | Context run MSE | Opposition-adjusted run MSE | Relative reduction | Unknown opposition tier |
|---|---:|---:|---:|---:|---:|
| Batting | 134,060 | 3.083991 | 3.079331 | 0.151% | 26,269 / 134,060 |
| Bowling | 133,652 | 3.102292 | 3.076754 | 0.823% | 27,811 / 133,652 |

Relative reduction is 100 × (1 − adjusted MSE / context MSE). These are per-ball chronological errors from one historical sequence, with no independent interval or external test. Batting dismissal MSE worsened slightly from 0.051624 to 0.051647. The run improvement is modest and does not establish that the profile ranking will predict future player performance.

| Role | Eligible | Historical leader | India stress overlap | Equal-weight overlap | Boundary residualisation overlap |
|---|---:|---|---:|---:|---:|
| Opener | 78 | Vaibhav Sooryavanshi | 10/10 | 10/10 | 8/10 |
| Top order | 107 | Harry Brook | 8/10 | 8/10 | 8/10 |
| Middle/lower order | 123 | Tim David | 10/10 | 9/10 | 8/10 |
| Late entrant | 45 | Mahendra Singh Dhoni | 9/10 | 10/10 | 9/10 |
| Powerplay bowling | 172 | Kyle Klein | 10/10 | 9/10 | 7/10 |
| Middle bowling | 221 | Mohammad Nawaz | 8/10 | 7/10 | 8/10 |
| Death bowling | 138 | Jasprit Bumrah | 9/10 | 9/10 | 8/10 |

Run–boundary residual correlations range from roughly +0.89 to +0.94. Residualising changes one to three top-ten memberships per role. Compare the runs-only or residualised-boundary formulation on a subsequent validation sample before relying on the composite as an independent measure of explosiveness. The role leaderboards share four v4 batting and three v4 bowling top-ten names across their respective role lists. They estimate overall contextual effectiveness rather than pressure lift alone.

The trend ledger has 173 qualifying player-role records, 97 with three scored years and 76 with four. Raw annual splits may cover 2022–2026, while chronology-adjusted values begin on 3 April 2023. Partial calendar years should not be treated as equivalent to complete seasons. A change in residuals can reflect changing roles, schedules or opposition alongside player performance.

## Evidence map and remaining work

| Dimension | Current evidence and unresolved scope |
|---|---|
| Opposition | Earlier-date individual and team residuals, prior-support tiers, style splits and chronologically scored errors. A tournament-strength hierarchy and opponent adjustment by specific phase need separate validation. |
| Sample size and quality | Role scores are shrunk, with balls, matches and innings recorded. Whole-match uncertainty for these new role scores remains open. |
| Explosiveness and roles | Seven role-specific leaderboards, boundary and six frequencies, dots and scoring rate. Immediate scoring after entry, chase completion and strike rotation sequences remain untested. |
| Time and age | Annual rates, weighted slopes and recency contrast. Age curves need date-of-birth data linked and verified by player ID. Career potential remains unestimated. |
| Pressure | Residual pressure-minus-ordinary splits per role, with minimum support reported. Calibrated role-specific exposure, win probability and match importance remain open. |
| Geography | India versus outside India and 1.5× weighting sensitivity. That sensitivity does not validate an optimal India preference. Home advantage, pitch characteristics and ground size need separate sources. |
| Audit | Earlier-date forecast error and overlap across weights, geography and boundary treatment. Player-level future forecast accuracy and stability remain untested for this role model. |

Run `python scripts/build_paprf_role_profiles.py`. See the [seven ordered top tens](../../outputs/rankings/paprf_contextual_role_top10_v1.csv), [player and scenario scores](../../outputs/tables/paprf_role_profile_scores.csv), [annual, phase, pressure, style and geography splits](../../outputs/tables/paprf_role_profile_splits.csv), [trend ledger](../../outputs/tables/paprf_role_profile_trends.csv), [audit JSON](../../work/paprf_contextual_roles.json), [correlation heatmaps](../../outputs/figures/paprf_role_component_heatmaps.png) and [illustrative annual trajectories](../../outputs/figures/paprf_role_annual_examples.png).

The [follow-up validation](paprf_role_profile_validation.md) adds whole-match score uncertainty and two later-window comparisons on common eligible players.
