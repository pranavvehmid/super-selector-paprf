# PAPRF v3 cell-granularity experiment

## Protocol declared before calculation

The v2 audit left 46 batters and 44 bowlers eligible after resampling. This experiment asks how much of that loss came from splitting the same opportunities into small cells. The v3 research candidate merges innings within each phase and competition family. This preserves powerplay, middle and death roles and keeps IPL and T20I baselines distinct. The sensitivity alternative merges competition families while preserving innings and phase. Both retain v1 pressure labels, player attribution, the 12-ball gate per cell and context, the 60-ball and six-match overall gates, 500 family-stratified match resamples and ranking by p10 with at least 475 valid draws. The fine-cell v2 model is replayed as a control.

Merging innings can confound pressure with the different scores and available resources of setting and chasing a target. Merging competitions can confound pressure with tournament mix. The v3 label identifies the prespecified phase-and-family comparison. It carries no presumption of superior validity.

For temporal checks rerun the point ranking independently in the two 391-match windows from the earlier audit. Use 12 balls per cell and 30 balls and three matches per player and context in each window. Compute Spearman correlation on the common eligible players, using midranks for ties. Compare point ranks to point ranks across all granularity options. This check measures repeatability across the observed windows and does not evaluate prediction.

## Results

| Cell dimensions | Matched eligible B / W | Bootstrap eligible B / W | Shared with v2 B / W | Temporal ρ B / W |
|---|---:|---:|---:|---:|
| Fine v2 | 105 / 119 | 46 / 44 | 10 / 10 | +0.048 / −0.288 |
| Phase + family v3 | 144 / 156 | 81 / 79 | 4 / 3 | +0.059 / −0.026 |
| Innings + phase | 111 / 123 | 77 / 74 | 6 / 5 | +0.080 / −0.149 |

B and W denote batting and bowling. V3 admits 35 more players per role than v2. Its temporal correlations are computed on 76 common batters and 79 common bowlers. There were zero shared top-ten players across the two halves in either role under v3. These common pools differ across designs, so correlation differences cannot be interpreted as a controlled improvement for the same players. Broader coverage is an observed gain. Persistent top-ten membership remains unsupported by this test.

The v3 list is ordered by the same conditional p10 as v2. Shahbaz Ahmed leads batting with p10 = 1.360511 and 499/500 valid draws. His signed dismissal-rate component, 6.189138, dominates his point raw signal. It deserves attribution and component-weight sensitivity checks. Naseem Shah leads bowling with p10 = 0.548019 and 485/500 valid draws. His seventh-place point estimate moves to first under lower-tail ordering. The [full ledger](../../outputs/tables/paprf_v3_granularity_ledger.csv) records each player’s deltas, signed components, sample sizes and scores separately. The [movement JSON](../../work/paprf_v3_validation.json) gives the reason for every v2 top-ten departure in each design.

## Calculation and reproduction

For a coarser cell, sum the fine-cell numerators and denominators within each match and context before dividing. For example, the v3 pressure scoring rate for a death-over IPL cell is the sum of the player's attributed pressure runs from both innings divided by the sum of their pressure balls faced from both innings. Averaging two innings rates without their denominators would estimate a different quantity. The remaining steps use the [v2 bootstrap equations](paprf_v2_uncertainty.md). Players with under 95% valid draws receive no research rank. An observed score does not measure a causal effect of pressure.

Run `python scripts/build_paprf_v3.py`. The script first verifies exact agreement with both v2 top tens and their p10 scores on fine cells. It writes [batting](../../outputs/rankings/paprf_batters_v3.csv) and [bowling](../../outputs/rankings/paprf_bowlers_v3.csv) rankings and a [temporal ledger](../../outputs/tables/paprf_v3_temporal_ledger.csv). The [comparison figure](../../outputs/figures/paprf_v3_granularity.png) shows the gain in coverage and the limited repeatability side by side. The next methodological test should partially pool sparse fine cells while preserving innings, and audit dismissal-rate influence on batting ranks.
