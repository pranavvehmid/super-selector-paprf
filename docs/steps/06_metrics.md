# Step 06 — Define role-appropriate batting and bowling metrics

**Status:** NOT STARTED  
**Code:** `src/rrselect/metrics.py`

## Goal
Measure what each player actually delivered.

## Tasks
- [ ] Batter metrics (to validate): runs/ball, strike rate, boundary frequency, dot-ball rate, dismissal rate/survival, contribution relative to innings context, across-match consistency.
- [ ] Bowler metrics (to validate): economy per legal ball, dot-ball rate, boundary-concession rate, wicket rate (bowler-credited dismissals only), across-match consistency.
- [ ] Resolve: batter vs team runs; which extras count against the bowler; which dismissals are bowler wickets; legal balls for economy; dismissals attributed to dismissed player (not automatically the striker).

## Output of this step
Metric specification: numerator, denominator, attribution rule, interpretation for each metric.

## Decision gate
Every metric computed from correctly attributed runs, balls, wickets and extras.

## Log of work on this step
_(append dated notes here and in PROJECT_LOG.md)_
