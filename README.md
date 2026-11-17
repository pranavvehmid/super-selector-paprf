# RR Super Select Cricket Auction Hackathon — Season 2

**Round 1 challenge:** Identify the Most Reliable Players Under Pressure (IPL + T20I data, 2022 onwards).

**Required deliverables:** (A) ordered top-10 batters and top-10 bowlers on Unstop; (B) a reproducible methodology report.

> **Taking over this project (human or model)?** Read in this order:
> 1. `AGENTS.md` — working rules and the mandatory log-update protocol
> 2. `PROJECT_LOG.md` — what has been done, newest entry last, plus the current "Next action"
> 3. `docs/steps/README.md` — the 12-step roadmap and status of each step
> 4. `docs/decisions.md` and `docs/assumptions.md` — what is decided vs. assumed
> 5. `docs/original/` — the original handoff (v2.0, 16 Nov 2026)

## Analysis design: three lenses, kept separate

| Lens | Name | What it is | Where |
|---|---|---|---|
| A | **By the numbers** | Transparent statistical rating: pressure vs. own baseline, shrinkage, match-clustered uncertainty | `docs/methodology/lens_a_numbers.md`, `src/rrselect/ranking_numbers.py` |
| B | **PLS** | Partial Least Squares model (handles many correlated predictors) predicting out-of-sample pressure performance | `docs/methodology/lens_b_pls.md`, `src/rrselect/ranking_pls.py` |
| C | **Squad-context overlay** | Filters/annotates A and B with retention list, auction availability, current RR squad, RR pick history, hometown/heritage | `docs/factors/`, `src/rrselect/squadfit.py` |

The pressure-reliability rankings (A and B) come **only from the supplied data**. Lens C never changes the statistical scores; it is a labelled interpretation layer. Which list is entered on Unstop is an open decision (see `docs/decisions.md`, D-003).

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
