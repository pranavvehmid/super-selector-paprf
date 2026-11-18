# Separate batting and bowling top tens

## Organiser requirement

The organiser's Round 1 problem statement, pages 1–2, requires an ordered top ten for batters under pressure and a separate ordered top ten for bowlers under pressure. Highest rating comes first in each category. The Unstop choices must agree with the submitted methodology report. The archived Lens A v1 pressure lists on the website address those two categories. This project also publishes a broader contextual index that measures effectiveness against role expectations across all eligible situations.

## Contextual rerun

The previous combined index assigned one primary role across all deployments. The revised contextual index fits the batting and bowling lists separately using the same match data, earlier-date expectations, role components, weights, reference scaling and opportunity shrinkage as the [methodology for the combined index](paprf_unified_ranking.md). For discipline d and player i, select the primary role from only the observed roles in d. Ties use scored matches, then unshrunk role signal and role ID. The selected primary needs at least 60 scored balls and six matches in the same discipline. Secondary credit comes from at most one supported role from that same discipline. A player can qualify for both lists independently. There is no cross-discipline bonus, and the two lists are not calculated by filtering the previous combined top ten.

| Contextual category | Observed IDs | Eligible | Rank 1 |
|---|---:|---:|---|
| Batting | 815 | 236 | Abhishek Sharma |
| Bowling | 587 | 249 | Varun Chakravarthy |

Each list is ordered by the historical role index rounded to six decimal places. Score components and uncertainty of the source role model are available in the player drill-down. Neither contextual list represents a forecast or replaces the organiser's pressure-only requirement.

## Files and audit

Run `python scripts/build_paprf_discipline_rankings.py` followed by the dashboard data and research-library build scripts. The [batting list](../../outputs/rankings/paprf_contextual_batters_top10_v2.csv), [bowling list](../../outputs/rankings/paprf_contextual_bowlers_top10_v2.csv), [assignment ledger](../../outputs/tables/paprf_contextual_discipline_assignments_v2.csv) and [score ledger](../../outputs/tables/paprf_contextual_discipline_scores_v2.csv) publish each result. The explanation of the official pressure method stays in the [Lens A formula ledger](lens_a_formula_ledger.md). The prior combined index remains available in the research archive.
