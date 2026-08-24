import os
import json
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEDULE_CSV = os.path.normpath(os.path.join(SCRIPT_DIR, "../05_Optimisation_and_Forecast/bess_schedule_tomorrow.csv"))

# --- 1. Tools Implementation ---

def bess_simulator(current_soc, power_kw, duration_h=1.0):
    """Simulates BESS state transition and checks constraints.
    power_kw: Positive for charging, Negative for discharging.
    """
    E_nom = 1500.0
    eta_ch = 0.95
    eta_dis = 0.95
    SoC_min = 0.15
    SoC_max = 0.95
    
    current_energy = E_nom * (current_soc / 100.0)
    
    # Calculate energy change
    if power_kw >= 0:
        energy_change = power_kw * eta_ch * duration_h
    else:
        energy_change = (power_kw / eta_dis) * duration_h
        
    new_energy = current_energy + energy_change
    new_soc = (new_energy / E_nom) * 100.0
    
    clamped_soc = max(SoC_min * 100.0, min(SoC_max * 100.0, new_soc))
    violation = False
    if new_soc < SoC_min * 100.0 or new_soc > SoC_max * 100.0:
        violation = True
        
    return {
        "initial_soc_percent": current_soc,
        "proposed_power_kw": power_kw,
        "new_soc_percent": np.round(clamped_soc, 2),
        "violation_detected": violation,
        "clamped_warning": "Warning: SoC bounds breached, action clamped!" if violation else "None"
    }

def self_consumption_calculator(start_time_str, end_time_str):
    """Calculates solar self-consumption rate (%) for the community."""
    if not os.path.exists(SCHEDULE_CSV):
        return {"error": "Schedule CSV data not found. Run daily_optimization.py first."}
        
    df = pd.read_csv(SCHEDULE_CSV, parse_dates=["timestamp"])
    mask = (df["timestamp"] >= start_time_str) & (df["timestamp"] <= end_time_str)
    df_slice = df[mask]
    
    if len(df_slice) == 0:
        return {"error": f"No data found in range {start_time_str} to {end_time_str}."}
        
    total_pv = df_slice["pv_forecast_kw"].sum()
    total_load = df_slice["load_forecast_kw"].sum()
    total_export = df_slice["grid_export_kw"].sum()
    self_consumed_pv = max(0.0, total_pv - total_export)
    
    self_consumption_rate = (self_consumed_pv / total_pv * 100.0) if total_pv > 0 else 100.0
    
    return {
        "total_solar_generated_kwh": np.round(total_pv, 2),
        "total_load_demand_kwh": np.round(total_load, 2),
        "solar_self_consumed_kwh": np.round(self_consumed_pv, 2),
        "self_consumption_rate_percent": np.round(self_consumption_rate, 2),
        "surplus_solar_exported_kwh": np.round(total_export, 2)
    }

def electricity_cost_estimator(start_time_str, end_time_str, use_bess=True):
    """Estimates net electricity bills (DKK) with and without BESS."""
    if not os.path.exists(SCHEDULE_CSV):
        return {"error": "Schedule CSV data not found."}
        
    df = pd.read_csv(SCHEDULE_CSV, parse_dates=["timestamp"])
    mask = (df["timestamp"] >= start_time_str) & (df["timestamp"] <= end_time_str)
    df_slice = df[mask]
    
    if len(df_slice) == 0:
        return {"error": "No data in range."}
        
    if use_bess:
        cost = (df_slice["grid_import_kw"] * df_slice["price_forecast_dkk_kwh"] - 
                df_slice["grid_export_kw"] * df_slice["price_forecast_dkk_kwh"]).sum()
    else:
        net_load = df_slice["load_forecast_kw"] - df_slice["pv_forecast_kw"]
        no_bess_import = np.where(net_load > 0, net_load, 0.0)
        no_bess_export = np.where(net_load < 0, np.minimum(500.0, np.abs(net_load)), 0.0)
        cost = (no_bess_import * df_slice["price_forecast_dkk_kwh"] - 
                no_bess_export * df_slice["price_forecast_dkk_kwh"]).sum()
                
    return {
        "mode": "With BESS" if use_bess else "No BESS (Baseline)",
        "estimated_net_cost_dkk": np.round(cost, 2)
    }

# Dictionary mapping tool names to actual functions
TOOLS = {
    "bess_simulator": bess_simulator,
    "self_consumption_calculator": self_consumption_calculator,
    "electricity_cost_estimator": electricity_cost_estimator
}

# --- 2. Multi-LLM API Connectors ---

