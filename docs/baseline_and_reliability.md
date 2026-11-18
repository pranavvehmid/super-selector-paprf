# Steps 7–8: Baselines and Reliability Protection

## Step 7 — Why player baselines are necessary

Raw pressure performance alone is not a fair ranking. A player who scores quickly in all contexts should not automatically look better under pressure than a player whose normal scoring level is lower but who improves materially when pressure rises.

Each player is therefore compared with themselves:

- **Ordinary context:** pressure index below 0.40.
- **Pressure context:** elevated or high pressure, meaning pressure index at least 0.40.

The comparison is role-specific:

| Role | Pressure-versus-ordinary measures |
|---|---|
| Batter | Runs per ball, dot-ball rate, dismissal rate. |
| Bowler | Economy, dot-ball rate, bowler-credited wicket rate. |

Positive batter evidence means a higher runs-per-ball delta, a lower dot-ball-rate delta, and a lower dismissal-rate delta. Positive bowler evidence means a lower economy delta, a higher dot-ball-rate delta, and a higher wicket-rate delta.

## Eligibility

A player needs at least 60 opportunities and six distinct matches in both ordinary and pressure contexts:

- Batter opportunity: ball faced.
- Bowler opportunity: legal ball bowled.

This retains 176 batters from 880 and 219 bowlers from 639 in the baseline files. The threshold was selected after checking the available population: it preserves broad pools while removing players whose apparent pressure signal rests on a handful of balls.

## Step 8 — Reliability protection

For each eligible role pool, the three pressure-versus-ordinary deltas are standardised within that role. They receive equal weight because the project has no supplied evidence that would justify privileging one measure.

The raw composite is then shrunk toward the eligible-peer average of zero:

shrunken signal = raw signal × pressure opportunities / (pressure opportunities + 60)

The 60-ball prior is deliberately visible and will be varied in Step 9. It means that:

- a player with 60 pressure opportunities keeps half of their raw signal;
- a player with 180 keeps 75 percent;
- a player with a much larger sample remains close to their observed performance.

This directly addresses the main ranking risk: an extreme rate over a tiny pressure sample should not outrank sustained evidence.

## Outputs

- outputs/tables/batter_pressure_baselines.csv
- outputs/tables/bowler_pressure_baselines.csv
- outputs/tables/batter_reliability_signals.csv
- outputs/tables/bowler_reliability_signals.csv
- outputs/figures/batter_reliability_diagnostic.png
- outputs/figures/bowler_reliability_diagnostic.png

The diagnostic charts show both the raw and shrunk signal against pressure opportunities. They are explanatory evidence, not final ranking charts.
