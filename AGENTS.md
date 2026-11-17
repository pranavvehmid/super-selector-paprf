# AGENTS.md — rules for any assistant or person working on this repo

## 1. Mandatory log protocol
After **every** meaningful action (file created/changed, decision made, data received, analysis run, error found), append an entry to `PROJECT_LOG.md` **before ending your turn**, using:

```
python scripts/log_progress.py --step <1-12 or "setup"> --summary "<what and why>" --files "<comma-separated paths>" [--decision "<D-xxx: ...>"] [--next "<next action>"]
```

The script appends the entry and updates the "Next action" line at the top. If you cannot run it, edit `PROJECT_LOG.md` by hand in the same format. Also update the status table in `docs/steps/README.md` when a step changes state, and `docs/decisions.md` / `docs/assumptions.md` when you decide or assume something.

## 2. Hard rules
1. **Never invent** dataset contents, statistics, player rankings, results, rosters, retention lists, auction pools, hometowns or official rules. If it was not in the supplied data or a cited source, it does not go in.
2. **Official requirements vs. interpretations:** keep them separate. Official facts live in `docs/00_official_requirements.md`; everything else is labelled *assumption*, *interpretation* or *proposed method*.
3. **Order matters.** Do not start a step until the previous step's decision gate (see `docs/steps/`) is recorded as passed in the log.
4. **Pressure = pre-delivery context only.** No outcome of the ball being rated, no final match result, no future information may enter a pressure label (no leakage).
5. **Batting and bowling are rated separately.**
6. **Join on IDs, never names.**
7. **Lens C (squad context) never alters Lens A/B statistical scores.** It is a separate, labelled layer.
8. **External facts** (IPL 2027 retention list, auction pool, RR squad, hometowns, RR historical picks) must be stored in `data/external/` with `source` and `retrieved_on` columns. Prefer spreadsheets supplied by the user; otherwise cite reliable public sources and mark the date retrieved. Never infer availability, price or likelihood of purchase without evidence.
9. **Reproducibility:** every threshold, join, exclusion and weight is written down (code + doc). Seeds are fixed and recorded.
10. **The report and the Unstop dropdown selections must match exactly.** Freeze a ranking version before submission (Step 10).
11. Do not begin implementing a step unless the user has asked for it (check the latest log entries for instructions).

## 2. Where things live
See `README.md` for the layout and `docs/steps/README.md` for the roadmap.

## 3. User collaboration preferences (from the original handoff)
Explain the approach and ordering before implementing; explain why each step precedes the next; help build, test and document in stages; keep the handoff current.
