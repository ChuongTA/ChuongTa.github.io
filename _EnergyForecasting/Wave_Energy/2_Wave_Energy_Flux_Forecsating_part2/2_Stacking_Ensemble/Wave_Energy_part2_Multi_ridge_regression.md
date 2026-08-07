---
title: "Ocean Wave Energy Flux Forecasting: A Stacking Ensemble (Part 2)"
excerpt: "Stacking Ridge Regression, Random Forest, and LightGBM with a ridge meta-model to forecast significant wave height and mean wave period, and checking whether it recovers the long-lead skill that pure LightGBM lost in Part 1."
layout: single
author_profile: true
permalink: /EnergyForecasting/Wave_Energy/Wave_Energy_Flux_Forecasting_part2/
usemathjax: true
image: "/EnergyForecasting/Wave_Energy/2_Wave_Energy_Flux_Forecsating_part2/2_Stacking_Ensemble/images/Fig1_Main_Pipeline.png"
date: 2026-08-08
category: "Wave Energy"
---

> **Series:** Wave Energy | **Part:** 3 (Flux Forecasting: Stacking Ensemble)

---

## Introduction

"Multi-ridge regression," or stacking with a ridge regression meta-model, means using L2-regularized linear regression to combine the predictions of several base machine learning models. In this part, the base models are Ridge Regression, Random Forest, and LightGBM. For background on the individual techniques, see the [Machine Learning Projects](/MachineLearningProjects/) section of this site.

<figure>
  <img src="/EnergyForecasting/Wave_Energy/2_Wave_Energy_Flux_Forecsating_part2/2_Stacking_Ensemble/images/Fig1_Main_Pipeline.png" alt="Stacking ensemble pipeline: Ridge, Random Forest, and LightGBM as base models feeding a ridge meta-model">
  <figcaption>Fig. 1: Main pipeline.</figcaption>
</figure>

**How ridge regression combines the base models:**

- **Stacking meta-regressor.** Instead of simple averaging, a ridge regression model treats the predictions of the individual base models as input features to predict the final target.[^1][^2][^3][^4]
- **L2 penalty control.** The ridge penalty stops the meta-model from assigning overly large or unstable weights to any single base model, and handles correlated base-model predictions gracefully.[^5][^6][^3]
- **Bias-variance balance.** It shrinks the coefficients of weak or redundant base models toward zero, which improves generalization on unseen data.

Data, walk-forward folds, and the best-lag choices per (target, lead time) are all reused unchanged from [Part 1](/EnergyForecasting/Wave_Energy/Wave_Energy_Flux_Forecasting_part1/); only the modeling stage changes here. For each target and lead time, RFE feature selection is re-run (since the best feature set can differ across model types), and the three base models are each fit and validated before the ridge meta-model learns how to combine them.

## Results

### 2.1 Base Models vs. Stacking Ensemble

Comparing MSE, NRMSE, and SMAPE across all four models (the three base models plus the stacking ensemble) by lead time:

<figure>
  <img src="/EnergyForecasting/Wave_Energy/2_Wave_Energy_Flux_Forecsating_part2/2_Stacking_Ensemble/images/Fig2_SWH_Performance_Bars.png" alt="Bar chart comparing MSE, NRMSE, and SMAPE for Ridge, Random Forest, LightGBM, and the stacking model, for significant wave height">
  <figcaption>Fig. 2: Performance comparison for SWH (Hs) by lead time.</figcaption>
</figure>

<figure>
  <img src="/EnergyForecasting/Wave_Energy/2_Wave_Energy_Flux_Forecsating_part2/2_Stacking_Ensemble/images/Fig3_MWP_Performance_Bars.png" alt="Bar chart comparing MSE, NRMSE, and SMAPE for Ridge, Random Forest, LightGBM, and the stacking model, for mean wave period">
  <figcaption>Fig. 3: Performance comparison for MWP (Te) by lead time.</figcaption>
</figure>

