# Roadmap and status

Order matters: understand data → reconstruct state → define pressure → measure → baseline → rate → validate → rank → squad context → report.

| # | Step | Status | Decision gate |
|---|---|---|---|
| 01 | [Lock the challenge scope and submission rules](01_scope.md) | GATE PASSED | Primary scope and active ranking method are explicit; proceed to Step 2. |
| 02 | [Build the data dictionary and relationship map](02_data_dictionary.md) | GATE PASSED | Every supplied field is documented; unresolved delivery semantics are prohibited from model use until Step 4 validation. |
| 03 | [Complete the data-quality and coverage audit](03_data_quality.md) | GATE PASSED | A reproducible policy holds out 70 special-condition matches pending Step 4 validation. |
| 04 | [Reconstruct each innings and the pre-delivery match state](04_state_reconstruction.md) | GATE PASSED | Validated pre-delivery state exists for 782 primary-scope matches; exceptional, out-of-scope and malformed matches are held out. |
| 05 | [Define pressure transparently (batting and bowling)](05_pressure_definition.md) | GATE PASSED | Pressure v1 is pre-delivery, interpretable, and independently validated on 186,620 deliveries. |
| 06 | [Define role-appropriate batting and bowling metrics](06_metrics.md) | GATE PASSED | Role-specific aggregates reconcile to 186,368 attributed delivery records; 252 ambiguous events are held out. |
| 07 | [Establish each player's normal-performance baseline](07_baselines.md) | GATE PASSED | 176 batter and 219 bowler ordinary-versus-pressure baselines pass formula and eligibility checks. |
| 08 | [Design a reliability rating with sample-size protection](08_reliability.md) | GATE PASSED | Three-component signals use transparent 60-ball shrinkage; diagnostics are generated. |
| 09 | [Validate the model and test ranking robustness](09_validation.md) | GATE PASSED | Rankings are stable across shrinkage priors; high-only sensitivity is disclosed. |
| 10 | [Produce the ranked top-10 lists](10_rankings.md) | GATE PASSED | Versioned Lens A lists validate with zero errors. |
| 11 | [Complete RR squad needs and player-fit context](11_squad_fit.md) | BLOCKED | Statistical scores are untouched; dated squad and availability data are not supplied. |
| 12 | [Prepare the methodology report and submission materials](12_report.md) | GATE PASSED | Review report, tables and figures are consistent; Unstop entry remains a manual final check. |

Status values: NOT STARTED · IN PROGRESS · GATE PASSED · BLOCKED. Update when a step changes state and log it in `PROJECT_LOG.md`.
