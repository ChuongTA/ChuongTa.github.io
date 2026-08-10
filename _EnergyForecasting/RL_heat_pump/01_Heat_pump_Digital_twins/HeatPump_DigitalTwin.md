---
title: "Heat Pump Digital Twins: Modeling and Hybrid State Estimation"
excerpt: "An introduction to heat pump technologies, thermodynamic cycles, coefficient of performance (COP), and building physical-informed digital twins."
layout: single
author_profile: true
permalink: /EnergyForecasting/RL_heat_pump/HeatPump_DigitalTwin/
usemathjax: true
date: 2026-08-10
categories:
  - "District Heating and Cooling"
  - "Heat Pump"
image: "/EnergyForecasting/RL_heat_pump/01_Heat_pump_Digital_twins/Images/Fig5.png"
---

## 1. Introduction to Heat Pump Technologies

A heat pump is an energy-efficient device that provides climate control by moving heat from one location to another using electricity and a refrigerant circuit, rather than generating heat by burning fossil fuels. In winter, it extracts thermal energy from the ambient air, ground, or water sources to heat a building. In summer, the cycle reverses, removing heat from the indoor air and exporting it outside, operating exactly like an air conditioner. (Source: [Carrier](https://www.carrier.com/us/en/residential/hvac-resources/heat-pumps/what-is-a-heat-pump-how-does-it-work/))

Beyond residential spaces, heat pumps meet heating requirements in commercial buildings and industrial applications, delivering hot air, hot water, or steam. Large-scale heat pumps integrated into industrial processes or district heating networks often require higher input temperatures. These systems frequently extract thermal energy from waste heat sources, such as data centers, wastewater treatment plants, and industrial exhaust streams. (Source: [IEA](https://www.iea.org/reports/the-future-of-heat-pumps/how-a-heat-pump-works))

---

## 2. Thermodynamic Advantages and Disadvantages

*(Note: Data and advantages synthesized from the Leonardo da Vinci project ENERSOL report: **Energy Saving and Renewable Energy in Vocational Education**)*

### 2.1 Advantages
*   **Energy Efficiency:** Heat pumps reduce electricity consumption by approximately $70\%$ compared to direct resistance electric heating. While conventional electric heaters convert electricity directly into heat at a $1:1$ ratio, heat pumps use electricity only to drive the compressor, extracting the remaining thermal energy from the environment.
*   **Economic Savings:** By using less electricity to deliver the same heating load, operational energy costs are significantly lower than resistance heating. Actual financial savings depend on local fuel tariffs, capital investment costs, and state subsidies.
*   **Environmental Impact:** Lower electricity demand reduces primary energy requirements and the associated emissions from power plants. Transitioning to heat pumps can reduce local $\text{NO}_x$ emissions by up to $70\%$ and $\text{SO}_2$ emissions by up to $30\%$.

### 2.2 Disadvantages
*   **Initial Capital Investment:** The primary drawback of heat pump systems is their high upfront cost, leading to typical payback periods of 6 to 8 years. The exact return on investment depends on the building's current insulation levels, the low-temperature heat source chosen, and government incentives.

---

## 3. Working Principles and Classifications

Heat pumps generally fall into two categories: **vapour compression** systems and **absorption** systems. (Source: [JICA Report](https://openjicareport.jica.go.jp/pdf/11511847_03.pdf))

### 3.1 Vapour Compression Systems
Most heat pumps operate on a closed vapour compression cycle. The system consists of four primary components: an evaporator, a compressor, a condenser, and an expansion valve.

<figure style="display: block; margin: 1.5em auto; text-align: center;">
  <img src="/EnergyForecasting/RL_heat_pump/01_Heat_pump_Digital_twins/Images/Fig1.png" alt="Working of the vapour compression heat pump" style="max-width: 100%; height: auto; border-radius: 8px; border: 1px solid var(--global-border-color);">
  <figcaption style="margin-top: 0.5em; font-size: 0.9em; color: var(--global-text-color-light);">Figure 1: Diagram of the vapour compression heat pump cycle. Source: Carrier</figcaption>
</figure>

The working fluid (refrigerant) circulates continuously through these components:
1.  **Evaporator (1):** The refrigerant is kept at a temperature lower than the external heat source, causing heat to transfer into the fluid and boil it into a low-pressure vapour.
2.  **Compressor (2):** The vapour is compressed, increasing its pressure and temperature. The compressor is the primary consumer of electrical energy in the system, typically driven by an electric motor.
3.  **Condenser (3):** The hot, high-pressure vapour enters the condenser, where it releases its latent heat to the building's heating circuit, condensing back into a liquid state.
4.  **Expansion Valve (4):** The high-pressure liquid refrigerant passes through the expansion valve, dropping in pressure and temperature back to the evaporator levels, completing the cycle.

<figure style="display: block; margin: 1.5em auto; text-align: center;">
  <img src="/EnergyForecasting/RL_heat_pump/01_Heat_pump_Digital_twins/Images/Fig2.png" alt="Basic heat pump components" style="max-width: 100%; height: auto; border-radius: 8px; border: 1px solid var(--global-border-color);">
  <figcaption style="margin-top: 0.5em; font-size: 0.9em; color: var(--global-text-color-light);">Figure 2: Exploded view of heat pump mechanical components. Source: Leonardo da Vinci project ENERSOL</figcaption>
</figure>

### 3.2 Absorption Heat Pumps
Unlike mechanical vapour compression systems, absorption heat pumps are thermally driven. Instead of using mechanical work (a compressor) to increase refrigerant pressure, they use high-temperature heat (from gas combustion, steam, or industrial waste heat). 

Absorption systems rely on the chemical affinity between a refrigerant and an absorbent. Common pairs include:
*   Water (refrigerant) and Lithium Bromide (absorbent)
*   Ammonia (refrigerant) and Water (absorbent)

The compression stage is replaced by a thermal circuit containing an absorber, a solution pump, a generator, and an expansion valve:

<figure style="display: block; margin: 1.5em auto; text-align: center;">
  <img src="/EnergyForecasting/RL_heat_pump/01_Heat_pump_Digital_twins/Images/Fig3.png" alt="Working principle of an absorption heat pump" style="max-width: 100%; height: auto; border-radius: 8px; border: 1px solid var(--global-border-color);">
  <figcaption style="margin-top: 0.5em; font-size: 0.9em; color: var(--global-text-color-light);">Figure 3: Schematic of an absorption heat pump cycle. Source: Leonardo da Vinci project ENERSOL / openjicareport.jica.go.jp</figcaption>
</figure>

1.  Low-pressure refrigerant vapour from the evaporator is absorbed by the absorbent liquid in the **absorber (1)**, releasing absorption heat.
2.  The liquid mixture is pumped to high pressure using a small **solution pump (2)** (requiring minimal electrical power).
3.  The pressurized mixture enters the **generator (3)**, where external heat boils off the refrigerant vapour from the absorbent.
4.  The separated refrigerant vapour moves to the condenser to release useful heat, while the concentrated absorbent returns to the absorber via an **expansion valve (4)**.

---

## 4. Key Performance Parameters

### 4.1 Coefficient of Performance (COP)
The efficiency of a heat pump is measured by the **Coefficient of Performance (COP)**, defined as the ratio of useful heat output to the electrical energy input:

$$\text{COP} = \frac{Q_{\text{output}}}{W_{\text{input}}}$$

Typical COP values range from $2.5$ to $4.0$, meaning that $1\text{ kWh}$ of electricity yields $2.5$ to $4.0\text{ kWh}$ of heat. The COP is not static; it is highly dependent on the temperature difference between the heat source and the target heating system. A smaller temperature difference results in a higher COP because the compressor works less.

We can approximate COP variation with outdoor temperature using a linear model:

$$\text{COP}(T_{\text{amb}}) = \text{COP}_0 + \alpha \cdot (T_{\text{amb}} - 5)$$

Where:
*   $\text{COP}_0$ is the baseline COP at $5^\circ\text{C}$ (e.g., $3.0$).
*   $\alpha$ is the temperature coefficient (e.g., $0.05$).

### 4.2 Heating Power
The total heating power delivered to the condenser is the sum of the environmental heat extracted by the evaporator and the electrical power converted into heat during compression:

$$\Phi_H = Q_{\text{evaporator}} + W_{\text{compressor}}$$

### 4.3 Seasonal Performance Factor (SPF)
While the COP measures efficiency at a specific operating point, the **Seasonal Performance Factor (SPF)** describes the heat pump's efficiency aggregated over an entire season. It accounts for variable heating and cooling loads, changing outdoor air/source temperatures, and auxiliary energy consumption over the year.

---

## 5. Heat Pump Configurations

Heat pumps are classified by their source and sink mediums:

<figure style="display: block; margin: 1.5em auto; text-align: center;">
  <img src="/EnergyForecasting/RL_heat_pump/01_Heat_pump_Digital_twins/Images/Fig4.png" alt="Heat pump configuration types" style="max-width: 100%; height: auto; border-radius: 8px; border: 1px solid var(--global-border-color);">
  <figcaption style="margin-top: 0.5em; font-size: 0.9em; color: var(--global-text-color-light);">Figure 4: Comparison of common heat pump source-to-sink configurations. Source: IEA</figcaption>
</figure>

### 5.1 Air-to-Water
Extracts heat from ambient outdoor air (or ventilation exhaust air) and transfers it to a water-based central heating loop. These systems are popular due to lower installation costs, but their efficiency drops during cold winter days.

### 5.2 Water-to-Water
Uses groundwater, surface water, or wastewater as the heat source. Because water temperatures remain relatively stable throughout the winter, these heat pumps maintain high efficiency, though they require access to a reliable water source.

### 5.3 Ground-to-Water (Geothermal)
Draws heat from the ground via horizontal pipe loops (buried 1–2 meters deep) or vertical boreholes (up to 100 meters deep). Antifreeze fluid circulates through the ground loop to absorb thermal energy, providing high and stable COPs year-round.

---

## 6. Digital Twins for Heat Pump Systems

A **Digital Twin** is a virtual, numerical representation of a physical system that adapts to its real-world counterpart. By continuously processing operational data, digital twins enable real-time state estimation, fault detection and diagnosis, predictive maintenance, and optimized control. (Source: [Danish Technological Institute](https://www.dti.dk/projects/digital-twins/41553))

<figure style="display: block; margin: 1.5em auto; text-align: center;">
  <img src="/EnergyForecasting/RL_heat_pump/01_Heat_pump_Digital_twins/Images/Fig5.png" alt="Digital Twin Concept" style="max-width: 100%; height: auto; border-radius: 8px; border: 1px solid var(--global-border-color);">
  <figcaption style="margin-top: 0.5em; font-size: 0.9em; color: var(--global-text-color-light);">Figure 5: Digital twin framework for large-scale heat pump and refrigeration systems. Source: Danish Technological Institute</figcaption>
</figure>

### 6.1 Hybrid State Estimation
A common strategy in district heating is deploying a hybrid digital twin. This approach combines a physics-based baseline model with a machine-learning model that learns the residual errors.

The physics layer models the thermal dynamics of the system (e.g., a storage tank or thermal loop) using a differential energy-balance equation:

$$C \frac{dT}{dt} = Q_{\text{hp}} - Q_{\text{demand}} - Q_{\text{loss}}$$

Where:
*   $C$ is the thermal heat capacity.
*   $Q_{\text{hp}}$ is the heat input from the heat pump.
*   $Q_{\text{demand}}$ is the network thermal load.
*   $Q_{\text{loss}}$ is the thermal loss to the ambient environment.

While this physics model ensures thermodynamic consistency (mass and energy conservation), it struggles with unmodeled dynamics, such as insulation degradation or sensor drift.

To correct these errors, a machine-learning model (such as LightGBM) is trained to predict the temperature residual ($T_{\text{measured}} - T_{\text{physics}}$). During operation, the final state estimate is obtained by combining both predictions:

$$T_{\text{corrected}} = T_{\text{physics}} + f_{\text{ML}}(\text{measured features})$$

This hybrid approach ensures the digital twin remains structurally grounded by physics while retaining the flexibility to adapt to real-world deviations.

---

## References

*   **Carrier Corporation:** [What Is A Heat Pump And How Does It Work?](https://www.carrier.com/us/en/residential/hvac-resources/heat-pumps/what-is-a-heat-pump-how-does-it-work/)
*   **International Energy Agency (IEA):** [How a heat pump works – The Future of Heat Pumps Analysis](https://www.iea.org/reports/the-future-of-heat-pumps/how-a-heat-pump-works)
*   **Leonardo da Vinci project ENERSOL:** *EU Heat Pumps – Energy Saving and Renewable Energy in Vocational Education Report*.
*   **Japan International Cooperation Agency (JICA):** [Vapour Compression and Absorption Systems Technical Report](https://openjicareport.jica.go.jp/pdf/11511847_03.pdf)
*   **Danish Technological Institute:** [Digital twins for large-scale heat pumps and refrigeration systems](https://www.dti.dk/projects/digital-twins/41553)

---
*The next post will explore Reinforcement Learning for smart heat pump control within this digital twin framework.*