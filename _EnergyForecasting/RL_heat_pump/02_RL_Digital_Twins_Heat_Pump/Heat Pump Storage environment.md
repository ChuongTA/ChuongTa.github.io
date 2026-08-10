We’ll build your **custom heat pump + storage environment** from scratch, train an RL agent on it using **your own weather and electricity price data**, and layer the digital twin correction on top. This gives you full control and directly matches your earlier equations (1–7).

Below is a complete, runnable project skeleton — copy, fill in your data files, and run.

---

## Project Structure

```
rl-heatpump-dt/
├── data/
│   ├── temperature.csv            # your hourly outdoor temp data
│   └── price.csv                  # your hourly electricity price data
├── environment/
│   └── heatpump_env.py            # custom Gym environment
├── models/
│   ├── price_forecaster.py        # (optional) if you want to forecast
│   └── residual_corrector.py      # digital twin ML corrector
├── train_rl.py                    # main script to train PPO
├── evaluate.py                    # run trained agent and plot results
├── generate_training_data.py      # one-off script to collect residual data
├── requirements.txt
└── README.md
```

---

## 1. The Gym Environment (`environment/heatpump_env.py`)

This implements equations (1)–(7) from your concept note, using your data.

**Key configuration parameters (you can tweak them):**

```python
class HeatPumpStorageEnv(gym.Env):
    def __init__(self, 
                 temp_csv='data/temperature.csv',
                 price_csv='data/price.csv',
                 dt=1.0,          # hours per step
                 C=50.0,          # kWh/K (storage capacity)
                 beta=0.5,        # kW/K pipe loss coefficient
                 kh=2.0,          # kW/K heating demand coefficient
                 cop0=3.0,        # COP at 5°C
                 alpha=0.05,      # COP slope
                 p_max=10.0,      # kW max heat pump electric input
                 T_min=40.0,      # °C minimum storage temp (SOC=0)
                 T_max=80.0,      # °C maximum storage temp (SOC=1)
                 soc_penalty_weight=10.0, # penalty for violating SOC limits
                 use_corrected_state=False):  # digital twin flag
        ...
```

**Observation space** (what the RL agent sees every hour):  
`[T_amb(t), SOC(t), price(t), hour_sin, hour_cos, price_forecast_6h]`  
(or a full 24h forecast if you have it). We’ll include a 6‑hour look‑ahead from your price CSV as a simple forecast.

**Action:** Continuous value `a ∈ [0,1]`, multiplied by `p_max` to get heat pump electric power.

**Reward:**  
`r(t) = - price(t) * P_elec(t) * dt - penalty`  
where `penalty` is added if SOC drops below 0.05 or exceeds 0.95 (safety limits).

**Full code (`environment/heatpump_env.py`):**

