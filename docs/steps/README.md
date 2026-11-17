# Roadmap and status

Order matters: understand data → reconstruct state → define pressure → measure → baseline → rate → validate → rank → squad context → report.

| # | Step | Status | Decision gate |
|---|---|---|---|
| 01 | [Lock the challenge scope and submission rules](01_scope.md) | NOT STARTED | Do not proceed to player scoring until scope is explicit. |
| 02 | [Build the data dictionary and relationship map](02_data_dictionary.md) | NOT STARTED | Every field used in the model has a clear interpretation and traceable source. |
| 03 | [Complete the data-quality and coverage audit](03_data_quality.md) | NOT STARTED | Do not score records whose delivery, player or match context cannot be interpreted reliably. |
| 04 | [Reconstruct each innings and the pre-delivery match state](04_state_reconstruction.md) | NOT STARTED | No pressure label until innings state and legal-ball logic pass validation. |
| 05 | [Define pressure transparently (batting and bowling)](05_pressure_definition.md) | NOT STARTED | Interpretable, available from the data, and leakage-free. |
| 06 | [Define role-appropriate batting and bowling metrics](06_metrics.md) | NOT STARTED | Every metric computed from correctly attributed runs, balls, wickets and extras. |
| 07 | [Establish each player's normal-performance baseline](07_baselines.md) | NOT STARTED | Comparison is like-for-like enough to interpret fairly. |
| 08 | [Design a reliability rating with sample-size protection](08_reliability.md) | NOT STARTED | No high-confidence rank from a handful of pressure deliveries. |
| 09 | [Validate the model and test ranking robustness](09_validation.md) | NOT STARTED | Final rankings remain defensible under sensible alternatives. |
| 10 | [Produce the ranked top-10 lists](10_rankings.md) | NOT STARTED | Report and Unstop dropdown selections match exactly. |
| 11 | [Add squad-context overlay (Lens C)](11_squad_fit.md) | NOT STARTED | Statistical scores untouched; all external facts sourced and dated. |
| 12 | [Prepare the methodology report and submission materials](12_report.md) | NOT STARTED | Report, tables and Unstop entries are consistent. |

Status values: NOT STARTED · IN PROGRESS · GATE PASSED · BLOCKED. Update when a step changes state and log it in `PROJECT_LOG.md`.
