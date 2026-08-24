# Battery Energy Storage System (BESS) Physical and Economic Parameters

This document defines the physical, operational, and economic parameters of the shared Battery Energy Storage System (BESS) for the energy community. These parameters serve as the foundation for both the sizing optimization (Pyomo) and the operational rules of the AI Agent.

---

## 1. Capacity and Energy Parameters

Energy parameters define the boundaries of how much charge the BESS can physically store and the operational safety limits to prevent cell damage:

* **Nominal Capacity ($E_{\text{nom}}$)**: **$1000\text{ kWh}$** ($1\text{ MWh}$).
* **State of Charge (SoC) Constraints**:
  * **$SoC_{\text{max}}$**: **$95\%$** (upper safety limit to prevent lithium plating and thermal runaway).
  * **$SoC_{\text{min}}$**: **$15\%$** (lower safety limit to prevent copper dissolution and over-discharge cell damage).
* **Operational Energy Capacity ($E_{\text{active}}$)**:
  $$E_{\text{active}} = E_{\text{nom}} \times (SoC_{\text{max}} - SoC_{\text{min}}) = 1000 \times (0.95 - 0.15) = 800\text{ kWh}$$
* **Initial State of Charge ($SoC_{\text{init}}$)**: **$50\%$** (starting point for simulations).

---

## 2. Power Parameters

Power parameters define how quickly energy can be transferred into or out of the battery pack (governed by the inverter capacity and battery chemistry C-rate):

* **Nominal Power Capacity ($P_{\text{nom}}$)**: **$500\text{ kW}$** (0.5C capability, meaning the battery can fully charge/discharge in 2 hours).
* **Maximum Charge Rate ($P_{\text{ch,max}}$)**: **$500\text{ kW}$** (positive power convention).
* **Maximum Discharge Rate ($P_{\text{dis,max}}$)**: **$500\text{ kW}$** (positive power convention).

---

## 3. Physics and Efficiency Parameters

These parameters govern the energy losses during charging, discharging, and standby idle phases:

* **Charging Efficiency ($\eta_{\text{ch}}$)**: **$95\%$** ($0.95$, due to inverter conversion losses and internal resistance heat generation).
* **Discharging Efficiency ($\eta_{\text{dis}}$)**: **$95\%$** ($0.95$, due to internal resistance heat generation and inverter extraction losses).
* **Round-Trip Efficiency ($\eta_{\text{rt}}$)**:
  $$\eta_{\text{rt}} = \eta_{\text{ch}} \times \eta_{\text{dis}} = 0.95 \times 0.95 = 90.25\%$$
* **Self-Discharge Rate ($\sigma_{\text{sd}}$)**: **$0.02\%$ per hour** (energy lost due to internal chemical side-reactions when idle).

---

## 4. Economic and Lifecycle Cost Parameters

Used to calculate the Levelized Cost of Storage (LCOS) and to define the degradation penalty function in optimization models:

* **CAPEX (Capital Cost)**: **$\$250/\text{kWh}$** (Total BESS investment = $\$250,000$).
* **Cycle Life**: **$6000\text{ cycles}$** at $80\%$ Depth of Discharge (DoD) before capacity drops to $80\%$ of nominal.
* **Degradation Cost ($C_{\text{deg}}$)**: **$0.40\text{ DKK/kWh}$** (throughput cost). This represents the marginal cost of cell wear-and-tear per kWh of energy throughput, calculated as:
  $$C_{\text{deg}} = \frac{\text{Battery Pack Cost}}{\text{Total Lifetime Energy Throughput}}$$

---

## 5. Governing Physical Equations (State of Charge Dynamics)

The state of charge of the BESS at time step $t+1$ is determined by the previous state, charging/discharging actions, and efficiency factors:

### Energy State Transition Equation
$$E(t+1) = E(t) \cdot (1 - \sigma_{\text{sd}}) + \left( P_{\text{ch}}(t) \cdot \eta_{\text{ch}} - \frac{P_{\text{dis}}(t)}{\eta_{\text{dis}}} \right) \Delta t$$

Where:
* $E(t)$: Battery energy stored at hour $t$ ($\text{kWh}$).
* $P_{\text{ch}}(t)$: Charging power imported to battery ($\text{kW}$), bounded by $[0,\ P_{\text{ch,max}}]$.
* $P_{\text{dis}}(t)$: Discharging power exported from battery ($\text{kW}$), bounded by $[0,\ P_{\text{dis,max}}]$.
* $\Delta t$: Duration of time step (hourly, $\Delta t = 1.0$).

### State of Charge (SoC) Calculation
$$SoC(t) = \frac{E(t)}{E_{\text{nom}}} \times 100\%$$
Subject to:
$$SoC_{\text{min}} \le SoC(t) \le SoC_{\text{max}}$$
$$15\% \le SoC(t) \le 95\%$$

---

## 6. Summary Table of BESS Parameters

