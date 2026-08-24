# Question 2 Requirements: Operational AI-Agent for Energy Community BESS Management

This document outlines the official requirements and checklist for **Question 2** extracted directly from the interview exam PDF ([Written test for interview.pdf](<file:///D:/33_Obsidian/77_Job-PhD/55_Interview/03_Marladen_University/Written%20test%20for%20interview.pdf>)).

---

## Submission Guidelines & Status

* **Format**: PDF document containing written responses. Code demonstration submitted as separate `.py` files or a GitHub repository link.
* **Deadline**: **2026-08-24 (Today) Monday at 23:59**
* **Submission Email**: `chang.su@mdu.se`

---

## Part A: Architecture Design (Mandatory, 1-page summary)

*Goal: Design a conceptual LLM-based AI-agent for operational BESS management advisory. Assume the Agent can shift load according to local demand and grid limits, consider future EV and heavy goods charging profiles, and return operational recommendations with explanations and uncertainty indicators.*

- [ ] **1. Agent Architecture**

  - [ ] Describe how the agent processes real-time and forecast data.
  - [ ] Map the interaction flow between the user (stakeholder), the LLM, and backend systems.
  - [ ] Explain how you handle the need for both immediate responses and computationally intensive optimization.
- [ ] **2. Data Integration**

  - [ ] Identify and list which kinds of data are needed.
  - [ ] Describe the required features of the data the agent should access (granularity, variables, etc. for community load, EV charging, PV generation, grid/market, and BESS).
- [ ] **3. Decision Support Logic**

  - [ ] Explain how the agent translates natural language queries into actionable recommendations.
  - [ ] Explain how the agent interfaces with optimization algorithms or rule-based systems.
  - [ ] Detail how the agent balances multiple objectives:
    - Cost minimization
    - Self-consumption maximization
    - Grid support
- [ ] **4. Uncertainty Handling**

  - [ ] Describe approaches for communicating forecast uncertainty to users.
  - [ ] Describe approaches for robust decision-making under uncertain PV/load forecasts.
  - [ ] Describe approaches for learning from prediction errors over time.

---

## Part B: Implementation Prototype (Optional, Python Code)

*Goal: Provide the AI-agent development pipeline in Python (model selection, orchestration framework, prompt engineering, reliability layers, monitoring, failure handling) along with sample Python code demonstrating key components.*

- [ ] **1. Basic Agent Structure**

  - [ ] Build a basic agent using an LLM framework (e.g., LangChain, LlamaIndex, or direct API calls).
- [ ] **2. Custom Tools (At least two required)**

  - [ ] **Tool 1: BESS State Simulator** (simplified model of charge/discharge dynamics).
  - [ ] **Tool 2: Self-Consumption Calculator** (aggregates local solar generation vs local consumption).
  - [ ] **Tool 3: Electricity Cost Estimator** (computes price based on time-of-use spot pricing).

  - *Note: Candidates can also use API access to existing open-source tools.*
- [ ] **3. Time-Series Data Integration**

  - [ ] Integrate (simplified or mock) time-series data for PV generation and load.
- [ ] **4. Query Demonstrations**

  - [ ] **Query 1**: *"Should we charge or discharge the battery in the next 2 hours given the current conditions?"*
  - [ ] **Query 2**: *"What was our self-consumption rate yesterday and how could it be improved?"*

---

## Notes

* **Mock Data**: Simplified models and synthetic data are acceptable. Focus on demonstrating the integration of LLM reasoning with domain-specific calculations.
* **Original Reasoning**: The review prioritizes original reasoning, reproducible design, and engineering reliability. Content that is generic, untested, or not grounded in realistic energy-system constraints will be ranked low.
