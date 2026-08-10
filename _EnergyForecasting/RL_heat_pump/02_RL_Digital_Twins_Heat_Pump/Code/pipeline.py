"""
Heat Pump Digital Twin + RL control pipeline.

Run one stage at a time, or the whole thing:

    python pipeline.py --stage data        # ERA5 + ENTSO-E raw files -> clean CSVs
    python pipeline.py --stage corrector   # train the digital-twin residual corrector
    python pipeline.py --stage train       # train the PPO control agent
    python pipeline.py --stage evaluate    # run the trained agent for one week, save metrics + plots
    python pipeline.py --stage all         # run every stage in order (default)

Requires: numpy, pandas, xarray, gymnasium, scikit-learn, joblib,
stable-baselines3, matplotlib (see requirements.txt).
"""
import argparse
import glob
import os

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

from environment.heatpump_env import HeatPumpStorageEnv

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CODE_DIR, "Data")
TEMP_DIR = os.path.join(DATA_DIR, "01_Temperature_Data")
PRICE_DIR = os.path.join(DATA_DIR, "00_Electricity_price")
RESULTS_DIR = os.path.join(CODE_DIR, "Results")

CORRECTOR_PATH = os.path.join(RESULTS_DIR, "residual_corrector.pkl")
MODEL_PATH = os.path.join(CODE_DIR, "ppo_heatpump_storage")
VECNORM_PATH = os.path.join(CODE_DIR, "vecnormalize.pkl")

# ---------------------------------------------------------------------------
# Hyperparameters - single source of truth (also quoted in the blog post).
# ---------------------------------------------------------------------------
ENV_TRUE_KWARGS = dict(C=50.0, beta=0.03)       # "actual" physical system
ENV_CORRUPT_KWARGS = dict(C=42.0, beta=0.036)   # drifted model (~15-20% error)
CORRECTOR_PARAMS = dict(n_estimators=100, max_depth=5, random_state=42)
PPO_HYPERPARAMS = dict(
    policy="MlpPolicy",
    learning_rate=3e-4,
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    ent_coef=0.01,   # small entropy bonus prevents premature collapse to a fixed action
    device="cpu",    # CPU is faster than GPU for this small MLP + state space
)
TOTAL_TIMESTEPS = 150_000
EVAL_HOURS = 168        # one week
EVAL_START_IDX = 1000   # fixed index so evaluation is reproducible


# ---------------------------------------------------------------------------
# Stage 1: raw ERA5 / ENTSO-E files -> clean, aligned input CSVs
# ---------------------------------------------------------------------------
def process_data():
    print("--- Processing ERA5 temperature data ---")
    temp_dfs = []
    for file_path in glob.glob(os.path.join(TEMP_DIR, "*.nc")):
        import xarray as xr
        print(f"Reading: {os.path.basename(file_path)}")
        ds = xr.open_dataset(file_path)
        t_avg = ds["t"].mean(dim=["latitude", "longitude"])
        if "pressure_level" in t_avg.dims:
            t_avg = t_avg.isel(pressure_level=0)
        df = t_avg.to_dataframe().reset_index()
        df["temperature"] = df["t"] - 273.15  # Kelvin -> Celsius
        temp_dfs.append(df[["valid_time", "temperature"]].rename(columns={"valid_time": "datetime"}))

    combined_temp = (
        pd.concat(temp_dfs, ignore_index=True)
        .drop_duplicates(subset=["datetime"])
        .sort_values("datetime")
        .reset_index(drop=True)
    )
    out_temp_path = os.path.join(DATA_DIR, "Stockholm_temperature.csv")
    combined_temp.to_csv(out_temp_path, index=False)
    print(f"Saved: {out_temp_path} ({len(combined_temp)} rows)")

    print("--- Processing ENTSO-E day-ahead price data ---")
    price_dfs = []
    for file_path in glob.glob(os.path.join(PRICE_DIR, "GUI_ENERGY_PRICES_*.csv")):
        print(f"Reading: {os.path.basename(file_path)}")
        df = pd.read_csv(file_path)
        start_str = df["MTU (CET/CEST)"].str.split(" - ").str[0].str.strip()
        start_str = start_str.str.replace(r"\s*\([^)]*\)", "", regex=True).str.strip()
        df["datetime"] = pd.to_datetime(start_str, format="%d/%m/%Y %H:%M:%S", errors="coerce")
        df["price"] = pd.to_numeric(df["Day-ahead Price (EUR/MWh)"], errors="coerce")
        price_dfs.append(df[["datetime", "price"]])

    combined_price = (
        pd.concat(price_dfs, ignore_index=True)
        .drop_duplicates(subset=["datetime"])
        .sort_values("datetime")
        .reset_index(drop=True)
    )
    out_price_path = os.path.join(DATA_DIR, "SE3_electricity_sport_price_ENTSO_E.csv")
    combined_price.to_csv(out_price_path, index=False)
    print(f"Saved: {out_price_path} ({len(combined_price)} rows)")


