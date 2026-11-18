# RR Super Select Hackathon — Project Handoff

**Updated:** 18 November 2026  
**State:** Statistical ranking and methodology report complete; RR-context overlay pending external inputs.

## What has been completed

The project is now at a submission-ready analytical state for Lens A:

- Primary official population: IPL and T20I only.
- Validated state population: 782 matches and 186,620 deliveries.
- Metric population: 186,363 eligible player-attribution deliveries; 257 ambiguous events are retained in the audit trail but excluded from rates.
- Eligible comparison pools: 176 batters and 219 bowlers.
- Robustness: batter top 10 is unchanged at 30/60/90 shrinkage priors; bowler overlap is 9/10 at prior 30 and 10/10 at 60/90.
- Frozen outputs: outputs/rankings/lens_a_batters_v1.csv and outputs/rankings/lens_a_bowlers_v1.csv.
- Validators: work/ranking-validation.json reports zero errors.

## The working method

1. Reconstruct the state before every delivery.
2. Apply the documented v1 pressure label using no delivery outcome data.
3. Measure batters by runs per ball, dot rate and dismissal rate; measure bowlers by economy, dot rate and wicket rate.
4. Compare pressure performance with the player’s own ordinary baseline.
5. Standardise within role and shrink pressure signals by sample size using a 60-opportunity prior.
6. Test reasonable alternatives, then freeze v1.

## Important decisions to preserve

- Do not merge player-fit or RR squad preferences into the Lens A score.
- Do not restore excluded competition types to official rankings without rerunning the scope and quality gates.
- Do not convert the 257 ambiguous attribution events into batter or bowler rates without a verified codebook rule.
- Use IDs from the ranking CSV when resolving platform display labels.

## Outstanding work

The only open analytical workstream is RR squad/auction context. It needs dated, source-backed files for the current RR squad, retention status, auction pool, player availability and—if used—price. Until then, no factual recommendation about availability or fit should be made.

The only required submission operation is a manual Unstop entry check: enter the two versioned lists in rank order and match each dropdown label to the frozen player ID. See outputs/report/round1_methodology_report_v1.md for the complete explanation and limitations.