The stacked model's own test-set metrics, together with the ridge meta-model's learned weight on each base model:

**Significant wave height (Hs / swh):**

| Lead (h) | MAE | RMSE | NRMSE | SMAPE | R² | ridge_coef | rf_coef | lgbm_coef |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.02 | 0.02 | 0.01 | 0.02 | 1.00 | 0.29 | 0.35 | 0.36 |
| 3 | 0.04 | 0.06 | 0.03 | 0.04 | 0.99 | 0.09 | 0.32 | 0.59 |
| 6 | 0.08 | 0.11 | 0.05 | 0.07 | 0.96 | 0.12 | 0.32 | 0.57 |
| 12 | 0.13 | 0.19 | 0.09 | 0.12 | 0.86 | -0.09 | 0.08 | 1.08 |
| 24 | 0.23 | 0.30 | 0.13 | 0.24 | 0.69 | 0.17 | -0.71 | 1.87 |
| 48 | 0.34 | 0.44 | 0.20 | 0.30 | 0.33 | 1.40 | 0.08 | 0.45 |

**Mean wave period (Te / mwp):**

| Lead (h) | MAE | RMSE | NRMSE | SMAPE | R² | ridge_coef | rf_coef | lgbm_coef |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.07 | 0.09 | 0.02 | 0.01 | 0.99 | 0.24 | 0.25 | 0.51 |
| 3 | 0.18 | 0.23 | 0.05 | 0.03 | 0.94 | 0.02 | 0.34 | 0.63 |
| 6 | 0.32 | 0.41 | 0.08 | 0.05 | 0.82 | 0.03 | 0.46 | 0.49 |
| 12 | 0.66 | 0.84 | 0.17 | 0.10 | 0.23 | -0.55 | 0.08 | 1.47 |
| 24 | 0.84 | 1.03 | 0.21 | 0.13 | -0.13 | -0.01 | -0.08 | 1.20 |
| 48 | 0.95 | 1.19 | 0.24 | 0.15 | -0.49 | 1.14 | -2.24 | 9.63* |

<small>*The mwp/48h lgbm_coef is reported as 9.63 in the raw results; given the intercept for that row is also unusually large in magnitude, this row's meta-model fit is clearly unstable rather than a meaningful weighting (see Simplifications below).</small>

Comparing these to Part 1's pure-LightGBM test R² at the same leads is the real payoff of the stacking approach: for **Hs**, stacking is better everywhere from 12h onward, and 48h flips from clearly negative (-0.66 in Part 1) to a solidly positive 0.33 here. For **Te**, the picture is mixed rather than uniformly better: stacking is roughly even with pure LightGBM through 6h, but actually a bit worse at 12h and 24h, and only marginally less negative at 48h. So the ensemble recovers real long-lead skill for wave height specifically, not for wave period.

The meta-model's coefficients also confirm the ridge penalty is doing real work: the weight on each base model shifts noticeably by lead time rather than settling on one fixed blend, and it occasionally goes negative (e.g. `rf_coef` at swh/24h and mwp/48h), where the meta-model is actively subtracting a correlated base prediction rather than simply averaging it in.

### 2.2 Time Series Forecasting

Each base model tends to lead at a different point in the lead-time range, with Random Forest not winning outright at any of them. At the shorter leads (1h, 3h, 6h), the stacking model, LightGBM, and Ridge each take turns being the best performer depending on lead time. At the longer leads (12h through 48h), the stacking model has the best overall performance for wave height, but for wave period stacking only wins at 24h; Ridge Regression wins on its own at 12h and 48h.

<figure>
  <img src="/EnergyForecasting/Wave_Energy/2_Wave_Energy_Flux_Forecsating_part2/2_Stacking_Ensemble/images/Fig4_Stacking_Forecast_1_3_6h.png" alt="Actual vs predicted time series for SWH, MWP, and wave power at 1h, 3h, and 6h lead times, using each lead time's best-performing model">
  <figcaption>Fig. 4: Actual vs. predicted, lead times 1h / 3h / 6h (best model per panel).</figcaption>
