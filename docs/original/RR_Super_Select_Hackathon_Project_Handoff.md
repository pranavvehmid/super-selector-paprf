# RR Super Select Cricket Auction Hackathon --- Master Project Handoff

**Version:** 2.0 --- Round 1 strategy updated\
**Last updated:** 16 November 2026\
**Project:** RR Super Select Cricket Auction Hackathon --- Season 2\
**Current focus:** Round 1 --- Identify the Most Reliable Players Under
Pressure

> **Purpose:** This is the portable project memory and working plan.
> Upload it into a new ChatGPT conversation together with the original
> data pack if you want the assistant to continue the project with the
> same context.

------------------------------------------------------------------------

# 1. User's objective and collaboration preferences

The user is participating in the **RR Super Select Cricket Auction
Hackathon** and wants ChatGPT to act as a project and technical
co-pilot.

The user expects the assistant to: - Carefully understand every
briefing, rule, dataset, and update they provide. - Explain the
challenge and proposed approach clearly before implementation. -
Establish the correct sequence of work and explain why each step comes
before the next. - Keep official requirements separate from
interpretations, assumptions, and proposed methods. - Help design,
build, test, and document the solution in stages. - Maintain a portable
project handoff so a new chat can continue without losing context. -
Never invent dataset contents, player rankings, statistics, results, or
official rules. - Not begin implementation or execute the roadmap unless
the user explicitly asks. The current request is to document the
approach and its order only.

**Current instruction:** The user asked for a clear analysis of how to
solve Round 1, with the steps established in the correct order, and
specifically asked that this plan be added to this handoff document.
They do **not** want the assistant to start carrying out the steps now.

------------------------------------------------------------------------

# 2. Official Round 1 problem statement

The official PDF is named:

`Round 1 Problem Statement _ SupeRR Selector Season 2.docx.pdf`

Its core challenge is:

**Identify the Most Reliable Players Under Pressure.**

The official problem asks participants to build a data-driven system
that measures how batters and bowlers perform in high-pressure match
situations compared with their usual performance levels, and use that
system to identify and rank players who deliver most consistently when
it matters.

## 2.1 What counts as pressure?

The official problem statement leaves the definition to the participant.
It says pressure might depend on: - Required run rate - Wickets in
hand - Balls remaining - Stage of an innings - How close the contest
is - A combination of factors - Other relevant match-context signals

The chosen definition must be explained, must distinguish pressure
situations from ordinary ones, and must work for both batting and
bowling.

## 2.2 Dataset described in the official PDF

The official PDF describes historical **IPL and T20 International
(T20I)** data from 2022 onwards, including: - Ball-by-ball
delivery-level records - Competitions - Teams - Players - Matches -
Playing XIs - Competition-team-player mappings

## 2.3 Required submission components

There are two required components:

### A. Player rankings on Unstop

-   One ordered top-10 list of batters, Rank 1 through Rank 10.
-   One ordered top-10 list of bowlers, Rank 1 through Rank 10.
-   Rank 1 must be the highest-rated player in the relevant category.
-   No repeated player within the same top-10 list.
-   The Unstop dropdown selections must match the rankings explained in
    the report.

### B. Methodology report

The report must explain: 1. **Pressure definition:** Match situations
and indicators used, and why they are meaningful. 2. **Performance
measurement:** Batting and bowling metrics, player baselines, and
rating/scoring logic. 3. **Fair comparisons:** Sample sizes, player
eligibility, different match contexts, and use of IPL and T20I data. 4.
**Evidence for top 10:** Results, comparisons, tables, or charts
supporting the selections and ordering. 5. **Reliability and
limitations:** How consistency across matches was checked and where the
model is less certain.

The methodology must be transparent enough for another person to
understand and reproduce. Rankings must be supported by the supplied
data, not reputation alone.

### Optional

A few photographs, screenshots, or a 30--60 second video describing the
approach and an interesting insight. The official PDF says this is
optional and does not affect evaluation.

### Additional context from the initial event briefing supplied by the user

The initial event briefing also asks the participant to explain how each
recommended player could strengthen the Rajasthan Royals squad. Treat
this as a useful squad-fit explanation to include where possible, while
keeping the two formal PDF requirements --- ranked lists and methodology
report --- central. Any squad-fit context should not override the
data-derived rankings.

------------------------------------------------------------------------

# 3. Original data pack: files received and inspected

The user supplied the ZIP:

`6af458274c1e8_data_pack.zip`

