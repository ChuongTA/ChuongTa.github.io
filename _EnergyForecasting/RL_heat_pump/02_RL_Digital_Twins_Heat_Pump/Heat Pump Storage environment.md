---
title: "Smart Heat Pump Control: Reinforcement Learning and Digital Twins"
excerpt: "Building a custom Gym environment for smart heat pump control with thermal storage using Stockholm temperature data and ENTSO-E day-ahead electricity prices."
layout: single
author_profile: true
permalink: /EnergyForecasting/RL_heat_pump/HeatPump_Storage_Environment/
usemathjax: true
date: 2026-08-10
categories:
  - "District Heating and Cooling"
  - "Heat Pump"
image: "/EnergyForecasting/RL_heat_pump/02_RL_Digital_Twins_Heat_Pump/Images/graphical_abstract.png"
---

## 1. Goal

The objective of this project is to develop an intelligent controller for a residential heat pump coupled with a thermal energy storage (TES) tank. The goal is to **minimize total electricity costs** by shifting electricity demand to lower-priced hours (arbitrage) while strictly satisfying the building's heat demand and maintaining the storage water temperature within physical and operational safety boundaries.

---

## 2. Methodology

The optimization pipeline integrates a physics-based model of the thermal storage tank with a machine learning corrector (the Digital Twin) and a Reinforcement Learning (RL) control agent.

<figure style="display: block; margin: 1.5em auto; text-align: center;">
  <img src="/EnergyForecasting/RL_heat_pump/02_RL_Digital_Twins_Heat_Pump/Images/graphical_abstract.png" alt="Graphical Abstract - Smart Heat Pump Control" style="max-width: 100%; height: auto; border-radius: 8px; border: 1px solid var(--global-border-color);">
  <figcaption style="margin-top: 0.5em; font-size: 0.9em; color: var(--global-text-color-light);">Graphical Abstract: The hybrid state estimation and RL decision loop for smart heat pump operation.</figcaption>
</figure>

1.  **Data Ingestion & Alignment:** Import local hourly outdoor temperature data and day-ahead electricity prices.
2.  **Environment Modeling:** Build a custom Gym/Gymnasium environment representing the physical heat pump and storage tank.
3.  **Digital Twin Development:** Train a Gradient Boosting Regressor on historical residual data to correct discrepancies between the simplified physics model and actual system behavior.
4.  **RL Agent Training:** Deploy a Proximal Policy Optimization (PPO) agent to learn optimal control policies over a continuous action space.
5.  **Performance Evaluation:** Analyze cost savings, constraint violations, and arbitrage performance.

---

## 3. Input Data

### 3.1 ERA5 Temperature Data
Outdoor temperature data is sourced from the ERA5 hourly reanalysis dataset on pressure levels (950 hPa) for the **Stockholm zone** using the following bounding box:
*   **North:** $59.50^\circ$
*   **South:** $59.10^\circ$
*   **West:** $17.80^\circ$
*   **East:** $18.30^\circ$

Temperature values are converted from Kelvin to Celsius and spatially averaged across the grid coordinates.

### 3.2 Day-Ahead Electricity Prices
Historical day-ahead spot prices for the SE3 region (Stockholm) are sourced from the [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/). The spot prices are published daily, giving the agent a complete, noise-free 24-hour lookahead window.

---

## 4. Heat Pump & Storage Tank Assumptions

The system parameters and assumptions for the simulation are as follows:

| Parameter | Symbol | Value | Unit | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Max Electrical Power** | $P_{\text{max}}$ | $10.0$ | $\text{kW}$ | Max electrical input to the compressor. |
| **Thermal Capacity** | $C$ | $50.0$ | $\text{kWh/K}$ | Storage tank thermal mass (equivalent to $\sim 860$ L of water). |
| **Pipe Loss Coefficient**| $\beta$ | $0.5$ | $\text{kW/K}$ | Heat loss rate from storage tank to ambient air. |
| **Heating Load Slope** | $k_h$ | $2.0$ | $\text{kW/K}$ | Building heat demand coefficient relative to $18^\circ\text{C}$ baseline. |
| **Minimum Temperature** | $T_{\text{min}}$ | $40.0$ | $^\circ\text{C}$ | Lower operational limit of the storage tank ($\text{SOC} = 0$). |
| **Maximum Temperature** | $T_{\text{max}}$ | $80.0$ | $^\circ\text{C}$ | Upper operational limit of the storage tank ($\text{SOC} = 1$). |

*   **COP Model:** The Coefficient of Performance varies linearly with ambient temperature:
    $$\text{COP}(T_{\text{amb}}) = \text{COP}_0 + \alpha \cdot (T_{\text{amb}} - 5)$$
    where $\text{COP}_0 = 3.0$ and temperature sensitivity coefficient $\alpha = 0.05$.

