text
---
title: "KNN for Wind Power Prediction 🌬️⚡"
layout: single
permalink: /MachineLearning/KNN_part2.md/
usemathjax: true
category: densys
---

# K‑Nearest Neighbors for Wind Power

In this example, a K‑Nearest Neighbors (KNN) regressor is used to predict wind‑turbine power from simple meteorological features: wind speed, air density, and turbulence intensity.  
The goal is to learn a flexible, data‑driven power curve without assuming a specific analytical formula.

---

## 1. Imports and setup

First import the libraries needed for numerical work, modeling, and plotting.

import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_absolute_error, r2_score

text

- `numpy` is used to generate synthetic data.  
- `matplotlib` will create colorful plots of the KNN predictions.  
- `train_test_split`, `StandardScaler`, and `KNeighborsRegressor` come from scikit‑learn and handle splitting, scaling, and the KNN model.  
- `mean_absolute_error` and `r2_score` evaluate prediction quality.

---

## 2. Simulating wind‑farm data

To keep the example self‑contained, a small synthetic dataset is generated.  
Each sample represents one 10‑minute period at a turbine.

np.random.seed(42)

n_samples = 800

Features
wind_speed = np.random.uniform(2, 20, n_samples) # m/s
air_density = np.random.normal(1.225, 0.04, n_samples) # kg/m^3
turbulence = np.random.uniform(0.02, 0.25, n_samples) # 0–1

Simple nonlinear power curve (3 MW turbine)
def power_curve(ws):
p = np.piecewise(
ws,
[ws < 3, (ws >= 3) & (ws < 13), (ws >= 13) & (ws < 25), ws >= 25],
[
0,
lambda x: 3_000 * ((x - 3) / (13 - 3))**3, # cubic ramp
3_000,
0,
],
)
return p

base_power = power_curve(wind_speed)

Modify by density and turbulence
density_factor = air_density / 1.225
turbulence_factor = 1.0 - 0.5 * turbulence

true_power = base_power * density_factor * turbulence_factor

Add measurement noise
noise = np.random.normal(0, 120, n_samples)
power_output = np.clip(true_power + noise, 0, 3_000)

X = np.column_stack([wind_speed, air_density, turbulence])
y = power_output

text

- `wind_speed`, `air_density`, and `turbulence` are the three input features.  
- `power_curve` mimics a typical turbine power curve (cut‑in, ramp, rated power, cut‑out).  
- Air density scales the power slightly; turbulence reduces it.  
- Random `noise` represents measurement/operational noise.  
- `X` is the feature matrix; `y` is the target power output.

---

## 3. Train–test split and feature scaling

KNN is sensitive to feature scales, so the data are split and then standardized.

X_train, X_test, y_train, y_test = train_test_split(
X, y, test_size=0.25, random_state=0
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

text

- `train_test_split` reserves 25 % of data for testing.  
- `StandardScaler` removes the mean and scales features to unit variance, ensuring wind speed, density, and turbulence contribute comparably to the distance metric.

---

## 4. Fitting the KNN regressor

The KNN model is defined with \(K=7\) neighbors and distance‑based weights, then fitted on the scaled data.

K = 7
knn = KNeighborsRegressor(n_neighbors=K, weights="distance")
knn.fit(X_train_scaled, y_train)

y_pred = knn.predict(X_test_scaled)

mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"KNN (K={K}): MAE = {mae:.1f} kW, R^2 = {r2:.3f}")

text

- `n_neighbors=7` means each prediction is a weighted average of the 7 closest training points.  
- `weights="distance"` gives more influence to nearer neighbors.  
- `MAE` (in kW) and \(R^2\) summarize how well the model predicts unseen data.

---

## 5. Visualizing a 2D slice of the power map

To understand the learned mapping, a 2D grid over wind speed and turbulence is plotted while fixing air density.

Grid over wind speed and turbulence
ws_grid = np.linspace(2, 20, 80)
ti_grid = np.linspace(0.02, 0.25, 80)
WS, TI = np.meshgrid(ws_grid, ti_grid)
rho_fixed = np.full_like(WS, 1.225)

grid_X = np.column_stack([WS.ravel(), rho_fixed.ravel(), TI.ravel()])
grid_X_scaled = scaler.transform(grid_X)
grid_pred = knn.predict(grid_X_scaled).reshape(WS.shape)

plt.figure(figsize=(8, 6))
cmap = plt.get_cmap("viridis")

contour = plt.contourf(
WS, TI, grid_pred,
levels=15,
cmap=cmap
)
cbar = plt.colorbar(contour)
cbar.set_label("Predicted power (kW)", fontsize=11)

Overlay training points colored by actual power
plt.scatter(
X_train[:, 0], # wind_speed
X_train[:, 2], # turbulence
c=y_train,
cmap=cmap,
edgecolor="white",
linewidth=0.4,
alpha=0.7,
s=30,
label="Training points"
)

plt.xlabel("Wind speed (m/s)", fontsize=11)
plt.ylabel("Turbulence intensity", fontsize=11)
plt.title(f"KNN wind-power map (K={K})", fontsize=13)
plt.legend(loc="upper right", framealpha=0.9)
plt.tight_layout()
plt.show()

text

- `WS` and `TI` form a grid of wind‑speed / turbulence pairs.  
- For each grid point, KNN predicts power; `contourf` visualizes this as a smooth color map.  
- Actual training samples are plotted on top, colored by their measured power, making it easy to compare data and model.

---

## 6. Predicting a new operating point

Finally, the trained model is used to estimate power for a specific condition.

new_point = np.array([[11.5, 1.24, 0.08]]) # ws, density, turbulence
new_point_scaled = scaler.transform(new_point)
new_pred = knn.predict(new_point_scaled)
print(
f"Predicted power at ws=11.5 m/s, rho=1.24 kg/m^3, TI=0.08: "
f"{new_pred:.0f} kW"
)

text

- `new_point` contains one row with the three features.  
- The same `scaler` is applied, then `knn.predict` returns the forecast power in kW.  
- This mirrors a practical use case: forecasting short‑term power from SCADA or met‑mast measurements.

---

This structure (short explanation, then code) should fit naturally into your GitHub Pages / Jekyll site in the same style as the PyWake documentation.