```python
import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces

class HeatPumpStorageEnv(gym.Env):
    metadata = {'render_modes': ['human']}

    def __init__(self, temp_csv='data/temperature.csv',
                 price_csv='data/price.csv',
                 dt=1.0,
                 C=50.0, beta=0.5, kh=2.0,
                 cop0=3.0, alpha=0.05,
                 p_max=10.0,
                 T_min=40.0, T_max=80.0,
                 soc_penalty_weight=10.0,
                 forecast_horizon=6,
                 use_corrected_state=False):
        super().__init__()
        # Physical parameters
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

        # Load data
        self.temp_data = pd.read_csv(temp_csv, parse_dates=['timestamp'], index_col='timestamp')
        self.price_data = pd.read_csv(price_csv, parse_dates=['timestamp'], index_col='timestamp')
        # Assume both have columns 'value' or similar; align by hourly index
        self.temp = self.temp_data['value'].values  # outdoor temp
        self.price = self.price_data['value'].values  # electricity price (e.g., SEK/kWh)
        self.n_steps = min(len(self.temp), len(self.price))
        self.time_idx = 0

        # State: T_amb, SOC, current price, hour_sin, hour_cos, price_forecast (6h)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf,
                                            shape=(3 + 2 + self.forecast_horizon,),
                                            dtype=np.float32)
        # Action: heat pump electric power fraction [0,1]
        self.action_space = spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)

        # Internal state
        self.T_storage = 60.0  # initial temperature

    def _get_state(self):
        Tamb = self.temp[self.time_idx]
        P_elec_price = self.price[self.time_idx]
        hour_of_day = (self.time_idx % 24) / 24.0 * 2 * np.pi
        hour_sin = np.sin(hour_of_day)
        hour_cos = np.cos(hour_of_day)

        # Simple forecast: next forecast_horizon prices (wrap around if end)
        if self.time_idx + self.forecast_horizon < self.n_steps:
            price_forecast = self.price[self.time_idx+1:self.time_idx+self.forecast_horizon+1]
        else:
            price_forecast = np.zeros(self.forecast_horizon)
        price_forecast = np.array(price_forecast, dtype=np.float32)

        SOC = (self.T_storage - self.T_min) / (self.T_max - self.T_min)
        SOC = np.clip(SOC, 0.0, 1.0)

        if self.use_corrected_state:
            # Placeholder: apply your digital twin correction model here
            # e.g., SOC_corrected = self.corrector.predict([...]) + SOC
            pass

        return np.array([Tamb, SOC, P_elec_price, hour_sin, hour_cos] + list(price_forecast),
                        dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.time_idx = np.random.randint(0, self.n_steps - 24*30)  # random start
        self.T_storage = 60.0  # or random between T_min+5 and T_max-5
        return self._get_state(), {}

    def step(self, action):
        action = np.clip(action, 0.0, 1.0)
        P_elec = action[0] * self.p_max  # kW electric
        Tamb = self.temp[self.time_idx]
        COP = self.cop0 + self.alpha * (Tamb - 5.0)
        Q_hp = P_elec * COP  # heat added

        # Demands and losses (kW)
        Q_heat = self.kh * max(0, 18 - Tamb)  # heating demand
        Q_loss = self.beta * max(0, self.T_storage - Tamb)

        # Energy balance (kWh change in one dt hour)
        delta_E = (Q_hp - Q_heat - Q_loss) * self.dt
        self.T_storage += delta_E / self.C
        self.T_storage = np.clip(self.T_storage, self.T_min - 10, self.T_max + 10)

        SOC = (self.T_storage - self.T_min) / (self.T_max - self.T_min)
        SOC = np.clip(SOC, 0.0, 1.0)

        # Reward: negative electricity cost minus safety penalty
        cost = self.price[self.time_idx] * P_elec * self.dt
        penalty = 0.0
        if SOC < 0.05:
            penalty = self.soc_penalty_weight * (0.05 - SOC) ** 2
        elif SOC > 0.95:
            penalty = self.soc_penalty_weight * (SOC - 0.95) ** 2
        reward = -cost - penalty

        self.time_idx += 1
        terminated = self.time_idx >= self.n_steps - 1
        truncated = False

        return self._get_state(), reward, terminated, truncated, {}
```

---

## 2. Generating Residual Training Data for the Digital Twin

You’ll run the environment once with **true** parameters (the ones you believe are correct) and once with **corrupted** parameters (e.g., storage capacity off by 20%, pipe loss wrong). Record SOC estimates from both and train a corrector.

**`generate_training_data.py`**

```python
import numpy as np
import pandas as pd
from environment.heatpump_env import HeatPumpStorageEnv

# True environment
env_true = HeatPumpStorageEnv(C=50.0, beta=0.5, use_corrected_state=False)
# Corrupted environment (wrong params)
env_corrupt = HeatPumpStorageEnv(C=40.0, beta=0.6, use_corrected_state=False)

n_steps = min(env_true.n_steps, env_corrupt.n_steps)
X, y = [], []
for t in range(n_steps):
    # Reset both to same timestep to align
    env_true.time_idx = t
    env_corrupt.time_idx = t
    state_true, _ = env_true.reset()  # this sets T_storage to 60, but we can force
    state_corrupt, _ = env_corrupt.reset()
    # Overwrite initial temp to same value for comparison
    env_true.T_storage = 60.0
    env_corrupt.T_storage = 60.0
    # Collect SOCs after one dummy step with zero action
    _, _, _, _, _ = env_true.step([0.0])
    _, _, _, _, _ = env_corrupt.step([0.0])
    SOC_true = (env_true.T_storage - env_true.T_min) / (env_true.T_max - env_true.T_min)
    SOC_corr = (env_corrupt.T_storage - env_corrupt.T_min) / (env_corrupt.T_max - env_corrupt.T_min)
    # Features: T_amb, SOC_corr, current price (use same as at timestep t)
    Tamb = env_true.temp[t]
    price = env_true.price[t]
    X.append([Tamb, SOC_corr, price])
    y.append(SOC_true - SOC_corr)

# Save for training
np.save('data/X_residual.npy', np.array(X))
np.save('data/y_residual.npy', np.array(y))
```

