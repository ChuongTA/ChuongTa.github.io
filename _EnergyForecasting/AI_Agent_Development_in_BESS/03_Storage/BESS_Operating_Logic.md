# Operational and Power Balance Logic for Hybrid Energy System

This document outlines the power-balance, operational priority, and optimization logic for a hybrid energy system consisting of:
$$\text{Community Load} + \text{PV Generation} + \text{Battery Energy Storage System (BESS)} + \text{Utility Grid}$$

---

## The Core Concept: Net Load

At any given operational time step $t$ (e.g., hourly or 15-minute intervals), the system dynamics are governed by the **Net Load** ($P_{\text{net}}(t)$), which is the difference between local electrical demand and local solar generation:

$$P_{\text{net}}(t) = P_{\text{load}}(t) - P_{\text{PV}}(t)$$

* If $P_{\text{net}}(t) > 0$: The energy community is in a **solar deficit** (demand is higher than local generation).
* If $P_{\text{net}}(t) < 0$: The energy community is in a **solar surplus** (local generation is higher than demand).
* If $P_{\text{net}}(t) = 0$: The system is in a **balanced state** where local generation exactly covers the load.

---

## Power Flow Logic & Operational Priorities

### 1. Deficit Scenario ($P_{\text{net}}(t) > 0$)
When consumption is higher than PV generation, the shortage is covered using a tiered priority approach:

```
[Net Load > 0]
      │
      ▼
┌──────────────┐      Yes      ┌──────────────────────┐
│  BESS empty? ├──────────────>│ Import from Grid     │
└──────┬───────┘               └──────────────────────┘
       │ No
       ▼
┌──────────────────────────────┐
│ Discharge BESS to cover load │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐      Yes      ┌──────────────────────┐
│ Deficit > Max Discharge Rate?├──────────────>│ Import remainder     │
└──────────────────────────────┘               │ from Grid            │
                                               └──────────────────────┘
```

* **Priority 1: BESS Discharge**  
  If the battery state of charge is above its minimum threshold ($SoC(t) > SoC_{\text{min}}$), the BESS discharges to cover the net load, constrained by its maximum discharging power limit ($P_{\text{dis,max}}$):
  $$P_{\text{BESS}}(t) = \min(P_{\text{net}}(t),\ P_{\text{dis,max}})$$
* **Priority 2: Grid Import (Buying)**  
  If the battery is depleted or cannot meet the full deficit due to its maximum discharge rate, the remaining power is imported from the utility grid:
  $$P_{\text{grid,import}}(t) = P_{\text{net}}(t) - P_{\text{BESS}}(t)$$

---

### 2. Surplus Scenario ($P_{\text{net}}(t) < 0$)
When PV generation exceeds local consumption, the excess renewable energy is handled as follows:

```
[Net Load < 0]
      │
      ▼
┌──────────────┐      Yes      ┌──────────────────────┐
│  BESS full?  ├──────────────>│ Export to Grid       │
└──────┬───────┘               └──────────────────────┘
       │ No
       ▼
┌──────────────────────────────┐
│ Route excess to BESS (Charge)│
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐      Yes      ┌──────────────────────┐
│ Surplus > Max Charging Rate? ├──────────────>│ Export remainder     │
└──────────────────────────────┘               │ to Grid              │
                                               └──────────────────────┘
```

* **Priority 1: BESS Charging**  
  Direct the surplus power to charge the battery to store it for future deficit periods. The charging power is limited by the maximum charging rate ($P_{\text{ch,max}}$) and BESS capacity limits ($SoC(t) < SoC_{\text{max}}$):
  $$P_{\text{BESS}}(t) = -\min(|P_{\text{net}}(t)|,\ P_{\text{ch,max}})$$
* **Priority 2: Grid Export (Selling / Feed-in)**  
  If the battery is fully charged or hits its charging power limit, the remaining excess solar energy is exported (sold) to the utility grid:
  $$P_{\text{grid,export}}(t) = |P_{\text{net}}(t)| - |P_{\text{BESS}}(t)|$$

---

## Advanced Multi-Objective Optimization Criteria

Under spot pricing (e.g., Denmark's Nord Pool DK1 zone), an AI Agent or mathematical optimization engine (like Pyomo/MILP) shifts this standard logic to maximize economic and grid benefits:

1. **Price Arbitrage (Time-of-Use Trading)**
   * **Grid-to-BESS charging**: When grid prices are extremely cheap or negative (e.g., during night valley hours), the system imports grid power directly to charge the battery.
   * **BESS-to-Load/Grid discharging**: The stored energy is discharged during high peak-price hours to avoid high import tariffs or to generate revenue via exports.
2. **Peak Shaving (Contractual Grid Support)**
   * Regardless of market price, if local consumption spikes close to the substation physical limit or contractual grid import limit (e.g., $500\text{ kW}$), the BESS discharges immediately to ensure grid stability and avoid high peak-demand penalties.
3. **BESS Health (Degradation Constraint)**
   * The optimization model balances financial arbitrage profits against the cost of battery degradation (wear and tear per cycle), preventing unnecessary cycles when price spreads are small.
