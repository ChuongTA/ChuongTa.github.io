import os
import joblib
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from environment.heatpump_env import HeatPumpStorageEnv

# Paths
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
corrector_path = os.path.join(CODE_DIR, "Data", "residual_corrector.pkl")
model_path = os.path.join(CODE_DIR, "ppo_heatpump_storage")

# Load models
print("Loading models for evaluation...")
corrector = joblib.load(corrector_path) if os.path.exists(corrector_path) else None
model = PPO.load(model_path) if os.path.exists(model_path + ".zip") else None

if model is None:
    raise FileNotFoundError("Trained PPO model not found. Please train the model first by running train_rl.py")

# Create evaluation environment
env = HeatPumpStorageEnv(use_corrected_state=(corrector is not None), corrector=corrector)
obs, _ = env.reset()

# Force starting index for evaluation visualization
env.time_idx = 1000  # Pick a stable point

# Run evaluation for 1 week (168 hours)
hours = 168
soc_hist, price_hist, action_hist, temp_hist = [], [], [], []

print(f"Simulating heat pump operations for {hours} hours...")
for _ in range(hours):
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)
    
    # Store variables
    soc_hist.append((env.T_storage - env.T_min) / (env.T_max - env.T_min))
    price_hist.append(env.price[env.time_idx - 1])
    action_hist.append(action[0])
    temp_hist.append(env.temp[env.time_idx - 1])

# Plotting Results
print("Generating evaluation plots...")
time_steps = np.arange(hours)

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

# 1. Temperature & Prices
ax1.plot(time_steps, temp_hist, color='orange', label='Outdoor Temperature (°C)', linewidth=1.5)
ax1_twin = ax1.twinx()
ax1_twin.step(time_steps, price_hist, color='blue', label='Day-ahead Price (EUR/MWh)', alpha=0.6, where='mid')
ax1.set_ylabel('Temperature (°C)', color='orange')
ax1_twin.set_ylabel('Price (EUR/MWh)', color='blue')
ax1.set_title('Stockholm Climate & Day-Ahead Spot Prices')
ax1.grid(True, linestyle='--', alpha=0.5)

# 2. State of Charge (SOC)
ax2.plot(time_steps, soc_hist, color='green', label='Storage SOC', linewidth=2)
ax2.axhline(0.05, color='red', linestyle=':', label='Min Safety SOC (5%)')
ax2.axhline(0.95, color='red', linestyle=':', label='Max Safety SOC (95%)')
ax2.set_ylabel('State of Charge (SOC)')
ax2.set_ylim(-0.05, 1.05)
ax2.set_title('Thermal Storage Tank State of Charge')
ax2.legend(loc='lower left')
ax2.grid(True, linestyle='--', alpha=0.5)

# 3. Action Output (Compressor Power)
ax3.step(time_steps, action_hist, color='purple', label='HP Action (0-1)', where='mid', linewidth=1.5)
ax3.set_ylabel('Action (Compressor Power)')
ax3.set_xlabel('Hours')
ax3.set_ylim(-0.05, 1.05)
ax3.set_title('RL Agent Compressor Load Adjustments')
ax3.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()

# Save evaluation plot
out_plot_path = os.path.join(CODE_DIR, "Data", "evaluation_results.png")
plt.savefig(out_plot_path, dpi=300)
print(f"Evaluation plot successfully saved to: {out_plot_path}")
plt.show()
