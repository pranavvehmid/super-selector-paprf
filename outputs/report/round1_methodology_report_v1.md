# RR Super Select Cricket Auction Hackathon — Round 1 Methodology Report

**Version:** Lens A / v1  
**Prepared:** 18 November 2026  
**Submission purpose:** Ordered top-10 batter and bowler lists, with a reproducible explanation of the choices.

## Executive summary

This submission ranks pressure performance from the supplied ball-by-ball data. It deliberately answers a narrow question: which players delivered the strongest, most reliable performance in elevated or high pre-delivery pressure relative to their own ordinary-context baseline? Batters and bowlers are rated separately because their objectives and opportunity definitions differ.

The analytical chain is: validate the raw data; reconstruct match state before each delivery; label pressure without using the delivery outcome; calculate role-specific ordinary and pressure performance; standardise within role; shrink small pressure samples; test sensitivity; then freeze the rankings. The versioned output passed the ranking validator with zero errors.

This report does not claim that every ranked player is available to Rajasthan Royals, affordable, or the best squad fit. Current squad, retention and auction-pool inputs were not supplied in a dated, source-backed form. Those facts are therefore excluded rather than guessed.

## Final Lens A rankings

### Batters

| Rank | Player | Player ID | Pressure balls | Pressure matches | Reliability signal |
|---:|---|---:|---:|---:|---:|
| 1 | Jason Holder | 2633 | 337 | 48 | 1.497900 |
| 2 | Dinesh Karthik | 143 | 501 | 50 | 1.484493 |
| 3 | Mahendra Singh Dhoni | 8 | 374 | 44 | 1.341489 |
| 4 | Fakhar Zaman | 2921 | 201 | 16 | 1.106621 |
| 5 | Sam Billings | 1924 | 80 | 6 | 1.056267 |
| 6 | Shashank Singh | 2756 | 364 | 29 | 1.051216 |
| 7 | Matthew Wade | 796 | 208 | 17 | 1.036560 |
| 8 | Gulbadin Naib | 2214 | 75 | 6 | 1.001369 |
| 9 | Gareth Delany | 7741 | 188 | 20 | 0.986658 |
| 10 | Babar Azam | 2485 | 224 | 13 | 0.925867 |

### Bowlers

| Rank | Player | Player ID | Pressure legal balls | Pressure matches | Reliability signal |
|---:|---|---:|---:|---:|---:|
| 1 | Tabraiz Shamsi | 4237 | 106 | 6 | 1.444478 |
| 2 | Sakib Hussain | 35318 | 150 | 10 | 1.373606 |
| 3 | Hasan Mahmud | 6643 | 119 | 12 | 1.331110 |
| 4 | Mohammad Nawaz | 2490 | 275 | 23 | 1.298983 |
| 5 | Praful Hinge | 25132 | 68 | 7 | 1.163051 |
| 6 | Matthew Humphreys | 22471 | 91 | 7 | 1.123418 |
| 7 | George Linde | 4229 | 74 | 6 | 1.119121 |
| 8 | Rasikh Salam | 7327 | 218 | 15 | 1.103338 |
| 9 | Sufiyan Muqeem | 34485 | 162 | 10 | 1.060173 |
| 10 | Mohit Sharma | 2878 | 360 | 28 | 1.015889 |

The full evidence records, including component deltas and shrinkage weights, are in outputs/rankings/lens_a_batters_v1.csv and outputs/rankings/lens_a_bowlers_v1.csv. Figures are in outputs/figures/batter_top10_v1.png and outputs/figures/bowler_top10_v1.png.

## Scope and data treatment

The primary analytical population is IPL and men’s T20I data. Other T20 competitions are excluded from the official calculation and reserved only for a future sensitivity exercise. This decision protects the brief from scope drift.

The source archive was profiled and joined through stable player and match IDs rather than display names. The workflow retained 782 validated primary-scope matches and 186,620 delivery rows. Exceptional matches, out-of-scope competitions, and three matches with malformed nonfinal overs were held out. Holding them out is a conservative data-quality decision, not a claim that they are invalid cricket matches.

## Pre-delivery state and pressure

Pressure must be known before the delivery is bowled. For every retained delivery, the workflow reconstructs the score, wickets, legal balls, phase, target, runs required and balls remaining using only preceding deliveries. Independent reconstruction checks found zero row-level errors.

The pressure score is an interpretable, innings-specific index on a 0–1 scale.

- In the first innings, it combines late-innings urgency and wickets lost.
- In the chase, it combines required-run-rate stress, wickets lost and innings progress.
- Ordinary is below 0.40; elevated is 0.40 to below 0.65; high is at least 0.65.

The official pressure sample is elevated plus high. The delivery outcome is not an input to the pressure label, preventing outcome leakage.

## Role-specific performance measures

Batters are compared on runs per ball, dot-ball rate and dismissal rate. Better pressure batting means higher runs per ball, lower dot rate and lower dismissal rate versus ordinary context.