The extracted directory contains the following six CSV files and the
official problem statement PDF:

  --------------------------------------------------------------------------------------------------
  File                                                    Rows              Columns Intended role in
                                                                                    analysis
  --------------------------------------- -------------------- -------------------- ----------------
  `ball_by_ball.csv`                                   200,999                   33 Delivery-level
                                                                                    batting,
                                                                                    bowling, and
                                                                                    match-state
                                                                                    reconstruction

  `matches.csv`                                            883                   22 Match date,
                                                                                    teams, stage,
                                                                                    result, venue,
                                                                                    toss, revised
                                                                                    target, knockout
                                                                                    indicator

  `competitions.csv`                                       141                    4 Competition
                                                                                    name, format,
                                                                                    and season

  `teams.csv`                                              353                    3 Team identifiers
                                                                                    and names within
                                                                                    competitions

  `playing_eleven.csv`                                  28,381                    9 Match
                                                                                    participation,
                                                                                    batting order,
                                                                                    captain,
                                                                                    wicketkeeper,
                                                                                    impact-player
                                                                                    flags

  `competition_team_player_mapping.csv`                  6,413                    6 Player
                                                                                    identifiers and
                                                                                    names associated
                                                                                    with
                                                                                    competitions and
                                                                                    teams

  Official PDF                                         2 pages                  --- Round 1
                                                                                    requirements and
                                                                                    deliverables
  --------------------------------------------------------------------------------------------------

## 3.1 Verified high-level dataset facts

These were checked from the supplied files: - `ball_by_ball.csv` has
200,999 rows and 33 columns. - Ball-by-ball records cover 867 distinct
match IDs. - `matches.csv` has 883 rows. - The 16 matches in
`matches.csv` with no ball-by-ball rows are all marked **Match
Abandoned**. - `competitions.csv` has 141 records: 134 marked T20I and 7
marked T20. - The seven T20 competition records comprise IPL seasons
2022, 2023, 2024, 2025, and 2026, plus Men's T20 Emerging Teams Asia Cup
2024 and Asia Cup Rising Stars 2025. - The ball-by-ball records join to
397 T20 matches and 470 T20I matches (867 total). - The
competition-team-player mapping contains 6,413 rows and 1,217 distinct
player IDs. - `playing_eleven.csv` contains 28,381 rows, 880 distinct
match IDs, and 1,082 distinct player IDs. - Match dates range from 22
January 2022 to 1 November 2026. - The ball-by-ball timestamp range is
23 January 2022 to 1 November 2026. - No exact duplicate rows were found
in the six CSV files during the initial audit. - All ball-by-ball match
IDs matched a match record; all match competition IDs matched
`competitions.csv`; all competition IDs in the player mapping matched
`competitions.csv`.

These are structural facts, not player-performance findings.

## 3.2 Important data fields

### `ball_by_ball.csv` --- 33 columns

`match_id`, `innings`, `overid`, `over_ball_num`, `innings_ball_num`,
`batting_team_id`, `bowling_team_id`, `striker_id`, `striker_name`,
`non_striker_id`, `non_striker_name`, `bowler_id`, `bowler_name`,
`batting_type`, `bowling_type`, `batting_order`, `runs`, `is_four`,
`is_six`, `is_wicket`, `dismissal_type_id`, `dismissal_type`,
`dismissed_player_id`, `extras_type`, `extras1_runs`, `extras_2_runs`,
`pace_or_spin`, `bowl_speed`, `stroke`, `delivery_style`,
`over_or_around`, `on_or_off`, `delivery_ist_time`.

### `matches.csv` --- 22 columns

`match_id`, `comp_id`, `match_number`, `match_date`, `stage`,
`venue_id`, `venue_country`, `home_team_id`, `home_team`,
`away_team_id`, `away_team`, `home_team_captain_id`,
`away_team_captain_id`, `toss_win_team_id`, `toss_opted`,
`man_of_the_match`, `first_inn_revised_overs`,
`second_inn_revised_overs`, `revised_target`, `knock_out`,
`win_team_id`, `result`.

### `competitions.csv` --- 4 columns

`comp_id`, `comp_name`, `match_format`, `season`.

### `playing_eleven.csv` --- 9 columns

`match_id`, `team_id`, `player_id`, `batting_order`, `is_played`,
`is_captain`, `is_wk`, `is_impact`, `is_impact_off`.

### `competition_team_player_mapping.csv` --- 6 columns

`comp_id`, `comp_name`, `team_id`, `team_name`, `player_id`,
`player_name`.

### `teams.csv` --- 3 columns

