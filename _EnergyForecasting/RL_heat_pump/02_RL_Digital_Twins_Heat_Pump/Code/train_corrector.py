import os
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
import joblib
from environment.heatpump_env import HeatPumpStorageEnv

# Ensure folders exist
os.makedirs("Data", exist_ok=True)

print("Initializing environments...")
# True parameters representing actual environmental behavior
env_true = HeatPumpStorageEnv(C=50.0, beta=0.5)
# Corrupted parameters representing model error inside physical model
env_corrupt = HeatPumpStorageEnv(C=42.0, beta=0.6)

n_steps = min(env_true.n_steps, env_corrupt.n_steps)
X, y = [], []

print("Simulating and generating residual dataset...")
for t in range(0, n_steps - 30, 24):
    env_true.time_idx = t
    env_corrupt.time_idx = t
    env_true.T_storage = 60.0
    env_corrupt.T_storage = 60.0
    
    for _ in range(24):
        # Apply random heat pump power actions to explore states
        action = [np.random.uniform(0.0, 1.0)]
        
        # Read temperature and price before step
        Tamb = env_true.temp[env_true.time_idx]
        current_price = env_true.price[env_true.time_idx]
        
        _, _, _, _, _ = env_true.step(action)
        _, _, _, _, _ = env_corrupt.step(action)
        
        SOC_true = (env_true.T_storage - env_true.T_min) / (env_true.T_max - env_true.T_min)
        SOC_corr = (env_corrupt.T_storage - env_corrupt.T_min) / (env_corrupt.T_max - env_corrupt.T_min)
        
        # Store features and the mismatch (target residual)
        X.append([Tamb, SOC_corr, current_price])
        y.append(SOC_true - SOC_corr)

print(f"Dataset generated with {len(X)} samples. Training Gradient Boosting corrector...")
X = np.array(X)
y = np.array(y)

model = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
model.fit(X, y)

# Save the trained corrector model
model_path = "Data/residual_corrector.pkl"
joblib.dump(model, model_path)
print(f"Digital Twin corrector model successfully saved to: {model_path}")
