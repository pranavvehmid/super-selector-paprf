# PAPRF v4 reanalysis protocol

## Four research passes

1. Audit scoring attribution. Count all observed dismissal flags and separate striker events on a counted ball from non-striker events, events without a counted ball and events lacking an ID.
2. Fit a regularised fine-cell model to the same pre-delivery pressure indicators. Compare outcomes within innings, phase and competition family. Use the historical 60-ball and six-match thresholds in both contexts, summed across overlapping cells.
3. Recalculate under different regularisation and outcome assumptions and repeat the chronological test.
4. Rebuild attribution from the organiser CSVs in a clean temporary directory, then recompute v4 and compare the resulting rankings and calculation ledgers byte for byte.

## Prespecified model

Batting dismissal risk is the number of recorded striker dismissals on counted balls faced divided by those balls. This aligns the at-risk unit with the numerator. A non-striker dismissal still affects subsequent match state. Bowling retains credited wickets per legal ball and conceded runs per six legal balls, including attributed illegal-delivery runs. No outcome enters the pressure label for its own delivery.

Let a and b be ordinary and pressure opportunities in a player's cell. Require a > 0 and b > 0. With raw cell rate difference d, estimate the cell lift by minimising

    (a b / (a + b)) × (theta − d)^2 + lambda × theta^2.

Differentiation gives theta = d × a b / [a b + lambda × (a + b)]. Thus small cells contribute an attenuated change. This is a zero-lift regulariser. It does not assume that an unobserved ordinary rate equals the player's observed pressure rate. Aggregate theta across supported cells with pressure-ball weights b. Use lambda = 12 for the primary model and test 6 and 24. Use observed role-peer mean and sample standard deviation for each aggregate component. Cap each signed z-score at ±3, give the three metrics equal weights and multiply the average by n/(n+60). This caps influence without deleting outlying observations. Test uncapped scores, historical dismissal attribution for batters and a two-component model that drops dismissal or wicket rate.

For the primary score, draw 500 whole-match samples within IPL and T20I with seed 20261118. Keep the observed qualifying cell set and peer scaling. A cell contributes in a resample only when both denominators are positive, and the pressure-ball denominator and shrinkage reflect the contributing cells in that draw. A draw with no overlapping opportunities is invalid. Require at least 475 valid draws. Rank by the 10th percentile using linear interpolation, six-decimal rounding and player ID as tie-break. Report the median, 90th percentile and conditional range. This conditional bootstrap does not reselect the model or estimate future performance.

Sensitivity scenarios compare point top tens with the primary point top ten. The temporal check splits at the existing 391-match boundary, uses 30 balls and three matches per context, fits role-peer scaling independently in each window and reports Spearman correlation on common eligible players.

## Results and interpretation

The 10,024 flagged dismissal events reconcile to 9,738 striker events on counted balls, 250 non-striker events, 35 striker events on uncounted balls and one event without an ID. This corrects the interim non-striker subtotal. See the band-by-band attribution counts in the validation JSON. Returning to historical player attribution preserves the batting point top-ten membership in this experiment. Removing the event metric changes five batting and two bowling positions by membership, making event weighting more consequential here than the attribution correction.

| Diagnostic | Batters | Bowlers |
|---|---:|---:|
| v4 point eligible | 149 | 156 |
| v4 bootstrap eligible | 149 | 156 |
| Shared with v1 top ten | 2/10 | 2/10 |
| Shared with v2 research top ten | 4/10 | 2/10 |
| Shared with v3 research top ten | 6/10 | 2/10 |
| Lambda 6, shared with primary point top ten | 8/10 | 8/10 |
| Lambda 24, shared with primary point top ten | 7/10 | 8/10 |
| Uncapped z, shared with primary point top ten | 10/10 | 10/10 |
| No event metric, shared with primary point top ten | 5/10 | 8/10 |
| Early / late point eligible | 124 / 133 | 137 / 143 |
| Common early and late eligible | 70 | 81 |
| Temporal Spearman | +0.154 | +0.002 |
| Shared across the early and late point top tens | 1/10 | 0/10 |

The broader pool is associated with two changes. Ridge attenuation replaces a hard 12-ball cell cutoff. In a resample, cells missing either context are omitted instead of invalidating the whole draw. Because a different subset of cells can contribute across draws, the v4 distribution answers a different support-conditioned question from v2 or v3. Low temporal agreement remains the strongest reason to qualify claims about historical rank order. The bootstrap guards against variation under resampling and cannot remove time drift or establish predictive reliability.

## Worked example

Reeza Hendricks (ID 768) had 17 runs from six ordinary balls and one run from four pressure balls in the first-innings T20I death cell. The unregularised lift is 1/4 − 17/6 = −2.583333 runs per ball. The regularisation factor is 6×4 / [6×4 + 12×(6+4)] = 1/6, hence the adjusted cell lift is −0.430556. It receives 4/269 of the full pressure weight. Combining all three supported cells yields a regularised scoring delta of +0.340801. His signed capped z-scores are 1.730557, 3, and 2.087024. Their average, about 2.272527, is multiplied by 269/329 to give a point score of 1.858084. His bootstrap p10 of 0.929171 ranks first in batting. Kyle Jamieson ranks first in bowling with p10 = 0.723396.

## Reproduction and review files

Run `python scripts/build_paprf_v4.py` for the attribution audit, model and stress tests. Run `python scripts/verify_paprf_rebuild.py` for the clean rebuild and scalar check. The clean replay starts with only the six organiser CSVs and source code in a temporary directory. It reconstructs match state, labels, player attribution and each ranking version in order. The separate scalar calculation recomputes every v4 point score from the cell numerators and independently orders the published p10 scores.

- [v4 batters](../../outputs/rankings/paprf_batters_v4.csv) and [v4 bowlers](../../outputs/rankings/paprf_bowlers_v4.csv) give the ordered research lists and their bootstrap quantiles.
- [Cell evidence](../../outputs/tables/paprf_v4_cells.csv) gives the numerators and denominators for every included player cell.
- [Player score ledger](../../outputs/tables/paprf_v4_rank_ledger.csv), [threshold and component tests](../../outputs/tables/paprf_v4_sensitivity.csv) and [temporal scores](../../outputs/tables/paprf_v4_temporal.csv) give the individual calculations.
- [v1–v4 progression](../../outputs/tables/paprf_v4_progression.csv) puts successive top-ten ranks side by side. Blank ranks indicate absence from that version’s top ten.
- [Sensitivity heatmap](../../outputs/figures/paprf_v4_sensitivity.png) compares point top-ten membership across tests. [Validation JSON](../../work/paprf_v4_validation.json) and [clean rebuild hashes](../../work/paprf_clean_rebuild.json) preserve the audit trail.

The [forward-validation audit](paprf_forward_validation.md) evaluates later periods with fixed pre-period peer scaling. It found weak and inconsistent predictive ordering. Wicket and dismissal weighting remains an open research question. The current rankings are the output of the declared historical estimand.
