# PAPRF matched split-half reliability audit

## Design recorded before evaluation

The forward test combines calendar drift with measurement variation. Here, 32 random splits interleave the calendar. For each split, shuffle whole matches within competition family and calendar year, then assign alternate matches to two disjoint halves. Randomise which half gets the first match in each stratum. This keeps adjacent deliveries and shared player appearances within a match together. Use seed 20261119. Evaluate the v4 point composite and individual components using the published full-sample peer scaling in both halves. This is a retrospective measurement diagnostic.

Rebuild both halves from opportunity counts, with a primary 30-ball and three-match gate in each context and a stricter 60-ball and six-match gate as sensitivity. The stricter gate filters the same scored halves so comparisons reflect coverage and composition. Use only player IDs with evidence on both sides. Compute Spearman correlation using midranks for both the composite and the signed component deltas. Top-ten membership uses the common pool and the same ID tie-break as v4.

For a descriptive null, sort common players by their full-sample pressure opportunity count and split them into three nearly equal exposure groups. Within each group, shuffle the second-half player assignments independently 200 times while preserving both halves' measured scores and their rank distributions. The first and second half samples themselves retain whole-match structure. This null breaks persistent player pairing conditional on these exposure groups. It does not create a new outcome data set or give a design-based significance test. Exposure strata do not control all differences in competition mix, roles, or shared match dependencies.

Report medians and 10th–90th percentile ranges across splits. Splits reuse matches, so these quantiles measure sensitivity to partition assignment. Do not treat 32 splits or 6,400 shuffles as independent realised seasons. Under the parallel-measurement assumption, the Spearman–Brown expression 2r/(1+r) translates a half-sample reliability r to a same-population full-sample heuristic. It is descriptive only because these halves differ in eligibility and support and Spearman correlation is rank based.

## Results

| Role and gate | Median common players | Observed median ρ [p10, p90] | Shuffle p10 to p90 | Splits above own shuffle p90 |
|---|---:|---:|---:|---:|
| Batting, 30 balls and 3 matches | 95 | +0.012 [−0.083, +0.095] | −0.133 to +0.128 | 1/32 |
| Bowling, 30 balls and 3 matches | 107 | −0.037 [−0.135, +0.068] | −0.120 to +0.131 | 0/32 |
| Batting, 60 balls and 6 matches | 52 | −0.031 [−0.149, +0.123] | −0.178 to +0.181 | 0/32 |
| Bowling, 60 balls and 6 matches | 67 | −0.055 [−0.237, +0.059] | −0.164 to +0.149 | 1/32 |

The stricter gate changes who qualifies and gives no observable improvement in median composite correlation. In the primary gate, median top-ten overlap is one name for batting and 0.5 for bowling, compared with median uniform random references of 1.05 and 0.93. The 0.5 is a median across integer overlaps.

| Role and gate | Rate ρ | Dot ρ | Dismissal or wicket ρ |
|---|---:|---:|---:|
| Batting, primary | +0.057 | −0.017 | −0.054 |
| Bowling, primary | −0.057 | −0.016 | −0.003 |
| Batting, strict | +0.079 | +0.009 | −0.043 |
| Bowling, strict | −0.184 | −0.054 | +0.019 |

All component values are medians. Batting scoring-rate lift shows a small positive relationship. Neither wicket nor dismissal lift reproduces strongly enough here to justify reweighting based on this test. Calendar drift alone cannot account for the low repeatability because the interleaved halves balance competition family and calendar year. Support changes, opponent and venue differences, and the construct measured by the pressure label can still matter. The top-ten lists remain defensible as descriptions of the observed sample under a declared method. These checks give little basis for claiming persistent player-level pressure skill.

## Reproduction

Run `python scripts/audit_paprf_split_reliability.py`. The [audit JSON](../../work/paprf_split_reliability.json) records input hashes, seed, strata and distributions. The [split summary](../../outputs/tables/paprf_split_reliability.csv), [match membership](../../outputs/tables/paprf_split_match_membership.csv) and [player ledger](../../outputs/tables/paprf_split_player_ledger.csv) provide scores, sample counts and exact match assignments. The [figure](../../outputs/figures/paprf_split_reliability.png) compares observed intervals with the exposure-conditioned shuffle. See [forward validation](paprf_forward_validation.md) for the chronological check.