| Parameter | Symbol | Value | Unit | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Nominal Energy Capacity** | $E_{\text{nom}}$ | $1000$ | kWh | Total physical energy capacity of BESS |
| **Minimum SoC Limit** | $SoC_{\text{min}}$ | $15$ | % | Lower safety depth of discharge limit |
| **Maximum SoC Limit** | $SoC_{\text{max}}$ | $95$ | % | Upper safety charging limit |
| **Active Energy Capacity** | $E_{\text{active}}$ | $800$ | kWh | Usable energy range ($SoC_{\text{max}} - SoC_{\text{min}}$) |
| **Nominal Power Capacity** | $P_{\text{nom}}$ | $500$ | kW | Inverter electrical limit (0.5C rate) |
| **Maximum Charge Rate** | $P_{\text{ch,max}}$ | $500$ | kW | Maximum power intake rate |
| **Maximum Discharge Rate** | $P_{\text{dis,max}}$ | $500$ | kW | Maximum power output rate |
| **Charging Efficiency** | $\eta_{\text{ch}}$ | $95$ | % | Efficiency of power conversion during charging |
| **Discharging Efficiency** | $\eta_{\text{dis}}$ | $95$ | % | Efficiency of power conversion during discharging |
| **Round-Trip Efficiency** | $\eta_{\text{rt}}$ | $90.25$ | % | Overall system efficiency ($\eta_{\text{ch}} \times \eta_{\text{dis}}$) |
| **Self-Discharge Rate** | $\sigma_{\text{sd}}$ | $0.02$ | %/hour | Standby losses per hour when idle |
| **Capital Expenditure** | CAPEX | $250$ | USD/kWh | Investment pack cost ($\$250,000$ total) |
| **Degradation Cost** | $C_{\text{deg}}$ | $0.40$ | DKK/kWh | Marginal lifecycle battery fade cost per throughput |
| **Cycle Life** | - | $6000$ | cycles | Total charging cycles expected at 80% DoD |

---

## 7. Optimization Formulation Framework (For Future Pyomo Implementation)

This section maps the BESS physical parameters to a standard Mixed-Integer Linear Programming (MILP) or Linear Programming (LP) optimization problem over a time horizon $T$ (e.g., $T = 24$ hours).

### A. Decision Variables
For each time step $t \in \{1, \dots, T\}$:
* $P_{\text{ch}}(t) \ge 0$: BESS charging power ($\text{kW}$)
* $P_{\text{dis}}(t) \ge 0$: BESS discharging power ($\text{kW}$)
* $E(t)$: Stored energy level ($\text{kWh}$)
* $P_{\text{grid,import}}(t) \ge 0$: Electricity imported from utility grid ($\text{kW}$)
* $P_{\text{grid,export}}(t) \ge 0$: Electricity exported (sold) to utility grid ($\text{kW}$)

### B. Objective Function (To Minimize Daily Cost)
The objective is to minimize total net cost, which includes purchasing electricity, BESS degradation costs, and subtracting revenues from exporting solar power:

$$\min \sum_{t=1}^{T} \left( \lambda_{\text{buy}}(t) \cdot P_{\text{grid,import}}(t) \cdot \Delta t + C_{\text{deg}} \cdot (P_{\text{ch}}(t) + P_{\text{dis}}(t)) \cdot \Delta t - \lambda_{\text{sell}}(t) \cdot P_{\text{grid,export}}(t) \cdot \Delta t \right)$$

Where:
* $\lambda_{\text{buy}}(t)$: Buy price of electricity at hour $t$ ($\text{SEK/kWh}$).
* $\lambda_{\text{sell}}(t)$: Sell price (feed-in tariff) of electricity at hour $t$ ($\text{SEK/kWh}$).
* $C_{\text{deg}}$: Degradation penalty per unit energy throughput ($0.40\text{ SEK/kWh}$).

### C. Constraints
For each time step $t$:
1. **Power Balance (Demand matching)**:
   $$P_{\text{load}}(t) - P_{\text{PV}}(t) = P_{\text{grid,import}}(t) - P_{\text{grid,export}}(t) + P_{\text{BESS,discharge}}(t) - P_{\text{BESS,charge}}(t)$$
2. **State of Charge Dynamics**:
   $$E(t) = E(t-1) \cdot (1 - \sigma_{\text{sd}}) + \left( P_{\text{ch}}(t) \cdot \eta_{\text{ch}} - \frac{P_{\text{dis}}(t)}{\eta_{\text{dis}}} \right) \Delta t$$
3. **BESS Capacity Limits**:
   $$E_{\text{nom}} \cdot \frac{SoC_{\text{min}}}{100} \le E(t) \le E_{\text{nom}} \cdot \frac{SoC_{\text{max}}}{100}$$
   $$150\text{ kWh} \le E(t) \le 950\text{ kWh}$$
4. **BESS Power Limits**:
   $$0 \le P_{\text{ch}}(t) \le P_{\text{ch,max}} \quad (500\text{ kW})$$
   $$0 \le P_{\text{dis}}(t) \le P_{\text{dis,max}} \quad (500\text{ kW})$$
5. **Grid Boundary Limits**:
   $$0 \le P_{\text{grid,import}}(t) \le P_{\text{grid,import,max}} \quad (500\text{ kW})$$
   $$0 \le P_{\text{grid,export}}(t) \le P_{\text{grid,export,max}} \quad (500\text{ kW})$$

