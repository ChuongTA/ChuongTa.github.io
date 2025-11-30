---
title: "KNN Regression Part 2 – Wind Power Prediction 🌬️⚡"
category: densys
excerpt: "This post demonstrates how to model wind turbine power using KNN regression with simulated wind-farm data."
layout: single
author_profile: true
permalink: /MachineLearning/KNN_part2.md/
usemathjax: true
---

In this post, I use a K-Nearest Neighbors (KNN) regressor to predict the power output of a 3-MW wind turbine using simulated atmospheric data.  
The features include wind speed 🌬️, air density 🫧, and turbulence intensity 🌪️.  
This demonstration shows how to simulate realistic turbine behavior, preprocess features, train a model, and visualize results.


From synthetic wind-farm measurements, I estimate turbine power using a nonlinear power curve modified by density and turbulence effects. After preprocessing with feature scaling, we train a distance-weighted KNN regressor and evaluate its performance. Finally, I visualize a 2-D prediction map and compute predictions for new operating conditions.

# 1. Simulating wind-farm data

## 1.1 Imports and Setup
```
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_absolute_error, r2_score
```
In this code ```ListedColormap``` is used to create custom color maps for plots, ```train_test_split``` diving data into training and testing sets. ```StandardScaler``` normalize data (crucial for KNN), ```KNeighborsRegressor``` implement the KNN algorithm for predicting numbers, ```mean_absolute_error``` along with ```r2_score```are used to evaluate prediction accuracy.

## 1.2 Data Generation and Realistic wind farm simulation
```
np.random.seed(42)  
n_samples = 800
# Features
wind_speed = np.random.uniform(2, 20, n_samples)          # m/s
air_density = np.random.normal(1.225, 0.04, n_samples)    # kg/m^3
turbulence = np.random.uniform(0.02, 0.25, n_samples)     # 0–1
```
Feature Explanations:This snippet sets the random seed for reproducibility with ```np.random.seed(42)```, defines ```n_samples as 800```, and generates three feature arrays: ```wind_speed``` with values uniformly distributed between 2 and 20 m/s, air_density following a normal distribution centered at 1.225 kg/m³ with a standard deviation of 0.04, and turbulence uniformly distributed between 0.02 and 0.25.

## 1.3 The power curve fucntion
```
def power_curve(ws):
    p = np.piecewise(
        ws,
        [ws < 3, (ws >= 3) & (ws < 13), (ws >= 13) & (ws < 25), ws >= 25],
        [
            0,
            lambda x: 3_000 * ((x - 3) / (13 - 3))**3,  # cubic ramp
            3_000,
            0,
        ],
    )
    return p
```
the function ```np.piecewise``` creates a piecewise function with different rules for different wind speed ranges:
| Wind Speed | Power Output   | Explanation                    |
|------------|----------------|------------------------------- |
| < 3 m/s    | 0 kW           | Cut-in speed not reached       |
| 3–13 m/s   | Cubic increase | Power ≈ (wind speed)^3         |
| 13–25 m/s  | 3,000 kW       | Rated power (maximum)          |
| > 25 m/s   | 0 kW           | Cut-out for safety             |

```
base_power = power_curve(wind_speed)
# Modify by density and turbulence
density_factor = air_density / 1.225
turbulence_factor = 1.0 - 0.5 * turbulence
true_power = base_power * density_factor * turbulence_factor

# Add measurement noise noise = np.random.normal(0, 120, n_samples) power_output = np.clip(true_power + noise, 0, 3_000)
```
This code first calculates base_power using a power_curve function applied to ```wind_speed```. It then adjusts for air density and turbulence with ```density_factor``` and ```turbulence_factor``` to get ```true_power```. Finally, it adds normally distributed measurement noise with a standard deviation of 120 and ```clip``` ensures power stays between 0-3000 kW.

Note: The turbulence factor is defined as ```turbulence_factor = 1.0 - 0.5 * turbulence``` to represent the typical effect of turbulence on wind turbine power output. Higher turbulence usually reduces effective aerodynamic efficiency, so multiplying by a factor slightly less than 1 reduces the base power proportionally to the turbulence level. The coefficient 0.5 is a simplified scaling to model this reduction, ensuring that as turbulence increases, the factor decreases linearly, but it doesn’t reduce power to zero unless turbulence is extremely high

## 1.4 Data preparation for ML
```
X = np.column_stack([wind_speed, air_density, turbulence])
y = power_output
```
X: Input features matrix (800 rows × 3 columns)
y: Target values vector (800 power outputs)

```
# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=0
)
```
Training set (75%): Used to teach the model. Test set (25%): Used to evaluate performance on unseen data and ```random_state=0```: Ensures same split every time

