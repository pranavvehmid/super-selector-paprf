# RR Super Select Cricket Auction Hackathon — Season 2

**Round 1 challenge:** Identify the Most Reliable Players Under Pressure (IPL + T20I data, 2022 onwards).

**Required deliverables:** (A) ordered top-10 batters and top-10 bowlers on Unstop; (B) a reproducible methodology report.

## PAPRF Round 1 dashboard

Open [the dashboard](dashboard/index.html) from a local checkout to explore pressure exposure, player calculations, ranking sensitivity and the research milestones. The [research review PDF draft](outputs/report/paprf_research_review_v3.pdf) summarises model versions through v3. See the [dashboard setup and publishing guide](dashboard/README.md) and the [current four-phase research plan](docs/methodology/paprf_four_phase_plan.md).

> **Taking over this project (human or model)?** Read in this order:
> 1. `AGENTS.md` — working rules and the mandatory log-update protocol
> 2. `PROJECT_LOG.md` — what has been done, newest entry last, plus the current "Next action"
> 3. `docs/steps/README.md` — the 12-step roadmap and status of each step
> 4. `docs/decisions.md` and `docs/assumptions.md` — what is decided vs. assumed
> 5. `docs/original/` — the original handoff (v2.0, 16 Nov 2026)

## Analysis design: exactly three workstreams

| Workstream | Purpose | Boundary |
|---|---|---|
| 1. **Data-led top-10 shortlist** | Produce the official pressure-performance rankings and demonstrate statistical reasoning, validation, and game understanding. | The only source of the official batter and bowler ranks; uses supplied historical data only. |
| 2. **Current RR squad-building needs** | Assess current squad coverage, retentions, remaining auction pool, and prior-season gaps from user-supplied current-context inputs. | A contextual needs assessment; never changes Workstream 1 scores or ranks. |
| 3. **RR-specific player fit** | Recommend realistic RR-fit options using playing style, development trajectory, availability scenarios, and Workstream 2 needs. | A labelled recommendation layer; never changes Workstream 1 scores or ranks. |

The previous Lens A (transparent pressure-versus-baseline rating) and Lens B (PLS, if confirmed) are alternative or complementary methods **within Workstream 1**. The previous Lens C is now split across Workstreams 2 and 3. See `docs/RR_Super_Select_Hackathon_Project_Handoff.md` for the current working plan.

## Repository layout

```
AGENTS.md            rules for any model/person continuing the work
PROJECT_LOG.md       living progress log (append-only)
docs/                steps, methodology, factors, decisions, assumptions, data dictionary
data/raw/            the original data pack (gitignored by default)
data/external/       user-supplied/verified spreadsheets (retention, auction pool, squad, hometowns, RR pick history)
data/interim|processed/  derived tables
src/rrselect/        Python module, one file per roadmap stage
scripts/             check_data_pack.py, log_progress.py, run_step.py
tests/               unit tests
outputs/             rankings, tables, figures, report
```

## Quick start

```bash
make setup                       # create venv + install requirements
# put the six CSVs from the data pack into data/raw/
make check                       # verifies the data pack is present and structurally as documented
make log STEP=1 MSG="what you did" FILES="paths"   # append to PROJECT_LOG.md
```

## Status
See `PROJECT_LOG.md` (current "Next action" is at the top) and `docs/steps/README.md`.
No player analysis has been run yet.
