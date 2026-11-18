# Pressure Definition (Step 5)

**Status:** GATE PASSED
**Version:** v1, 18 November 2026

## Scope and guardrail

The pressure label describes the pre-delivery match context faced by both players on a delivery. Batter and bowler performance are measured separately in Step 6; the shared context label does not make their outcomes equivalent.

The calculation reads only pre-delivery state, innings number, and the second-innings target known before that innings begins. It does not read the rated delivery's outcome, a later delivery, the match result, or the winning team.

## Inputs

| Input | Definition |
|---|---|
| pre_delivery_legal_balls | Validated legal balls before the delivery. |
| pre_delivery_wickets | Source wicket flags before the delivery. |
| pre_delivery_runs_required | Runs needed before a second-innings delivery. |
| pre_delivery_balls_remaining | Legal balls available before the delivery. |
| target | First-innings total plus one, known before the second innings. |

## Continuous pressure index

All components are bounded between zero and one.

### First innings

First-innings pressure uses late-innings urgency and wickets lost:

late_innings_stress = clamp((legal_balls - 72) / 48)

wicket_stress = wickets / 10

pressure_index = 0.70 × late_innings_stress + 0.30 × wicket_stress

The first 12 overs do not receive late-innings urgency. The final eight overs progressively do.

### Second innings

Second-innings pressure uses chase difficulty, wickets lost, and innings progress:

required_run_rate = 6 × runs_required / max(balls_remaining, 1)

run_rate_stress = clamp((required_run_rate - 7) / 5)

progress = legal_balls / 120

pressure_index = 0.55 × run_rate_stress + 0.25 × wicket_stress + 0.20 × progress

This treats a 7-run required rate as the start of rate stress and caps the rate component at 12 runs per over. These are transparent modelling choices, not official facts.

## Bands

| Band | Index |
|---|---:|
| Ordinary | < 0.40 |
| Elevated | 0.40–<0.65 |
| High | ≥ 0.65 |

The official ranking workflow will compare high/elevated pressure performance with ordinary-context baselines. Step 9 will test alternative thresholds and weights.

## Implementation and checks

src/rrselect/pressure.py contains the pure definition; scripts/apply_pressure_definition.py writes data/processed/pressure_labeled_deliveries.csv.

The v1 output contains 186,620 primary-scope deliveries. Its independent validation in work/pressure-definition-validation.json found zero band, range, target, or leakage-guard errors.
