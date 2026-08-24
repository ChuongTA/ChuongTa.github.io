---
title: "Building an LLM Agent for BESS Operations"
excerpt: "A conceptual architecture and a working prototype for an LLM-based agent that advises on battery dispatch: day-ahead price forecasting with LightGBM, BESS sizing and scheduling in Pyomo, and a provider-agnostic ReAct tool-use agent on top."
layout: single
author_profile: true
permalink: /EnergyForecasting/AI_Agent_Development_in_BESS/
usemathjax: true
image: "/EnergyForecasting/AI_Agent_Development_in_BESS/bess_agent_architecture.jpg"
date: 2026-08-24
category: "Electricity Market"
---

## Why an agent, and not just an optimizer

A battery energy storage system (BESS) attached to a small energy community sits between three things that never quite agree: a load profile that peaks in the evening, solar generation that peaks at noon, and a spot price that does its own thing depending on wind and interconnector flows. An optimizer can schedule the battery against forecasts of all three. What it cannot do is explain itself to the person who has to sign off on the schedule, or answer a follow-up question in plain language when something looks off.

That's the gap an LLM agent is meant to fill: not replacing the optimizer, but sitting on top of it, translating "should we discharge in the next two hours" into a tool call, and translating the tool's numeric output back into a sentence a non-specialist can act on. This post walks through a small end-to-end system built around that idea, from synthetic load and PV data through a day-ahead price forecaster, a Pyomo battery scheduler, and a provider-agnostic ReAct agent with three tools.

## System overview

![BESS AI agent architecture: time-series inputs feeding LightGBM price forecasting, a Pyomo BESS optimizer, and an LLM agent that routes user queries to tools](/EnergyForecasting/AI_Agent_Development_in_BESS/bess_agent_architecture.jpg)

Every stage writes its output to a plain CSV or PNG that the next stage reads, so the pipeline can be inspected or re-run stage by stage.

### Data

Load and PV are synthetic, generated to look like a real energy community rather than pulled from a live meter. The community load profile combines a double-Gaussian model of the morning and evening demand peaks with a logistic curve that separates weekday and weekend behavior, scaled to a peak of 952 kW. PV output comes from ERA5 solar irradiance scaled to a 50 MW farm. The one real dataset in the pipeline is the day-ahead spot price for the DK1 bidding zone, sourced from Denmark's Energi Data Service, covering 2024-01-01 through 2025-09-30 in hourly resolution.

### Forecasting the price

Day-ahead prices are forecast with LightGBM rather than the quantile regression forest used in an earlier post in this series, mainly for speed: at this data volume, gradient boosting trains and predicts an order of magnitude faster while using less memory. Rather than a single recursive model, each lead time from 1 to 24 hours gets its own model, trained on calendar features (hour, day of week, month, weekend flag) and price lags at 24 and 168 hours.

Uncertainty comes from a binned residual bootstrap instead of a second set of quantile models. Out-of-fold validation residuals get grouped into bins by the model's own predicted price level, so a test prediction draws its P10/P90 offsets only from the bin with a similar predicted price. Residuals during calm periods stay narrow; residuals during volatile periods stay wide. This is the same heteroscedasticity-aware idea from the [probabilistic price forecasting series](/EnergyForecasting/PEPF_part1/), reused here because the BESS scheduler needs a price band, not just a point estimate.

### Sizing the battery

Before scheduling day to day, the battery needs a capacity. `bess_sizing.py` solves a Pyomo linear program, with GLPK as the backend solver, once per candidate capacity (250, 500, 1000, 1500, and 2000 kWh), over the full 2024-01-01 to 2025-06-06 historical window. For each hour, four power variables and one energy variable are constrained by the standard state-of-charge dynamics:

$$E(t) = E(t-1) + \left(P_{\text{ch}}(t)\cdot\eta_{\text{ch}} - \frac{P_{\text{dis}}(t)}{\eta_{\text{dis}}}\right)$$

