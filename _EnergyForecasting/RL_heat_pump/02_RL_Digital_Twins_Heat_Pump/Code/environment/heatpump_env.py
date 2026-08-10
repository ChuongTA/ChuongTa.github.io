import numpy as np
import pandas as pd
# pyrefly: ignore [missing-import]
import gymnasium as gym
from gymnasium import spaces

class HeatPumpStorageEnv(gym.Env):
    metadata = {'render_modes': ['human']}

    def __init__(self, temp_csv='Data/Stockholm_temperature.csv',
                 price_csv='Data/SE3_electricity_sport_price_ENTSO_E.csv',
                 dt=1.0, C=50.0, beta=0.03, kh=0.3,
                 cop0=3.0, alpha=0.05, p_max=10.0,
                 T_min=40.0, T_max=80.0, soc_penalty_weight=50.0,
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

        # Resolve paths relative to this file
        import os
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        temp_csv_path = os.path.join(base_path, temp_csv)
        price_csv_path = os.path.join(base_path, price_csv)

        # Load aligned datasets
        self.temp_df = pd.read_csv(temp_csv_path, parse_dates=['datetime'])
        self.price_df = pd.read_csv(price_csv_path, parse_dates=['datetime'])
        
        merged = pd.merge(self.temp_df, self.price_df, on='datetime').sort_values('datetime').reset_index(drop=True)
        self.temp = merged['temperature'].values
        self.price = merged['price'].values
        self.n_steps = len(merged)
        self.time_idx = 0
        self.T_storage = 60.0
        self.episode_steps = 0

        # Observation Space: Tamb, SOC, Price, Sin(hour), Cos(hour), Price Forecast (24h)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf,
                                             shape=(3 + 2 + self.forecast_horizon,),
                                             dtype=np.float32)
        
        # Action Space: Heat pump electrical power fraction [0, 1]
        self.action_space = spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)

    def _get_state(self):
        Tamb = self.temp[self.time_idx]
        current_price = self.price[self.time_idx]
        hour = (self.time_idx % 24) / 24.0 * 2 * np.pi
        
        # Get next 24 hours of prices (wrap around at the end of the dataset)
        if self.time_idx + self.forecast_horizon < self.n_steps:
            price_forecast = self.price[self.time_idx+1:self.time_idx+self.forecast_horizon+1]
        else:
            # Pad with current price if at the very end
            remaining = self.n_steps - 1 - self.time_idx
            padding_len = self.forecast_horizon - remaining
            price_forecast = np.concatenate([
                self.price[self.time_idx+1:],
                np.full(padding_len, current_price)
            ])
            
        SOC = (self.T_storage - self.T_min) / (self.T_max - self.T_min)
        SOC = np.clip(SOC, 0.0, 1.0)

        # Apply digital twin corrector if active
        if self.use_corrected_state and self.corrector is not None:
            features = np.array([[Tamb, SOC, current_price]])
            delta_SOC = self.corrector.predict(features)[0]
            SOC = np.clip(SOC + delta_SOC, 0.0, 1.0)

        return np.array([Tamb, SOC, current_price, np.sin(hour), np.cos(hour)] + list(price_forecast),
                        dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.time_idx = np.random.randint(0, self.n_steps - self.forecast_horizon - 24*30)
        self.T_storage = 60.0
        self.episode_steps = 0
        return self._get_state(), {}

    def step(self, action):
        action_val = np.clip(action[0], 0.0, 1.0)
        P_elec = action_val * self.p_max
        Tamb = self.temp[self.time_idx]
        
        COP = self.cop0 + self.alpha * (Tamb - 5.0)
        Q_hp = P_elec * COP
        Q_heat = self.kh * max(0, 18 - Tamb)
        Q_loss = self.beta * max(0, self.T_storage - Tamb)

        # Dynamic update
        delta_E = (Q_hp - Q_heat - Q_loss) * self.dt
        self.T_storage += delta_E / self.C
        self.T_storage = np.clip(self.T_storage, self.T_min - 10, self.T_max + 10)

        SOC = (self.T_storage - self.T_min) / (self.T_max - self.T_min)
        SOC = np.clip(SOC, 0.0, 1.0)

        # Reward: negative electricity cost (convert price from EUR/MWh to EUR/kWh)
        cost = (self.price[self.time_idx] / 1000.0) * P_elec * self.dt
        penalty = 0.0
        if SOC < 0.05:
            penalty = self.soc_penalty_weight * (0.05 - SOC) * 100.0 + 5.0
        elif SOC > 0.95:
            penalty = self.soc_penalty_weight * (SOC - 0.95) * 100.0 + 5.0
        reward = -cost - penalty

        self.time_idx += 1
        self.episode_steps += 1
        terminated = (self.time_idx >= self.n_steps - self.forecast_horizon - 1) or (self.episode_steps >= 720)
        return self._get_state(), reward, terminated, False, {}
