# PAPRF v2 research ranking and uncertainty

## Design recorded before running the comparison

The matched-context audit exposed two problems with pooled v1 rank interpretation. Scoring rates vary with phase and competition mix, and rank repeatability across the chronological halves was weak. The v2 research iteration therefore uses the matched point estimate and ranks the lower tail of its match-resampling distribution. The main estimand is pressure lift within a player's observed innings, phase and competition family. The organiser submission version remains recorded as v1 for traceability. The project's evolving research ranking is v2.

Use the 12-ball-per-context cell cutoff from the previous audit as the primary design. Check matched point rankings at 6 and 24 balls per context, while retaining the player-level gate of 60 balls and six opportunity-bearing matches per bucket. Use exactly 500 bootstrap replicates and seed 20261118. Within each competition family, draw the original number of distinct matches with replacement. A match's multiplicity applies to all players and deliveries from that match and a replicate uses the same draw for both roles. Preserve the observed eligible player pool, retained cells and peer standardisation parameters. Recompute rates, pressure-cell weights and shrinkage for each draw. A draw is invalid for a player if any retained cell loses either opportunity denominator. Require at least 95% valid draws for the v2 ranking.

The research score is the empirical 10th percentile of a player's valid bootstrap scores. Also publish the median and 90th percentile. Quantiles are computed by linear interpolation and scores are rounded to six decimals for ranking, with smaller numeric player ID breaking ties. This conservative score accounts for match-to-match variability in the observed sample. The percentile range is conditional on observed cell support and peer scaling. It is neither a rank confidence interval nor evidence of out-of-sample predictive accuracy.

## Calculation details

For each player, cell, metric and context, the observed match contributes a numerator x and a ball denominator n. In draw b, let wᵦₘ be the number of times match m is selected. Each resampled rate is Σₘ wᵦₘxₘ / Σₘ wᵦₘnₘ. Bowling economy multiplies that ratio by six. Subtract ordinary from pressure in each cell. Average those differences across retained cells weighted by their resampled pressure-ball counts. Convert each difference to a signed z-score using the observed matched cohort's mean and sample standard deviation, average the three z-scores, then apply nᵦ/(nᵦ+60), where nᵦ is the draw's pressure-ball total. For M valid sorted scores, quantile q is linearly interpolated at the zero-indexed position (M − 1)q.

For example, batting leader Reeza Hendricks (ID 768) had 265 matched pressure balls and 140 ordinary balls, with a matched point score of 1.815560. There were 491 valid draws out of 500, or 98.2%. The 10th percentile therefore uses zero-indexed position 49, giving 1.061415. The 90th percentile is 3.449639. The coverage gate requires at least 475 valid draws. Bowling leader Sufiyan Muqeem (ID 34485) qualified in 500/500 draws. His matched point score of 1.024149 and 10th percentile of 0.271975 quantify different aspects of the same evidence.

## Cohort sensitivity and ranking movement

| Diagnostic | Batters | Bowlers |
|---|---:|---:|
| 6-ball cells, matched eligible | 127 | 144 |
| 6-ball versus 12-ball point top-ten overlap | 4/10 | 4/10 |
| 12-ball cells, matched eligible | 105 | 119 |
| 24-ball cells, matched eligible | 87 | 92 |
| 24-ball versus 12-ball point top-ten overlap | 6/10 | 2/10 |
| 12-ball design, at least 95% valid draws | 46 | 44 |
| v2 top-ten overlap with matched point model | 8/10 | 2/10 |
| v2 top-ten overlap with v1 | 2/10 | 1/10 |

Fakhar Zaman and Babar Azam remain in the batting top ten. Six v1 top-ten batters lack matched support, one lacks enough valid draws and one qualifies outside the v2 top ten. Sufiyan Muqeem moves from ninth in v1 to first in v2. Seven v1 top-ten bowlers lack matched support and two lack enough valid draws. Among qualifying bowlers, Tushar Deshpande moves from matched point rank 18 to research rank 3 when ordered by the lower tail. The versioned ledgers give exact ranks and scores for the whole assessed population.

Cell granularity and the resampling gate substantially affect coverage. Even among ranked players, a negative p10 indicates the lower tail is below the matched peer reference. The bootstrap conditions on observed cells and does not account for selection of cells, temporal drift or model formulation. The 95% gate may preferentially remove players with sparse exposure across many cells. Before treating v2 as a final submission model, compare it with partial pooling or coarser cells that keep the pre-delivery pressure definition and reduce sparse-cell attrition.

## Reproduction and artifacts

Run `python scripts/build_paprf_v2.py` from the repository root with the original local data files and the Phase 2 context audit available. Random weights are generated by NumPy's default generator and the recorded seed. The script checks the number of resampled matches and replays both 12-ball point top tens before writing v2. Input and frozen ranking hashes are in the audit JSON.

| Artifact | Contents |
|---|---|
| [Batters](../../outputs/rankings/paprf_batters_v2.csv) and [bowlers](../../outputs/rankings/paprf_bowlers_v2.csv) | Versioned v2 top tens with v1 top-ten rank, matched point rank and uncertainty. |
| [Uncertainty ledger](../../outputs/tables/paprf_v2_uncertainty.csv) | Valid draw counts, matched point scores, quantiles and research ranks for all 224 matched-eligible player-role records. |
| [Threshold ledger](../../outputs/tables/paprf_v2_threshold_sensitivity.csv) | Samples, deltas, standardised components and point scores at every tested threshold. |
| [Validation and movement JSON](../../work/paprf_v2_validation.json) | Source hashes, seeds, cohorts, overlaps and the reason each departing v1 player left the list. |
| [Uncertainty plot](../../outputs/figures/paprf_v2_uncertainty.png) | Horizontal 10th–90th percentile ranges with lower-tail scores and matched point estimates. Wider ranges indicate greater resampling variability. |
