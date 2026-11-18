# PAPRF publication and verification

**18 November 2026 · Evidence run `e5f524236dbf`**

The supplied Round 1 problem statement calls for ten batters and ten bowlers. The frozen Lens A v1 lists answer the pressure question. The contextual batting and bowling indices answer how much players exceeded expectations in their observed roles. Within each discipline, frequency determines the primary role, performance is compared with its eligible peers, and one supported secondary role can earn limited extra credit. The dashboard publishes both questions and keeps the historical mixed-role experiment in the research archive.

## Changes and their effects

| Area | Changes | Effect |
| --- | --- | --- |
| Ranked evidence | Extended the clean rebuild through pressure versions, forward and split validation, contextual role profiles and the separate discipline rankings | All 25 tracked artifacts matched byte for byte. All 305 independent scalar point scores reproduced. Rank, score and role changes from this publication iteration are zero. |
| Model documentation | Added a formula catalogue covering scoring rules, symbols, worked examples and known sources of bias | The previous and current ranking equations are identical. The comparison between the contextual and pressure lists reflects different questions and eligibility rules. |
| Website | Eleven deep-linkable views, two themes, score breakdowns, data coverage and role distributions, interactive pressure curves, and an eighteen-chapter research library | Rankings, documentation and downloads are available through the same evidence bundle. |
| Report | Added a native LaTeX document and generated tables, with a compiled PDF and an editable source archive | The report, website and hashed analytical inputs share the evidence run ID. Existing evidence files and prior reports are retained as version history. |

## Reproduction

Run from the repository root. The original six CSVs are required in the local input structure described in the repository. The web bundle carries derived data and published evidence.

```powershell
python scripts/verify_paprf_rebuild.py
python scripts/build_paprf_latex.py --engine <path-to-tectonic>
python scripts/build_dashboard_data.py
python scripts/build_paprf_research_library.py
python -m pytest -q tests
```

The reproducibility result is in [paprf_clean_rebuild.json](../../work/paprf_clean_rebuild.json). The [publication manifest](../../work/publication_manifest.json) records the hashes and run ID. The formula and threshold provenance is in the [formula reference](../methodology/paprf_publication_formula_reference.md).

## Verification

- The project test suite passed all three tests. The scoped invocation selects the active repository tests and avoids a duplicate test copy in an unversioned incoming archive.
- The Edge browser harness, `scripts/verify_paprf_site.cjs`, passed all eleven routes at widths of 390, 768, 1280, 1440 and 1920 pixels in light and dark themes. It also exercises selected contrast, keyboard navigation, history, filters, formula rendering and downloads. The run used pinned local KaTeX assets and fallback fonts.
- Tectonic 0.17.0 compiled the seven-page A4 PDF. Final output had no overfull box or unresolved reference warnings. All rendered pages were reviewed. Text extraction verified the evidence ID and all 40 formatted name/score pairs across the four top-ten tables against their source CSVs. The local served and canonical PDFs were byte-identical.
- The PDF SHA-256 at the initial publication was `5da4e5c5d897bdb331b02dcaf9618cb56878978ce8612551640a83e7f98eeecf`. After the author credit update, the PDF SHA-256 is `09c3cf45476d6ca839ff79e81e76d2217a0e7f0b9920a18d6b935804a0bc3f79`. The analytical evidence run ID is unchanged.
- The same browser checks passed against the production alias. The published evidence export, research library, PDF and LaTeX source archive each returned HTTP 200 and matched their local file byte for byte. [Production dashboard](https://dashboard-seven-delta-35.vercel.app/)

## Interpretation and limits

Historical repeatability of the pressure-only ranking is weak. Some contextual roles carry over better, with sparse cohorts and some simpler baselines outperforming the weighted composite. The rebuild establishes reproducibility on the supplied sample. External holdout performance and transfer to other settings remain unverified. Venue country is a limited condition proxy, and the current index provides no age or developmental projections. The new browser checks cover selected contrast and interactions. The About page uses the author's supplied public details.

## Expanded report and dashboard Home

Evidence run `33b601c24ae8` covers the same ranking calculations as `e5f524236dbf` and includes additional hashed inputs for the printed validation tables and figures. Home leads with both complete contextual top tens. Page 2 of the 57-page report prints the same two lists. The archive preserves the separate Round 1 pressure-only lists.

The report includes worked reconstructions for each of the 20 contextual leaders, separate discipline comparisons, raw-file coverage and missingness, all seven role leaderboards, the v2–v4 match-resampling lists, and temporal, shuffle and sensitivity evidence. It reproduces all eight Figure Atlas charts and adds four static figures generated from dashboard evidence or the implemented chase formula. Interactive selectors stay available in the dashboard. The source archive packages the 18 full research chapters alongside the LaTeX, tables and figure assets.

The generator reconciled both contextual CSVs with the shared dashboard export and independently recomputed the published six-decimal final scores. Text extraction verified 40 name-and-score pairs, the 20 detailed traces and all 12 numbered figure captions. All 57 PDF pages were rendered for inspection. The PDF SHA-256 is `0442bffe4f0de8f31b7362d1d1697bd6414a8bd5fcb8875a2d1bdca2771ca918`.

The Edge checks passed on the local preview and production across 11 routes, five widths, and both themes, including an ordered comparison of the 20 Home rows with the published evidence. Production Home, the evidence export, the PDF and the editable source matched local files byte for byte.

## Editorial layout and evidence index

The grouped contents rail replaces the single navigation strip. The Home tables still show all 20 ranked players, with links that open their score traces and can be reloaded or shared. The six numbered framework panels fit a 390-pixel viewport. The expanded library contains 12 display equations and 11 named formula topics. Edge verified that the local math font loaded with external requests blocked, along with route navigation in both themes.

The research library starts with the dashboard reading guide and the two ranking methodologies. The editable archive includes 19 Markdown chapters and a JSON snapshot tested for equality against the complete published dashboard evidence. The update changes presentation and documentation. The analytical evidence run remains `33b601c24ae8`. The updated 57-page PDF SHA-256 is `3466c985b48ae664d58ef96ecabf123db5cc0be367729044f1e9edc7dd0c0810`.
## Blush dashboard design

The homepage presents the full contextual rankings in a rounded panel, with three match-coverage cards alongside at wide widths and below the tables on phones. The stacked pressure bars use the same six innings-phase groups and within-phase percentages as Appendix A of the report and the Pressure page. The live label for each bar lists the three band shares. This visual iteration uses the established evidence run and report.
