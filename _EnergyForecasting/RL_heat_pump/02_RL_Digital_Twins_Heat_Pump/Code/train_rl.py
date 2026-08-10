import os
import joblib
from stable_baselines3 import PPO
from environment.heatpump_env import HeatPumpStorageEnv

# Define paths
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
corrector_path = os.path.join(CODE_DIR, "Data", "residual_corrector.pkl")

# Load Digital Twin residual corrector
print("Loading Digital Twin corrector model...")
if os.path.exists(corrector_path):
    corrector = joblib.load(corrector_path)
    use_dt = True
    print("Digital Twin corrector loaded successfully.")
else:
    corrector = None
    use_dt = False
    print("WARNING: Digital Twin corrector not found! Running environment without corrections.")

# Create the training environment
env = HeatPumpStorageEnv(use_corrected_state=use_dt, corrector=corrector)

print("Initializing PPO agent model...")
model = PPO(
    policy="MlpPolicy",
    env=env,
    verbose=1,
    learning_rate=3e-4,
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    device="cpu"  # CPU is faster for small state spaces
)

print("Starting PPO agent training (150,000 timesteps)...")
model.learn(total_timesteps=150_000)

model_save_path = os.path.join(CODE_DIR, "ppo_heatpump_storage")
model.save(model_save_path)
print(f"PPO training finished. Model saved to: {model_save_path}")
