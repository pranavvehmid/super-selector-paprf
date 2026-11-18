# Step 3 Data-Quality and Coverage Audit

**Audit source:** scripts/audit_data_quality.py  
**Machine-readable result:** work/data-quality-audit.json  
**Run date:** 18 November 2026

## Structural result

All six CSV files have zero exact duplicate rows. The audit confirms 200,999 delivery rows, 883 match rows, 141 competition rows, 353 team rows, 28,381 playing-XI rows, and 6,413 competition-team-player mapping rows.

All ball-by-ball and playing-XI match IDs are present in matches.csv; all match competition IDs are present in competitions.csv. No player ID has multiple display names within the mapping, striker, non-striker, or bowler fields.

## Coverage and ordering

- Ball-by-ball data covers 867 matches; matches.csv covers 883; playing-XI data covers 880.
- The 16 matches with no delivery rows are all labelled Match Abandoned.
- Delivery records cover 105,727 first-innings rows, 95,234 second-innings rows, 25 third-innings rows, and 13 fourth-innings rows.
- innings_ball_num is populated as an integer on every delivery. There are no duplicate (match_id, innings, innings_ball_num) coordinates and no regressions in raw-file order. This supports its use as a candidate ordering field, but does not establish legal-ball semantics.

## Special-match flags

The audit flags 40 matches labelled Match Abandoned or No Result, 34 matches with at least one revised-overs or revised-target field populated, and 6 matches containing innings 3 or 4 (34429, 40725, 45512, 48027, 48029, 50359). The union contains 70 matches.

## Provisional inclusion and exclusion policy

For the primary statistical population, retain only the 813 ball-by-ball matches not in the 70-match special-condition union. Hold out the following categories until Step 4 validates state reconstruction and any required special-match handling:

1. Matches labelled Match Abandoned or No Result.
2. Matches with populated revised-overs or revised-target fields.
3. Matches containing innings 3 or 4.

This is an evidence-preserving holdout, not a judgement that those records are erroneous. Re-admit a category only through a documented, validated Step 4 rule. The policy does not validate runs, extras, legal balls, dismissals, or targets; those remain Step 4 requirements.

## Step 3 gate decision

**Gate passed on 18 November 2026.** The audit creates a reproducible inclusion/exclusion policy and prevents special-condition records from entering future scoring before their context can be reconstructed reliably. No player scoring or ranking has been performed.
