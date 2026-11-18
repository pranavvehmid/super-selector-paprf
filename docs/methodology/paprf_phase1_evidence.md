# PAPRF Phase 1 evidence record

## Source and grain

The organiser pack has six CSVs. Delivery events carry match, innings and ball identifiers. Match metadata carries date, venue ID and host country. Competition, team, participation and player mappings provide the other lookup and participation records. See the [77-field dictionary](../data_dictionary.md) and [quality audit](../../work/data-quality-audit.json). Match-to-competition joins use competition ID. Delivery-to-match joins use match ID. Player aggregation uses player ID.

The raw delivery CSV has 200,999 rows and the match CSV has 883 records. The earliest and latest values of the raw match date field are 2022-01-22 and 2026-11-01. The [validated pressure file](../../data/processed/pressure_labeled_deliveries.csv) has 186,620 delivery events from 782 distinct IPL/T20I match IDs. Pressure exposure counts every event in this file, including events that may be illegal balls or excluded for player-rate attribution. The separate attribution stage holds out 252 rows, leaving 186,368 metric-eligible events. These figures answer different questions and use different denominators.

## Five pillars and evidence readiness

| Pillar | Phase 1 evidence | Boundary or next test |
|---|---|---|
| Pressure context | Pre-delivery innings, legal balls, wickets and known chase state. The existing formula assigns three bands. | Compare phase coverage and threshold sensitivity before approving a changed model. |
| Pressure-adjusted performance | Separate player outcomes with runs, dots and dismissals or wickets, plus ordinary baselines and shrinkage. | Test whether matching on phase or competition changes the conclusions. |
| Execution quality | The raw file contains labels such as pace/spin, stroke and delivery style. | A label can support a descriptive split after validation. Technique, intent, yorker accuracy and physical conditions need additional evidence. |
| Consistency and resilience | Distinct match counts and sample-size shrinkage are available. | Repeatability requires match-level or temporal tests. Shrinkage alone does not estimate it. |
| Opposition and contextual difficulty | Venue, opponent and competition identifiers are available. | An identity is not a strength or pitch rating. Any strength estimate needs a dated, leakage-safe method and coverage checks. |

## Calculation and independent reconciliation

The [formula ledger](lens_a_formula_ledger.md) gives the equations and role-specific scoring signs. Run `python scripts/build_paprf_descriptives.py` from the repository root. The script recalculates the index and phase directly from the pre-delivery columns, compares the index at the six-decimal storage precision, derives its band and checks it against the stored label. It then counts events by innings, phase and band, emits all 18 cells including zeros, and records the input and ranking hashes in the [audit JSON](../../work/paprf_phase1_audit.json).

For cell count C, total delivery events N and events in the same innings and phase M:

    Percentage of the full sample = 100 × C / N
    Percentage within innings and phase = 100 × C / M

The [distribution CSV](../../outputs/tables/paprf_pressure_distribution.csv) publishes C, N and M for every cell. Display percentages are rounded to six decimals. A zero within-phase denominator is left blank.

| Band | Count | Calculation | Share of all deliveries |
|---|---:|---|---:|
| Ordinary | 117,832 | 100 × 117,832 / 186,620 | 63.140071% |
| Elevated | 33,343 | 100 × 33,343 / 186,620 | 17.866788% |
| High | 35,445 | 100 × 35,445 / 186,620 | 18.993141% |
| Elevated or high | 68,788 | 100 × (33,343 + 35,445) / 186,620 | 36.859929% |

For example, the 611 high-pressure chasing powerplay events are 2.082907% of the 29,334 events in that phase and 0.327403% of all 186,620 events. The [distribution figure](../../outputs/figures/paprf_pressure_distribution.png) plots counts to show the size of each sample. The CSV gives within-phase percentages for comparing unequal samples.

The audit found zero disagreements in the index, phase and band. This establishes agreement with the published calculation. Calibration against an independent measure of pressure remains open.

## Structural finding and model decision

For the first 72 legal balls of innings one, the late-innings term is zero. The wicket term is capped at 0.30, below the 0.40 elevated threshold. The model therefore classifies all 29,322 first-innings powerplay events as ordinary by construction. Conversely, 4,629 chase death-over events were ordinary. Phase and pressure overlap asymmetrically, which can change who gets enough qualifying opportunities and can confound pressure lift with usual phase-specific scoring patterns.

The recommended Phase 2 comparison starts with the shared pre-delivery context and separate batting and bowling outcomes. An experimental role-specific model can distinguish the batting side’s resource stress from the bowling side’s defending difficulty, with an explicit test for first-innings early collapses. The experiment should report eligible pools, phase and competition composition, and top-10 overlap against v1 before any replacement decision. Thresholds should be declared before reviewing individual ranks.
