# RR Super Select — Analytical Review and Submission Record

**Project:** RR Super Select Cricket Auction Hackathon, Season 2, Round 1  
**Prepared:** 18 November 2026  
**Official method:** Lens A, version v1

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
| 6. Metrics | Gate passed | 186,363 eligible attribution records; 257 ambiguous records held out. |
| 7. Baselines | Gate passed | 176 eligible batters and 219 eligible bowlers. |
| 8. Reliability | Gate passed | Three-component role signals, shrunk with a transparent 60-opportunity prior. |
| 9. Robustness | Gate passed | Prior tests retain 10/10 batter and 9–10/10 bowler top-10 overlap; high-only sensitivity disclosed. |
| 10. Rankings | Gate passed | Frozen Lens A v1 CSVs validate with zero errors. |
| 11. RR context | Blocked by missing inputs | Separate from statistical scoring. |
| 12. Report | Gate passed | outputs/report/round1_methodology_report_v1.md and matching figures created. |

## Submission assets

- Official report: outputs/report/round1_methodology_report_v1.md
- Batter list: outputs/rankings/lens_a_batters_v1.csv
- Bowler list: outputs/rankings/lens_a_bowlers_v1.csv
- Frozen-file manifest: outputs/rankings/ranking_manifest_v1.json
- Ranking figures: outputs/figures/batter_top10_v1.png and outputs/figures/bowler_top10_v1.png

## Remaining manual submission checks

1. Enter the frozen batter and bowler lists into Unstop in rank order.
2. Verify every platform dropdown label maps to the player ID in the CSV, especially names with possible formatting variants.
3. Attach or paste the methodology report as permitted by the submission form.
4. Do not add a claim about RR fit, availability, price or retention unless a dated source is attached.

## Why the approach is defensible

The scoring question is limited to historical pressure performance, not reputation. Pressure is determined before the delivery, player outcomes are attributed using explicit rules, each player is assessed against their own ordinary baseline, and uncertainty is controlled through eligibility thresholds and shrinkage. Reasonable changes to the shrinkage prior do not materially alter the official top 10. All remaining caveats are stated in the report rather than obscured.
