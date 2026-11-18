# Contextual role profile validation

## Design recorded before evaluation

This pass tests the role leaderboards released in commit 173d13c. It checks uncertainty in the historical ranking and tests whether the ranked differences recur in later player samples. No result is used to tune the original ranking.

Recreate per-match player-role sums of the three scored contextual residuals: runs, boundaries and dismissals or wickets. Context and opponent expectations for each date use only preceding dates, as in the original profile. Forward-score training uses the 3 April 2023 warm-up cutoff and ends before each test window. Test windows are 8 May 2024 to 5 September 2025, and 6 September 2025 to the end of the supplied data. Within these windows, the contextual baseline may update after an observed match date. Fitted ranking parameters stay fixed.

Compare four training predictors on the common eligible test players: the original role score, the original score with the boundary residual orthogonalised to runs, direction-corrected runs-only and opportunity volume. Fit peer means, sample standard deviations and the boundary-on-runs slope on eligible training players only. Training requires 60 balls and six matches in the role. Test outcomes require 60 scored balls and six matches in the same role. The realised test target uses runs and events only, with the configured boundary weight allocated to runs, so boundary duplication does not define success. Standardise the target using training means and scales, orient signs and cap z-scores at ±3. Test ranks omit the ball-count shrinkage penalty. Score comparisons use Spearman correlation and, where the common pool exceeds ten, top-ten overlap. Count original training leaders who are test eligible separately. Report a signed run-residual target as a secondary correlation.

For historical uncertainty, draw 500 whole-match samples with replacement within IPL and T20I, with seed 20261118 and a shared set of match multiplicities for every player. Keep the original eligible player pool and peer scales fixed. Recalculate each player's mean residuals and n/(n+120) factor from the resample. Rank each draw at six decimal places with numeric player ID as tie-break. Record p10, median, p90 and the fraction of draws in the top ten. These are conditional results given earlier-date residuals, fitted scales and observed eligibility. They do not propagate uncertainty from fitting opponent baselines or establish future performance.

## Results

| Role | Common players, earlier / later window | Primary rho, earlier / later | Runs-only rho, earlier / later | Historical leader in resampled top ten |
|---|---:|---:|---:|---:|
| Opener | 22 / 39 | +0.582 / +0.396 | +0.509 / +0.452 | 499/500 |
| Top order | 27 / 30 | +0.380 / +0.192 | +0.366 / +0.250 | 467/500 |
| Middle/lower order | 25 / 33 | +0.352 / −0.228 | +0.394 / −0.267 | 426/500 |
| Late entrant | 1 / 0 | Unavailable | Unavailable | 476/500 |
| Powerplay bowling | 44 / 52 | +0.317 / −0.048 | +0.163 / −0.005 | 309/500 |
| Middle bowling | 56 / 69 | +0.346 / +0.217 | +0.463 / +0.264 | 289/500 |
| Death bowling | 35 / 34 | +0.301 / −0.185 | +0.245 / −0.121 | 479/500 |

The opener profile showed the strongest consistent primary association. Top order and middle bowling were also positive in both windows. Middle bowling's runs-only predictor beat the composite in both windows. Middle/lower batting, powerplay bowling and death bowling reversed sign. Late-entrant coverage is too sparse to quantify rank association, despite high retention of the historical leader in resampling. Among the two opener windows, six and eight members of the original training top ten had enough later evidence. The forward analyses apply to those with common eligibility.

The residualised-boundary predictor beat the primary predictor in three of the twelve assessable role-window comparisons. Runs-only beat it in seven of twelve. Those counts are descriptive. Test windows are disjoint in match IDs but can include the same players, and predictions share expanding training history. The target also puts no direct weight on boundaries. These results support testing simpler scores on a future sample. They do not establish that replacing the current scoring weights will improve future rankings.

Leader stability varies separately from list stability. For example, 479/500 resamples include Jasprit Bumrah in the death-bowling top ten, yet six of the ten published death bowlers appear in fewer than half the draws. In powerplay bowling, eight of the historical ten have a resampling share below 50%. Resampling shares describe the historical sample and should not be interpreted as selection probabilities for future matches.

## Reproduction

Run `python scripts/validate_paprf_role_profiles.py`. The script rebuilds player-match residuals, checks the full-sample peer scales and eligible counts, and reproduces all 70 original top-ten scores and positions before writing validation evidence.

- [Audit JSON](../../work/paprf_role_profile_validation.json) includes training peer scales, test cohorts, target correlations, top-ten reproducibility and bootstrap intervals.
- [Forward player ledger](../../outputs/tables/paprf_role_forward_player_ledger.csv) provides the train predictions, realised outcomes and evaluation membership.
- [Bootstrap ledger](../../outputs/tables/paprf_role_bootstrap_ledger.csv) provides the score intervals and top-ten shares for every eligible profile.
- [Benchmark figure](../../outputs/figures/paprf_role_forward_validation.png) compares the four training predictors across roles and windows. No plotted marker for late entry means there was insufficient evidence to estimate a correlation.

The historical role top tens remain the reference. The next priority is a whole-match validation of the run-only alternative for middle bowling and a separate check of how pool depth changes with playing time in late-entry batting.