Then train the corrector (`models/residual_corrector.py`):

```python
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
import joblib

X = np.load('data/X_residual.npy')
y = np.load('data/y_residual.npy')

model = GradientBoostingRegressor(n_estimators=100, max_depth=5)
model.fit(X, y)

joblib.dump(model, 'models/residual_corrector.pkl')
print("Residual corrector trained.")
```

---

## 3. Training the RL Agent

**`train_rl.py`**

```python
from environment.heatpump_env import HeatPumpStorageEnv
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback
import joblib

# Load the corrector if you want to use digital-twin-corrected observations
use_dt = False  # toggle to True after you have corrector trained
corrector = None
if use_dt:
    corrector = joblib.load('models/residual_corrector.pkl')

# Create environment (no correction at first)
env = HeatPumpStorageEnv(use_corrected_state=False)
# If you want corrected state inside the env, you need to modify env to accept the corrector
# (We'll keep it simple for now; you can add a set_corrector method later)

eval_env = HeatPumpStorageEnv(use_corrected_state=False)

# PPO model
model = PPO("MlpPolicy", env, verbose=1,
            learning_rate=3e-4, n_steps=2048, batch_size=64,
            n_epochs=10, gamma=0.99, device='cpu')

eval_callback = EvalCallback(eval_env, best_model_save_path='./logs/',
                             log_path='./logs/', eval_freq=10000)

model.learn(total_timesteps=200_000, callback=eval_callback)
model.save("ppo_heatpump_storage")
print("Training finished.")
```

---

## 4. Evaluation and Plots

**`evaluate.py`**

```python
import matplotlib.pyplot as plt
from environment.heatpump_env import HeatPumpStorageEnv
from stable_baselines3 import PPO

env = HeatPumpStorageEnv()
model = PPO.load("ppo_heatpump_storage")

obs, _ = env.reset()
soc_history, price_history, action_history = [], [], []
for _ in range(24*7):  # one week
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, _ = env.step(action)
    soc = obs[1]
    price = obs[2]
    soc_history.append(soc)
    price_history.append(price)
    action_history.append(action[0])
    if terminated or truncated:
        break

fig, ax = plt.subplots(3, 1, figsize=(12,8))
ax[0].plot(soc_history, label='Storage SOC')
ax[0].set_ylabel('SOC')
ax[0].legend()
ax[1].plot(price_history, label='Electricity price')
ax[1].set_ylabel('Price (SEK/kWh)')
ax[1].legend()
ax[2].step(range(len(action_history)), action_history, label='HP power fraction')
ax[2].set_ylabel('Action')
ax[2].set_xlabel('Hour')
ax[2].legend()
plt.tight_layout()
plt.savefig('rl_results.png')
plt.show()
```

---

## 5. Plugging in Your Data

You said you already have **electricity price model** and **weather data**. Place them as:

- `data/temperature.csv` – must have columns `timestamp` and `value` (hourly outdoor temperature in °C).
- `data/price.csv` – same format, `timestamp` and `value` (hourly electricity price, e.g., SEK/kWh).

If your data covers a full year, the environment will run through it. You can also use your own synthetic price model to generate a CSV before training.

---

## 6. Integrating the Digital Twin Correction into RL

After training the corrector, you can modify the environment to use it:

In `heatpump_env.py`, add a method:

```python
def set_corrector(self, corrector):
    self.corrector = corrector
```

Then inside `_get_state()`, after computing SOC from raw physics, if `self.use_corrected_state` and hasattr(self, 'corrector'):
```python
features = np.array([[self.temp[self.time_idx], SOC, self.price[self.time_idx]]])
residual = self.corrector.predict(features)[0]
SOC += residual
SOC = np.clip(SOC, 0.0, 1.0)
```

Now you can train two agents: one that sees raw SOC (from corrupted physics) and one that sees corrected SOC, and compare cost savings.

---

## 7. Requirements

**`requirements.txt`**

```
gymnasium
stable-baselines3
numpy
pandas
matplotlib
scikit-learn
joblib
```

---

This gives you a complete, RL‑ready **custom heat pump + storage environment** using your own data, with a built‑in digital twin correction path. Run it, tune the physics parameters to match a realistic small district, and you’ll have a strong GitHub showcase that directly demonstrates the skills you described in your PhD application.