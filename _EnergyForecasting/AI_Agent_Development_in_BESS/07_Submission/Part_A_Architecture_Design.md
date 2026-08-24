# Part A: Conceptual Architecture — LLM-Based AI-Agent for Operational BESS Management

*Energy Community BESS Management Advisory Agent*

---

## 1. Agent Architecture

### 1.1 Real-time and forecast data processing

The agent is split into a **fast advisory path** and a **slow optimization path**, both fed by a shared **State & Forecast Cache** that is refreshed on independent clocks:

* **Real-time telemetry** (BESS SoC, PCC power flow, community load, PV output) is polled every **1–5 minutes** from the site SCADA/meter and written to the cache as the current system state $\big(SoC(t),\ P_{\text{load}}(t),\ P_{\text{PV}}(t),\ P_{\text{grid}}(t)\big)$.
* **Forecasts** (day-ahead price $P_{10}/P_{50}/P_{90}$, PV, load, and — going forward — EV/HGV charging demand) are recomputed on a **rolling hourly cadence** (new forecast origin each hour, 24-hour horizon) and cached as forecast tables, not recomputed per query.

The LLM **never re-runs a forecast or optimization on every user turn** — it reads the latest cached state/forecast and calls tools that operate on it. This keeps conversational latency low while forecast/optimization freshness is governed by its own schedule.

### 1.2 Interaction flow: stakeholder ↔ LLM ↔ backend

```
 Stakeholder (community operator / EV fleet manager)
        │  natural-language query
        ▼
 ┌────────────────────────┐
 │   LLM Agent (ReAct)    │  Thought → Action → Observation → Response
 └───────────┬────────────┘
             │ tool calls (function calling)
             ▼
 ┌─────────────────────────────────────────────────────────┐
 │  Tool Layer                                              │
 │  • bess_simulator            (fast, ms)                  │
 │  • self_consumption_calculator (fast, ms)                │
 │  • electricity_cost_estimator  (fast, ms)                │
 │  • optimizer_query           (reads cached LP solution)   │
 │  • trigger_reoptimization    (async job, if stale)       │
 └───────────┬─────────────────────────────┬────────────────┘
             ▼                             ▼
 ┌───────────────────────┐     ┌─────────────────────────────┐
 │ State & Forecast Cache │     │ Background Jobs              │
 │ (SoC, load, PV, price) │◄────┤ • LightGBM price forecaster   │
 └───────────────────────┘     │ • Pyomo/GLPK day-ahead LP     │
                               └─────────────────────────────┘
```

* The **stakeholder** asks operational questions in natural language ("Should we discharge in the next 2 hours?").
* The **LLM** parses intent, decides which tool(s) answer it, and calls them with structured arguments.
* **Backend systems** (simulator, forecaster, optimizer) do the numeric work; the LLM only orchestrates and explains.
* The response returns figures with explanation and, where relevant, uncertainty bounds — never a bare number.

### 1.3 Balancing immediate responses vs. heavy optimization

Two response tiers, matched to what the question actually requires:

| Tier | Trigger | Mechanism | Latency |
| :--- | :--- | :--- | :--- |
| **Tier 1 — Advisory (fast)** | "Should we charge/discharge now?", "What's our self-consumption?" | LLM calls lightweight tools that read the **already-solved** day-ahead schedule and cached telemetry, or run a cheap rule-based/simulated check | seconds |
| **Tier 2 — Re-optimization (slow)** | Conditions have materially changed (large forecast revision, new EV charging event, grid constraint change) or the user explicitly asks "what if..." | LLM enqueues an **async** Pyomo/GLPK solve job and either (a) answers immediately from the last valid solution with a staleness caveat, or (b) tells the user it is recomputing and follows up | seconds–minutes |

The optimizer is never called synchronously inside the chat turn. It runs on its own schedule (hourly day-ahead, plus event-triggered re-solves) and publishes a schedule that Tier-1 tools consume — this is what keeps the agent responsive.

---

## 2. Data Integration

### 2.1 Data sources needed

| Domain | Source type | Purpose |
| :--- | :--- | :--- |
| Community load | Smart meters / AMI | Net-load calculation, load-shift feasibility |
| PV generation | Inverter telemetry + weather forecast (e.g., ERA5-derived irradiance) | Surplus/deficit prediction |
| EV / heavy-goods charging | Depot/charger telemetry + booking/dispatch schedule | Anticipate large, semi-controllable load blocks |
| Grid / market | DSO contractual limits (import/export kW cap) + day-ahead spot price (e.g., Nord Pool DK1) | Cost signal and hard operating constraint |
| BESS | BMS/inverter telemetry | SoC, power limits, health/degradation state |

### 2.2 Required data features per domain

* **Community load**: hourly-or-finer granularity (15-min preferred for peak detection), per-feeder or aggregate kW, weekday/weekend and seasonal labels, at least 12–18 months history for seasonal model training.
* **EV / HGV charging**: per-session start time, plug-in duration, energy requested (kWh), deadline/flexibility window, and — critically — a **flexibility flag** (can this session be shifted, and by how much) since the agent's core lever is load-shifting these profiles.
* **PV generation**: 15-min-to-hourly generation (kW/kWh), plus forward weather forecast (irradiance, cloud cover) to drive next-day PV forecasts; site metadata (capacity, orientation) for scaling.
* **Grid/market**: day-ahead hourly spot price (P10/P50/P90 once forecast), the contractual PCC import/export limit (kW), and any DSO flexibility/congestion signals.
* **BESS**: SoC (%), usable capacity, max charge/discharge power, round-trip efficiency, degradation cost per kWh throughput, and current health/cycle count — all needed to keep both the simulator and the optimizer physically realistic.

