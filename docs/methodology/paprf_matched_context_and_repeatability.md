# PAPRF matched-context and repeatability audit

## Design declared before calculation

Both diagnostics use Lens A v1 pressure labels, the same delivery attribution and separate batting and bowling outcome models. Changes in eligible opportunity and match counts are part of the evidence. Match IDs count toward eligibility when the player has at least one role-eligible opportunity in the relevant bucket. Runs, dots, dismissals and wickets retain the v1 attribution conventions.

### Matched-context comparison

For each player, define a cell by innings, phase and competition family (IPL or T20I). Keep cells with at least 12 ordinary balls and 12 pressure balls. A player needs at least 60 balls and six opportunity-bearing matches in each context across retained cells. This design compares the player with their own baseline in situations with comparable phase and competition family. It trades coverage for comparability. It does not match teams, opponents or venues.

For metric j in cell k, let P and O be pressure and ordinary rates and let n be pressure balls. Compute the player’s matched delta as Σ nₖ(Pⱼₖ − Oⱼₖ) / Σ nₖ. The pressure weighting estimates lift over the distribution of pressure opportunities retained for that player. Each rate uses the cell’s own denominator. For bowling economy, multiply runs per legal ball by six before subtracting. Standardise deltas within the matched eligible role pool with the sample standard deviation, orient the signs as in v1, average the three signed z-scores and multiply by N/(N+60), where N is retained pressure balls. Ties at six decimals use ascending player ID.

### Chronological repeatability

Sort retained matches by the source match date and match ID. Use the date of the middle match as the split, with all matches on the split date in the later period. Independently rank each half with pooled v1-style ordinary-to-pressure deltas. A half requires at least 30 balls and three opportunity-bearing matches in each bucket. Use the same component signs and 60-ball shrinkage prior. The smaller gate is a diagnostic choice that preserves more players despite shorter windows. Compare only players eligible in both periods. Spearman correlation is Pearson correlation of their within-common-pool score ranks, with average ranks for ties. The top-ten overlap uses each half’s full eligible pool and therefore includes eligibility changes. These results describe temporal stability, with no predictive accuracy claim.

## Results

The input reconciles to 186,620 delivery events in 782 matches. The earlier period runs from 22 January 2022 through 7 May 2024, and the later period starts on 8 May 2024 and ends on 1 November 2026. Each contains 391 matches.

| Diagnostic | Batters | Bowlers |
|---|---:|---:|
| Eligible in matched contexts | 105 | 119 |
| Frozen top 10 still eligible | 4/10 | 3/10 |
| Matched and frozen top-ten overlap | 2/10 | 2/10 |
| Matched overlap against v1 top ten restricted to the same eligible IDs | 6/10 | 3/10 |
| Early eligible | 163 | 195 |
| Late eligible | 171 | 206 |
| Eligible in both halves | 102 | 128 |
| Spearman ρ among the common pool | 0.0625 | 0.1484 |
| Shared between the two period top tens | 0/10 | 1/10 |

The restricted comparator filters the original pooled score table to matched-eligible IDs and retains the original scores. The comparison isolates the ranking agreement after restricting who can be selected, with changes from both context weighting and peer re-standardisation still present. The original 2/10 overlaps combine eligibility loss and changes in scoring. The weak period correlations give little support for claiming persistent rank order over time. Opponents, venues, role changes and sampling variation remain plausible contributors. An eligibility failure means insufficient evidence under this particular rule.

## Worked example

Babar Azam (ID 2485) retained three second-innings T20I cells. Each runs-per-ball calculation uses these numerators and denominators.

| Phase | Ordinary runs / balls | Pressure runs / balls | Weight in matched delta |
|---|---:|---:|---:|
| Death | 44/36 | 51/21 | 21/173 |
| Middle | 225/172 | 155/98 | 98/173 |
| Powerplay | 180/164 | 78/54 | 54/173 |

    Scoring delta = [21 × (51/21 − 44/36)
                  + 98 × (155/98 − 225/172)
                  + 54 × (78/54 − 180/164)] / 173
                  ≈ 0.409638 runs per ball
    Raw signal ≈ (1.077967 + 1.858828 + 0.148932) / 3 = 1.028576
    Shrinkage = 173 / (173 + 60) ≈ 0.742489
    Matched score = round(raw signal × shrinkage, 6) = 0.763706

Counts sum to 372 ordinary balls and 173 pressure balls. Distinct match IDs are unioned across cells before counting, yielding 22 ordinary matches and nine pressure matches. Rank eight is specific to the matched batting diagnostic. Full precision is retained during scoring and the displayed rank score is rounded once.

## Reproduction and file map

Run `python scripts/audit_paprf_context.py` from the repository root. The algorithm is deterministic. The source files are the attributed deliveries and the organiser’s match and competition tables, joined by IDs. The summary records their SHA-256 hashes and the hashes of the frozen ranking files.

| Artifact | What to check |
|---|---|
| [Matched-cell ledger](../../outputs/tables/paprf_matched_cells.csv) | Player, innings, phase, competition family, retained flag and all ordinary and pressure numerators and denominators. |
| [Temporal ledger](../../outputs/tables/paprf_temporal_periods.csv) | One player-role-period row with both evidence buckets and match counts. |
| [Score ledger](../../outputs/tables/paprf_context_audit_scores.csv) | Eligible player, diagnostic, contributing cells, aggregate counts, deltas, signed standardised inputs, shrinkage and rank. |
| [Audit JSON](../../work/paprf_context_audit.json) | Input versions, peer scaling parameters, cutoff, eligible pools, overlaps and correlation. |

The audit motivates a match-cluster uncertainty analysis and a shorter support-threshold sensitivity check before any ranking change is considered.