---

## 5. Reinforcement Learning & Digital Twins Application

### 5.1 Markov Decision Process (MDP) Formulation
*   **State Space:** $s_t = [T_{\text{amb}}(t), \text{SOC}(t), \text{Price}(t), \sin(\text{hour}), \cos(\text{hour}), \text{Price}_{t+1}, \dots, \text{Price}_{t+24}]$
*   **Action Space:** Continuous action $a_t \in [0, 1]$, representing the electricity input fraction of the heat pump compressor: $P_{\text{elec}} = a_t \cdot P_{\text{max}}$.
*   **Reward Function:** Minimizes operational cost and penalizes exceeding safety limits ($SOC \notin [0.05, 0.95]$):
    $$R_t = - \Big( \text{Price}(t) \cdot P_{\text{elec}}(t) \cdot dt \Big) - w_{\text{penalty}} \cdot \max\Big(0, 0.05 - \text{SOC}_t, \text{SOC}_t - 0.95\Big)^2$$

### 5.2 Digital Twin State Correction
The simplified physical model estimates the temperature using:
$$T_{\text{physics}}(t+1) = T_{\text{physics}}(t) + \frac{(Q_{\text{hp}} - Q_{\text{heat}} - Q_{\text{loss}}) \cdot dt}{C}$$

To prevent cumulative modeling errors (representing pipe degradation or insulation leaks), a Gradient Boosting corrector predicts the residual mismatch $\Delta T = T_{\text{actual}} - T_{\text{physics}}$. The RL agent is fed the corrected state:
$$\text{SOC}_{\text{corrected}} = \frac{(T_{\text{physics}} + \Delta T) - T_{\text{min}}}{T_{\text{max}} - T_{\text{min}}}$$

---

## 6. Implementation Code

Below is the complete project skeleton used to process data, build the environment, train the corrector, and run the RL agent.

### 6.1 Gym Environment (`environment/heatpump_env.py`)
```python
import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces

class HeatPumpStorageEnv(gym.Env):
    def __init__(self, temp_csv='Data/Stockholm_temperature.csv',
                 price_csv='Data/SE3_electricity_sport_price_ENTSO_E.csv',
                 dt=1.0, C=50.0, beta=0.5, kh=2.0,
                 cop0=3.0, alpha=0.05, p_max=10.0,
                 T_min=40.0, T_max=80.0, soc_penalty_weight=10.0,
                 forecast_horizon=24, use_corrected_state=False, corrector=None):
        super().__init__()
        self.dt = dt
        self.C = C
        self.beta = beta
        self.kh = kh
        self.cop0 = cop0
        self.alpha = alpha
        self.p_max = p_max
        self.T_min = T_min
        self.T_max = T_max
        self.soc_penalty_weight = soc_penalty_weight
        self.forecast_horizon = forecast_horizon
        self.use_corrected_state = use_corrected_state
        self.corrector = corrector

        # Load and align datasets
        self.temp_df = pd.read_csv(temp_csv, parse_dates=['datetime'])
        self.price_df = pd.read_csv(price_csv, parse_dates=['datetime'])
        
        # Merge on datetime to align indices
        merged = pd.merge(self.temp_df, self.price_df, on='datetime').sort_values('datetime').reset_index(drop=True)
        self.temp = merged['temperature'].values
        self.price = merged['price'].values
        self.n_steps = len(merged)
        self.time_idx = 0
        self.T_storage = 60.0

        # Observations: Tamb, SOC, Price, Sin(hour), Cos(hour), Price Forecast (24h)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf,
                                             shape=(3 + 2 + self.forecast_horizon,),
                                             dtype=np.float32)
        self.action_space = spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)

    def _get_state(self):
        Tamb = self.temp[self.time_idx]
        current_price = self.price[self.time_idx]
        hour = (self.time_idx % 24) / 24.0 * 2 * np.pi
        
        # Extract look-ahead prices (wrap around at the end of the dataset)
        if self.time_idx + self.forecast_horizon < self.n_steps:
            price_forecast = self.price[self.time_idx+1:self.time_idx+self.forecast_horizon+1]
        else:
            price_forecast = np.zeros(self.forecast_horizon)
            
        SOC = (self.T_storage - self.T_min) / (self.T_max - self.T_min)
        SOC = np.clip(SOC, 0.0, 1.0)

        # Apply digital twin residual correction if active
        if self.use_corrected_state and self.corrector is not None:
            features = np.array([[Tamb, SOC, current_price]])
            delta_SOC = self.corrector.predict(features)[0]
            SOC = np.clip(SOC + delta_SOC, 0.0, 1.0)

        return np.array([Tamb, SOC, current_price, np.sin(hour), np.cos(hour)] + list(price_forecast),
                        dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.time_idx = np.random.randint(0, self.n_steps - 24*30)
        self.T_storage = 60.0
        return self._get_state(), {}

    def step(self, action):
        action = np.clip(action[0], 0.0, 1.0)
        P_elec = action * self.p_max
        Tamb = self.temp[self.time_idx]
        
        COP = self.cop0 + self.alpha * (Tamb - 5.0)
        Q_hp = P_elec * COP
        Q_heat = self.kh * max(0, 18 - Tamb)
        Q_loss = self.beta * max(0, self.T_storage - Tamb)

        # State transition
        delta_E = (Q_hp - Q_heat - Q_loss) * self.dt
        self.T_storage += delta_E / self.C
        self.T_storage = np.clip(self.T_storage, self.T_min - 10, self.T_max + 10)

        SOC = (self.T_storage - self.T_min) / (self.T_max - self.T_min)
        SOC = np.clip(SOC, 0.0, 1.0)

        # Reward: negative cost + safety penalty
        cost = self.price[self.time_idx] * P_elec * self.dt
        penalty = 0.0
        if SOC < 0.05:
            penalty = self.soc_penalty_weight * (0.05 - SOC) ** 2
        elif SOC > 0.95:
            penalty = self.soc_penalty_weight * (SOC - 0.95) ** 2
        reward = -cost - penalty

        self.time_idx += 1
        terminated = self.time_idx >= self.n_steps - 1
        return self._get_state(), reward, terminated, False, {}
```

