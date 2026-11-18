# Step 6 Metric Specification

**Status:** GATE PASSED  
**Population:** 186,363 metric-eligible deliveries from the 782 validated primary-scope matches.

## Why attribution is separated from pressure

Pressure answers the question “how difficult was the situation before this ball?” Attribution answers “what did the player actually produce on this ball?” Keeping them separate prevents outcome assumptions from leaking into the pressure label and keeps batting and bowling comparable only within their own roles.

## Delivery eligibility

The analysis keeps a delivery in player-rate calculations unless its attribution is ambiguous:

- The source labels other or Penalty extras are excluded because the supplied data has no provider definition for their player attribution.
- A None extras label with a non-zero extras field is excluded as a source inconsistency.
- A bye or leg-bye label with non-zero batter runs is excluded as a source inconsistency.

This holds out 257 of 186,620 reconstructed deliveries. They remain in the state and pressure audit trail; they are not silently discarded from the source.

## Batter metrics

| Metric | Numerator | Denominator | Rule and interpretation |
|---|---:|---:|---|
| Runs | Source runs on bat-attributed events | — | Credited to the striker. Byes, leg-byes, wides, other, and penalties contribute zero batter runs. |
| Balls faced | Eligible delivery not labelled wide | — | Wides are excluded; Overstep/no-ball-labelled deliveries are included as a batter opportunity. |
| Runs per ball | Batter runs | Balls faced | Main scoring-rate measure. |
| Dot-ball rate | Eligible balls faced with zero batter runs | Balls faced | Measures unproductive batting opportunities. |
| Boundary frequency | Batter-run events equal to 4 or 6 | Balls faced | Uses the validated runs field, not is_four or is_six, because those flags disagree on 22 records. |
| Dismissal rate | Source dismissal rows joined through dismissed_player_id | Balls faced | Dismissals belong to the dismissed player, not automatically the striker. One unmatched Retire Out record is not assigned. |

## Bowler metrics

| Metric | Numerator | Denominator | Rule and interpretation |
|---|---:|---:|---|
| Runs conceded | Batter runs plus extras for wide and Overstep | — | Byes and leg-byes do not count against the bowler. |
| Legal balls | Eligible deliveries not labelled wide, Overstep, or other | — | Validated during Step 4 from completed-over structure. |
| Economy | Runs conceded × 6 | Legal balls | Runs allowed per six legal balls. |
| Dot-ball rate | Legal deliveries with zero team runs | Legal balls | Measures delivery-level restriction. |
| Wicket rate | Bowler-credited wickets | Legal balls | Excludes RunOut, Retire Out, and both recorded spellings of obstructing the field. |

## Rule sources and limitations

MCC Laws and ICC Playing Conditions state that bowler debits include batter runs, no-ball extras, and wides, while byes and leg-byes are not bowler debits. Run-outs are not credited to the bowler. The implementation applies those rules to the dataset labels wide and Overstep; other and penalty-labelled rows remain excluded because the provider did not supply a codebook.

Source references:

- MCC Laws of Cricket, Laws 18, 21, 22 and 23: https://www.lords.org/getattachment/e8b12929-1e84-4927-af4e-2a5875b53589/Laws-of-Cricket-2017-Code-4th-Edition-%282026%29.pdf
- ICC scoring-runs playing condition: https://images.icc-cricket.com/image/upload/prd/lm8owaz03i86m1eneb7m.pdf
- ICC Run Out playing condition: https://www.icc-cricket.com/news/mens-test-match-clause-38-run-out

## Outputs and validation

- data/processed/metric_attribution_deliveries.csv preserves every delivery and its attribution flags.
- outputs/tables/batter_context_metrics.csv contains player-by-pressure-band batting counts.
- outputs/tables/bowler_context_metrics.csv contains player-by-pressure-band bowling counts.
- work/player-metrics-validation.json independently recomputes every aggregate and reports zero errors.