</figure>

<figure>
  <img src="/EnergyForecasting/Wave_Energy/2_Wave_Energy_Flux_Forecsating_part2/2_Stacking_Ensemble/images/Fig5_Stacking_Forecast_12_24_48h.png" alt="Actual vs predicted time series for SWH, MWP, and wave power at 12h, 24h, and 48h lead times, using each lead time's best-performing model">
  <figcaption>Fig. 5: Actual vs. predicted, lead times 12h / 24h / 48h (best model per panel).</figcaption>
</figure>

## Simplifications

- **The meta-model is fit on validation-set predictions only** (`meta_X_valid`), a fairly small sample to learn three coefficients and an intercept from; the unstable mwp/48h row above is a direct symptom of this.
- **"Best model per lead" is chosen by test-set RMSE**, which is a look at the test set itself rather than a fully blind selection; treat the Section 2.2 comparisons as descriptive of this run, not as a guaranteed ranking on unseen data.
- **Only one of six walk-forward folds is shown**, the same limitation carried over from Part 1.
- **Wave power is still a derived, ex-post quantity**: each target's best model is picked independently, then combined multiplicatively, so Hs and Te errors compound in the power estimate exactly as in Part 1.

## Conclusion

Stacking Ridge Regression, Random Forest, and LightGBM with a ridge meta-model answers the question Part 1 ended on: it does recover meaningful long-lead skill, but only for significant wave height, where 48h R² turns from negative to a positive 0.33. Mean wave period doesn't get the same benefit: stacking is roughly a wash or slightly worse than plain LightGBM at 12-24h. Part 3 moves to probabilistic forecasting (Quantile Regression, Quantile Regression Forest, and bootstrapped residuals), which should matter most exactly where these first two parts have shown point forecasts breaking down.

## References

[^1]: ["Bagging vs Boosting vs Stacking in Machine Learning"](https://medium.com/grabngoinfo/bagging-vs-boosting-vs-stacking-in-machine-learning-65fe4d1684c0), GrabNGoInfo.
[^2]: ["Building Multi-Output Regression Models: Linear & Ridge Regression"](https://www.linkedin.com/pulse/building-multi-output-regression-models-linear-ridge-r-awc3c), LinkedIn.
[^3]: ["Understanding Ridge Regression"](https://www.certometer.com/blogs/machine-learning/understanding-ridge-regression), Certometer.
[^4]: ["Stacking ensemble machine learning"](https://www.sciencedirect.com/science/article/pii/S2589721725000807), ScienceDirect.
[^5]: ["What is Ridge Regression?"](https://www.geeksforgeeks.org/machine-learning/what-is-ridge-regression/), GeeksforGeeks.
[^6]: ["What is Regularization in Machine Learning?"](https://www.acte.in/what-is-regularization-in-machine-learning), ACTE.

## Code

- [Stacking_Ensemble_ERA5.py](/EnergyForecasting/Wave_Energy/2_Wave_Energy_Flux_Forecsating_part2/2_Stacking_Ensemble/Stacking_Ensemble_ERA5.py): loads Part 1's data and best-lag table, fits the three base models and the ridge meta-model per (target, lead), and produces all figures above.
- [plot_all.py](/EnergyForecasting/Wave_Energy/2_Wave_Energy_Flux_Forecsating_part2/2_Stacking_Ensemble/plot_all.py): plotting helpers shared across figures.
- [stacking_ensemble_results.csv](/EnergyForecasting/Wave_Energy/2_Wave_Energy_Flux_Forecsating_part2/2_Stacking_Ensemble/Results_Stacking/stacking_ensemble_results.csv): the full results table above, including the meta-model coefficients.

**Next:** Part 3 turns to probabilistic forecasting (Quantile Regression, Quantile Regression Forest, and bootstrapped residuals) to put uncertainty bounds around the point forecasts from Parts 1 and 2.
