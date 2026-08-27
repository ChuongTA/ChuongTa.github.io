# Mathematical Modeling and Generation Logic for Community Loads

This document provides the detailed mathematical formulations, profiles, and parameter specifications for generating the synthetic energy community load profile. 

The goal is to translate these exact logical and mathematical steps into a Python script (`generate_load_profiles.py`) to output a high-resolution time-series CSV file containing load profiles for all components.

---

## 1. Output CSV Structure

The generated CSV file will cover the same timeline as the weather data (January 1, 2024, to September 30, 2025, hourly frequency) with the following columns:

| Column Name | Unit | Description |
| :--- | :--- | :--- |
| `timestamp` | YYYY-MM-DD HH:MM:MM | Datetime index (hourly) |
| `office_load_kw` | kW | Demand profile for commercial office buildings |
| `logistics_load_kw` | kW | Demand profile for logistics centers |
| `manufacturing_load_kw` | kW | Demand profile for light manufacturing facilities |
| `ev_passenger_load_kw` | kW | Flexible demand from employee passenger EVs |
| `ev_hgv_load_kw` | kW | Flexible demand from heavy goods vehicles (HGVs) |
| `total_load_kw` | kW | Aggregated sum of all demand components |

---

## 2. Mathematical Formulations per Sector

To simulate realistic electrical behaviors, each load profile combines a **baseline consumption**, a **diurnal time-of-day profile (using step, trigonometric, or Gaussian functions)**, a **weekly day-of-week modifier**, and **stochastic noise (representing random demand fluctuations)**.

$$P_{\text{load}}(t) = \left( P_{\text{base}} + P_{\text{diurnal}}(t) \right) \times M_{\text{day}}(t) + \epsilon(t)$$

Where:
* $P_{\text{base}}$: Constant baseline standby power ($\text{kW}$).
* $P_{\text{diurnal}}(t)$: Time-of-day profile function.
* $M_{\text{day}}(t)$: Multiplier based on day of the week (weekday vs. weekend).
* $\epsilon(t)$: Random Gaussian noise $\sim \mathcal{N}(0, \sigma^2)$ representing electrical volatility.

---

### A. Office Buildings (Commercial Pattern)
Office loads are highly dependent on business hours (08:00 to 18:00) during weekdays, showing dual peaks (morning arrival and afternoon activity) and collapsing to a minor standby baseline at night and on weekends.

* **Parameters**:
  * $P_{\text{base}} = 10\text{ kW}$
  * Peak Active Power: Up to $80\text{ kW}$ additional (total $90\text{ kW}$ peak).
  * Weekday Multiplier ($M_{\text{weekday}}$): $1.0$
  * Weekend Multiplier ($M_{\text{weekend}}$): $0.1$ (only basic heating/ventilation and server standby).
* **Diurnal Equation** ($P_{\text{diurnal}}(t)$ where $h$ is hour of day 0–23):
  We model the office active hours using a double Gaussian curve to represent the two peak periods (10:00 and 15:00):
  $$P_{\text{diurnal}}(h) = 80 \times \left( 0.5 \times e^{-\frac{(h-10)^2}{2 \times 1.5^2}} + 0.5 \times e^{-\frac{(h-15)^2}{2 \times 1.5^2}} \right)$$
* **Noise**:
  $$\epsilon(t) \sim \mathcal{N}(0, 2^2)\ \text{(Standard deviation } \sigma = 2\text{ kW)}$$

---

### B. Logistics Centers (Shift & Shipping Spikes)
Logistics centers operate with a constant low background load, but experience sharp peaks during truck loading/unloading shift intervals.

* **Parameters**:
  * $P_{\text{base}} = 20\text{ kW}$
  * Morning Loading Peak (06:00 – 09:00): $+120\text{ kW}$
  * Evening Unloading Peak (17:00 – 20:00): $+150\text{ kW}$
  * Operating Days: Monday to Saturday.
  * Multipliers: Weekdays/Saturdays = $1.0$, Sundays = $0.15$ (maintenance/security only).
* **Diurnal Equation** ($P_{\text{diurnal}}(h)$ where $h$ is hour 0–23):
  Represented by step functions or localized Gaussians around the shipping hours:
  $$P_{\text{diurnal}}(h) = \begin{cases} 
        120 \times e^{-\frac{(h-7.5)^2}{2 \times 1.0^2}} & \text{if } 5 \le h \le 10 \\
        150 \times e^{-\frac{(h-18.5)^2}{2 \times 1.0^2}} & \text{if } 16 \le h \le 21 \\
        15 & \text{for midday operations } (10 < h < 16) \\
        0 & \text{otherwise}
     \end{cases}$$
