# PAPRF Phase 2 pressure sensitivity

## Rules specified before running

The comparison uses the exact same delivery rows, eligibility thresholds, attribution, three signed metrics and 60-opportunity shrinkage as Lens A v1. Its purpose is to isolate pressure-label effects. All cutoffs below are exploratory modelling choices. They carry no claim of calibrated probabilities or proven psychological pressure.

| Scenario | Rule for pressure classification |
|---|---|
| Reproduce v1 | Elevated or high in the stored band. |
| Batter early-collapse | v1 pressure, or first innings with fewer than 36 completed legal balls and at least three wickets already lost. The extra rule represents the loss of batting resources during the powerplay. |
| Bowler late defence | v1 pressure, or second innings with 6–24 balls remaining, at least two batting wickets in hand, and a required rate from 7 to 12 runs per over inclusive. The extra rule tests a challenging but reachable target range during the closing overs. |

The rules only promote ordinary events into the pooled pressure comparison. They assign no separate high label. For the bowler rule, use integer inequalities 7B ≤ 6R ≤ 12B, with R runs required and B balls remaining, so threshold comparisons avoid floating-point rounding. This proxy describes the scoreboard situation and cannot establish how close the teams’ win probabilities actually were. A pre-delivery win probability would need independently validated, time-separated training. The scenarios test different hypotheses, so compare each role only with its own reference.

Primary comparison outputs are newly flagged delivery events by match phase and competition family, eligibility changes, and top-10 overlaps. On v1 labels, test weights 50/25/25 for scoring rate plus the two complementary measures and 25/25/50 for dismissal or wicket rate. Compare each with equal weighting. These are stress tests, with no search for weights that favour specific players.

## Reproduction and calculation ledger

Run `python scripts/run_paprf_phase2.py` from the repository root. The script reads the [delivery attribution file](../../data/processed/metric_attribution_deliveries.csv) and joins match and competition metadata by ID for the exposure split. The [score ledger](../../outputs/tables/paprf_phase2_score_ledger.csv) contains each eligible player’s runs, balls, dots, dismissals or credited wickets, and match counts in each bucket. The [sensitivity JSON](../../work/paprf_phase2_sensitivity.json) records source hashes, peer statistics, weights, exposure counts and the exact candidate IDs in rank order.

For each role, metric and player, subtract the ordinary rate from the pressure rate. Rates divide each numerator by eligible opportunities. Economy multiplies runs conceded per legal ball by six. Round deltas to six decimals before standardising against eligible peers, as in v1. On each metric, compute the signed z-score as s × (delta − peer mean) / peer sample standard deviation. A zero standard deviation contributes zero. Batters use signs (+, −, −) for scoring, dot and dismissal rates. Bowlers use (−, +, +) for economy, dot and wicket rates.

    Raw score = sum(weight parts × signed z-scores) / sum(weight parts)
    Shrinkage factor = pressure opportunities / (pressure opportunities + 60)
    Ranking score = round(raw score × shrinkage factor, 6)
    Top-ten overlap = count of shared player IDs / 10

Both ordinary and pressure buckets require 60 opportunities and six distinct matches. The v1 replay retains the historical match-count and dismissal conventions, including counting an attributed player's recorded context appearance even on some rows that contribute no eligible opportunity. As a separate fairness check, Phase 2 should test counting only matches with an eligible opportunity. The script requires exact agreement with all 20 frozen top-ten rank and score pairs before writing the comparison outputs.

## Results

The batting rule promoted 636 IPL and 959 T20I first-innings powerplay events. The resulting 1,595 promotions are 100 × 1,595 / 186,620 = 0.854678% of all delivery rows. The bowling rule promoted 325 IPL and 259 T20I second-innings death-over events. Its 584 promotions are 100 × 584 / 186,620 = 0.312935%. These percentages use delivery events as their denominator. Player-rate denominators use attributed opportunities.

| Scenario | Eligible batters | Batters shared with v1 | Eligible bowlers | Bowlers shared with v1 |
|---|---:|---:|---:|---:|
| v1 replay, equal weights | 176 | 10/10 | 219 | 10/10 |
| Role-specific rule, equal weights | 178 | 9/10 | 219 | 9/10 |
| v1 labels, scoring or economy at 50% | 176 | 10/10 | 219 | 9/10 |
| v1 labels, dismissal or wicket rate at 50% | 176 | 8/10 | 219 | 8/10 |

Under the early-collapse scenario, Romario Shepherd entered the batting top ten and Gulbadin Naib left it. Under the late-defence scenario, Anshul Kamboj entered the bowling top ten and Mohit Sharma left it. These are scenario-specific movements from the ID-keyed results. Overlap measures membership. Players can change position even when overlap is ten out of ten.

This sensitivity analysis measures how assumptions affect the same historical sample. It does not establish which rule identifies pressure more accurately. The weight test changed more top-ten memberships than the tested exposure additions. Phase- and competition-matched baselines and match-level repeatability remain necessary before recommending a replacement model. Nationality, opposition strength and psychological pressure were not measured in this experiment.