subject to a 15 to 95 percent state-of-charge band, a 500 kW grid import/export limit, and a degradation penalty of 0.40 DKK/kWh of throughput in the objective, alongside the price of imported and exported energy. The two smallest capacities came back infeasible: they simply don't have enough discharge power to keep the community's peak import under the 500 kW grid limit. Of the feasible sizes, 1500 kWh with a 750 kW inverter came out ahead on net annual benefit:

| Capacity (kWh) | Power (kW) | CAPEX (DKK) | Annual OPEX (DKK) | Annual savings (DKK) | Payback (years) |
|---:|---:|---:|---:|---:|---:|
| 1500 | 750 | 2,797,500 | 41,962.50 | 239,508.59 | 11.68 |
| 2000 | 1000 | 3,730,000 | 55,950.00 | 307,858.74 | 12.12 |

Eleven and a half years is not a fast payback, but it is what the numbers say once degradation cost and the 500 kW grid constraint are taken seriously rather than assumed away.

### Scheduling the week

With the size fixed, `daily_optimization.py` solves a second Pyomo/GLPK model, this time as a one-shot 168-hour linear program over a rolling 7-day window, using the LightGBM price forecast (with its P10/P90 band) instead of historical actuals. Over the sample week (2025-06-07 to 2025-06-13), the schedule saved 2,064 DKK against a no-BESS baseline, importing and exporting right up against the 500 kW grid limit at points and cycling roughly 2,300 to 2,500 kWh through the battery.

![7-day BESS dispatch schedule showing price, load, PV, and battery state of charge](/EnergyForecasting/AI_Agent_Development_in_BESS/05_Optimisation_and_Forecast/daily_schedule_7_days.png)
*7-day dispatch schedule: spot price with its P10-P90 band on top, battery charge/discharge and state of charge below.*

The script also writes a zoomable interactive HTML version with Plotly, useful for looking at any individual day up close rather than squinting at a week compressed into one static plot.

## Putting an agent in front of it

The scheduler produces a table, not an answer. The agent's job is to sit between a person's question and that table.

### Design: fast advice, slow optimization

Instead of running the LP synchronously inside a chat turn, the design splits into two tiers. Advisory questions ("should we discharge now," "what was our self-consumption yesterday") read the already-solved schedule and answer in seconds. Anything that would require a fresh solve, a large forecast revision or a genuine what-if scenario, triggers an optimization run asynchronously, and the agent either answers from the last valid solution with a staleness note or tells the user it's recomputing. The optimizer runs on its own hourly cadence; the chat interface never blocks on it.

### Three tools, one source of truth

All three required tools read from the same solved schedule CSV, so their answers stay consistent with each other and traceable back to one optimizer run:

* **`bess_simulator`** checks a proposed charge or discharge action against the 15 to 95 percent SoC bounds and flags a violation instead of silently clamping past them.
* **`self_consumption_calculator`** sums PV generation and load over a time window and reports what fraction of local solar was actually consumed on site versus exported.
* **`electricity_cost_estimator`** computes the net grid bill in DKK over a window, with a `no_bess` mode for comparison against the baseline.

The LLM never computes any of these numbers itself. It emits a small JSON tool call, Python executes it deterministically, and the model's only job afterward is to explain the returned figures in plain language. That split is what keeps the agent's answers numerically trustworthy regardless of which LLM is behind it.

### One agent, five providers

The agent loop (`bess_agent.py`) doesn't depend on LangChain or any particular vendor SDK. A small router function switches between OpenAI, Anthropic, Gemini, DeepSeek, and a local Ollama model based on which API key is set in the environment, plus a mock mode that runs the full reasoning loop with no key at all, useful for testing or for demoing the tool-call flow offline.

Two required queries exercise the loop end to end:

> "Should we charge or discharge the battery in the next two hours given the current conditions?"

The agent calls `bess_simulator` with the current state of charge and a proposed power level, gets back the resulting SoC, any bound violation, and the price context at that hour, and answers something like: *"Recommend discharging at 750 kW, moving SoC from 50% to 15%. Price is forecast at about 0.4 DKK/kWh, range 0.1-0.64 DKK/kWh (P10-P90). (Per the day-ahead LP solve.)"* The uncertainty range and the schedule citation aren't decoration, they're a fixed part of the response contract in the system prompt: a bare point number is treated as an incomplete answer.

