# Multi-LLM AI Agent Architecture

This document describes the modular architecture for integrating the BESS simulator and forecasting system with Large Language Models (LLMs) from different providers (Google Gemini, Anthropic Claude, OpenAI, DeepSeek, or open-source local models).

---

## 1. Unified Architecture Design

To ensure the system is model-agnostic, we implement a **custom Tool-Use (Function Calling) Router**. Rather than locking the codebase into a specific framework like LangChain (which can be bloated and change frequently), we use a clean **Model Adapter Pattern**:

```
                       ┌───────────────────┐
                       │    User Query     │
                       └─────────┬─────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │   AI Agent Router     │
                     │  (gemini/claude/gpt/  │
                     │   deepseek/ollama)    │
                     └───────────┬───────────┘
                                 │ (Extracts parameters)
                                 ▼
                     ┌───────────────────────┐
                     │    Function Router    │
                     └─────────┬─┬─┬─────────┘
            ┌──────────────────┘ │ └──────────────────┐
            ▼                    ▼                    ▼
   ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
   │ Tool 1: BESS   │   │ Tool 2: Solar  │   │ Tool 3: Price  │
   │ State Simulator│   │ Self-Consump.  │   │ Cost Estimator │
   └────────────────┘   └────────────────┘   └────────────────┘
```

---

## 2. Model Adapter Configuration

The agent script uses a standard adapter interface to switch between APIs by reading environmental variables:

| Provider                | SDK / API Target             | Base URL (Endpoint)                           | Model Name                             |
| :---------------------- | :--------------------------- | :-------------------------------------------- | :------------------------------------- |
| **OpenAI**        | `openai` client            | `https://api.openai.com/v1`                 | `gpt-4o`                             |
| **Anthropic**     | `anthropic` client         | `https://api.anthropic.com/v1`              | `claude-3-5-sonnet`                  |
| **Google Gemini** | `google-generativeai`      | `https://generativelanguage.googleapis.com` | `gemini-1.5-pro`                     |
| **DeepSeek**      | `openai` client compatible | `https://api.deepseek.com/v1`               | `deepseek-chat` / `deepseek-coder` |
| **Ollama**        | Local Host server            | `http://localhost:11434/v1`                 | `llama3` / `mistral`               |

---

## 3. Tool Definitions

The LLM is provided with descriptions of three custom python tools.

### Tool 1: BESS State Simulator

* **Input**: Current SoC (%), target charge/discharge power (kW), duration (hours).
* **Process**: Simulates charging/discharging physics using the $1500\text{ kWh}$ BESS parameters, ensuring SoC stays between $15\%$ and $95\%$.
* **Output**: Final SoC (%), violation signals, energy stored.

### Tool 2: Self-Consumption Calculator

* **Input**: Start timestamp, End timestamp.
* **Process**: Extracts PV generation and load demand, calculating the percentage of local PV output consumed by the community rather than exported.
* **Output**: Self-consumption rate (%), peak solar surplus hours (kW).

### Tool 3: Electricity Cost Estimator

* **Input**: Start timestamp, End timestamp, BESS operation mode (`with_bess` vs. `no_bess`).
* **Process**: Calculates the electricity bill in DKK based on net grid imports and spot pricing.
* **Output**: Total grid bill (DKK), battery degradation wear costs.

---

## 4. Prompt Engineering for Action Planning

The system prompt forces the LLM to structure its reasoning using the **ReAct (Reasoning and Acting)** framework:

```text
System Prompt:
You are an expert Energy Management AI Agent. You manage a 1.5 MWh / 750 kW BESS system.
You have access to:
- Tool 1: bess_simulator(current_soc, power_kw, duration_h)
- Tool 2: calculate_self_consumption(start_date, end_date)
- Tool 3: estimate_electricity_cost(start_date, end_date, use_bess)

When the user asks a question, follow this loop:
1. Thought: What information do I need? Which tool should I call?
2. Action: Call the appropriate tool with arguments.
3. Observation: Analyze the output returned by the tool.
4. Response: Synthesize the final human-readable explanation containing exact figures.
```