`comp_id`, `team_id`, `team_name`.

## 3.3 Data caveats already visible

-   The ball-by-ball file has missing dismissal fields on most
    non-wicket deliveries; this is expected structurally, but dismissal
    coding must be interpreted carefully.
-   `extras_type` is missing on most deliveries and has observed values
    including `wide`, `legbyes`, `Overstep`, `byes`, `other`, and
    `Penalty`.
-   `runs`, `extras1_runs`, and `extras_2_runs` are separate fields.
    Their precise meanings and how to calculate total runs, batter runs,
    bowler-conceded runs, and legal balls must be validated before
    metric construction.
-   There is no single explicit `is_legal_delivery` field in the
    supplied ball-by-ball header. Legal-ball treatment must be derived
    carefully from extras/delivery rules and validated.
-   `over_ball_num` has values beyond six in some overs. Do not assume
    it is a legal-ball count.
-   Match-level revised-overs and revised-target fields are mostly
    blank. Their use must be conditional; missing values do not
    automatically mean a standard match if the match record is
    incomplete.
-   Match innings include innings 1 and 2 predominantly, plus a small
    number of innings 3 and 4 records. These should be investigated and
    treated consistently rather than silently discarded.
-   `playing_eleven.csv` has missing batting-order/captain/wicketkeeper
    fields for some rows. The participation and impact-player flags need
    interpretation.
-   The player mapping is competition/team-specific. A stable player ID
    should be used for joins; names alone should not be treated as
    unique identifiers.
-   The dataset includes IPL and T20I as described in the brief, but it
    also contains two non-IPL T20 competitions. Their inclusion or
    exclusion from the primary rankings must be an explicit scope
    decision, not an accidental consequence of filtering on
    `match_format == T20`.

------------------------------------------------------------------------

# 4. Recommended solution strategy --- ordered roadmap

**This section is the main Round 1 plan requested by the user. It is a
proposed sequence, not a record of completed analysis. Do not start
executing these steps unless the user asks.**

The order matters: we must first understand and validate the source
data, then reconstruct match situations, then define pressure, then
measure player performance, then build and test ratings, and only after
that produce rankings and the report.

## Step 1 --- Lock the challenge scope and submission rules

**Goal:** Translate the official challenge into a precise analysis
target before touching player rankings.

Actions to plan: 1. Treat the two required outputs as fixed: top-10
batters, top-10 bowlers, and a reproducible methodology report. 2. Keep
batting and bowling as separate ranking problems. 3. Use the official
requirement to compare performance under pressure with each player's
usual performance level. 4. Record the requirement that the pressure
definition must work for both batting and bowling. 5. Resolve dataset
scope: the PDF names IPL and T20I data, while the supplied competition
table also contains two non-IPL T20 competitions. Decide whether the
primary analysis uses only IPL + T20I, and whether the other T20
competitions are excluded or used only in a separately labelled
sensitivity analysis. 6. Record any further Unstop eligibility or
submission rules if the user supplies them.

**Output of this step:** A one-page scope specification with required
deliverables, included competitions, excluded competitions, and
definitions still to be decided.

**Decision gate:** Do not proceed to player scoring until the scope is
explicit.

## Step 2 --- Build the data dictionary and relationship map

**Goal:** Understand what every relevant field means and how the files
connect.

Actions to plan: 1. Document every column in each file, its likely
meaning, data type, and whether it is a key, identifier, context
variable, or outcome. 2. Confirm join paths: - `ball_by_ball.match_id` →
`matches.match_id` - `matches.comp_id` → `competitions.comp_id` -
`playing_eleven.match_id` → `matches.match_id` -
`playing_eleven.player_id` and team/match context → player mapping -
`competition_team_player_mapping` links competition, team, and player
IDs/names - `teams` supplies team names within competitions. 3. Use IDs,
not names, as primary join keys. 4. Identify whether player IDs are
globally stable across competitions and check for any ID/name
inconsistencies. 5. Create a field-level data dictionary, including
explicit notes where the source does not define a field's semantics.

**Output of this step:** Data dictionary, entity/relationship diagram,
and join specification.

**Decision gate:** Every field used in the model must have a clear
interpretation and traceable source.

## Step 3 --- Complete the data-quality and coverage audit

**Goal:** Establish what data is reliable enough to use and identify
exclusions.