> "What was our self-consumption rate yesterday and how could it be improved?"

The agent calls `self_consumption_calculator` over the requested day, reports the percentage, suggests shifting battery charging toward the midday PV surplus rather than cheap overnight grid import as one lever to raise it, and again names the schedule the figures came from.

### Try it

GitHub Pages is static hosting, so there's no server here to run a live model against. What's embedded below is a client-side version of the three tools, running in JavaScript directly on this solved 7-day schedule. The "routing" step (deciding which tool a question needs) is a handful of regular expressions standing in for the LLM call, so it only recognizes the same three question shapes as the queries above. Everything downstream of that, the tool math and the numbers in the response, is the same logic as `bess_agent.py`, not a mock.

<iframe src="/EnergyForecasting/AI_Agent_Development_in_BESS/06_LLM/bess_agent_demo.html" width="100%" height="1150" style="border: 1px solid #ddd; border-radius: 8px;" loading="lazy" title="BESS agent demo, client-side with a fake LLM router"></iframe>

*If the embed doesn't load, [open the demo directly](/EnergyForecasting/AI_Agent_Development_in_BESS/06_LLM/bess_agent_demo.html).*

## What this leaves out

The battery-sizing and weekly-dispatch models use the real DK1 price series, but load and PV forecast error inside the scheduler is injected as synthetic Gaussian noise (5 percent on load, 12 percent on PV) rather than coming from trained load and PV forecasters. That's a reasonable simplification for a prototype meant to demonstrate the agent-to-optimizer interface, but it means the price forecast is the one component actually validated against real held-out data end to end.

The dispatch model is also a single 7-day solve rather than a genuinely rolling one that re-optimizes each day as new forecasts arrive, and EV or heavy-goods charging flexibility, which would show up as additional shiftable load in the same LP, isn't wired in yet. Both are natural next steps if this moves past a prototype.

## Code

* [`01_Load/generate_load_profiles.py`](/EnergyForecasting/AI_Agent_Development_in_BESS/01_Load/generate_load_profiles.py) — synthesizes the community load profile (double-Gaussian diurnal peaks, weekday/weekend logistic modulation).
* [`02_PV_Generation/simulate_pv_generation.py`](/EnergyForecasting/AI_Agent_Development_in_BESS/02_PV_Generation/simulate_pv_generation.py) — scales ERA5 irradiance to a 50 MW solar farm.
* [`05_Optimisation_and_Forecast/bess_sizing.py`](/EnergyForecasting/AI_Agent_Development_in_BESS/05_Optimisation_and_Forecast/bess_sizing.py) — Pyomo/GLPK capacity sizing sweep and financial feasibility report.
* [`05_Optimisation_and_Forecast/daily_optimization.py`](/EnergyForecasting/AI_Agent_Development_in_BESS/05_Optimisation_and_Forecast/daily_optimization.py) — LightGBM price forecast plus binned residual bootstrap, 7-day Pyomo/GLPK dispatch schedule, static and interactive plots.
* [`06_LLM/bess_agent.py`](/EnergyForecasting/AI_Agent_Development_in_BESS/06_LLM/bess_agent.py) — the ReAct tool-use agent loop and its three tools, with the multi-provider router.
* [`06_LLM/bess_agent_demo.html`](/EnergyForecasting/AI_Agent_Development_in_BESS/06_LLM/bess_agent_demo.html) — the client-side demo above: the same three tools ported to JavaScript, with a regex router standing in for the LLM.

The full project, including the synthetic data, the GLPK solver package, and every intermediate result file, lives in [this folder on GitHub](https://github.com/ChuongTA/ChuongTa.github.io/tree/master/_EnergyForecasting/AI_Agent_Development_in_BESS). GitHub's own directory download button there gets you a zip of everything at once, so it isn't duplicated as a separate download on this page.