# ---------------------------------------------------------------------------
# Stage 2: digital-twin residual corrector
# ---------------------------------------------------------------------------
def train_corrector():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("Initializing true vs. corrupted environments...")
    env_true = HeatPumpStorageEnv(**ENV_TRUE_KWARGS)
    env_corrupt = HeatPumpStorageEnv(**ENV_CORRUPT_KWARGS)
    n_steps = min(env_true.n_steps, env_corrupt.n_steps)

    print("Simulating and generating residual dataset...")
    X, y = [], []
    for t in range(0, n_steps - 30, 24):
        env_true.time_idx = env_corrupt.time_idx = t
        env_true.T_storage = env_corrupt.T_storage = 60.0

        for _ in range(24):
            action = [np.random.uniform(0.0, 1.0)]  # random actions to explore the state space
            Tamb = env_true.temp[env_true.time_idx]
            current_price = env_true.price[env_true.time_idx]

            env_true.step(action)
            env_corrupt.step(action)

            soc_true = (env_true.T_storage - env_true.T_min) / (env_true.T_max - env_true.T_min)
            soc_corrupt = (env_corrupt.T_storage - env_corrupt.T_min) / (env_corrupt.T_max - env_corrupt.T_min)

            X.append([Tamb, soc_corrupt, current_price])
            y.append(soc_true - soc_corrupt)  # residual mismatch to learn

    print(f"Dataset generated with {len(X)} samples. Training Gradient Boosting corrector...")
    model = GradientBoostingRegressor(**CORRECTOR_PARAMS)
    model.fit(np.array(X), np.array(y))

    joblib.dump(model, CORRECTOR_PATH)
    print(f"Digital Twin corrector saved to: {CORRECTOR_PATH}")


# ---------------------------------------------------------------------------
# Stage 3: PPO control agent
# ---------------------------------------------------------------------------
def _load_corrector():
    if os.path.exists(CORRECTOR_PATH):
        return joblib.load(CORRECTOR_PATH)
    print("WARNING: Digital Twin corrector not found - running without state correction.")
    return None


def train_rl():
    corrector = _load_corrector()
    make_env = lambda: HeatPumpStorageEnv(use_corrected_state=corrector is not None, corrector=corrector)

    # VecNormalize keeps a running mean/std for observations AND rewards. Without it, the
    # SOC-violation penalty (can spike into the hundreds) dwarfs the per-step electricity
    # cost (a few cents), the value function never learns (explained_variance stays ~0),
    # and PPO collapses onto a single "safe" constant action instead of a real policy.
    vec_env = VecNormalize(DummyVecEnv([make_env]), norm_obs=True, norm_reward=True, clip_reward=10.0)

    print("Initializing PPO agent...")
    model = PPO(env=vec_env, verbose=1, **PPO_HYPERPARAMS)

    print(f"Training PPO for {TOTAL_TIMESTEPS:,} timesteps...")
    model.learn(total_timesteps=TOTAL_TIMESTEPS)

    model.save(MODEL_PATH)
    vec_env.save(VECNORM_PATH)
    print(f"Model saved to: {MODEL_PATH}.zip")
    print(f"Normalization stats saved to: {VECNORM_PATH}")