## 1.5 Fit colorful KNN model
```
K = 7
knn = KNeighborsRegressor(n_neighbors=K, weights="distance")
knn.fit(X_train_scaled, y_train)

y_pred = knn.predict(X_test_scaled)

mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"KNN (K={K}): MAE = {mae:.1f} kW, R^2 = {r2:.3f}")
```
```n_neighbors = 7```: uses 7 most similar data points
```weights= "distance"```: close neighbors have more influence

Evulation metric:
- MAE (Mean Absolute Error): Average prediction error in kW (more detail in [this link](https://www.datacamp.com/tutorial/mean-absolute-error))
- $$R^2$$: How mych better than just guessing the average (0-1) (more detail in [this link](https://www.datacamp.com/tutorial/r-squared))


The dataset contains 800 synthetic observations.  
Wind speed is drawn uniformly between 2–20 m/s, air density from a normal distribution around 1.225 kg/m³, and turbulence intensity from 0.02–0.25.

A simplified power curve is used:

- No production below cut-in (3 m/s)  
- Cubic ramp-up between 3–13 m/s  
- Rated power (3000 kW) between 13–25 m/s  
- Automatic shutdown above 25 m/s  

Density and turbulence modify the output using multiplicative factors, and Gaussian noise simulates SCADA measurement uncertainty.

## 1.6 Feature Scaling 
scaler = StandardScaler()
```
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```
For the beginning, let me explain about why we need to scale the features. 
With unscaled features dominate distance calculations.
we have example data:
```
point_A = [15,   1.22,  0.08]   # wind_speed=15, density=1.22, turbulence=0.08
point_B = [12,   1.25,  0.12]   # wind_speed=12, density=1.25, turbulence=0.12
```
and then KNN distance calculation without scaling:
```
distance = √[(15-12)² + (1.22-1.25)² + (0.08-0.12)²]
         = √[3² + (-0.03)² + (-0.04)²]
         = √[9 + 0.0009 + 0.0016]
         = √9.0025 ≈ 3.0004
```
The problem arise:
- Wind speed difference (3) contributes: 9 (99.97% of total)
- Density difference (0.03) contributes: 0.0009 (0.01% of total)
- Turbulence difference (0.04) contributes: 0.0016 (0.02% of total)

Therefore, we need to stand scale. The package in sklearn is StandardScaler. Below is the guidance how we can transform mathematically.

First, we have a training Data (including both points A and B)::
```
Wind speeds: [10, 15, 8, 12] m/s                    # Includes 15 and 12
Air densities: [1.20, 1.22, 1.18, 1.25] kg/m³      # Includes 1.22 and 1.25  
Turbulence: [0.05, 0.08, 0.03, 0.12]               # Includes 0.08 and 0.12
```
Calculate mean (average):
```
Mean_wind_speed = (10 + 15 + 8 + 12) / 4 = 45 / 4 = 11.25
Mean_density = (1.20 + 1.25 + 1.18 + 1.22) / 4 = 4.85 / 4 = 1.2125
Mean_turbulence = (0.05 + 0.10 + 0.03 + 0.08) / 4 = 0.26 / 4 = 0.065
```
Then, calculate standard deviation:
```
Std_wind_speed = √[Σ(x - mean)² / (n-1)]
               = √[( (10-11.25)² + (15-11.25)² + (8-11.25)² + (12-11.25)² ) / 3]
               = √[(1.5625 + 14.0625 + 10.5625 + 0.5625) / 3]
               = √[26.75 / 3] = √8.9167 = 2.986
```

Next step is applying scaling formula
Scaling formula:
```
scaled_value = (original_value - mean) / standard_deviation
```
For the 1st point: 
```
Scaled_wind_speed = (15 - 11.25) / 2.986 = 3.75 / 2.986 = 1.256
Scaled_density = (1.22 - 1.2125) / 0.0287 = 0.0075 / 0.0287 = 0.261
Scaled_turbulence = (0.08 - 0.065) / 0.0280 = 0.015 / 0.0280 = 0.536
```
Then, for the 2nd point:
```
Scaled_wind_speed = (12 - 11.25) / 2.986 = 0.75 / 2.986 = 0.251
Scaled_density = (1.25 - 1.2125) / 0.0287 = 0.0375 / 0.0287 = 1.307
Scaled_turbulence = (0.12 - 0.065) / 0.0280 = 0.055 / 0.0280 = 1.964
```
The 3rd step is calculating distance with scaled values
Scaled points:
```
Point_A_scaled = [1.256, 0.261, 0.536]
Point_B_scaled = [0.251, 1.307, 1.964]
```
Distance calculation change to:
```
distance = √[(1.256 - 0.251)² + (0.261 - 1.307)² + (0.536 - 1.964)²]
         = √[(1.005)² + (-1.046)² + (-1.428)²]
         = √[1.010 + 1.094 + 2.039]
         = √4.143 = 2.035
```
The contribution of each feature now has changed:
- Wind speed: 1.010 (24.4%)
- Density: 1.094 (26.4%)
- Turbulence: 2.039 (49.2%)

The last step is verifying scaled data properties:
Again we have:
scaled_value = (original_value - mean) / standard_deviation

for the 1st value: v_1 = 10 m/s
```
scaled = (10 - 11.25) / 2.986
       = (-1.25) / 2.986
       = -0.418
```
The same apply for three values left, the scaled values are 1.256, -1.088, 0.251
Check Scaled Training Data:
```
Scaled_wind_speeds = [-0.418, 1.256, -1.088, 0.251]
Mean = (-0.418 + 1.256 - 1.088 + 0.251) / 4 = 0.001 ≈ 0
Std = √[Σ(x²)/(n-1)] = √[(0.175 + 1.578 + 1.184 + 0.063)/3] = √[3.000/3] = 1.000
```
All scaled features now have:
- Mean ≈ 0
- Standard Deviation = 1
- Equal influence on distance calculations

## 1.7 Visualizsation - understanding the model
```
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
```


```
# Create a 2D grid by fixing air density
ws_grid = np.linspace(2, 20, 80)      # 80 points from 2 to 20 m/s
ti_grid = np.linspace(0.02, 0.25, 80) # 80 points from 0.02 to 0.25
```

What ```mesgrid``` does:
Before:
```
ws_grid = [2, 3, 4]        # Only 3 points for simplicity
ti_grid = [0.02, 0.03]     # Only 2 points for simplicity
```
and after:
```
WS = [[2, 3, 4],           # 2x3 grid of wind speeds
      [2, 3, 4]]
      
TI = [[0.02, 0.02, 0.02],  # 2x3 grid of turbulence values  
      [0.03, 0.03, 0.03]]
```
It creates ALL combinations:
- (ws=2, ti=0.02), (ws=3, ti=0.02), (ws=4, ti=0.02)
- (ws=2, ti=0.03), (ws=3, ti=0.03), (ws=4, ti=0.03)

FIX AIR DENSITY
```
rho_fixed = np.full_like(WS, 1.225)  # Constant air density
```
result:
```
rho_fixed = [[1.225, 1.225, 1.225],
             [1.225, 1.225, 1.225]]
```
Now we have 3D data in 2D arrays:
- WS: Wind speed variations
- TI: Turbulence variations
- rho_fixed: Constant air density

Prepare for prediction
A problem arises KNN expects 1D feature arrays, but we have 2D grids, then a solution is:
                     Convert 2D → 1D → predict → 1D → 2D
```
grid_X = np.column_stack([WS.ravel(), rho_fixed.ravel(), TI.ravel()])
```
What ```.ravel()``` does:
Before ```.ravel()```:
```
WS = [[2, 3, 4],        # 2x3 grid
      [2, 3, 4]]
      
WS.ravel() = [2, 3, 4, 2, 3, 4]  # Flattened to 1D
```
After ```column_stack```:
```
grid_X = [
    [2,   1.225, 0.02],   # Combination 1
    [3,   1.225, 0.02],   # Combination 2  
    [4,   1.225, 0.02],   # Combination 3
    [2,   1.225, 0.03],   # Combination 4
    [3,   1.225, 0.03],   # Combination 5
    [4,   1.225, 0.03]    # Combination 6
]
```
Make predictins
```
grid_X_scaled = scaler.transform(grid_X)      # Scale the features
grid_pred_1d = knn.predict(grid_X_scaled)     # Get predictions (1D array)
```
Predictions come back as 1D:
```
grid_pred_1d = [150, 450, 800, 140, 430, 780]  # Power predictions for each point
```
then, reshape back to 2D for plotting:
```
grid_pred = grid_pred_1d.reshape(WS.shape)
```
What ```.reshape()``` does:
```
# Before reshape (1D):
grid_pred_1d = [150, 450, 800, 140, 430, 780]

# After reshape to WS.shape (which is 2x3):
grid_pred = [[150, 450, 800],
             [140, 430, 780]]
```
1.8 Making new predictions
```
new_point = np.array([[11.5, 1.24, 0.08]])  # ws, density, turbulence
new_point_scaled = scaler.transform(new_point)
new_pred = knn.predict(new_point_scaled)[0]
```

- Create new data point as 2D array
- Scale using SAME scaler as training data
- Predict and extract single value with [0]
![Result](/images/output_off_example_KNN.png)


You can also download code through (this link)[/files/KNN_part2_pratice.ipynb]:
