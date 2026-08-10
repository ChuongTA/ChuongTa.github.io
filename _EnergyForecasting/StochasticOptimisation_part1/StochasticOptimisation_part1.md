---
title: "Stochastic Optimisation for Energy Storage (Part 1)"
excerpt: "From deterministic to stochastic decision-making: two-stage and multi-stage stochastic programs, common solution approaches, and why battery storage scheduling needs to account for uncertain prices, demand, and generation."
layout: single
author_profile: true
permalink: /EnergyForecasting/StochasticOptimisation_part1/
usemathjax: true
image: "/EnergyForecasting/StochasticOptimisation_part1/fig_deterministic_vs_stochastic.png"
date: 2026-08-06
category: "Electricity Market"
---
> **Series:** Stochastic Optimisation for Energy Storage | **Part:** 1 (Theory)

---

This post introduces the logic behind stochastic optimisation, using battery storage as the running example. Theory only, kept general. A later part will turn this into a concrete battery model with real code.

## 1. General Introduction

Power systems are shifting toward renewable generation and away from centralised, fully controllable plants. Wind and solar output cannot be scheduled the way a gas plant can, so the systems built around them must plan under uncertainty rather than around a single known outcome. Battery storage is one of the main tools for managing this: it can shift energy in time, smoothing the mismatch between when electricity is generated and when it is needed.

Deciding how to operate a battery, when to charge and when to discharge, depends on future prices, demand, and generation, none of which are known in advance. Storage is expected to be one of the critical tools for firming supply in low-carbon grids, and how well it is scheduled under that uncertainty directly affects how much value it delivers (Yurdakul & Billimoria, n.d.). This is exactly the setting stochastic optimisation is built for.

## 2. Deterministic Optimisation

Deterministic optimisation is the standard case: every input to the problem, prices, demand, generation, is treated as known in advance, and the task is to find the single best sequence of decisions given that fixed information. A generic deterministic optimisation problem takes the form:

$$
\min_{x} \; c^T x \quad \text{s.t.} \quad Ax = b, \; x \geq 0
$$

where $x$ is the decision variable, $c$ the cost weights, and $Ax = b$ the fixed constraints, capacity limits, balance equations, and so on. Everything in this formulation is known ahead of time; nothing is random.

This is the same logic behind classical optimisation methods such as linear and mixed-integer programming, and it also matches the structure of classic inventory control problems: a resource is held in stock, and decisions are made period by period to use it optimally. It is also the approach behind a project completed as part of the DENSYS Energy Systems module at Université de Liège: sizing and operating a microgrid (PV, battery, grid connection, generator, EV charging) using mixed-integer nonlinear programming (MINLP) in Pyomo, minimising operating cost under fixed assumptions about future load, tariffs, and generation ([project summary and report](/MasterProgramProjects/Liege_Projects/)).

Applied to a battery, a deterministic model assumes the full price and demand path for the planning horizon is known ahead of time, and solves for the one charge/discharge schedule that maximises profit against that fixed path.

## 3. Stochastic Optimisation

Stochastic optimisation extends the deterministic case to situations where key inputs are uncertain rather than known. Instead of a single fixed value for each future price or demand level, the uncertain quantity is represented as a random variable with an associated probability distribution, and the decision problem is solved with respect to that distribution rather than a single guess.

A decision maker in this setting does not simply solve once and stop: because the system evolves over time, a decision made now affects the costs and opportunities available at every future stage. Stochastic optimisation is built to account for that, producing decisions that perform well across the range of ways the future could unfold, not just the one path that was assumed.

![Deterministic vs. Stochastic Optimisation](/EnergyForecasting/StochasticOptimisation_part1/fig_deterministic_vs_stochastic.png)
*Left: a deterministic model plans around one assumed path. Right: a stochastic model plans against a range of paths the uncertain quantity could actually take, weighted by how likely each one is.*

## 4. Equations and Common Approaches

The most common way to represent a stochastic decision problem is as a two-stage program. Decisions are split into two groups: first-stage decisions, made before the uncertain outcome is known, and second-stage decisions, made in reaction to it. The general form is:

$$
\min_{x} \; c^T x + \mathbb{E}[Q(x, \xi)]
$$

where $x$ is the first-stage decision, $\xi$ is the random data, and $Q(x, \xi)$ is the optimal value of the second-stage problem once $\xi$ is known.

![The Two-Stage Stochastic Program](/EnergyForecasting/StochasticOptimisation_part1/fig_two_stage_program.png)
*$x$ is locked in before $\xi$ is known; $y(\xi)$ is free to react to whatever $\xi$ turns out to be.*

Many real problems require more than two stages. A multi-stage stochastic program extends this to a sequence of decisions $x_1, x_2, \dots, x_T$, each made after observing the random data revealed so far:

$$
x_1 \rightarrow \xi_2 \rightarrow x_2 \rightarrow \cdots \rightarrow \xi_T \rightarrow x_T
$$

A key rule applies throughout: a decision at stage $t$ may depend on everything observed up to that point, but never on future observations. This is called nonanticipativity, and it is what keeps the model realistic rather than assuming foreknowledge.

Beyond the two-stage and multi-stage formulations, several common solution approaches exist:

- **Stochastic dynamic programming**, including Markov decision processes, where the uncertain process is assumed to depend only on its most recent state, not its full history.
- **Scenario trees and scenario lattices**, which represent an uncertain process as a finite set of possible paths, used when the exact probability distribution is too complex to handle directly.
- **Stochastic dual dynamic programming (SDDP)** and **approximate dual dynamic programming (ADDP)**, both designed to solve multi-stage problems with many stages without the computational cost of enumerating every possible scenario path.

Wimmeder (2021) applies this exact toolkit to a battery scheduling problem, formulating it as a multi-stage stochastic program and solving it with ADDP under uncertain prices, demand, and PV generation. Similar formulations appear elsewhere in the literature: Kraft et al. (2021) apply stochastic optimisation to trading strategies across sequential electricity markets, and Arandia Goettsch (2024) optimises battery bidding strategies under market uncertainty.

## 5. Application to Battery Systems

### 5.1 Relevant Battery Services

A battery generates value in several distinct ways:

- **Arbitrage**: charging when electricity is cheap and discharging when it is expensive.
- **Peak shaving and time-shifting**: storing surplus renewable generation and releasing it when demand or price is high, reducing reliance on the grid at peak times.
- **Reliability**: reducing the impact of supply interruptions for the end user.
- **Ancillary services**: supporting grid functions such as frequency regulation.

### 5.2 The Need for Stochastic Optimisation in Battery Operation

Three inputs to the battery scheduling problem are genuinely uncertain: electricity prices, consumer demand, and, where relevant, solar or wind generation. Each is difficult to forecast precisely, prices because of market volatility, generation because of weather dependence, and demand because of variable consumer behaviour. A schedule built around a single forecast for these inputs can perform well on average and still fail badly at exactly the moments that matter, if the actual outcome departs from the assumed one. Yurdakul and Billimoria (n.d.) find that storage assets scheduled without accounting for this uncertainty can fail to respond to strong price signals precisely when they are needed most. Stochastic optimisation addresses this by planning against a representative set of possible outcomes instead of one.

### 5.3 Model Structure Under Uncertainty

The battery's physical characteristics, power rating, energy capacity, charge and discharge efficiency, and self-discharge, do not change with the introduction of uncertainty. What changes is how the uncertain inputs, price, demand, and generation, enter the model: instead of fixed values, they are represented as scenarios, each with an associated probability. The scheduling problem is then formulated as a two-stage or multi-stage stochastic program, and solved for the schedule that performs best across the scenario set as a whole, rather than the one schedule that would be optimal under a single assumed future.

## References

- Wimmeder, S. (2021). *Stochastic Optimization of a Battery Storage System*. Master's thesis, TU Wien, in cooperation with the Austrian Institute of Technology.
- Kraft, E., Russo, M., Keles, D., & Bertsch, V. (2021). *Stochastic Optimization of Trading Strategies in Sequential Electricity Markets*. Working Paper Series in Production and Energy, No. 58, Karlsruhe Institute of Technology.
- Arandia Goettsch, R. M. (2024). *Optimization of Bidding Strategies for a Battery Storage System in the Energy Market*. MSc thesis, University of Groningen.
- Yurdakul, O., & Billimoria, F. (n.d.). *Risk-Averse Self-Scheduling of Storage in Decentralized Markets*. Argonne National Laboratory, Technical University of Berlin, and University of Oxford.
- Université de Liège, DENSYS Programme. [Operational Planning and Sizing of a Microgrid](/MasterProgramProjects/Liege_Projects/) — academic project summary and report.

## Code

- [make_stochastic_optimisation_part1_figures.py](/EnergyForecasting/StochasticOptimisation_part1/make_stochastic_optimisation_part1_figures.py), generates the deterministic-vs-stochastic figure above. The two-stage program diagram was built manually.

**Next:** Part 2 builds this logic into a working battery dispatch model with real code.
