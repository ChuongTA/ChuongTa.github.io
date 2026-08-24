# Part B: Implementation Prototype — Overview

*AI-Agent Development Pipeline for Operational BESS Management (Python)*

This is a working, runnable prototype of the architecture described in Part A, scoped to a single energy community: synthetic load + PV time series, a day-ahead price forecaster with uncertainty bands, an LP-based BESS scheduler, and a multi-provider LLM tool-use agent that answers the two required queries against real solved output.

---

## 1. Pipeline Overview

```
01_Load/                  → Community_Load_Profiles.csv   (double-Gaussian + logistic synthetic load, 1.5 yrs, peak 952 kW)
02_PV_Generation/         → ERA5_PV_Generation_50MW.csv    (ERA5 irradiance scaled to a 50 MW solar farm)
04_Electricity_Price/     → Data.csv                       (DK1 day-ahead spot price, Energi Data Service, 2024-01-01→2025-09-30)
        │
        ▼
05_Optimisation_and_Forecast/bess_optimization.py
        │  1. Merge load + PV + price on timestamp
        │  2. Train LightGBM point forecaster (hour/day-of-week/month + 24h/168h price lags)
        │  3. Binned-residual bootstrap → price_P10 / price_P90 bands
        │  4. Inject ±5%/±12% synthetic forecast error into load/PV for the target day
        │  5. Solve 24-hour LP (scipy.optimize.linprog, HiGHS) for the BESS schedule
        │  6. Write bess_schedule_tomorrow.csv + bess_schedule_simulation.png
        ▼
06_LLM/bess_agent.py
        │  ReAct tool-use loop reading bess_schedule_tomorrow.csv
        ▼
   Query 1 / Query 2 demonstrations
```

Each stage is a standalone, inspectable script/CSV — there is no hidden state, so any stage can be re-run or swapped (e.g. a different LP horizon, a different LLM provider) without touching the others.

---

## 2. Model Selection & Orchestration Framework

* **Forecasting**: `LightGBM` chosen over Quantile Regression Forests for speed/memory at this data volume (see [`Forecasting_Logic.md`](../04_Electricity_Price/Forecasting_Logic.md)). Uncertainty is obtained *without* training separate quantile models — out-of-fold residuals are binned by predicted price level and bootstrapped for P10/P90, capturing heteroscedastic (regime-dependent) uncertainty cheaply.
* **Optimization**: a linear program over a 24-hour horizon, solved with `scipy.optimize.linprog` (HiGHS backend) — decision variables per hour $t$: $P_{\text{ch}}(t), P_{\text{dis}}(t), P_{\text{import}}(t), P_{\text{export}}(t), E(t)$. Objective minimizes `price·import + C_deg·(charge+discharge) − price·export`; constraints enforce the SoC state-transition equation, BESS SoC/power bounds (15–95% SoC, ±500 kW), and the 500 kW grid import/export limit. This is the same formulation as [`BESS_Parameters_and_Physics.md §7`](../03_Storage/BESS_Parameters_and_Physics.md), implemented directly with `linprog` rather than a full Pyomo model — the constraint structure and results are equivalent, at lower dependency overhead for a single-day horizon.
* **Orchestration**: no LangChain/LlamaIndex — a lightweight custom **Model Adapter Router** (`call_llm()` in `bess_agent.py`) so the same agent loop runs unmodified against OpenAI, Anthropic Claude, Google Gemini, DeepSeek, or a local Ollama model, selected by an `api_config` dict or auto-detected from environment API keys. A **mock provider** is included so the full ReAct loop is demonstrable with zero API keys.

---

## 3. Custom Tools (3 implemented)

All three tools live in `bess_agent.py` and read the solved `bess_schedule_tomorrow.csv` (or take arguments directly), so tool outputs always trace back to a concrete optimizer run:

| Tool | Purpose | Inputs | Outputs |
| :--- | :--- | :--- | :--- |
| `bess_simulator` | Simplified charge/discharge physics check | `current_soc`, `power_kw`, `duration_h` | new SoC (%), `violation_detected` flag if outside 15–95% SoC bounds |
| `self_consumption_calculator` | Aggregates local PV vs. local load over a window | `start_time_str`, `end_time_str` | total PV/load (kWh), self-consumption rate (%), exported surplus |
| `electricity_cost_estimator` | Time-of-use cost from spot price × grid flow | `start_time_str`, `end_time_str`, `use_bess` | net grid bill (DKK), with a `no_bess` baseline mode for comparison |

The LLM never computes these figures itself — it emits a structured `{"tool": ..., "parameters": ...}` JSON call, the Python layer executes it deterministically, and the LLM only narrates the returned observation. This is the reliability layer: numeric correctness is guaranteed by code, not by model output.

---

## 4. Time-Series Data Integration

The agent's tools operate on the LP-solved schedule table (`bess_schedule_tomorrow.csv`), which carries, per hour: `price_forecast_dkk_kwh` (+ `price_P10`/`price_P90`), `load_forecast_kw`, `pv_forecast_kw`, `bess_charge_kw`/`bess_discharge_kw`, `bess_soc_percent`, `grid_import_kw`/`grid_export_kw`. This gives every tool a single, consistent source of truth for "what is the plan and why," instead of separate ad hoc calculations per query.

---

## 5. Query Demonstrations

**Query 1** — *"Should we charge or discharge the battery in the next 2 hours given the current conditions?"*
→ Agent emits a `bess_simulator` call (e.g. discharging at −750 kW* over 2h from 50% SoC in the mock path), returns new SoC and whether the action stays within safety bounds, then explains the recommendation in terms of the forecast price trajectory around the current hour.
*(mock-mode default; a live LLM instead reasons from the actual current SoC/price context and may request a different power level.)*

**Query 2** — *"What was our self-consumption rate yesterday and how could it be improved?"*
→ Agent calls `self_consumption_calculator` over the requested day, reports total PV generated, PV self-consumed vs. exported, and the resulting self-consumption %, then suggests improvement levers (e.g. shifting BESS charging to coincide with midday PV surplus rather than cheap night-time grid import).

Both queries are run end-to-end in `bess_agent.py::main()`, printing the full Thought → Action → Observation → Response trace.

---

## 6. Reliability, Monitoring & Failure Handling

* **Deterministic tool execution**: all numeric results come from pandas/numpy/linprog, never from LLM free-text — the LLM only selects and parameters tools and narrates results.
* **Bounded/clamped physics**: `bess_simulator` clamps SoC to [15%, 95%] and raises a `violation_detected` flag rather than silently returning an infeasible state.
* **Graceful data-missing handling**: `self_consumption_calculator` / `electricity_cost_estimator` return an explicit `{"error": ...}` payload (missing schedule CSV, empty time window) instead of raising, so the agent can surface a clear message rather than crashing mid-conversation.
* **Provider-agnostic fallback**: if no API key is configured, the router transparently drops to a rule-based **mock provider** that still exercises the full tool-call loop — useful for CI/offline demos and as a safety net if a live API is unreachable.
* **Provenance**: every tool call reads from a versioned, on-disk `bess_schedule_tomorrow.csv` produced by a single optimizer run, so a monitoring layer only needs to check "is this CSV stale" to know whether the agent's answers reflect the latest forecast — the same staleness check described as the async re-optimization trigger in Part A §1.3.

---

## 7. Known Simplifications (honesty about scope)

* Single-day (24h) LP horizon, not a rolling multi-day horizon.
* Load/PV forecast error is injected synthetically (±5%/±12% Gaussian noise) rather than from a trained load/PV forecaster — acceptable given the exercise's "mock data" allowance, but the day-ahead **price** forecast (LightGBM + binned bootstrap) is the one component trained on real historical data end-to-end.
* EV/heavy-goods charging flexibility (Part A §2/§3) is not yet wired into the LP as a shiftable decision variable in this prototype — it is designed for, not implemented, given the submission deadline.
