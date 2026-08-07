Internal progress notes for the EnergyForecasting series. Not part of the Jekyll collection output (no front matter, so it won't be picked up by `site.EnergyForecasting` or listed on the blog page).

## Done

- **Probabilistic Electricity Price Forecasting (PEPF)** — 3 parts, DK1 day-ahead prices, Energi Data Service data (2024-01-01 to 2025-09-30).
  - Part 1 (2026-07-01): theory — European/Danish market structure, quantiles, QR/QRF, evaluation metrics (pinball loss, CRPS, PIT histogram).
  - Part 2 (2026-08-02): QR and QRF implementation, walk-forward CV, feature set (production/consumption by source).
  - Part 3 (2026-08-03): bootstrapped-residual intervals on top of an XGBoost point forecast, in-sample vs out-of-sample residuals, binned residuals, multiple interval levels.

- **Stochastic Optimisation for Energy Storage** — 2 parts, feeds off PEPF's quantile forecasts.
  - Part 1 (2026-08-06): theory — deterministic vs stochastic optimisation, two-stage/multi-stage stochastic programs.
  - Part 2 (2026-08-06): two-stage battery dispatch model in Pyomo, scenarios built from QR quantiles (0.10/0.30/0.50/0.70/0.90) for a real DK1 test day (2025-07-10), compared against naive (median-only) and perfect-foresight baselines.

## Not done yet

- "ImBalance Forecasting" (Nordic imbalance price/volume forecasting) — mentioned as a possible next side project, not started. Don't reference it as existing work (CV, cover letters) until it actually exists.

## Possible next steps

- Extend PEPF/stochastic dispatch work toward imbalance/reserve markets — natural link to TSO reserve-sizing and cross-border coordination topics (e.g. DTU Nordic-Sec PhD applications).
- Multi-stage (not just two-stage) stochastic dispatch, or scenario reduction methods.