Actions to plan: 1. Check missing values, duplicates, impossible values,
and inconsistent IDs. 2. Check match coverage across the ball-by-ball,
match, competition, and playing-XI files. 3. Identify abandoned,
shortened, tied, super-over, incomplete, and multi-innings matches. 4.
Review revised overs and revised targets, and identify matches needing
special handling. 5. Validate chronology and ball ordering within each
match and innings. 6. Investigate player mapping consistency, aliases,
and players with incomplete metadata. 7. Determine which records are
suitable for performance analysis and document exclusion reasons.

**Output of this step:** Data-quality report and a reproducible
inclusion/exclusion policy.

**Decision gate:** Do not calculate performance scores from records
whose delivery, player, or match context cannot be interpreted reliably.

## Step 4 --- Reconstruct each innings and the pre-delivery match state

**Goal:** Turn delivery records into a trustworthy timeline of what the
match situation was before each ball.

Actions to plan: 1. Order deliveries within each match and innings using
the available innings-ball/over/ball fields and timestamps where useful.
2. Validate whether `runs` represents batter runs and how the two extras
fields combine into team total runs. 3. Derive legal balls and balls
remaining. Do not assume `over_ball_num` alone identifies legal
deliveries. 4. Derive cumulative innings score and wickets lost before
each delivery. 5. Reconstruct striker, non-striker, bowler, batting
team, and bowling team context. 6. For second innings, derive the target
and runs required from the first innings total, while correctly handling
revised targets and shortened matches where the data supports it. 7.
Calculate runs required, balls remaining, required run rate, wickets in
hand, current run rate, and other pre-delivery context features. 8.
Cross-check reconstructed innings totals and wickets against match
records or other available evidence. 9. Treat first-innings and
second-innings states separately because the first innings does not have
a known chase target.

**Output of this step:** A validated ball-level analytical table where
every delivery has a reconstructed *pre-delivery* match state.

**Decision gate:** No pressure label should be created until the innings
state and legal-ball logic have passed validation.

## Step 5 --- Define pressure transparently and separately for batting and bowling

**Goal:** Create a meaningful, reproducible definition of pressure using
only information available before the delivery being evaluated.

The official brief leaves pressure open to the participant. The
following is a proposed framework to test, not a final formula.

### Second-innings pressure candidates

-   Required run rate and how it compares with a suitable scoring
    expectation.
-   Balls remaining.
-   Wickets in hand.
-   Runs required and the closeness of the chase.
-   Innings phase.
-   Whether the match is a knockout/final, if that context is judged
    relevant and consistently available.

### First-innings pressure candidates

There is no chase target, so required run rate is not available in the
same way. Potential indicators: - Balls/overs remaining. - Wickets in
hand. - Current scoring rate compared with an appropriate first-innings
scoring expectation for that competition/season/phase. - Innings phase
and resource constraints.

### Batting and bowling perspectives

-   A batting pressure label should describe the difficulty faced by the
    batting side/player.
-   A bowling pressure label should describe the pressure context in
    which the bowler is required to prevent scoring or take wickets. It
    can use the opponent's batting situation, but the bowler's
    performance outcomes must be measured separately.
-   A common match-state index may be useful, but batting and bowling
    ratings should not be forced into the same metric formula.

### Important safeguards

1.  Use only pre-delivery context to define pressure; do not use the
    outcome of the ball being rated.
2.  Avoid using final match result or future information as an input to
    the pressure score.
3.  Define ordinary/non-pressure situations as a meaningful comparison
    group.
4.  Test both a continuous pressure index and understandable bands (for
    example, ordinary, elevated, high), if justified by the data.
5.  Explain why each indicator is included and how weights/thresholds
    are selected.
6.  Test whether the results change materially when reasonable
    thresholds or weights change.
7.  Do not assume knockout status alone means every ball is high
    pressure.

**Output of this step:** A written pressure definition, formula/logic,
pressure bands, and rationale for both innings contexts and both player
disciplines.

**Decision gate:** The pressure definition must be interpretable,
available from the data, and not leak future outcomes.

## Step 6 --- Define role-appropriate batting and bowling performance metrics

**Goal:** Measure what the player actually delivered in the pressure and
comparison situations.

### Batter metrics to evaluate

Possible metrics, subject to field validation: - Runs scored per ball
faced / strike rate. - Boundary frequency or boundary-run
contribution. - Dot-ball rate. - Dismissal rate or survival. -
Contribution relative to the team's innings context. - Consistency of
these measures across separate matches.

### Bowler metrics to evaluate

Possible metrics, subject to field validation: - Runs conceded per legal
ball / economy rate. - Dot-ball rate. - Boundary concession rate. -
Wicket-taking rate. - Wickets credited to the bowler, excluding
dismissals not credited to the bowler. - Consistency across separate
matches.