* **Noise**:
  $$\epsilon(t) \sim \mathcal{N}(0, 4^2)\ \text{(Standard deviation } \sigma = 4\text{ kW)}$$

---

### C. Light Manufacturing Facility (Industrial Shift Load)
Manufacturing facilities operate continuously during weekdays with specific block shifts, and shut down for maintenance over weekends.

* **Parameters**:
  * $P_{\text{base}} = 80\text{ kW}$
  * Shift 1 (06:00 to 14:00): $+220\text{ kW}$ (Total $300\text{ kW}$)
  * Shift 2 (14:00 to 22:00): $+220\text{ kW}$ (Total $300\text{ kW}$)
  * Shift 3 (22:00 to 06:00): $+120\text{ kW}$ (Night shift, total $200\text{ kW}$)
  * Weekday Multiplier ($M_{\text{weekday}}$): $1.0$
  * Weekend Multiplier ($M_{\text{weekend}}$): $0.15$ (maintenance cooling/standby, total $\approx 15\text{ kW}$).
* **Diurnal Equation** ($P_{\text{diurnal}}(h)$ where $h$ is hour 0–23):
$$
P_{\text{diurnal}}(h) =
\begin{cases}
220 & \text{if } 6 \le h < 22 \ \text{(Shift 1 and 2)} \\
120 & \text{if } h < 6 \ \text{or} \ h \ge 22 \ \text{(Shift 3)}
\end{cases}
$$

* **Noise**:
  $$\epsilon(t) \sim \mathcal{N}(0, 6^2)\ \text{(Standard deviation } \sigma = 6\text{ kW)}$$

---

### D. Employee Passenger EVs (Flexible Daytime)
Employee vehicles arrive in the morning, plug in, and charge dynamically based on solar abundance or price. To simulate the *unmanaged/baseline* charging profile before optimization:

* **Parameters**:
  * 30 charging points, max power $11\text{ kW}$ per charger.
  * Connection window: Weekdays, arrival between 07:30 and 09:00, departure between 16:30 and 18:00.
  * Baseline charging profile: Vehicles plug in and charge at maximum power until full (average energy needed is $25\text{ kWh}$ per vehicle, taking $\approx 2.3$ hours).
* **Baseline Diurnal Equation** ($P_{\text{diurnal}}(h)$ on Weekdays):
  $$P_{\text{ev\_pass}}(h) = \begin{cases} 
        200 \times e^{-\frac{(h-9.5)^2}{2 \times 1.2^2}} & \text{if } 8 \le h \le 13 \\
        0 & \text{otherwise}
     \end{cases}$$
  *(Weekend baseline charging is $0\text{ kW}$).*

---

### E. HGV Fleet Charging (Flexible Nighttime Depot)
Heavy Goods Vehicles return to the depot in the evening and charge overnight.

* **Parameters**:
  * 5 HGV chargers, max power $150\text{ kW}$ each (Total capacity $750\text{ kW}$).
  * Connection window: Monday to Friday nights, arrival 18:00 to 20:00, departure 05:00 to 07:00.
  * Baseline charging profile: Vehicles charge at maximum rate upon arrival (average energy needed is $300\text{ kWh}$ per vehicle, taking $\approx 2.0$ hours).
* **Baseline Diurnal Equation** ($P_{\text{diurnal}}(h)$ on Weekdays):
  $$P_{\text{ev\_hgv}}(h) = \begin{cases} 
        600 \times e^{-\frac{(h-20.5)^2}{2 \times 1.0^2}} & \text{if } 18 \le h \le 23 \\
        0 & \text{otherwise}
     \end{cases}$$

---

## 3. Total Aggregated Community Load

The final total load column is calculated as:
$$P_{\text{total}}(t) = P_{\text{office}}(t) + P_{\text{logistics}}(t) + P_{\text{manufacturing}}(t) + P_{\text{ev\_pass}}(t) + P_{\text{ev\_hgv}}(t)$$
All values are clipped at a minimum of $0.0\text{ kW}$ to prevent noise from generating negative power values.