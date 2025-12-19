---
title: "Icing formation in Wind turbines in Cold climate region (part 1)"
category: densys
excerpt: "In this first post of wind energy, I will walk you through the topic icing formation. In the cold climate regions, icing on wind turbines is significant problem, impacting both performance and physical reliability..."
layout: single
author_profile: true
permalink: /WindEnergy/Icing_formation.md/
usemathjax: true
---

In the Nordic countries, the wind energy capacity is substantially higher in winter due stronger wind and higher air density. Therefore, countries with a high wind potential and intensive cold climates to advance wind power development. 

![Average wind speed in the world in winter](/files/Icing_formation/Wind_speed_winter_in_europe.png)
*Figure 1: Average wind speed in the world in winter [1](https://climate.copernicus.eu/esotc/2022/wind-solar-energy-resources)*

![Countries by january average low temperature](/files/Icing_formation/temperature_in_january.jpg)
*Figure 2: Countries by january average low temperature [2](https://www.reddit.com/r/europe/comments/kob7to/countries_by_january_average_low_temperatures_of/)*

By 2050, wind energy capacity in cold climate regions throughout Scandinavia, North America, Europe and Asia is projected to reach approximately [250-400 GW] (estimated based on current growth trajectories from the 200+ GW installed by 2024). In spite of that, wind turbines in severely cold climates must withstand challenging conditions, particularly frequent subzero temperatures and ice formation(https://windren.se/WW2021/14_2_21_Karlsson_IEA_Wind_Task_19_Cold_climate_wind_market_study_Public.pdf).

In addition to average air temperatures below zero Celcius degree for large part of the year, high humidity levels promote ice formation and accumation on wind-expose structures and wind farm access routes. Generally speaking, the term "icing" describes ice accumulation from atmospheric precipitation and marine spray. This accretion stationary and dynamic turbine parts by modifying aerodynamic profile performance and adding mass to contaminated components.

For offshore icing: "creepy icing" has been recognised as a problem for sea structures.
In the cold climates, offshore wind turbines are threaten by:
- Sea sprays: Saltwater spray origininating from the sea surface.
- Atmospheric icing: freshwater ice originating from atmosphere.
- Sea ice: Floating ice blocks or ice parks that cause additional static and dynamic forces, and vibration on the wind turbine tower/foundation. 

## 1.Fundamental physics of ice accretion

The phenomenon is a multiphase interaction involving fluid dynamics, thermodynamics, and cloud microphysics.

### 1.1. Meteorological preconditions and microphysics

Liquid water content (LWC), median volumetric diameter (MVD), and Ambient temperature ($$T_a$$)

- Liquid water content (LWC) is defined as the mass of water contained in a unit volume of air. It acts as the "fuel" for the accretion process. Higher LWC values effectively increase the flux of water mass impinging on the blade surface, leading to rapid ice buildup and a shorter duration required to reach critical power loss thresholds.
- Median Volumetric Diameter (MVD) is the droplet size that divides the total water volume in half. If the MVD is 200 micrometers, it means 50% of the water volume comes from droplets smaller than 200 μm, and 50% from droplets larger than 200 μm. This differs from simply counting droplets because larger droplets contain much more water than smaller ones. Larger droplets (high MVD) possess greater inertia, meaning they are less likely to follow the streamline deflection around the airfoil and more likely to impact the blade surface ballistically. Conversely, smaller droplets maybe swept around the leading edge by aerodynamic forces, reducing the collision efficiency. MVD is therefore a determinant of both rate of accretion and the limit of impingement - how far back along the chord the ice can form.

![Median volumetric diameter.](/files/Icing_formation/vmd-ncsu.gif)
*Figure 3: Median volumetric diameter [4](https://pesticidestewardship.org/pesticide-drift/understanding-droplet-size/)*

- Ambient temperature and phase change: The temperature describe the thermodynamic solidification process. It determines the "sticking fraction" (how much water adheres) and the freezing rate. This thermal balance is what differentiates the two primary ice types: rime and glaze.

### 1.2 Ice Models

Scientists have developed various mathematical models to predict how ice forms on structures. These models serve as the foundation for computer software that simulates ice buildup in various meteorological conditions.

#### Messinger Model (1953)
The Messinger model uses an energy balance approach, tracking all the heat flowing into and out of the icing surface.

**Energy Balance Equation:**
$$Q_{conv} + Q_{rad} + Q_{evap} = Q_{imp} + Q_{lat}$$



Detailed explanations for each heat transfer term:

**Heat Losses:**
* **Convective heat transfer ($$Q_{conv} = q_c (T_a - T_s)$$):** Cold air rushing over the wing removes heat, similar to how blowing on hot soup cools it. The heat transfer coefficient $$q_c$$ determines how efficiently this occurs.
* **Radiative cooling ($$Q_{rad} = -\epsilon \sigma (T_s^4 - T_a^4)$$):** The surface radiates heat to the cold sky, following Stefan-Boltzmann law. This effect is usually small but becomes important at high altitudes.
* **Evaporative cooling ($$Q_{evap} = -\dot{m}_s L_s$$):** Water molecules can evaporate or sublimate directly from ice, carrying away significant energy - about 2.83 MJ/kg.

**Heat Sources:**
* **Laten heat from freezing ($$Q_{lat} = \dot{m}_{freeze} L_f$$):** When water freezes, it release energy-about 3.34 MJ/kg. On the wing surface, this released heat actually opposes further freezing.
* **Sensible heat from droplets ($$Q_{imp} = m_{imp} c_{p,w} (T_a - T_s)$$):** incoming droplets carry thermal energy based on their temperature. If they're warmer than the surfcae, the deposit heat when they impact.

---

#### Makkonen Model
The Makkonen model directly calculates ice mass accumlation rate:

**Mass Accumulation Equation:**
$$\frac{dM}{dt} = \alpha_1 \alpha_2 \alpha_3 \omega v A$$

* **Collision efficiency ($$\alpha_1$$):** Not all droplets in the air actually hit the object—some flow around it. Small droplets follow air streamlines better and miss the object, while large droplets have more inertia and collide.
* **Collision efficiency ($$\alpha_2$$):** Some droplets that hit the surface bounce off or shatter instead of sticking. This depends on impact velocity and droplet size.
* **Accretion efficiency ($$\alpha_3$$):** Of the water that sticks, only a fraction actually freezes—the rest may run off as liquid. This is determined by the freezing fraction:
  $$\alpha_3 = \frac{c_{p,w} (T_f - T_d) + L_f}{L_f + L_s - c_{p,i} T_s}$$
  showing how droplet temperature and surface conditions determine freezing fraction.
* **Mass flux ($$\omega v A$$):** This is simply the rate at which water would flow through the cross-sectional area if no object were there, liquid water content times velocity times are.

## 2.Type of ice
### a, Rime ice

Rime ice forms under conditions of low temperature (typically $$<-10^\circ C$$) and low LWC. In this regime, the convective heat transfer is sufficient to remove the latent heat of fusion almost instantly upon droplet impact. The droplets freeze individually at the point of impingement, trapping air pockets between the ice granules.
- Characteristics: Rime ice appears opaque, milky, and rough. It has a low density, typically ranging from 200 to 600 $$kg/m^3$$.
- Aerodynamic Implication: Because it freezes on impact, rime ice tends to conform to the leading edge, growing forward into the wind. While it preserves the general airfoil shape better than glaze, its rough surface texture acts as a powerful trip mechanism for the boundary layer, inducing premature turbulence.

![Rime ice](/files/Icing_formation/Heavy_of_rime_ice_in_wind_blade.png)
*Figure 4: Heavy of rime ice in wind blade [5](https://www.aere.iastate.edu/~huhui/WT-icing.html)*

### b, Glaze ice

Glaze ice, frequently referred to as clear ice, forms when supercooled precipitation strikes a cold surface and freezes. During this process, the release of latent heat prevents the water from freezing instantly, allowing it to flow and expand over the surface. This continuous liquid film prevents air pockets from becoming trapped, resulting in a dense, transparent, and uniform ice structure. Because it is clear and does not crumble, glaze ice is often difficult to spot with the naked eye. It typically has a high density of around $$900 \text{ kg/m}^3$$and forms in temperatures between$$0^{\circ}\text{C}$$and$$-6^{\circ}\text{C}$$, often in the presence of freezing rain. This phenomenon is similar to the "black ice" found on roadways, which is notoriously hard to detect due to its thinness and transparency. 

![Glaze Ice](/files/Icing_formation/glaze_ice.jpg)
*Figure 5: Glaze ice [6](https://en.wikipedia.org/wiki/Glaze_%28ice%29)*

### c, Mixed ice and wet snow
When temperatures fluctuate between 0 °C and 3°C, snow crystals with a high water content can adhere and bond to structures. When the temperature drops, accumulated wet snow freezes to form ice that has a density varying between 300 and 600 kg/m3. Visually, it resembles rime.

### d, Hoar frost 

At very low temperatures, the likelihood of ice formation diminishes, as the water droplets no longer exist in a supercooled state. However, another phenomenon may occur, namely the solid condensation of water vapor in the air. This type of ice, known as hoar frost, is produced when relative air humidity is high (above 90%) and winds are low. Although this type of ice is responsible for corona losses on power transmission lines, its density and bond strength are low, which limits the mechanical loads imparted on the structures. As a result, hoar frost is also less dangerous in terms of ice shed. 

![Freezing fog (hoar frost) on top of a wind turbine](/files/Icing_formation/Freezing_fog.png)
*Figure 6: Freezing fog (hoar frost) on top of a wind turbine [7](https://www.reddit.com/r/mildlyinteresting/comments/ke87j9/freezing_fog_hoar_frost_on_top_of_a_wind_turbine/)*

### Consequences of icing formation on wind turbines

A critical debate in the literature, illuminated by recent CFD studies, concerns the relative impact of surface roughness versus gross geometric deformation.
- Roughness Effects: Even the initial accretion of ice creates a surface roughness analogous to sandpaper. This roughness perturbs the laminar boundary layer, causing a transition to turbulent flow near the leading edge. This increases skin friction drag and reduces the maximum lift coefficient ($$C_{L,max}$$). Simulation data suggests that extended roughness regions in the chordwise direction can be as detrimental to power output as the macroscopic ice shape itself.
- Geometric Effects: As ice structures grow (particularly glaze horns), they act as bluff bodies attached to the streamlined airfoil. This induces massive pressure drag and large-scale flow separation bubbles.
- Structural: Added mass of ice (up to 50% of blade weight). Uneven ice accretion and mass imbalance. Also, it increases Loads and Fatigue: Higher static and dynamic loads; reduced fatigue lifetime on components. Vibrations: Excessive vibrations due to rotor unbalance. Reduced Natural Frequency: Natural frequencies decrease, risking resonance.
- Operational/Safety: Ice accumulation on sensors. Ice chunks detaching (shedding). Technical Unavailability: WT stoppage, downtime, and reduced availability. Safety Hazard: Ice throw/fall risks to personnel and nearby asset.

![Icing formation in wind turbine consequences](/files/Icing_formation/WT_icing_consequences.jpg)
*Figure 7: Icing formation in wind turbine consequences [8](https://www.aere.iastate.edu/~huhui/WT-icing.html)*

### 5. De-icing methods
The de-icing methods are described in the table below: 

**Table 1: Wind Turbine De-icing and Anti-icing Methods**

| Method | Type | Description | Source |
| :--- | :--- | :--- | :--- |
| **Electrical Resistance Heating** | Active (Thermal) | Heating elements (often embedded) raise the blade surface temperature to prevent or remove ice. While successful, it is noted to be energy inefficient. | [Habibi et al.](https://doi.org/10.1016/j.coldregions.2016.04.011)|
| **Hot Air Circulation** | Active (Thermal) | Circulates hot air inside the blade to heat the surface. This method consumes a significant amount of energy, potentially up to 15% of the turbine's nominal output. | [Habibi et al.](https://doi.org/10.1016/j.coldregions.2016.04.011)<br>[Martini et al.](https://doi.org/10.3390/en14165207)|
| **Microwave Heating** | Active (Thermal) | Uses microwave energy to heat the ice/blade interface. It is described as having poor performance in some studies. | [Habibi et al.](https://doi.org/10.1016/j.coldregions.2016.04.011)|
| **Pulse Electro-Thermal** | Active (Thermal) | A more recent technique involving pulsed heating to de-ice, often discussed in the context of optimizing energy consumption. | [Martini et al.](https://doi.org/10.3390/en14165207)|
| **Ultrasonic Guided Waves (UGW)** | Active (Mechanical) | Uses high-frequency waves to induce shear stress at the ice-blade interface, weakening the bond to de-bond the ice layer. | [Habibi et al.](https://doi.org/10.1016/j.coldregions.2016.04.011)|
| **Low-Frequency Vibration (LFV)** | Active (Mechanical) | Induces high accelerations (e.g., 25g to 30g) in the blade to mechanically shed ice that has already been weakened (often used in combination with UGW). | [Habibi et al.](https://doi.org/10.1016/j.coldregions.2016.04.011)|
| **Active Pitching** | Active (Mechanical) | Adjusting the blade pitch to physically shake off ice or alter aerodynamic loads. This is associated with risks to structural integrity. | [Habibi et al.](https://doi.org/10.1016/j.coldregions.2016.04.011)|
| **Coatings and Painting** | Passive | Applying special hydrophobic or ice-phobic coatings to reduce ice adhesion. Drawbacks include potential heat absorption issues and durability. | [Habibi et al.](https://doi.org/10.1016/j.coldregions.2016.04.011)|
| **Anti-freeze Chemicals** | Passive/Active | Application of chemicals to lower the freezing point of water. This method is noted to have environmental pollution risks. | [Habibi et al.](https://doi.org/10.1016/j.coldregions.2016.04.011)|

### 6. How forcasting help
This information is compiled from two primary research sources: **Martini et al. (2021)** [[Source Link](https://doi.org/10.3390/en14165207)] and **Ye & Ezzat (2024)** [[Source Link](https://doi.org/10.1016/j.renene.2024.120879)].

Forecasting is a critical tool for wind farm operations in cold climates, primarily helping to mitigate the significant economic and safety impacts of ice accretion on wind turbine blades. Based on these papers, forecasting provides essential support through two primary modes: **diagnostic** (detection) and **prognostic** (prediction).

### a,Production Loss Estimation and Management
Forecasting models help operators quantify the immediate and future impact of icing on energy output.

* **Quantifying Losses:** By reproducing ice growth on blades, numerical simulations provide detailed information on energy production losses and aerodynamic degradation caused by iced airfoil deformation.
* **Refining Accuracy:** Advanced machine learning (ML) frameworks, such as "TIGER," leverage historical sensor data to disentangle icing events from regular production noise, significantly reducing errors in power loss estimation compared to standard benchmarks.
* **Energy Planning:** Accurate short-term (day-ahead) forecasting is vital for balancing the electricity grid and minimizing the costs associated with grid imbalance.

### b, Operational Decision-Decision Making and Safety
Forecasting enables proactive rather than reactive maintenance and operation strategies.

* **Activating Protection Systems:** Alerts from forecasting systems assist operators in proactively initiating Icing Protection Technologies (IPTs), such as de-icing or anti-icing systems, before ice accumulation reaches critical levels.
* **Risk Mitigation:** Forecasting helps anticipate safety hazards like "ice throw," where large chunks of ice are dislodged from rotating blades, threatening nearby people, roads, and facilities.
* **Maintenance Scheduling:** By predicting when and where ice will form, operators can better schedule maintenance and ice removal services, reducing overall downtime.
