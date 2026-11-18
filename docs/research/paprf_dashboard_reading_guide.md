# Dashboard reading guide and evidence index

## Start with the rankings

The [Home page](https://dashboard-seven-delta-35.vercel.app/) shows the complete contextual top tens for batters and bowlers. Open a name to jump to its score calculation. The [project report](https://dashboard-seven-delta-35.vercel.app/reports/paprf_research.pdf) starts with the same tables, then explains the data, equations and validation before presenting the detailed ledgers.

The competition asks for two pressure-only lists. These are the frozen Lens A v1 tables in the report's Ranking evidence section and the dashboard's Pressure page. The contextual index answers a broader question about player effectiveness. Later-window tests show weak repeatability for the pressure-only ranking and stronger but role-dependent carryover for some contextual roles.

## Read the calculations and their evidence

| Page | What you can inspect | Report or archive location |
| --- | --- | --- |
| Home | Both contextual top tens, evidence totals, pressure bands, principal findings | Ultimate Top 10, Validation, Appendix A, `disciplines`, `audit`, `distribution` |
| Ultimate Top 10 | Discipline switch, eligible and unranked players, role inputs, contribution bridge, sensitivity, venue and annual evidence | Mathematical framework, Appendices B and E, `disciplines` |
| Player profiles | Name or ID search, eligibility, primary and secondary role trace, annual rates and residuals | Appendix B prints the 20 leaders. `disciplines.lists` has the other eligible profiles and observed unranked players. |
| Role leaderboards | Seven deployments, weights, resample shares, score bins, India weighting, equal weights, residualised boundaries and later tests | Appendices C and E, `role_profiles`, `role_histograms`, `role_validation` |
| Dataset | Six files, rows, columns, duplicate rows, field blanks and raw versus retained scope | Problem and data, Appendix A, data dictionary, `datasets`, `audit` |
| Framework and formulas | Data pipeline, rate metrics, context hierarchy, standardisation, pressure bands, role assignment, bounded credit and glossary | Mathematical framework, Glossary and the formula reference |
| Pressure and Round 1 | Counts and shares, pressure sliders, v1 and three experimental rankings, player inputs and the matched audit | Ranking evidence, Appendices A, D and E, `distribution`, `rankings`, `ledger`, `model`, `contexts`, `context_audit`, `robustness` |
| Compare players | Same-discipline comparisons of role, evidence, score components and latest raw rates. The figure selector has eight charts. | Appendix B gives rank-one and rank-two examples. Appendix E has all eight charts. `disciplines.lists` has the other comparison inputs. |
| Validation | v2–v4 leaders, prior-list exits, matching and support sensitivity, chronological folds, alternate predictors, interleaved splits and shuffle benchmarks | Appendices C–E, `research`, `granularity`, `regularised`, `forward`, `split_reliability`, `role_validation` |
| Documentation | Run ID, report and source downloads, methodology and milestones | Version history and reproducibility, Appendix F, `publication` |
| About | Author and supplied contact links | Report title page and the dashboard’s About page |

## Reuse the evidence

The [editable report archive](https://dashboard-seven-delta-35.vercel.app/reports/paprf_research_source.zip) contains the research chapters, LaTeX, figures and `dashboard_evidence.json`, a machine-readable copy of the dashboard data. It includes rows beyond the printed top tens and inputs behind the interactive filters. The report presents comparison examples. The JSON lets you reconstruct other player pairs and filter settings. The organiser's raw CSVs are separate.

For reproduction commands and verification results, see the [publication QA record](paprf_publication_qa.md). The [formula reference](../methodology/paprf_publication_formula_reference.md) explains the inputs, interpretation and limitations.