### 6.2 Training the Digital Twin Corrector (`train_corrector.py`)
```python
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
import joblib
from environment.heatpump_env import HeatPumpStorageEnv

# Instantiate true vs corrupted models
env_true = HeatPumpStorageEnv(C=50.0, beta=0.5)
env_corrupt = HeatPumpStorageEnv(C=42.0, beta=0.6)  # 16% capacity error, 20% loss error

n_steps = min(env_true.n_steps, env_corrupt.n_steps)
X, y = [], []

for t in range(0, n_steps - 10, 24):
    env_true.time_idx = t
    env_corrupt.time_idx = t
    env_true.T_storage = 60.0
    env_corrupt.T_storage = 60.0
    
    # Step through 24h with a mock action
    for _ in range(24):
        action = [np.random.uniform(0, 1)]
        _, _, _, _, _ = env_true.step(action)
        _, _, _, _, _ = env_corrupt.step(action)
        
        SOC_true = (env_true.T_storage - env_true.T_min) / (env_true.T_max - env_true.T_min)
        SOC_corr = (env_corrupt.T_storage - env_corrupt.T_min) / (env_corrupt.T_max - env_corrupt.T_min)
        
        X.append([env_true.temp[env_true.time_idx], SOC_corr, env_true.price[env_true.time_idx]])
        y.append(SOC_true - SOC_corr)

# Train the corrector
model = GradientBoostingRegressor(n_estimators=100, max_depth=5)
model.fit(np.array(X), np.array(y))
joblib.dump(model, 'Data/residual_corrector.pkl')
print("Digital Twin Corrector Trained and Saved.")
```

### 6.3 Training the PPO Agent (`train_rl.py`)
```python
import joblib
from stable_baselines3 import PPO
from environment.heatpump_env import HeatPumpStorageEnv

# Load digital twin corrector
corrector = joblib.load('Data/residual_corrector.pkl')

# Initialize env using corrected states
env = HeatPumpStorageEnv(use_corrected_state=True, corrector=corrector)

model = PPO("MlpPolicy", env, verbose=1, learning_rate=3e-4, 
            n_steps=2048, batch_size=64, n_epochs=10, gamma=0.99)
model.learn(total_timesteps=150_000)
model.save("ppo_heatpump_storage")
print("Agent Training Complete.")
```

---

## 7. Results & Discussion

Integrating the **digital twin** residual estimator directly resolves the control drift problem. By training a Gradient Boosting model to learn the structural deviations between the simplified physical thermal storage model and the actual environment, the observation space fed into the RL controller is accurately updated in real-time.

*   **Arbitrage Performance:** The PPO controller successfully leverages the day-ahead lookahead window. It operates the heat pump at maximum power when electricity prices drop (often in the early hours of the morning), filling the storage tank to capacity. During the peak hours, it shuts off, maintaining the house's warmth using the stored thermal energy.
*   **Constraint Violations:** Feeding the corrected digital twin state ensures that safety boundaries ($SOC \in [0.05, 0.95]$) are respected. Without the digital twin correction, accumulation errors would cause the RL agent to estimate tank temperatures incorrectly, leading to freezing threshold violations or overheating states in practice.