# ---------------------------------------------------------------------------
# Stage 4: evaluation
# ---------------------------------------------------------------------------
def evaluate():
    if not os.path.exists(MODEL_PATH + ".zip"):
        raise FileNotFoundError("Trained PPO model not found. Run --stage train first.")

    corrector = _load_corrector()
    model = PPO.load(MODEL_PATH)

    vecnorm = None
    if os.path.exists(VECNORM_PATH):
        dummy_env = DummyVecEnv([lambda: HeatPumpStorageEnv(use_corrected_state=corrector is not None, corrector=corrector)])
        vecnorm = VecNormalize.load(VECNORM_PATH, dummy_env)
        vecnorm.training = False

    env = HeatPumpStorageEnv(use_corrected_state=corrector is not None, corrector=corrector)
    obs, _ = env.reset()
    env.time_idx = EVAL_START_IDX
    env.T_storage = 60.0
    start_date = env.temp_df.iloc[env.time_idx]["datetime"]

    print(f"Simulating {EVAL_HOURS} hours of operation...")
    dates_hist, soc_hist, price_hist, action_hist, temp_hist = [], [], [], [], []
    for _ in range(EVAL_HOURS):
        model_input = vecnorm.normalize_obs(obs[None, :])[0] if vecnorm else obs
        action, _ = model.predict(model_input, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)

        dates_hist.append(env.temp_df.iloc[env.time_idx - 1]["datetime"])
        soc_hist.append((env.T_storage - env.T_min) / (env.T_max - env.T_min))
        price_hist.append(env.price[env.time_idx - 1])
        action_hist.append(float(action[0]))
        temp_hist.append(env.temp[env.time_idx - 1])

    os.makedirs(RESULTS_DIR, exist_ok=True)
    eval_df = pd.DataFrame({
        "datetime": dates_hist,
        "outdoor_temperature": temp_hist,
        "electricity_price_eur_mwh": price_hist,
        "storage_soc": soc_hist,
        "compressor_action": action_hist,
    })
    eval_df.to_csv(os.path.join(RESULTS_DIR, "evaluation_results.csv"), index=False)

    total_elec = sum(np.array(action_hist) * env.p_max * env.dt)
    total_cost = sum(np.array(price_hist) / 1000.0 * np.array(action_hist) * env.p_max * env.dt)
    avg_price_paid = total_cost / total_elec * 1000.0 if total_elec > 0 else 0.0
    avg_market_price = float(np.mean(price_hist))
    cost_reduction = (avg_market_price - avg_price_paid) / avg_market_price * 100.0 if total_elec > 0 else 0.0

    summary_path = os.path.join(RESULTS_DIR, "evaluation_summary.txt")
    with open(summary_path, "w") as f:
        f.write("=" * 50 + "\n")
        f.write("HEAT PUMP DIGITAL TWIN EVALUATION REPORT\n")
        f.write("=" * 50 + "\n")
        f.write(f"Simulation Start: {start_date}\n")
        f.write(f"Simulation Duration: {EVAL_HOURS} hours (1 week)\n\n")
        f.write(f"Total Electricity Consumed: {total_elec:.2f} kWh\n")
        f.write(f"Total Operating Cost: {total_cost:.2f} EUR\n")
        f.write(f"Average Spot Price Paid: {avg_price_paid:.2f} EUR/MWh\n")
        f.write(f"Average Market Spot Price: {avg_market_price:.2f} EUR/MWh\n")
        f.write(f"Cost Reduction relative to Market Mean: {cost_reduction:.2f}%\n")
        f.write("=" * 50 + "\n")
    print(f"Summary saved to: {summary_path}")

    time_steps = np.arange(EVAL_HOURS)
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    ax1.plot(time_steps, temp_hist, color="orange", label="Outdoor Temperature (°C)", linewidth=1.5)
    ax1_twin = ax1.twinx()
    ax1_twin.step(time_steps, price_hist, color="blue", alpha=0.6, where="mid", label="Day-ahead Price (EUR/MWh)")
    ax1.set_ylabel("Temperature (°C)", color="orange")
    ax1_twin.set_ylabel("Price (EUR/MWh)", color="blue")
    ax1.set_title("Stockholm Climate & Day-Ahead Spot Prices")
    ax1.grid(True, linestyle="--", alpha=0.5)

    ax2.plot(time_steps, soc_hist, color="green", label="Storage SOC", linewidth=2)
    ax2.axhline(0.05, color="red", linestyle=":", label="Min Safety SOC (5%)")
    ax2.axhline(0.95, color="red", linestyle=":", label="Max Safety SOC (95%)")
    ax2.set_ylabel("State of Charge (SOC)")
    ax2.set_ylim(-0.05, 1.05)
    ax2.set_title("Thermal Storage Tank State of Charge")
    ax2.legend(loc="lower left")
    ax2.grid(True, linestyle="--", alpha=0.5)

    ax3.step(time_steps, action_hist, color="purple", where="mid", linewidth=1.5, label="HP Action (0-1)")
    ax3.set_ylabel("Action (Compressor Power)")
    ax3.set_xlabel("Hours")
    ax3.set_ylim(-0.05, 1.05)
    ax3.set_title("RL Agent Compressor Load Adjustments")
    ax3.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plot_path = os.path.join(RESULTS_DIR, "evaluation_results.png")
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"Plot saved to: {plot_path}")


STAGES = {
    "data": process_data,
    "corrector": train_corrector,
    "train": train_rl,
    "evaluate": evaluate,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--stage", choices=list(STAGES) + ["all"], default="all")
    args = parser.parse_args()

    stages_to_run = STAGES.values() if args.stage == "all" else [STAGES[args.stage]]
    for stage_fn in stages_to_run:
        stage_fn()


if __name__ == "__main__":
    main()
