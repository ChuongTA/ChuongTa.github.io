---
title: "Probabilistic Electricity Price Forecasting (Part 3)"
category: densys
excerpt: "Bootstrapped residuals and split conformal prediction for DK1 day-ahead prices, adapted from skforecast's guides and evaluated with the same walk-forward cross-validation as Part 2, including a head-to-head comparison against QR and QRF."
layout: single
author_profile: true
permalink: /EnergySystems/PEPF_part3/
usemathjax: true
---

> **Series:** Probabilistic Electricity Price Forecasting | **Part:** 3 (Bootstrapped Residuals and Conformal Prediction)

---

QR and QRF, covered in [Part 2](/EnergySystems/PEPF_part2/), estimate the conditional distribution directly: QR fits one linear model per quantile, QRF reads every quantile off a single forest's weighted empirical CDF. This post covers two different, older techniques that instead take a **single point-forecast model** and turn its **residuals** into an interval. Both come from skforecast's user guides ([Bootstrapped Residuals](https://skforecast.org/0.15.0/user_guides/probabilistic-forecasting-bootstrapped-residuals), [Conformal Prediction](https://skforecast.org/0.15.0/user_guides/probabilistic-forecasting-conformal-prediction)), and this write-up adapts the concepts to this project's own XGBoost pipeline and tests them on real DK1 data rather than skforecast's bike-sharing/ETT examples.

## 1. Bootstrapped Residuals

The idea: fit one point-forecast model, collect its residuals $e_t = y_t - \hat y_t$, then simulate alternative future outcomes by resampling from that residual pool and adding the draws back to the point forecast. Repeating this many times (`n_boot` draws) builds an empirical distribution at each forecast horizon; percentiles of that distribution become the prediction interval.

![Bootstrapping predictions diagram](/EnergySystems/PEPF_part3/BC_basic_bootstrap_diagram.png)
*Repeated resampling of past residuals builds a collection of alternative predictions, whose spread represents forecast uncertainty. Source: [skforecast.org, Bootstrapped Residuals](https://skforecast.org/0.15.0/user_guides/probabilistic-forecasting-bootstrapped-residuals).*

Taking the $\alpha/2$ and $1-\alpha/2$ percentiles of that spread, at every forecasting horizon, turns the individual bootstrap paths into a single interval band:

![Bootstrapped prediction intervals animation](/EnergySystems/PEPF_part3/BC_basic_bootstrap_animation.gif)
*Each gray line is one bootstrap path; the red band is the resulting prediction interval once percentiles are taken at each horizon. Source: [skforecast.org, Bootstrapped Residuals](https://skforecast.org/0.15.0/user_guides/probabilistic-forecasting-bootstrapped-residuals).*

> "One of the main advantages of this strategy is that it requires only a single model to estimate any interval. However, performing hundreds or thousands of bootstrapping iterations can be computationally expensive." ([skforecast, Bootstrapped Residuals](https://skforecast.org/0.15.0/user_guides/probabilistic-forecasting-bootstrapped-residuals))

### Which residuals: in-sample vs. out-of-sample

This is the part skforecast's docs spend the most time on, and it turns out to matter enormously for DK1.

- **In-sample residuals**: computed on the same data the model was trained on. The model has already fit that data, so its errors there systematically understate how wrong it will be on genuinely new data. skforecast's own docs flag this: "this can result in intervals that are too narrow (overly optimistic)."
- **Out-of-sample residuals**: computed on a held-out calibration/validation split the model never trained on. Wider, but honest.

**This project's `forecast.py` currently uses in-sample residuals**: `train_residuals = y_train.values - model.predict(X_train)` is fit directly on the training set the model just saw. Testing this on real DK1 data (1h-ahead XGBoost, last walk-forward fold) shows exactly the effect skforecast warns about, and it's dramatic:

![In-sample vs out-of-sample residual distributions](/EnergySystems/PEPF_part3/BC_residuals_in_vs_out.png)
*Real DK1 residuals from the same XGBoost model: in-sample (evaluated on training data) vs out-of-sample (evaluated on a held-out validation window).*

| Residual source | Std. dev. | n |
|---|---|---|
| In-sample (train) | 5.6 €/MWh | 12,866 |
| Out-of-sample (val) | 28.6 €/MWh | 168 |

A **5x gap**. The consequence on actual interval coverage, measured on held-out test data:

| Residual source | Nominal 80%, actual coverage | Nominal 95%, actual coverage |
|---|---|---|
| In-sample | **52.1%** | 78.9% |
| Out-of-sample | **88.7%** | 99.7% |

The in-sample intervals claim 80% coverage and deliver barely half that: they are badly overconfident. This isn't a hypothetical failure mode, it's what the existing code does today. **Fix: compute residuals on a held-out split, not the training set.** The walk-forward validation split already built in `main_pipeline.py` is the natural place to source these residuals from.

### Binned residuals (conditioning on heteroscedasticity)

Bootstrapping assumes residuals are exchangeable regardless of the situation, which is rarely true: errors are usually larger when the underlying value is larger or more volatile. skforecast partitions residuals into bins (by default, bins of the *predicted value*) so that bootstrapping samples from the right slice of the error distribution depending on what's being predicted.

This project's `BootstrappedPI` class already bins, but by **hour-of-day**, not predicted value, on the reasoning that DK1 volatility is hour-dependent (peak vs. off-peak). Testing both binning strategies against no binning at all, using an 8-week calibration window (large enough for about 56 samples per hour bin) on the same test fold:

![Coverage comparison by binning strategy](/EnergySystems/PEPF_part3/BC_binning_coverage.png)
*Empirical coverage against the nominal target, for three ways of conditioning the residual pool: no binning, hour-of-day, and predicted-value quantile bins.*

| Method | Nominal 80% | Nominal 90% | Nominal 95% |
|---|---|---|---|
| Unbinned (global) | cov 87.8%, width 26.6 | cov 95.8%, width 39.8 | cov 98.8%, width 55.7 |
| **Hour-binned** (this project's current choice) | cov **73.2%**, width 25.1 | cov 86.6%, width 34.5 | cov 93.5%, width 43.2 |
| **Value-binned** (skforecast's default) | cov 88.4%, width 26.1 | cov 96.4%, width 38.1 | cov 98.8%, width 53.6 |

This is a genuinely useful, non-obvious result: **hour-binning makes the interval narrower but noticeably worse-calibrated** on this fold (73% actual vs 80% claimed), while value-binning performs essentially the same as the unbinned baseline. A likely explanation: the XGBoost point forecast already includes `hour` as an input feature, so much of the systematic hour-of-day heteroscedasticity is already absorbed into the point prediction itself, leaving less left over for hour-binned residuals to explain. Binning by the *predicted value* instead, which reflects the model's own sense of how extreme the situation is, captures residual heteroscedasticity that hour alone misses.

**Recommendation for this project:** switch `BootstrappedPI`'s conditioning variable from hour-of-day to predicted-value bins (or test both properly within the walk-forward framework before committing), and always source the residual pool from a held-out split.

## 2. Conformal Prediction (Split Conformal)

Conformal prediction solves the same problem, turning a point forecast plus residuals into a calibrated interval, without the resampling loop. Skforecast implements Split Conformal Prediction (SCP): reserve a calibration set, compute residuals on it once, then read the $(\alpha/2, 1-\alpha/2)$ empirical quantiles of those residuals directly as a fixed offset added to every future point forecast.

![Conformal regression diagram](/EnergySystems/PEPF_part3/BC_basic_conformal_diagram.png)
*Conformal regression turns point predictions into prediction intervals using a single correction learned once from a calibration set. Source: [skforecast.org, Conformal Prediction](https://skforecast.org/0.15.0/user_guides/probabilistic-forecasting-conformal-prediction), citing Christoph Molnar, [Introduction To Conformal Prediction With Python](https://leanpub.com/conformal-prediction).*

> "Conformal methods can also calibrate prediction intervals generated by other techniques, such as quantile regression or bootstrapped residuals... Skforecast implements Split Conformal Prediction (SCP) due to its simplicity and efficiency." ([skforecast, Conformal Prediction](https://skforecast.org/0.15.0/user_guides/probabilistic-forecasting-conformal-prediction))

No draws, no resampling, just one quantile lookup from the calibration residuals. A first, one-off timing test on a single fold (336 test rows, one 80% interval, fully vectorized) suggested roughly 54x, but that number was optimistic: it timed the narrowest possible case. Running both methods properly, across all 4 walk-forward folds and all 4 lead times, with per-row binned lookups for the full 13-quantile grid (needed for pinball loss and CRPS, not just one interval), gives a more honest and still solid speedup:

| Method | Time per fold (mean ± std) |
|---|---|
| Bootstrap (`n_boot=1000`) | 40.3 ms ± 8.5 ms |
| Conformal (direct quantile) | 5.5 ms ± 1.7 ms |
| **Speedup** | **~7.4x** |

The gap narrows from the earlier single-shot estimate because computing 13 quantile levels with per-row bin lookups carries its own Python-level overhead for *both* methods; conformal's advantage is the resampling step it skips, not the binning logic, which both methods share. Still a clear, consistent win, just a more modest one than the first quick test suggested.

### Results: Walk-Forward Comparison

Both methods were run through the exact same walk-forward folds as QR and QRF (`bootstrap_conformal_pipeline.py`), calibrated on out-of-sample validation residuals, value-binned, wrapping the same XGBoost point-forecast family used in `forecast.py`:

| Model | Lead Time | MAE (median) | Mean Pinball | CRPS (approx.) |
|---|---|---|---|---|
| Bootstrap | 1h | 8.10 (±1.82) | 2.73 (±0.55) | 5.45 (±1.11) |
| Conformal | 1h | 8.10 (±1.84) | **2.70 (±0.56)** | **5.39 (±1.12)** |
| Bootstrap | 6h | **15.36 (±1.04)** | **4.93 (±0.42)** | **9.87 (±0.84)** |
| Conformal | 6h | 15.30 (±1.06) | 4.94 (±0.38) | 9.88 (±0.75) |
| Bootstrap | 12h | 15.64 (±0.94) | **5.18 (±0.37)** | **10.36 (±0.74)** |
| Conformal | 12h | 15.58 (±0.90) | 5.19 (±0.34) | 10.38 (±0.69) |
| Bootstrap | 24h | 16.17 (±1.81) | **5.11 (±0.60)** | **10.22 (±1.19)** |
| Conformal | 24h | 16.19 (±1.84) | 5.12 (±0.56) | 10.24 (±1.12) |

Bootstrap and Conformal are statistically indistinguishable on point accuracy and sharpness, exactly as expected: both derive from the same calibration-residual quantiles.

Coverage tells a different story. Bootstrap consistently covers *more* than Conformal, at every lead time and every nominal level, while also being *wider*:

| Model | Lead Time | Cov 80% | Width 80% | Cov 90% | Width 90% | Cov 95% | Width 95% |
|---|---|---|---|---|---|---|---|
| Bootstrap | 1h | **0.781** | 30.8 | **0.880** | 46.0 | **0.935** | 61.7 |
| Conformal | 1h | 0.763 | 29.2 | 0.853 | 41.3 | 0.911 | 50.7 |
| Bootstrap | 6h | **0.692** | 46.5 | **0.804** | 66.7 | **0.851** | 81.9 |
| Conformal | 6h | 0.667 | 44.3 | 0.763 | 59.7 | 0.827 | 71.6 |
| Bootstrap | 12h | **0.688** | 49.8 | **0.816** | 68.9 | **0.887** | 82.8 |
| Conformal | 12h | 0.673 | 47.3 | 0.776 | 62.6 | 0.841 | 73.2 |
| Bootstrap | 24h | **0.682** | 47.5 | **0.807** | 65.0 | **0.871** | 79.3 |
| Conformal | 24h | 0.670 | 45.2 | 0.770 | 58.5 | 0.833 | 69.4 |

This is a real, non-obvious finding the single-fold test didn't reveal: resampling with replacement from a calibration pool (Bootstrap) introduces extra variance beyond the pool's raw empirical quantiles, which widens the tails and pushes coverage slightly higher than the direct quantile lookup (Conformal) achieves from the exact same pool. Neither dominates: **Conformal is sharper (narrower intervals for near-identical accuracy), Bootstrap is safer (better coverage at the cost of width)**. Which one to prefer depends on whether the downstream decision cares more about tight intervals or about not being caught outside them.

![Bootstrap vs Conformal forecast fan chart, 1h ahead](/EnergySystems/PEPF_part3/BC_walkforward_forecast_1h.png)
*Bootstrap vs Conformal, 1h ahead, on the most recent fold's test window.*

![Bootstrap vs Conformal reliability diagram](/EnergySystems/PEPF_part3/BC_walkforward_reliability.png)
*Empirical vs nominal coverage, averaged across all 4 folds, for both methods at all 4 lead times. Conformal sits consistently below Bootstrap, matching the coverage tables above.*

![Bootstrap vs Conformal timing](/EnergySystems/PEPF_part3/BC_walkforward_timing.png)
*Real timing, averaged across all 16 fold/lead-time combinations.*

### How do all four methods compare?

Putting Bootstrap and Conformal's mean pinball loss next to QR and QRF's from [Part 2](/EnergySystems/PEPF_part2/):

| Lead Time | QR | QRF | Bootstrap | Conformal |
|---|---|---|---|---|
| 1h | 3.53 | 2.74 | 2.73 | **2.70** |
| 6h | 6.35 | 5.55 | **4.93** | 4.94 |
| 12h | 6.48 | 5.49 | **5.18** | 5.19 |
| 24h | 6.39 | **4.89** | 5.11 | 5.12 |

QR, the linear model, is the weakest of the four at every horizon, as it was on its own. More interesting: at 1h, 6h, and 12h, the XGBoost-plus-residuals methods (Bootstrap, Conformal) actually beat QRF on sharpness, sometimes by a wide margin (4.93 vs 5.55 at 6h). Only at 24h does QRF pull back ahead. On coverage, though, the pattern reverses: QRF's 80% interval coverage (0.726 to 0.862 across horizons) is consistently closer to nominal than Bootstrap's (0.682 to 0.781) or Conformal's (0.667 to 0.763). **The sharpest method isn't the best-calibrated one here**, which is exactly why both properties need to be reported together rather than picking a single "winner."

### The multi-step-ahead caveat

Skforecast is explicit about this: SCP's coverage guarantee is only rigorous for **one-step-ahead** predictions. For multi-step horizons, the coverage probability is not theoretically guaranteed, it has to be checked empirically.

> "When applied to time series forecasting, their coverage guarantees are only valid for one-step-ahead predictions. For multi-step-ahead predictions, the coverage probability is not guaranteed." ([skforecast, Conformal Prediction](https://skforecast.org/0.15.0/user_guides/probabilistic-forecasting-conformal-prediction))

This matters directly for this project, which forecasts 1h, 6h, 12h, and 24h ahead. There's no shortcut around it: coverage has to be measured empirically at each horizon, exactly as the walk-forward pipeline already does for QR and QRF. Conformal prediction should be evaluated the same way, per lead time, rather than assumed valid because it "is conformal."

## 3. Implementation for This Project

The simplified version below shows the core mechanism. The actual implementation used to produce every result in this post, including both the single-fold binning comparison above and the full walk-forward comparison below, lives in `bootstrap_conformal_pipeline.py` (included alongside this post), alongside a matching `BootstrappedPI` class built the same way.

```python
import numpy as np

class ConformalPI:
    """
    Split Conformal Prediction (SCP), adapted from skforecast's approach
    (https://skforecast.org/0.15.0/user_guides/probabilistic-forecasting-conformal-prediction).

    Fits once on a held-out calibration set's residuals, no resampling.
    Optionally conditions the residual quantiles on a bin variable
    (predicted value or hour) for adaptive/heteroscedasticity-aware
    intervals, matching skforecast's `use_binned_residuals`.
    """

    def __init__(self, coverage_levels=(0.80, 0.90, 0.95), bin_by=None, n_bins=5, min_bin_size=15):
        self.coverage_levels = coverage_levels
        self.bin_by = bin_by  # None, "value", or "hour"
        self.n_bins = n_bins
        self.min_bin_size = min_bin_size

    def fit(self, cal_residuals, cal_point_preds=None, cal_hours=None):
        self._residuals = np.asarray(cal_residuals)
        self._bin_edges = None

        if self.bin_by == "value":
            self._bin_edges = np.quantile(cal_point_preds, np.linspace(0, 1, self.n_bins + 1))
            bins = np.clip(np.digitize(cal_point_preds, self._bin_edges[1:-1]), 0, self.n_bins - 1)
        elif self.bin_by == "hour":
            bins = np.asarray(cal_hours, dtype=int)
        else:
            bins = np.zeros(len(self._residuals), dtype=int)

        self._offsets = {}
        for b in np.unique(bins):
            pool = self._residuals[bins == b]
            pool = pool if len(pool) >= self.min_bin_size else self._residuals
            for cov in self.coverage_levels:
                alpha = 1 - cov
                self._offsets[(b, cov)] = (
                    np.quantile(pool, alpha / 2),
                    np.quantile(pool, 1 - alpha / 2),
                )
        self._bins_seen = set(np.unique(bins))
        return self

    def predict(self, point_preds, point_or_hour=None):
        point_preds = np.asarray(point_preds)
        if self.bin_by == "value":
            bins = np.clip(np.digitize(point_or_hour, self._bin_edges[1:-1]), 0, self.n_bins - 1)
        elif self.bin_by == "hour":
            bins = np.asarray(point_or_hour, dtype=int)
        else:
            bins = np.zeros(len(point_preds), dtype=int)

        result = {}
        for cov in self.coverage_levels:
            lo, hi = np.empty(len(point_preds)), np.empty(len(point_preds))
            for i, b in enumerate(bins):
                b_use = b if b in self._bins_seen else min(self._bins_seen, key=lambda x: abs(x - b))
                lo_off, hi_off = self._offsets[(b_use, cov)]
                lo[i], hi[i] = point_preds[i] + lo_off, point_preds[i] + hi_off
            result[f"lower_{int(cov * 100)}"] = lo
            result[f"upper_{int(cov * 100)}"] = hi
        return result
```

Usage, matching this project's walk-forward folds:

```python
# 1. Fit the point-forecast model on the fold's training window only
model.fit(X_train, y_train)

# 2. Calibrate on the held-out validation window (out-of-sample residuals)
cal_point_preds = model.predict(X_val)
cal_residuals = y_val - cal_point_preds

conformal = ConformalPI(coverage_levels=(0.80, 0.90, 0.95), bin_by="value", n_bins=5)
conformal.fit(cal_residuals, cal_point_preds=cal_point_preds)

# 3. Predict intervals on the test window
point_test = model.predict(X_test)
intervals = conformal.predict(point_test, point_or_hour=point_test)
```

The same `ConformalPI` object, with `bin_by=None`, also reproduces the corrected (out-of-sample) bootstrap-equivalent interval: the two techniques share the same calibration-set requirement, and conformal is simply the fast, closed-form way to get there.

## 4. Summary: What to Change in This Project

1. **Fix `BootstrappedPI` to use out-of-sample residuals.** It currently calibrates on training-set residuals, which this data shows understate the true error spread by roughly 5x, and under-cover its own nominal target by nearly 30 percentage points (52% actual vs 80% claimed) on a single test fold. `bootstrap_conformal_pipeline.py` implements the fix: calibrate on the walk-forward validation split instead.
2. **Reconsider the binning variable.** Hour-of-day binning, this project's current choice, was empirically worse-calibrated than no binning at all in the single-fold test; value-binning (skforecast's default) matched the unbinned baseline and is what the full walk-forward pipeline now uses for both methods.
3. **Conformal is meaningfully faster, but the margin is smaller than a quick test suggests.** Measured across all 16 fold/lead-time combinations: about 7.4x (5.5 ms vs 40.3 ms per fold), not the ~54x a single fully-vectorized test implied. Still a real, consistent win for anywhere the existing bootstrap approach's computational cost has been a bottleneck.
4. **Pick Bootstrap or Conformal based on what the decision needs, not blindly.** Across all four lead times, Bootstrap consistently achieves better coverage (closer to nominal) at the cost of wider intervals, and Conformal is consistently sharper but less well-calibrated. Neither is a strict upgrade over the other.
5. **QRF is not automatically the best model once all four are compared.** At 1h, 6h, and 12h ahead, the XGBoost-plus-residuals methods (Bootstrap, Conformal) actually beat QRF on mean pinball loss; only at 24h does QRF pull ahead. QRF does have the most consistently well-calibrated coverage of the four, though, so the right choice again depends on whether sharpness or calibration matters more for the use case.
6. **Validate coverage per lead time, not just once.** Split conformal's coverage guarantee formally holds only for one-step-ahead forecasts; at 6h/12h/24h it must be checked empirically, exactly as this project's walk-forward pipeline now does for all four methods.

## References

- Skforecast. *Probabilistic Forecasting: Bootstrapped Residuals*. [skforecast.org/0.15.0/user_guides/probabilistic-forecasting-bootstrapped-residuals](https://skforecast.org/0.15.0/user_guides/probabilistic-forecasting-bootstrapped-residuals)
- Skforecast. *Probabilistic Forecasting: Conformal Prediction*. [skforecast.org/0.15.0/user_guides/probabilistic-forecasting-conformal-prediction](https://skforecast.org/0.15.0/user_guides/probabilistic-forecasting-conformal-prediction)
- MAPIE. *Theoretical Description, Split Conformal Prediction*. [mapie.readthedocs.io/en/stable/theoretical_description_regression.html](https://mapie.readthedocs.io/en/stable/theoretical_description_regression.html)
- Molnar, C. *Introduction To Conformal Prediction With Python.* [leanpub.com/conformal-prediction](https://leanpub.com/conformal-prediction)

---

**Files accompanying this post:** `bootstrap_conformal_pipeline.py`, `main_pipeline.py`, `plot.py`, and the `Results/` folder (per-fold metrics, cross-fold summary, and timing summary CSVs).
