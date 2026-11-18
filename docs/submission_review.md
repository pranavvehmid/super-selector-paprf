# RR Super Select — Analytical Review and Submission Record

**Project:** RR Super Select Cricket Auction Hackathon, Season 2, Round 1  
**Prepared:** 18 November 2026  
**Official method:** Lens A, version v1

## Submit these two deliverables

1. Use the two frozen lists on page 1 of the [Round 1 submission PDF](../outputs/report/latex/round1_submission.pdf) for the Unstop dropdowns. Enter each discipline in order from 1 to 10.
2. Upload that same PDF as the methodology report. The longer contextual report is supporting research. Its contextual rankings belong to a different question.

The supplied two-page Round 1 brief specifies the ordered dropdowns and methodology upload. The event listing also asks how the selections could strengthen Rajasthan Royals. Pages 3–4 give player-by-player on-field hypotheses derived from the pressure evidence. The remaining auction questions require dated roster and availability information. [Official Unstop event](https://unstop.com/o/owqQZ3f)

## Current position

The full statistical workstream is complete and reproducible. The project moved from raw ball-by-ball files to two frozen, ordered top-10 lists using a pre-delivery pressure definition, role-specific metrics, player baselines, reliability shrinkage and robustness checks. Ranking validation reports zero errors.

The current-squad and player-fit workstream is intentionally not complete: no dated, source-backed RR squad, retention, auction-pool, price or availability data was supplied. It has not changed the statistical ranking.

## Completed evidence chain

| Step | Status | Evidence |
|---|---|---|
| 1. Scope | Gate passed | IPL and T20I are primary; extra competitions are excluded from official rankings. |
| 2. Data dictionary | Gate passed | Source fields and ID joins documented. |
| 3. Data quality | Gate passed | Exceptional/out-of-scope conditions are explicitly held out. |
| 4. State reconstruction | Gate passed | 782 matches and 186,620 deliveries; zero row-level reconstruction errors. |
| 5. Pressure | Gate passed | Pre-delivery v1 pressure labels; zero validation errors. |
| 6. Metrics | Gate passed | 186,368 eligible attribution records; 252 ambiguous records held out. |
| 7. Baselines | Gate passed | 176 eligible batters and 219 eligible bowlers. |
| 8. Reliability | Gate passed | Three-component role signals, shrunk with a transparent 60-opportunity prior. |
| 9. Robustness | Gate passed | Prior tests retain 10/10 batter and 9–10/10 bowler top-10 overlap; high-only sensitivity disclosed. |
| 10. Rankings | Gate passed | Frozen Lens A v1 CSVs validate with zero errors. |
| 11. RR context | Blocked by missing inputs | Separate from statistical scoring. |
| 12. Report | Gate passed | outputs/report/round1_methodology_report_v1.md and matching figures created. |

## Submission assets

- Submission PDF: outputs/report/latex/round1_submission.pdf
- Earlier methodology notes: outputs/report/round1_methodology_report_v1.md
- Expanded research report: outputs/report/latex/paprf_research.pdf
- Batter list: outputs/rankings/lens_a_batters_v1.csv
- Bowler list: outputs/rankings/lens_a_bowlers_v1.csv
- Frozen-file manifest: outputs/rankings/ranking_manifest_v1.json
- Ranking figures: outputs/figures/batter_top10_v1.png and outputs/figures/bowler_top10_v1.png

## Remaining manual submission checks

1. Enter the frozen batter and bowler lists into Unstop in rank order.
2. Verify every platform dropdown label maps to the player ID in the CSV, especially names with possible formatting variants.
3. Upload the dedicated Round 1 PDF and confirm the final review shows the file and both ordered lists.
4. Do not add a claim about RR fit, availability, price or retention unless a dated source is attached.

## Why the approach is defensible

Pressure is determined before the delivery. Each player is assessed against their ordinary baseline. Eligibility and shrinkage limit small-sample influence. Shrinkage-prior changes retain 9–10 of the 10 names. The high-only test has lower overlap, and the historical repeatability checks are weak. The PDF gives the eligibility counts, outcome gaps and actual overlap values.

## Final audit and comparison review

- Replayed the analytical pipeline from the six organiser CSVs in a clean temporary directory. All 25 checked outputs matched exactly. The replay independently verified 305 v4 point scores. The submission builder separately recomputed all 395 v1 eligible scores and reconciled the two ordered top tens with the ranking manifest and CSVs.
- Corrected the old attribution counts to 252 ambiguous and 186,368 metric-eligible delivery events. Frozen v1 kept the match metadata and counted the two ambiguous events with a wicket flag and dismissed-player ID as batting dismissals. The v4 sensitivity analysis uses stricter striker-only attribution. No frozen rank or score changed.
- Verified all 20 page-one name/score pairs in order, including their printed player IDs on pages 3–4. The PDF SHA-256 is `f291e41d6533951d7481eec10e2bb34bec2273b5595ceb1d83f301499faac558`.
- Reviewed the public comparison site. Its player view puts context rates, sample size and uncertainty near the selected player. PAPRF now puts paired pressure/ordinary rate bars beside the pressure ranking and makes annual contextual evidence chartable for each profile with scored years. [Comparison dashboard](https://ipl-tau-six.vercel.app/)
- The comparison site's published cohort is 818 matches with roughly 19% of events flagged as high pressure, whereas PAPRF uses 782 validated matches and flags 36.9% as elevated or high. The displayed repeatability estimates are different experiments. A predictive head-to-head requires shared data, outcome, cutoffs, exposure and evaluation folds. Our chronological comparison uses aligned eligible IDs within each window. The pooled point comparator beats v4 p10 in five of six discipline/window pairs, so the audit does not infer a win for v4 from its extra complexity. [PAPRF validation](https://dashboard-seven-delta-35.vercel.app/?page=validation)
