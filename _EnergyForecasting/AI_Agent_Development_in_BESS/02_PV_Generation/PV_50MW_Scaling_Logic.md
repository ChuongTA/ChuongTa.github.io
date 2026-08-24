# PV Power Plant Scaling Logic: 50 MW utility-scale solar generation from ERA5 meteorological data

This document details the engineering logic, physical equations, and conversion factors required to simulate hourly generation profiles for a **50 MW (50,000 kWp) PV Power Plant** using historical or forecast Surface Solar Radiation Downwards (SSRD) from the ERA5 reanalysis dataset.

---

## Sizing & Area Sizing Logic
To size a 50 MWp plant, we estimate the total required active module area ($A_{\text{total}}$). 

### 1. Panel Assumptions
* **Peak Output ($P_{\text{module}}$)**: $400\text{ Wp}$ to $550\text{ Wp}$ per panel. We assume standard utility-scale monocrystalline panels of **$500\text{ Wp}$** ($0.5\text{ kWp}$).
* **Module Dimensions**: Typically $2.2\text{ m} \times 1.1\text{ m} \approx 2.42\text{ m}^2$ per panel.
* **Peak Output Density**: 
  $$\frac{500\text{ Wp}}{2.42\text{ m}^2} \approx 206.6\text{ Wp/m}^2$$
* **Area per kWp Rule of Thumb**:
  $$\frac{2.42\text{ m}^2}{0.5\text{ kWp}} \approx 4.84\text{ m}^2/\text{kWp}$$
  Using a conservative industry standard design value: **$5\text{ m}^2$ of active panel surface area is required per $1\text{ kWp}$**.

### 2. Sizing Calculations
For a **50 MWp** (or $50,000\text{ kWp}$) plant capacity:
* **Number of Panels**: 
  $$N_{\text{panels}} = \frac{50,000\text{ kWp}}{0.5\text{ kWp/panel}} = 100,000\text{ panels}$$
* **Total Active Aperture Area ($A_{\text{total}}$)**:
  $$A_{\text{total}} = 50,000\text{ kWp} \times 5\text{ m}^2/\text{kWp} = 250,000\text{ m}^2$$
  *(This corresponds to exactly **25 hectares (ha)** of active panel surface. Including row spacing and access roads, the physical land footprint would be around **50–60 hectares**).*

---

## The Solar Conversion Equation

### Step 1: Converting ERA5 SSRD to Irradiance ($G_{\text{avg}}$)
ERA5 provides solar radiation as accumulated **Surface Solar Radiation Downwards (SSRD)** in Joules per square meter ($\text{J/m}^2$) over the hourly interval.

Since $1\text{ Watt} = 1\text{ Joule/second}$, and there are $3600\text{ seconds}$ in an hour, the average hourly solar irradiance ($G_{\text{avg}}$ in $\text{W/m}^2$) is:
$$G_{\text{avg}} = \frac{\text{SSRD}}{3600}\ \left[\text{W/m}^2\right]$$

### Step 2: The PV Performance Model
The electrical power output $P_{\text{PV}}(t)$ is given by the standard photo-thermal equations:
$$P_{\text{PV}}(t) = G_{\text{avg}} \times A_{\text{total}} \times \eta_{\text{PV}} \times \eta_{\text{system}} \times \eta_{\text{temp}}$$

Where:
1. **$G_{\text{avg}}$**: Irradiance hitting the panels ($\text{W/m}^2$).
2. **$A_{\text{total}}$**: Active panel area ($250,000\text{ m}^2$).
3. **$\eta_{\text{PV}}$**: Nominal module efficiency at Standard Test Conditions (STC, $25^\circ\text{C}$, $1000\text{ W/m}^2$). Set to **$20\%$** ($0.20$).
4. **$\eta_{\text{system}}$**: System losses including inverter efficiency ($98\%$), AC/DC cabling losses ($3\%$), transformer losses ($1.5\%$), and soiling/dust losses ($2\%$). Combined: **$90\%$** ($0.90$).
5. **$\eta_{\text{temp}}$**: Temperature-related losses. For cold climates like Sweden, the annual average temperature derating factor is low. Set to **$95\%$** ($0.95$).

### Step 3: Simplifying the Scaling Factor
Let's combine all constants into a single parameter:
$$\text{Factor} = A_{\text{total}} \times \eta_{\text{PV}} \times \eta_{\text{system}} \times \eta_{\text{temp}}$$
$$\text{Factor} = 250,000 \times 0.20 \times 0.90 \times 0.95 = 42,750\ \left[\text{m}^2\right]$$

To convert Watts to Kilowatts ($\text{kW}$), divide by $1000$:
$$P_{\text{PV}}(t)\ [\text{kW}] = G_{\text{avg}} \times 42.75$$

To express the plant output directly in Megawatts ($\text{MW}$):
$$P_{\text{PV}}(t)\ [\text{MW}] = G_{\text{avg}} \times 0.04275$$

---

## Sample Irradiance to Power Output Mapping

The table below demonstrates how the 50 MW plant behaves under different sky and meteorological conditions:

| Sky Condition | ERA5 SSRD ($\text{J/m}^2$) | Irradiance $G_{\text{avg}}$ ($\text{W/m}^2$) | Plant Output $P_{\text{PV}}$ ($\text{kW}$) | Plant Output $P_{\text{PV}}$ ($\text{MW}$) |
| :--- | :--- | :--- | :--- | :--- |
| **Nighttime** | $0$ | $0$ | $0\text{ kW}$ | $0.00\text{ MW}$ |
| **Overcast / Low Light** | $720,000$ | $200$ | $8,550\text{ kW}$ | $8.55\text{ MW}$ |
| **Partly Cloudy** | $1,800,000$ | $500$ | $21,375\text{ kW}$ | $21.38\text{ MW}$ |
| **Sunny (Standard)** | $2,880,000$ | $800$ | $34,200\text{ kW}$ | $34.20\text{ MW}$ |
| **Clear Sky Peak (Sweden Summer)** | $3,600,000$ | $1,000$ | $42,750\text{ kW}$ | $42.75\text{ MW}$ |

*Note: Even under maximum irradiance of $1000\text{ W/m}^2$, the plant outputs $42.75\text{ MW}$ due to system losses ($10\%$) and temperature losses ($5\%$), which is highly realistic for real-world solar systems.*
