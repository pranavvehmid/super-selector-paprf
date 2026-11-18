# PAPRF Round 1 research plan

The four phases group stages A–I from the user’s Round 1 project master prompt, sections 17–18 (attachment SHA-256 A22B8BBE657808F29EB06F92C5980946F079DD91A87F0A6B321AE98E2AA0AEDB). The [official requirements](../00_official_requirements.md) establish the two ordered top-10 submissions and methodology review. The project specification adds an interactive dashboard and a research PDF. Scope is historical T20 pressure performance. Auction, retention, recruitment and video production are outside this research plan.

| Phase | Original stages | Work and completion evidence |
|---|---|---|
| 1. Data and pressure foundation | A, B and C | Verify source structure and coverage. Map the five PAPRF pillars to supported fields. Recalculate the current pressure index and quantify where it classifies pressure. Record alternatives and bring the definition to the user for review. |
| 2. Statistical models and research execution | D and H | Evaluate batter and bowler outcomes separately. Compare shared pressure context with role-specific alternatives using the same matches and an explicitly documented evaluation design. Test phase and competition effects, weight changes, repeatability, sample size and match-clustered uncertainty where viable. Record numerator, denominator, units, transformation, seed and cutoff for each estimate. |
| 3. Dashboard and research PDF | E, F and G | Review WASM versus browser JavaScript with Python-generated aggregates, then agree on navigation and report structure. Build two views from one versioned evidence bundle. Show official results and sensitivity scenarios with distinct labels. Validate interaction and render the PDF for layout checks. |
| 4. Validation and submission package | I | Reproduce results, reconcile the PDF, dashboard and ordered ranking CSVs by ID, document coverage and uncertainty, check platform labels where accessible, and obtain final approval. |

Stages H and I span analysis and validation. Phase 2 is where model experiments run, while Phase 4 is the final end-to-end check. The existing Lens A v1 rankings are the reference for comparisons. The user authorised starting Phase 1. The attachment reserves final model, dashboard architecture, PDF structure and delivery decisions for user review.

## Evidence standard

Phase 2 evidence includes the [pressure and weight experiment](paprf_phase2_experiment.md), [matched-context and temporal audit](paprf_matched_context_and_repeatability.md), [v2 uncertainty audit](paprf_v2_uncertainty.md), [v3 granularity comparison](paprf_v3_cell_granularity.md) and [v4 regularised fine-cell reanalysis](paprf_v4_reanalysis.md). The [formula ledger](lens_a_formula_ledger.md) records the baseline algorithms. The dashboard and v4 research review supplement include the [forward validation](paprf_forward_validation.md) and [matched split-half reliability audit](paprf_split_reliability.md). The clean rebuild implements the reproducibility portion of Phase 4. Final submission model choice and untouched external validation remain open.

For each result, record the source path and version or hash, row grain, ID join, population, exclusions, numerator, denominator, formula, units, precision, code entry point and verification result. Use the claim and source registers for external facts. Keep proposed and measured values identifiable. An unavailable result is reported as unavailable with its reason. The [Phase 1 record](paprf_phase1_evidence.md) provides the first reproducible calculation and audit.

The [contextual role profiles](paprf_contextual_role_profiles.md) extend the project with earlier-date opposition benchmarks, deployment-specific leaderboards, geography and annual splits, and alternative weights. These profiles estimate a broader question than the pressure-only rankings and are accessible in their own dashboard section.
