# PAPRF forward validation

## Protocol

The full-sample v4 ranking estimates historical pressure lift. This audit tests whether earlier scores predict later pressure lift. Sort matches by date and ID. Take the dates at indices floor(N/4), floor(N/2) and floor(3N/4) as cutoffs. Keep every match on a cutoff date on the later side. The three test windows are disjoint and the training window expands. No match contributes to both training and testing in one fold. These are retrospective forward tests of a model already developed using the supplied dataset. They do not constitute an untouched external validation.

Compute four training-only predictors in each fold:

| Predictor | Calculation |
|---|---|
| v4 p10 | v4 with its original eligibility gates, training-only peer scales and 500 family-stratified training match resamples. |
| v4 point | The same matched model before bootstrap quantile ranking. |
| Pooled point | Same attribution, component directions, clipping and score shrinkage. Pool contexts per player before differencing and omit cell regularisation. |
| Pressure volume | Training pressure balls in the v4-supported cells. |

The test target uses v4 regularised cell differences and the frozen training peer means and standard deviations. It averages the three signed capped z-scores without multiplying by test sample-size shrinkage. Test eligibility requires at least 30 balls and three opportunity-bearing matches in each bucket across supported test cells. This target describes the same measured construct as v4 and can favour a matched predictor. The secondary target uses only signed scoring-rate or economy lift. Evaluate all predictors on the intersection of their available predictions and test eligibility. To keep missing evidence visible, also count how many of each predictor's original training top ten satisfy the test eligibility gate. Never treat lack of test evidence as a zero score.

Report Spearman rank correlation (Pearson correlation of midranks), overlap with the test top ten and the original training top ten's assessable count. Top-ten overlap filters predictions to the common pool before comparing. No tuning uses test-window results, and folds can share training observations. Report all folds separately. Do not interpret repeated player rows as independent trials.

## Results

| Fold | Last training date | Test dates | Train matches | Test matches |
|---|---|---|---:|---:|
| 1 | 2023-04-02 | 2023-04-03 through 2024-05-07 | 195 | 196 |
| 2 | 2024-05-07 | 2024-05-08 through 2025-09-05 | 391 | 195 |
| 3 | 2025-09-05 | 2025-09-06 through 2026-11-01 | 586 | 196 |

| Fold / role | Common N | v4 p10 ρ | v4 point ρ | Pooled point ρ | Pressure volume ρ |
|---|---:|---:|---:|---:|---:|
| 1 batters | 21 | −0.117 | −0.214 | +0.161 | +0.234 |
| 1 bowlers | 25 | −0.094 | −0.115 | +0.030 | −0.263 |
| 2 batters | 37 | +0.050 | +0.038 | +0.052 | −0.165 |
| 2 bowlers | 47 | −0.286 | −0.217 | −0.084 | −0.106 |
| 3 batters | 47 | −0.106 | −0.032 | −0.183 | −0.245 |
| 3 bowlers | 49 | +0.119 | +0.144 | +0.199 | −0.029 |

The v4 p10 score beats the pooled point correlation in one of six role-window comparisons. It has negative correlation in four. Under the secondary rate-only target, v4 p10 correlations range from −0.222 to +0.138. The pooled point score and pressure volume also change sign across windows. This sample gives no clear basis for claiming a consistently superior predictor.

For a common pool of N players, two independent uniformly sampled top tens have expected overlap 100/N. Each of the ten names from the first list has inclusion probability 10/N in the second. This is a descriptive reference, with no significance claim.

| Fold / role | v4 p10 common-pool overlap | Random reference 100/N | Original v4 p10 top ten assessable |
|---|---:|---:|---:|
| 1 batters | 4/10 | 4.76 | 9/10 |
| 1 bowlers | 4/10 | 4.00 | 7/10 |
| 2 batters | 3/10 | 2.70 | 7/10 |
| 2 bowlers | 0/10 | 2.13 | 5/10 |
| 3 batters | 1/10 | 2.13 | 2/10 |
| 3 bowlers | 2/10 | 2.04 | 4/10 |

The common-pool calculation asks how the model orders players with enough evidence on both sides. Original top-ten coverage answers a separate operational question. The final batting window has 47 common players, yet eight of the original training leaders lack adequate test-side opportunities. This attrition prevents generalising the common-pool results to every selected player. Short windows also make realised pressure estimates noisy. Earlier development used the entire dataset, so the retrospective dates test the ordering protocol and do not provide an untouched competition holdout.

## Reproduction and decision

Run `python scripts/validate_paprf_forward.py` from the repository root. The [validation JSON](../../work/paprf_forward_validation.json) records cutoffs, sample sizes, training means and standard deviations, predictor coverage, IDs and correlation for both targets. The [player ledger](../../outputs/tables/paprf_forward_validation_ledger.csv) lists every prediction and test observation with denominators and common-pool flag. The [comparison figure](../../outputs/figures/paprf_forward_validation.png) displays the six common-pool correlations per predictor.

The forward results do not justify switching historical rankings to any competing predictor. Retain the existing historical ordering and report forecast performance as unresolved. A useful next test is to compare historical lift with a null model that preserves match clustering and phase, then estimate how much repeatable signal is detectable under observed player exposure.
