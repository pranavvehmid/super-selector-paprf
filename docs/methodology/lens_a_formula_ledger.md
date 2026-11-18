# Lens A v1 Formula and Calculation Ledger

**Purpose:** Exact equations, signs, populations and evidence locations behind the frozen Round 1 rankings.  
**Scope:** IPL and T20I only; 782 validated matches and 186,620 reconstructed deliveries.  
**Ranking version:** v1.

## Evidence provenance

| Item | Evidence file or implementation |
|---|---|
| Scope/exclusions | docs/data_quality_report.md; work/data-quality-audit.json |
| Pre-delivery state | scripts/reconstruct_state.py; work/state-reconstruction-validation.json |
| Pressure | src/rrselect/pressure.py; work/pressure-definition-validation.json |
| Attribution | src/rrselect/metrics.py; work/player-metrics-validation.json |
| Baselines | src/rrselect/baselines.py; work/baseline-validation.json |
| Reliability | src/rrselect/reliability.py; outputs/tables/*_reliability_signals.csv |
| Sensitivity | scripts/validate_robustness.py; work/robustness-validation.json |
| Frozen result | outputs/rankings/ranking_manifest_v1.json; work/ranking-validation.json |

## 1. Pre-delivery pressure

Let L be legal balls completed before the rated delivery, W wickets lost, R runs required, B legal balls remaining, and Clamp(x) = max(0, min(1, x)).

First innings:

    progress = Clamp(L / 120)
    wicket_stress = Clamp(W / 10)
    late_innings_stress = Clamp((L - 72) / 48)
    pressure_index = 0.70 × late_innings_stress + 0.30 × wicket_stress

Second innings:

    required_run_rate = 6 × R / max(B, 1)
    run_rate_stress = Clamp((required_run_rate - 7) / 5)
    progress = Clamp(L / 120)
    wicket_stress = Clamp(W / 10)
    pressure_index = 0.55 × run_rate_stress + 0.25 × wicket_stress + 0.20 × progress

    ordinary: index < 0.40
    elevated: 0.40 ≤ index < 0.65
    high: index ≥ 0.65

Official pressure opportunities are elevated plus high. The rated delivery's outcome does not enter its label.

## 2. Attribution and eligibility

Rows are excluded from player-rate metrics when extras_type is other or Penalty, when a None row has non-zero extras, or when a bye/leg-bye row has non-zero batter runs. That leaves 186,363 eligible deliveries and holds out 257 ambiguous rows.

    batter_runs = 0 for wide/byes/legbyes/other/Penalty; else source runs
    batter_ball_faced = eligible and extras_type ≠ wide
    bowler_runs = batter_runs + extras1_runs + extras_2_runs for wide or Overstep
    bowler_legal_ball = eligible and source legal-ball rule

Run outs, retire outs and obstructing-the-field dismissals are not bowler wickets. Batter dots are balls faced with zero batter runs; bowler dots are eligible legal balls with zero team runs.

## 3. Baseline deltas

Rate(x) = x / opportunities. Eligibility requires at least 60 ordinary opportunities, 60 pressure opportunities, six ordinary matches and six pressure matches.

    batter delta_RPB = pressure runs/balls − ordinary runs/balls
    batter delta_dot = pressure dots/balls − ordinary dots/balls
    batter delta_dismissal = pressure dismissals/balls − ordinary dismissals/balls

    bowler delta_economy = 6 × pressure conceded/legal balls − 6 × ordinary conceded/legal balls
    bowler delta_dot = pressure dots/legal balls − ordinary dots/legal balls
    bowler delta_wicket = pressure wickets/legal balls − ordinary wickets/legal balls

Better batting has positive RPB and negative dot/dismissal deltas. Better bowling has negative economy and positive dot/wicket deltas.

## 4. Standardisation, weighting and shrinkage

For delta j within an eligible role-specific peer population:

    z_j = (delta_j − mean(delta_j of eligible peers)) / sample_sd(delta_j of eligible peers)
    batter_raw = (z_RPB − z_dot − z_dismissal) / 3
    bowler_raw = (−z_economy + z_dot + z_wicket) / 3
    shrinkage_weight = pressure_opportunities / (pressure_opportunities + 60)
    reliability_signal = raw_signal × shrinkage_weight

The freeze script sorts the reliability_signal stored to six decimal places in the signal CSV. Equal stored scores preserve the input row order. Charts display two decimals. IDs are the identity key.

## 5. Sensitivity mathematics

For prior P in {30, 60, 90}:

    alternative_signal(P) = raw_signal × pressure_opportunities / (pressure_opportunities + P)

Top-10 overlap is the size of the intersection between the official P=60 top ten and each alternative top ten. A high-only test rebuilds eligibility, peer distributions and signals using high pressure only. Results: 10/10 batter overlap for each prior; bowler overlap is 9/10 at P=30 and 10/10 at P=60/90; high-only overlap is 7/10 batters and 5/10 bowlers.
