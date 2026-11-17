# Lens B — PLS (Partial Least Squares)

**Status:** PROPOSED FRAMEWORK, based on assumption A-001 ("PLS" = Partial Least Squares). **Confirm with the user (D-002).** Nothing computed yet.

## Why PLS
Player performance features (baseline metrics, phase splits, pressure-band metrics, role, competition mix) are numerous and highly correlated. PLS regression extracts a few latent components that maximise covariance with a target, giving stable estimates where ordinary regression is unstable, and gives interpretable loadings/VIP scores.

## Proposed design
- **Unit of observation:** player × time block (e.g., season, or a rolling window of matches), batters and bowlers modelled separately.
- **Response (Y):** pressure-situation performance in a **later** block (e.g., standardised pressure runs/ball and dismissal rate for batters; economy, dot-ball and wicket rate for bowlers).
- **Predictors (X):** features from **earlier** blocks only — baseline metrics, phase-wise metrics, past pressure metrics, role/position, competition mix, sample sizes.
- **Model:** `sklearn.cross_decomposition.PLSRegression`; number of components chosen by cross-validation grouped by match/season (no leakage across time).
- **Ranking score:** predicted pressure performance for the player's latest data (shrunk by construction) and/or the player's latent-component score; reliability proxy = out-of-sample predictive stability.
- **Interpretability outputs:** loadings, VIP scores, cross-validated R²/Q², rank agreement with Lens A (Spearman).

## Risks to document
Few seasons (2022–2026) means limited training blocks; small pressure samples inflate noise; features must not contain future information.

## Outputs
`outputs/rankings/lens_b_batters.csv`, `outputs/rankings/lens_b_bowlers.csv`.

## Code
`src/rrselect/ranking_pls.py`
