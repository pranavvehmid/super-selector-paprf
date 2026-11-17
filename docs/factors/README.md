# Lens C — Squad-context factors

Purpose: annotate and (optionally) filter the statistical top lists using what matters for an auction recommendation. **These factors never change Lens A/B scores.** How they are combined into a recommendation shortlist is decision D-004.

| Factor | Data file (data/external/) | What it answers | Source rule |
|---|---|---|---|
| IPL 2027 retention list | `ipl_retention_2027.csv` | Who is retained by their franchise (not available) | User spreadsheet or cited public source + retrieval date |
| Available players (auction pool) | `auction_pool_2027.csv` | Who can actually be bought | same |
| Current RR squad | `rr_current_squad.csv` | Who RR already has; role/overseas-slot gaps (many recent changes — always re-verify date) | same |
| RR past picking history | `rr_historical_picks.csv` | Patterns in who RR buys (role, age, price band, domestic team, region, overseas/Indian) | same |
| Hometown / heritage | `player_origin.csv` | Region/home-state links to the franchise's picking pattern | same |

## Method outline (Step 11)
1. Join each ranked player to retention / auction / squad flags by `player_id` (fallback: verified name match, logged).
2. Squad-strength gap analysis by role: openers, middle order, finishers, wicketkeeper, pace (powerplay/death), spin, overseas slots.
3. Pick-history profile: describe RR's past pattern from `rr_historical_picks.csv` only; report counts and caveats (small samples → descriptive, not predictive).
4. Hometown/heritage: report as a descriptive feature of RR's history; do not claim causation; flag small-sample risk.
5. Output a shortlist table per lens with columns: pressure rank, availability status, role-gap fit, history-fit note, evidence/source.

## Hard rules
- No invented rosters, prices, or availability. Every row needs `source_url` and `retrieved_on`.
- Retention and squads change quickly: record the retrieval date and re-check before submission.