def call_llm(messages, api_config):
    """Universal router to send messages to OpenAI, Anthropic, Gemini, DeepSeek, or Ollama."""
    provider = api_config.get("provider", "mock")
    model = api_config.get("model")
    api_key = api_config.get("api_key")
    
    if provider == "openai" or provider == "deepseek":
        # Supports both OpenAI and DeepSeek via OpenAI SDK
        from openai import OpenAI
        base_url = "https://api.deepseek.com/v1" if provider == "deepseek" else "https://api.openai.com/v1"
        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.0
        )
        return response.choices[0].message.content
        
    elif provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        # Format messages for Anthropic
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_messages = [m for m in messages if m["role"] != "system"]
        response = client.messages.create(
            model=model,
            system=system_msg,
            messages=user_messages,
            max_tokens=1000,
            temperature=0.0
        )
        return response.content[0].text
        
    elif provider == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        # Format messages for Google Generative AI
        chat_model = genai.GenerativeModel(model)
        chat = chat_model.start_chat()
        # For simple compatibility, send the compiled system prompt + last message
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        last_msg = messages[-1]["content"]
        response = chat.send_message(f"System Context:\n{system_msg}\n\nUser Question:\n{last_msg}")
        return response.text
        
    elif provider == "ollama":
        import requests
        url = "http://localhost:11434/api/chat"
        payload = {"model": model, "messages": messages, "stream": False, "options": {"temperature": 0}}
        response = requests.post(url, json=payload)
        return response.json()["message"]["content"]
        
    else:
        # Mock / Fallback Mode (So it runs immediately without keys)
        last_msg = messages[-1]["content"].lower()
        if "charge" in last_msg or "discharge" in last_msg or "next 2 hours" in last_msg:
            return '{"tool": "bess_simulator", "parameters": {"current_soc": 50.0, "power_kw": -750.0, "duration_h": 2.0}}'
        elif "self-consumption" in last_msg or "yesterday" in last_msg:
            return '{"tool": "self_consumption_calculator", "parameters": {"start_time_str": "2025-06-08 00:00:00", "end_time_str": "2025-06-08 23:00:00"}}'
        else:
            return "I am a BESS AI Agent. Please ask me about charging schedules or self-consumption rates."

# --- 3. The Agent Reasoning & Tool-Use Execution Loop ---

class BESSAgentLoop:
    def __init__(self, api_config):
        self.api_config = api_config
        self.system_prompt = (
            "You are an expert Energy Management AI Agent. You manage a 1.5 MWh / 750 kW BESS system.\n"
            "You have access to the following Python tools:\n"
            "1. Tool: bess_simulator(current_soc, power_kw, duration_h)\n"
            "   - Input: current_soc (float, %), power_kw (float, + for charge, - for discharge), duration_h (float)\n"
            "2. Tool: self_consumption_calculator(start_time_str, end_time_str)\n"
            "   - Input: start_time_str (str, 'YYYY-MM-DD HH:MM:SS'), end_time_str (str)\n"
            "3. Tool: electricity_cost_estimator(start_time_str, end_time_str, use_bess)\n"
            "   - Input: start_time_str (str), end_time_str (str), use_bess (bool)\n\n"
            "If you need to call a tool, you MUST respond ONLY with a single JSON block of the format:\n"
            '{"tool": "tool_name", "parameters": {"param1": val1, ...}}\n'
            "Do NOT include any extra text before or after the JSON if you are calling a tool.\n\n"
            "Once you receive the tool's output observation, write your final response. "
            "Explain your reasoning and state the exact figures clearly in DKK."
        )

    def run(self, user_query):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        print(f"User: \"{user_query}\"")
        print("Agent: (Thinking...)")
        
        # Step 1: Send query to LLM
        response = call_llm(messages, self.api_config).strip()
        
        # Step 2: Check if LLM requested a tool call
        try:
            tool_call = json.loads(response)
            tool_name = tool_call.get("tool")
            params = tool_call.get("parameters", {})
            
            if tool_name in TOOLS:
                print(f"-> [AI requested Tool-Use]: Calling '{tool_name}' with parameters {params}")
                # Execute Python Function
                observation = TOOLS[tool_name](**params)
                print(f"<- [Observation Output]: {observation}")
                
                # Append tool call and observation to message history
                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "user", "content": f"Observation from '{tool_name}': {json.dumps(observation)}"})
                
                # Step 3: Call LLM again with tool results to generate final human explanation
                print("Agent: (Formulating final answer...)")
                final_response = call_llm(messages, self.api_config)
                return final_response
            else:
                return response
        except json.JSONDecodeError:
            # If the response is not JSON, it is the final answer directly
            return response

# --- 4. Main Demonstration Execution ---

def main():
    # --- CONFIGURE YOUR API HERE ---
    # Set to "openai", "anthropic", "gemini", "deepseek", "ollama", or "mock"
    api_config = {
        "provider": "mock", # Change this to connect a live model!
        "model": "gpt-4o",  # e.g., "claude-3-5-sonnet", "gemini-1.5-pro", "deepseek-chat"
        "api_key": os.environ.get("OPENAI_API_KEY") # Sourced from env or hardcode here
    }
    
    # Auto-detect live API keys in environment to save manual setup
    for p in ["openai", "anthropic", "gemini", "deepseek"]:
        key = os.environ.get(f"{p.upper()}_API_KEY")
        if key:
            api_config = {"provider": p, "model": "gpt-4o" if p == "openai" else "claude-3-5-sonnet" if p == "anthropic" else "gemini-1.5-pro" if p == "gemini" else "deepseek-chat", "api_key": key}
            print(f"Auto-detected environment config: Active Provider = '{p}'")
            break

    print("=========================================================")
    print(f"      BESS AI AGENT TOOL-USE LOOP (Active: {api_config['provider'].upper()})")
    print("=========================================================\n")
    
    agent = BESSAgentLoop(api_config)
    
    # Run Query 1
    q1 = "Should we charge or discharge the battery in the next 2 hours given the current conditions?"
    ans1 = agent.run(q1)
    print(f"\nFinal Agent Response:\n{ans1}\n")
    print("-" * 57 + "\n")
    
    # Run Query 2
    q2 = "What was our self-consumption rate yesterday and how could it be improved?"
    ans2 = agent.run(q2)
    print(f"\nFinal Agent Response:\n{ans2}\n")
    print("=========================================================")

if __name__ == "__main__":
    main()