---

## 3. Decision Support Logic

### 3.1 Natural language → actionable recommendation

The LLM does not "decide" physics — it **translates intent into tool calls** and **narrates results**:

1. **Parse** the query into an intent category (immediate charge/discharge advice, historical performance review, what-if scenario, cost explanation).
2. **Resolve** the time window and required data (e.g., "next 2 hours" → current SoC + next 2 hourly forecast/schedule points; "yesterday" → historical load/PV logs).
3. **Call** the matching tool(s) with structured arguments extracted from the query.
4. **Compose** a response: exact figures from the tool output + plain-language reasoning ("prices are forecast to rise from 0.9 to 2.1 DKK/kWh after 17:00, and SoC is at 62%, so discharging now avoids the peak-price window") + any uncertainty caveat.

### 3.2 Interfacing with optimization / rule-based systems

* **Rule-based layer** (fast, always available): the deterministic priority logic — discharge BESS before importing on deficit, charge BESS before exporting on surplus, always respect the PCC limit — gives a safe fallback answer even if the optimizer hasn't run recently.
* **Optimization layer** (Pyomo + GLPK LP): solved on the rolling hourly cadence over a 24h horizon, minimizing $\sum_t \big(\lambda_{\text{buy}}(t) P_{\text{import}}(t) + C_{\text{deg}}(P_{\text{ch}}+P_{\text{dis}}) - \lambda_{\text{sell}}(t) P_{\text{export}}(t)\big)$ subject to power balance, SoC dynamics, BESS power/energy limits, and the PCC import/export cap.
* The LLM queries **which** layer produced the current schedule and states that provenance ("per the day-ahead LP solve at 06:00" vs. "per the rule-based fallback, since the optimizer output is >2h stale").

### 3.3 Balancing multiple objectives

The optimizer's objective already nets cost against export revenue and degradation; the agent adds two further levers on top:

* **Cost minimization**: primary LP objective term (arbitrage against forecast spot price, penalized by degradation cost so cheap arbitrage doesn't cause needless cycling).
* **Self-consumption maximization**: enforced as an implicit priority in the rule-based layer (charge BESS from surplus PV before exporting) and can be weighted explicitly in the LP objective (a shadow revenue term or export-price discount) when self-consumption is a stated community goal rather than pure profit.
* **Grid support**: modeled as a **hard constraint** (PCC import/export limit), not a soft objective term — peak-shaving via forced BESS discharge overrides price-arbitrage behavior whenever the community's net load would otherwise breach the contractual limit. This ordering (constraint first, cost objective second) is what the agent explains to the user when a "why did it discharge even though price is low" question comes up.

With EV/HGV charging added, the same structure extends naturally: flexible charging sessions become additional shiftable decision variables in the LP (bounded by their deadline windows), rather than a new objective — the agent explains schedule shifts the same way it explains BESS actions.

---

## 4. Uncertainty Handling

### 4.1 Communicating forecast uncertainty

Every price/PV/load figure the agent surfaces carries its **P10 / P50 / P90** band (produced via LightGBM point forecasts + binned-residual bootstrap, §Forecasting_Logic), and the agent is prompted to state it in plain language, e.g.: *"Price is expected around 1.4 DKK/kWh, but could range from 0.9 to 2.1 DKK/kWh (P10–P90) depending on demand and wind generation."* Point-only answers are treated as incomplete by the system prompt's response contract.

### 4.2 Robust decision-making under uncertain forecasts

* **Chance-constrained / scenario-aware operation**: rather than optimizing only against the P50 price/PV path, the schedule is sanity-checked against the P10/P90 bands — if a discharge plan would breach the PCC limit under a plausible P10 PV / P90 load scenario, the agent flags the risk rather than presenting the P50 plan as certain.
* **Conservative SoC buffers**: the BESS is never scheduled to the physical SoC limits (15–95%) for arbitrage; a margin is reserved so that forecast error doesn't push the system into an infeasible or grid-breaching state.
* **Constraint-first ordering** (§3.3) is itself a robustness mechanism — grid limit compliance never depends on forecast accuracy, since it is enforced against realized, not forecast, power flow.

### 4.3 Learning from prediction errors over time

* **Residual tracking**: forecast errors (actual − predicted) are logged per lead time and rolled into the same binned-residual pool used for uncertainty bands, so the P10/P90 spread naturally widens for regimes that have recently been harder to predict — the interval calibration self-updates without a full model retrain.
* **Periodic retraining**: the LightGBM models are retrained on a fixed cadence (e.g., monthly) as new realized data accumulates, capturing seasonal drift (new EV load patterns, tariff changes).
* **Outcome feedback loop**: realized self-consumption, cost, and peak-shaving performance (from the same tools the agent uses for advisory answers) are compared against the schedule's forecast assumptions; systematic bias (e.g., PV consistently over-forecast in winter) is surfaced to a human operator as a model-health signal rather than silently absorbed.