Bowlers are compared on economy, dot-ball rate and wicket rate. Better pressure bowling means lower economy, higher dot rate and higher wicket rate versus ordinary context.

The attribution rules explicitly handle wides, no-balls, byes, leg-byes and dismissal types. Ambiguous events are never silently forced into a rate: 257 deliveries are excluded from player-rate attribution while remaining in the state and pressure audit trail. The resulting metric population is 186,363 eligible deliveries.

## Baseline, reliability and why the score is credible

Each player is compared with their own ordinary-context baseline. This avoids treating a high-scoring specialist and a lower-scoring specialist as though their expected ordinary output were identical.

Eligibility requires at least 60 pressure opportunities and six pressure matches, plus the corresponding ordinary-context comparison. This yields 176 eligible batters and 219 eligible bowlers.

Within each role, the three performance deltas are standardised and equally combined into a raw signal. A transparent empirical-Bayes shrinkage weight then contracts smaller pressure samples toward zero:

    reliability signal = raw signal × pressure opportunities / (pressure opportunities + 60)

This is why a strong but smaller sample can rank well without being allowed to dominate an equally strong, well-established record. The reliability signal—not reputation, player name or squad preference—sets the ordering.

## Robustness checks

The pressure sample threshold and the shrinkage prior were tested before freezing the list.

| Test | Batters | Bowlers | Interpretation |
|---|---:|---:|---|
| Eligible under official elevated/high definition | 176 | 219 | Broad comparison population. |
| Eligible under high-only definition | 105 | 157 | Expected contraction when only the most intense contexts are retained. |
| Top-10 overlap when prior = 30 balls | 10/10 | 9/10 | Rankings are not driven by the prior choice. |
| Top-10 overlap when prior = 90 balls | 10/10 | 10/10 | Strong stability under more conservative shrinkage. |
| High-only top-10 overlap with official list | 7/10 | 5/10 | A useful sensitivity result, disclosed rather than hidden. |

The high-only result is not used as the official rule because it removes substantial evidence and changes which players qualify. It shows that the most extreme-pressure-only framing is materially different, especially for bowlers. The official elevated/high definition is retained because it has more evidence, a documented threshold and transparent validation.

## What each choice was made for

| Choice | Reason |
|---|---|
| IPL plus T20I primary scope | Keeps the official analysis aligned to the declared data scope and avoids accidental inclusion of unrelated T20 competitions. |
| Pre-delivery pressure label | Prevents a player’s delivery outcome from defining the pressure they are then judged under. |
| Separate batter and bowler models | Runs, survival, economy, dots and wickets have different cricket meanings by role. |
| Player’s own ordinary baseline | Measures pressure lift relative to what that player normally produces. |
| 60 opportunities and six matches | Removes very small pressure samples while retaining usable player breadth. |
| 60-ball shrinkage prior | Makes sample-size uncertainty visible and reduces small-sample overstatement. |
| Versioned v1 freeze | Ensures the report, tables, figures and final platform entry can be matched exactly. |

## Limitations and remaining actions

1. The supplied data does not include a provider field codebook. Scoring and legal-ball rules are validated against internal match totals and over structure; ambiguous player-attribution events are excluded.
2. The ranking is a historical statistical answer, not an availability or purchase recommendation.
3. A current RR squad, retention list, auction pool, pricing and availability dataset has not been provided. The RR-fit workstream remains separate and incomplete until those dated inputs are supplied.
4. The final human task is to enter the player labels into the Unstop dropdown in exactly the frozen order and confirm they map to the IDs above. The platform itself is outside this offline data pack.

## Reproduction map

1. scripts/audit_data_quality.py
2. scripts/validate_delivery_accounting.py and scripts/validate_state_rules.py
3. scripts/reconstruct_state.py and scripts/validate_reconstructed_state.py
4. scripts/apply_pressure_definition.py and scripts/validate_pressure_definition.py
5. scripts/build_player_metrics.py and scripts/validate_player_metrics.py
6. scripts/build_baselines.py and scripts/validate_baselines.py
7. scripts/build_reliability_scores.py
8. scripts/validate_robustness.py
9. scripts/freeze_rankings.py and scripts/validate_rankings.py

The manifest at outputs/rankings/ranking_manifest_v1.json identifies the frozen source files and ranking version.

## Formula and evidence supplement

The [PAPRF Phase 1 evidence record](../../docs/methodology/paprf_phase1_evidence.md) includes the pressure distribution by innings and phase, denominator-level calculations and the formula reconciliation. The [four-phase plan](../../docs/methodology/paprf_four_phase_plan.md) maps the remaining model, dashboard, PDF and validation work to the project specification.

The full mathematical expression ledger, metric-attribution rules, rounding treatment, validation calculations and source-to-artifact map are maintained in docs/methodology/lens_a_formula_ledger.md. The audit against the user’s broader scouting specification and the evidence gaps for future work are in docs/methodology/master_prompt_methodology_audit.md and docs/evidence/master_prompt_intake_and_traceability.md.