### Accounting rules that must be resolved

-   Distinguish batter runs from total team runs.
-   Determine which extras count against the bowler and which do not.
-   Determine which dismissal types count as bowler wickets.
-   Use legal deliveries for economy and balls-per-over calculations.
-   Attribute batting outcomes to the striker and dismissals to the
    dismissed player, not automatically to the striker.
-   Avoid treating every delivery as an independent player performance
    observation.

**Output of this step:** A documented metric specification for batters
and bowlers, with numerator, denominator, attribution rule, and
interpretation for each metric.

**Decision gate:** Every metric must be calculated from correctly
attributed runs, balls, wickets, and extras.

## Step 7 --- Establish each player's normal-performance baseline

**Goal:** Answer the central question in the brief: how does the player
perform under pressure compared with their usual level?

Actions to plan: 1. Calculate each player's baseline performance in
ordinary/non-pressure situations. 2. Calculate their performance in
elevated/high-pressure situations. 3. Compare pressure performance with
that player's own baseline, not only with other players' raw totals. 4.
Use role-appropriate metrics and consider batting position, innings
phase, competition, and season where the data supports adjustment. 5.
Avoid comparing a batter's pressure strike rate at the death directly
with their baseline opening strike rate without accounting for
role/context. 6. Consider both absolute pressure performance and the
change from baseline. A player may be reliable because they maintain
their normal standard, even if their raw output is not the highest. 7.
Keep IPL and T20I context visible; assess whether format/competition
adjustment or separate comparisons are necessary.

**Output of this step:** Player-level baseline and pressure-performance
tables, with context definitions.

**Decision gate:** The comparison must be like-for-like enough to
support a fair interpretation.

## Step 8 --- Design a reliability rating with sample-size protection

**Goal:** Avoid rankings driven by small samples or a few exceptional
performances.

Actions to plan: 1. Define minimum eligibility requirements for pressure
opportunities, balls faced/bowled, and distinct matches. Set thresholds
after examining the distribution, and explain them. 2. Measure
consistency across matches, not just aggregate delivery totals. 3.
Quantify uncertainty around pressure-versus-baseline differences. 4.
Consider shrinkage/regularisation so players with small samples are not
rewarded for noisy extreme results. 5. Consider match-clustered
bootstrap confidence intervals or another defensible uncertainty method.
6. Combine performance under pressure, change from baseline, and
repeatability in a transparent rating. 7. Avoid an opaque arbitrary
weighted sum. If weights are used, justify them and test alternatives.
8. Publish both the score and its supporting components so the ranking
can be audited.

**Output of this step:** A documented role-specific rating formula,
eligibility rules, uncertainty estimates, and confidence indicators.

**Decision gate:** A player should not receive a high-confidence rank
merely because of a small number of pressure deliveries.

## Step 9 --- Validate the model and test ranking robustness

**Goal:** Check whether the rankings represent repeatable pressure
performance rather than an artefact of the chosen formula.

Actions to plan: 1. Check consistency across matches and seasons. 2.
Compare performance across IPL and T20I, while accounting for format and
competition differences. 3. Test alternative reasonable pressure
thresholds/weights. 4. Test whether rankings are dominated by one
competition, one season, one innings phase, or a small number of
matches. 5. Use season- or competition-based holdouts where feasible to
check whether the method generalises. 6. Review the top-ranked players
manually against their underlying match-level evidence, without
replacing data with reputation. 7. Identify players whose score is
strong but uncertainty is high. 8. Record limitations, missing contexts,
and possible biases.

**Output of this step:** Validation tables, sensitivity analysis,
confidence/uncertainty notes, and a finalised rating specification.

**Decision gate:** Final rankings should remain reasonably defensible
under sensible alternative assumptions.

## Step 10 --- Produce the two ranked top-10 lists

**Goal:** Generate the formal outputs required by Unstop.

Actions to plan: 1. Rank eligible batters using the final batter rating.
2. Rank eligible bowlers using the final bowler rating. 3. Check for
duplicate players within each list. 4. Verify player identity and exact
dropdown name using the player mapping. 5. Ensure Rank 1 is the
highest-rated player in each list. 6. Record each player's score, key
components, sample size, and uncertainty. 7. Freeze the ranking version
used in the report and Unstop submission.

**Output of this step:** Final top-10 batter and top-10 bowler lists
with evidence.

**Decision gate:** The report and Unstop dropdown selections must match
exactly.

