---
title: "Icing formation in Wind turbines in Cold climate region (part 1)"
category: densys
excerpt: "In this first post of wind energy, I will walk you through the topic icing formation. In the cold climate regions, icing on wind turbines is significant problem, impacting both performance and physical reliability...
"
layout: single
author_profile: true
permalink: /WindEnergy/Icing_formation.md/
usemathjax: true
---

In the Nordic countries, the wind energy capacity is substantially higher in winter due stronger wind and higher air density. Therefore, countries with a high wind potential and intensive cold climates to advance wind power development. 

- Image 1
![Average wubd speed in the world in winter](
source: https://climate.copernicus.eu/esotc/2022/wind-solar-energy-resources


- Image 2: Minimum temperature in degree celcius in January in Europe
source: https://www.reddit.com/r/europe/comments/kob7to/countries_by_january_average_low_temperatures_of/

By 2050, wind energy capacity in cold climate regions throughout Scandinavia, North America, Europe and Asia is projected to reach approximately [250-400 GW] (estimated based on current growth trajectories from the 200+ GW installed by 2024). In spite of that, wind turbines in severely cold climates must withstand challenging conditions, particularly frequent subzero temperatures and ice formation.

Link: https://windren.se/WW2021/14_2_21_Karlsson_IEA_Wind_Task_19_Cold_climate_wind_market_study_Public.pdf

In addition to average air temperatures below zero Celcius degree for large part of the year, high humidity levels promote ice formation and accumation on wind-expose structures and wind farm access routes. Generally speaking, the term "icing" describes ice accumulation from atmospheric precipitation and marine spray. This accretion stationary and dynamic turbine parts by modifying aerodynamic profile performance and adding mass to contaminated components.

For offshore icing: "creepy icing" has been recognised as a problem for sea structures.
In the cold climates, offshore wind turbines are threaten by:
	• Sea sprays: Saltwater spray origininating from the sea surface.
	• Atmospheric icing: freshwater ice originating from atmosphere.
	• Sea ice: Floating ice blocks or ice parks that cause additional static and dynamic forces, and vibration on the wind turbine tower/foundation. 

## 1.Fundamental physics of ice accretion

The phenomenon is a multiphase interaction involving fluid dynamics, thermodynamics, and cloud microphysics.

### 1.1. Meteorological preconditions and microphysics

Liquid water content (LWC), median volumetric diameter (MVD), and Ambient temperature (T_a)

- Liquid water content (LWC) is defined as the mass of water contained in a unit volume of air (Kraj &Bibeau, 2010 - link: Phases of icing on wind turbine blades characterized by ice accumulation - ScienceDirect) usually expressed the unit of g/m3. It acts as the "fuel" for the accretion process. Higher LWC values effectively increase the flux of water mass impinging on the blade surface, leading to rapid ice buildup and a shorter duration required to reach critical power loss thresholds.
- Median Volumetric Diameter (MVD) is the droplet size that divides the total water volume in half. If the MVD is 200 micrometers, it means 50% of the water volume comes from droplets smaller than 200 μm, and 50% from droplets larger than 200 μm. This differs from simply counting droplets because larger droplets contain much more water than smaller ones. Larger droplets (high MVD) possess greater inertia, meaning they are less likely to follow the streamline deflection around the airfoil and more likely to impact the blade surface ballistically. Conversely, smaller droplets maybe swept around the leading edge by aerodynamic forces, reducing the collision efficiency. MVD is therefore a determinant of both rate of accretion and the limit of impingement - how far back along the chord the ice can form.
- Ambient temperature and phase change: The temperature describe the thermodynamic solidification process. It determines the "sticking fraction" (how much water adheres) and the freezing rate. This thermal balance is what differentiates the two primary ice types: rime and glaze.

### 1.2 Ice models
cientists have developed different mathematical models to predict how ice form. These models serve as the foundation for computer software that simulate ice buidup in various conditions.

Messinger Model (1953)
The Messinger model uses an energy balance approach, tracking all the heat flowing into and out of the icing surface.

Q_conv+Q_rad+Q_evap=Q_imp+Q_lat
For each heat transfer term, the detail explanation are shown below:
Heat losses:  
	• Convective heat transfer Q_conv= q_c (T_a−T_s )  : Cold air rushing over the wing removes heat, similar to how blowing on hot soup cools it. The heat transfer coefficient q_c  determines how efficiently this occurs.
	• Radiative cooling (Q_rad=−ϵσ(T_s^4−T_a^4): The surface radiates heat to the cold sky, following Stefan-Boltzmann law. This effect is usually small but becomes important at high altitudes.
	• Evaporative cooling (Q_evap=−m ̇_s L_s: Water molecules can evaporate or sublimate directly from ice, carrying away significant energy - about 2.83 MJ/kg
Heat in: 
	• Laten heat from freezing (Q_lat=m ̇_freeze L_f): When water freezes, it release energy-about 3.34 MJ/kg. On the wing surface, this released heat actually opposes further freezing.
	• Sensible heat from droplets (Q_imp=m_imp c_(p,w) (T_a−T_s):  incoming droplets carry thermal energy based on their temperature. If they're warmer than the surfcae, the deposit heat when they impact
	
Makknonen model equation

The Makkonen model directly calculates ice mass accumlation rate:
dM/dt=α_1 α_2 α_3 ωvA 
	- Collision efficiency (α_1): Not all droplets in the air actually hit the object—some flow around it. Small droplets follow air streamlines better and miss the object, while large droplets have more inertia and collide.
	- Collision efficiency (α_2): Some droplets that hit the surface bounce off or shatter instead of sticking. This depends on impact velocity and droplet size.
	- Accretion efficiency (α_3): Of the water that sticks, only a fraction actually freezes—the rest may run off as liquid. This is calculated from energy balance:
	α_3=(c_(p,w) (T_f−T_d )+L_f)/(L_f+L_s−c_(p,i) T_s )
	showing how droplet temperature and surface conditions determine freezing fraction
	- Mass flux (ωvA): This is simply the rate at which water would flow through the cross-sectional area if no object were there, liquid water content times velocity times are.

