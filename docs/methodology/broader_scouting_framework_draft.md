# Evidence-Gated Broader T20 Scouting Framework — Draft v0.1

**Status:** Proposed future framework; not applied to Lens A v1 and not used to select any player.  
**Purpose:** Translate the user-supplied master prompt into a repeatable scouting overlay once source-backed evidence exists.

## Design rules

1. Statistical performance, technical observation and evidence confidence are separate fields.
2. Missing evidence is Not assessed, never zero.
3. A player must be compared within the intended role before cross-role discussion.
4. No component may be counted twice: for example, an outcome can support quality-of-performance or pressure handling, but its use must be recorded once in the claim register.
5. Lens A v1 remains a standalone historical pressure-reliability output. This draft cannot revise it.

## Scales

Each assessed dimension uses a 0–100 rubric with an accompanying evidence confidence:

| Score band | Interpretation |
|---:|---|
| 85–100 | Exceptional, repeatedly evidenced in relevant T20 context. |
| 70–84 | Strong, with meaningful repeatable evidence. |
| 55–69 | Adequate/mixed; limitations are material. |
| 40–54 | Limited evidence of suitability or recurring weakness. |
| Below 40 | Clear evidence that the defined role is currently unsuitable. |
| Not assessed | Evidence does not meet the stated standard; no numeric substitute is allowed. |

Confidence multiplier is reported separately and never silently lowers the performance score: High = 1.00, Medium = 0.65, Low = 0.35. These values are a proposed reporting convention, not a claim about player ability.

## Core weighted formula

For each available dimension j, let S_j be its 0–100 score, W_j its role weight, and C_j its evidence-confidence multiplier.

    evidence_coverage = Σ(W_j for assessed dimensions) / 100
    performance_score = Σ(W_j × S_j for assessed dimensions) / Σ(W_j for assessed dimensions)
    evidence_confidence_index = Σ(W_j × C_j for assessed dimensions) / Σ(W_j for assessed dimensions)

Publish a composite only when evidence_coverage is at least 0.70 and no mandatory role dimension is unassessed. Otherwise report the component evidence and the verdict Monitor / insufficient evidence. The confidence index accompanies, but does not alter, performance_score.

## Dimensions and evidence rules

| Dimension | Permitted evidence | Must not be inferred from |
|---|---|---|
| Technical execution | Cited video or structured observation, with match/timestamp. | Aggregate runs/wickets alone. |
| Performance quality | Contextual event data, opposition/conditions evidence and repeatability. | One highlight or raw volume. |
| Recent form/consistency | Dated, predeclared rolling-period metrics. | One exceptional match. |
| Adaptability | Adequate samples across documented conditions. | Country label or league reputation. |
| Tactical intelligence | Cited tactical observations and repeatable contextual decisions. | Outcome alone. |
| Pressure/match impact | Lens A evidence plus separately cited close/knockout context where valid. | Match result alone. |
| Opposition quality | Declared opponent-strength model/source. | Assumptions about nationality. |
| Role suitability | Demonstrated role usage and role-specific evidence. | Generic overall record. |
| Physical/fielding | Verified, relevant observations or official data. | Appearance or private medical speculation. |
| Potential | Age-group/development evidence and trajectory, explicitly distinct from proven output. | Youth alone. |

## Proposed role matrices (each totals 100%)

| Dimension | Batter | Wicketkeeper | Fast bowler | Spinner | All-rounder | Specialist finisher |
|---|---:|---:|---:|---:|---:|---:|
| Technical execution | 20 | 20 | 22 | 21 | 16 | 19 |
| Performance quality | 15 | 16 | 16 | 16 | 15 | 17 |
| Recent form/consistency | 15 | 14 | 13 | 13 | 13 | 14 |
| Adaptability | 12 | 10 | 10 | 11 | 11 | 10 |
| Tactical intelligence | 10 | 11 | 11 | 11 | 10 | 11 |
| Pressure/match impact | 10 | 10 | 11 | 11 | 10 | 12 |
| Opposition quality | 6 | 6 | 6 | 6 | 6 | 5 |
| Role suitability/versatility | 8 | 8 | 7 | 7 | 12 | 9 |
| Physical/fielding | 2 | 3 | 2 | 2 | 3 | 1 |
| Development/potential | 2 | 2 | 2 | 2 | 4 | 2 |
| **Total** | **100** | **100** | **100** | **100** | **100** | **100** |

## Mandatory role gates

Before a Select verdict, the following cannot be Not assessed:

- Batter: technical execution, recent form/consistency, role suitability.
- Wicketkeeper: batting technical evidence, keeping evidence, role suitability.
- Fast bowler: technical execution/control, role suitability, workload/availability evidence where relevant and public.
- Spinner: technical execution/variation evidence, role suitability, adaptability evidence.
- All-rounder: separate batting and bowling evidence; neither discipline can be carried by the other.
- Specialist finisher: role-specific pressure and tactical evidence plus relevant recent-form evidence.

## Verdict rules

| Verdict | Evidence-led condition |
|---|---|
| Select | Coverage and mandatory gates pass; performance score is at least 70; no critical unmitigated role risk is documented. |
| Reserve | Coverage and gates pass, but score is 55–69 or the role fit is contingent. |
| Monitor | Evidence is promising but coverage is below 70%, development evidence is incomplete, or recency needs confirmation. |
| Reject for current brief | Evidence indicates the defined role requirement is not met; record specific cited reason. |

These thresholds are proposed decision rules. They must be validated against an actual, source-backed discovery population before they are used for any selection.