## Step 11 --- Add Rajasthan Royals squad-fit context carefully

**Goal:** Explain why the data-derived picks could be useful to RR
without allowing subjective squad assumptions to distort the pressure
ranking.

Actions to plan: 1. Use relevant, current public information only where
needed to describe player role, experience, or potential squad fit. 2.
If discussing RR squad needs, verify the relevant roster and role
context for the IPL 2027 auction period from reliable public sources. 3.
Explain how each player could contribute in a cricketing role or
pressure situation. 4. Keep this as a separate interpretation layer from
the statistical reliability score. 5. Do not infer availability, auction
price, or likely purchase without evidence.

**Output of this step:** Concise, evidence-aware squad-fit notes for the
recommended players, if required by the event briefing.

## Step 12 --- Prepare the methodology report and submission materials

**Goal:** Turn the analysis into a transparent, judge-friendly
deliverable.

Suggested report structure: 1. Executive summary and final top-10 lists.
2. Challenge interpretation and scope. 3. Dataset overview and
data-quality treatment. 4. Pressure definition and rationale. 5.
Delivery-state reconstruction and feature engineering. 6. Batting and
bowling performance metrics. 7. Player baselines and
pressure-versus-normal comparisons. 8. Reliability rating, eligibility,
and uncertainty. 9. Validation and sensitivity analysis. 10. Evidence
and explanation for each top-10 selection. 11. RR squad-fit context,
where appropriate. 12. Limitations and conclusion.

Submission checks: - Produce the PDF/PPT/report/dashboard format
accepted by the event. - Confirm both top-10 lists are entered in Unstop
in the correct order. - Ensure the dropdown selections match the
report. - Include enough detail that another analyst can reproduce the
approach. - Optional 30--60 second video/screenshots can be prepared
only after the core analysis is complete.

**Output of this step:** Final report and matching Unstop rankings.

------------------------------------------------------------------------

# 5. Core modelling principles to preserve

1.  **Pressure is context, performance is outcome.** Do not mix them.
2.  **Use pre-delivery state.** The delivery's outcome must not
    influence the pressure label assigned to that same delivery.
3.  **Compare players with themselves as well as with peers.** The
    challenge explicitly asks for pressure performance relative to usual
    performance.
4.  **Batters and bowlers need separate ratings.** Their performance
    metrics and attribution rules differ.
5.  **Account for opportunity.** Use balls faced/bowled and match
    counts; raw totals are not enough.
6.  **Account for context.** Competition, format, season, batting
    position, innings phase, and match conditions may affect fair
    comparison.
7.  **Protect against small samples.** Use eligibility rules and
    uncertainty estimates.
8.  **Avoid leakage.** Do not use final result or future match
    information to define pre-delivery pressure.
9.  **Make the model reproducible.** Every formula, threshold, join,
    exclusion, and assumption must be documented.
10. **Keep rankings data-led.** Reputation or subjective preference
    cannot replace evidence from the supplied data.

------------------------------------------------------------------------

# 6. Current project status

## Completed

-   User supplied the initial Round 1 event briefing.
-   User supplied the official problem statement PDF.
-   User supplied the original ZIP data pack.
-   The ZIP was extracted and all six CSV files were opened for an
    initial structural audit.
-   The official PDF was read.
-   The ordered Round 1 solution roadmap has now been documented in this
    handoff.

## Not yet performed

-   Full column-by-column data dictionary.
-   Detailed data-quality resolution and final inclusion/exclusion
    policy.
-   Innings-state reconstruction.
-   Legal-delivery and extras accounting validation.
-   Pressure-index definition and thresholds.
-   Batting/bowling metric construction.
-   Player baselines and pressure comparisons.
-   Reliability score, uncertainty estimation, and validation.
-   Player rankings.
-   RR squad-fit research.
-   Final report or dashboard.

**Important:** The user explicitly asked not to begin carrying out the
roadmap yet. The next assistant should not start coding, calculating
player scores, constructing pressure labels, or ranking players unless
the user gives that instruction.

------------------------------------------------------------------------

# 7. New-chat continuation prompt

Paste this with the handoff file in a new conversation:

"Read this RR Super Select Cricket Auction Hackathon handoff carefully.
It contains the official Round 1 requirements, verified data-pack
inventory, dataset caveats, and the ordered strategy for solving the
challenge. The current task was to document the plan only. Do not start
implementing the steps, analysing player performance, or generating
rankings yet. First confirm that you understand the plan and that you
will wait for my instruction before beginning the first step."
