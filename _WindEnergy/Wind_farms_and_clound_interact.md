---
title: "How offshore wind farms and clouds interact (Part 1)"
category: densys
excerpt: "Offshore wind farms become larger and wind turbines become higher and higher every year. And they stir up the air and change how low clounds form over the ocean."
layout: single
author_profile: true
permalink: /WindEnergy/Wind_farms_and_clound_interact.md/
usemathjax: true
---
Offshore wind farms are growing rapidly because winds over the ocean are strong, steady, and far from populated areas. Modern installations routinely contain hundreds of turbines spanning tens of kilometers, and some proposed developments will generate multiple gigawatts from single sites. At these scales, the farms begin to measurably modify the atmospheric environment in which they operate—particularly the marine boundary layer, which is the lowest one to two kilometers of atmosphere directly influenced by the sea surface [1](https://drawdown.org/explorer/deploy-offshore-wind-turbines#current-state). 


Over cool ocean regions, especially the eastern subtropical oceans, a particular type of low cloud called marine stratocumulus frequently forms. These aren't the towering cumulus clouds of summer afternoons; rather, they're extensive, sheet-like decks of gray or white cloud typically positioned below 1.5 km altitude. Despite looking rather unremarkable, these clouds matter enormously for climate. Their bright surfaces reflect 30–60% of incoming solar radiation back to space while emitting relatively weak thermal infrared radiation, producing a net cooling effect. Climate models consistently show that even modest reductions in marine stratocumulus coverage can produce measurable warming—which makes understanding potential anthropogenic perturbations to these clouds rather important [2](https://www.sciencedirect.com/topics/earth-and-planetary-sciences/stratocumulus-clouds).

This raises a natural question:
"When you put a very large wind farm under a deck of low clouds, do the turbines and the clouds start to affect each other in a systematic way?"

"or when large wind farm installations operate beneath stratocumulus decks, do the turbines alter the boundary layer structure in ways that promote or suppress cloud formation? And conversely, do changes in cloud properties feedback to affect the wind profiles experienced by turbines, thereby influencing power production?"

![Cloud interact](/files/Wind_farms_and_clouds_interact/hydro-meteo.jpg)
*Figure 1: Wind farms and clouds interact [[3]]([https://en.wikipedia.org/wiki/Glaze_%28ice%29](https://noordzeeloket.nl/en/functions-use/offshore-wind-energy/shipping-safety-around-offshore-wind-farms-moswoz/hydrometeo/))*

# 2. The Marine Boundary Layer

The marine boundary layer extends from the sea surface to somewhere between several hundred meters and about 1.5 km, depending on conditions. What defines this layer is direct coupling with the ocean surface through turbulent mixing - momentum exchange via surface friction, heat transfer, and moisture addition through evaporation all shape the properties within this zone [4](https://acp.copernicus.org/articles/21/10965/2021/).

![MBL](/files/Wind_farms_and_clouds_interact/MBL.jpg)
*Figure 2: Marine Boundary Layer [[5]](https://asr.science.energy.gov/news/program-news/post/13377))*

Several features characterize the marine boundary layers:
- Well-mixed by turbulence, with eddies continuosly stirring and homogenizing the air.
- The top is frequently capped by a temperature inversion - a thin layer where temperature increases rather than decreases with height. This inversion acts a a lid, suppresssing vertical mixing and effectively separating the boundary layer from the free troposhere above.
- Within the boundary layer itself, turbulent transport dominates over molecular diffusion for momentum, heat, and moisture.

The vertical wind profile in neutral conditions (neither strongly heated nor cooled) follows the well-known lograithmic law:

$$U(z) = \frac{u_s}{\kappa} \ln\left(\frac{z-d}{z_0}\right)$$

where $$U(z)$$ is mean horizontal wind speed at height $$z$$, $$u_*$$ is the friction velocity (characterizing surface stress), $$\kappa \approx 0.4$$ is von Kármán's constant, $$d$$ is displacement height (zero over flat ocean), and $$z_0$$ is aerodynamic roughness length, which depends on wave state [6](https://docs.nrel.gov/docs/fy20osti/78009.pdf).

Offshore wind turbines, with hub heights around 100–150 m, sit squarely within this layer. Crucially, the same turbulent processes that establish the wind profile also control the formation and evolution of clouds at the boundary layer top—which means the marine boundary layer is the shared physical domain where wind farms and stratocumulus can influence one another.

# 3. Marine Stratocumulus Clouds

## 3.1 Formation and climate role

Marine straocumulus are low-altitude, horizontally extensive clouds forming as relatively uniform dects or broken patches, typically gray or white when viewed from below and residing below 2 km altitude. They predominantly form near the top of the marine boundary layer, where rising moist air reaches saturation. The ocean surface continuously supplies moisture through evaporation; as this moist air is mixed upward by turbulence and encounters cooler temperatures near the inversion, water vapor condenses into cloud droplets [7](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2014JD022939).

![Stratocumulus clouds](/files/Wind_farms_and_clouds_interact/Stratocumulus_clounds.jpg)
*Figure 3: Vertical profiles of radiative infrared cooling flux (orange) and temperature change (green) for a nocturnal stratocumulus cloud layer at equatorial latitudes. Upward sensible heat and moisture fluxes from the ocean surface provide the buoyancy and water vapor required for cloud formation, and radiative cooling from the cloud top provides downward entrainment and mixing of dry air from aloft to feed cloud thickening [8](https://www.sciencedirect.com/science/article/pii/B9780128170922000023)*

These clouds cover roughly 20% of Earth's oceans at any given time, with particularly persistent decks forming over the eastern subtropical oceans where cold ocean currents meet stable air aloft. Their climate significance stems from their high albedo—they reflect substantial incoming solar radiation while emitting relatively weak thermal infrared, producing strong net cooling. Sensitivity studies consistently find that even modest reductions in marine stratocumulus coverage produce substantial positive radiative forcing [9](http://www.srderoode.nl/pubs/Wind_Energy_Clouds.pdf).

## 3.2 Maintenance mechanisms

Several competing physical processes determine whether stratocumulus clouds thicken, thin, or dissipate. Understanding these processes is essential for predicting how external perturbations—such as those from wind farms—might affect clouds.

Cloud-top radiative cooling: This is the dominant process maintaining many marine stratocumulus decks. Cloud droplets are efficient emitters of longwave (thermal infrared) radiation. At night, or even during daytime when longwave effects dominate, the cloud top emits radiation upward to space but receives little downward radiation from the dry air above. This creates a strong radiative cooling rate at the cloud top, often exceeding 5–10 K per hour.[10](https://acp.copernicus.org/articles/22/12241/2022/).

The cooled air at cloud top becomes denser than the air below. This density difference creates negative buoyancy—the cold air sinks. As it sinks, warmer air rises to replace it, creating convective overturning that generates turbulence throughout the cloud layer and often throughout the entire boundary layer depth. This radiatively driven turbulence is crucial for maintaining cloud layer properties and keeping it well-mixed.

*Entrainment*: While cloud-top cooling generates the turbulence that maintains clouds, that same turbulence can also contribute to cloud erosion through a process called entrainment. Turbulent motions at the boundary layer top can penetrate upward into the capping inversion, mixing parcels of warm, dry air from the free troposphere downward into the cloudy boundary layer.

When warm, dry air mixes into the cloud layer, two things happen. First, the warm air adds heat, which must be distributed throughout the layer. Second, and more importantly, the dry air is far from saturation, so when it mixes with cloudy air, cloud droplets evaporate to humidify the dry air. This evaporation removes cloud liquid water, thinning the cloud. If entrainment is strong enough relative to other moisture sources, it can erode and eventually eliminate the stratocumulus deck.

*Surface moisture supply*: The ocean surface provides the fundamental moisture source sustaining the boundary layer and its clouds. Evaporation rates depend on wind speed (stronger winds enhance evaporation), sea surface temperature, and the humidity of near-surface air (drier air allows more evaporation). This upward moisture flux partially counteracts the drying effect of entrainment from above.

*The critical balance*: Stratocumulus persistence results from a delicate balance between processes that promote cloud formation (moisture supply from below, cooling-driven mixing) and processes that erode clouds (entrainment of dry air from above). Small perturbations to any of these—particularly changes in turbulence intensity and spatial distribution—can tip the balance toward cloud thickening or dissipation.

# 4. Offshore wind farms and wake dynamics

## 4.1 Wake effect

Behind each operating turbine, the extraction of momentum produces a wake characterized by two primary features: reduced wind speed and enhanced turbulence. The velocity deficit (reduction in wind speed compared to ambient conditions) is strongest immediately behind the rotor and gradually recovers with distance downstream as momentum is mixed back into the wake by turbulence.

Near the turbine, the wake exhibits organized structures including helical tip vortices shed from blade tips (similar to wingtip vortices behind aircraft). These coherent structures gradually break down through turbulent cascade processes as they propagate downwind. Simultaneously, the wake expands radially as turbulent mixing transports momentum from surrounding faster-moving air into the slower wake region [11](https://www.windtech-international.com/articles/wind-farm-wake).

The recovery rate depends critically on atmospheric turbulence intensity. In highly turbulent conditions (unstable atmosphere, strong convection), vigorous mixing rapidly restores wake velocity, and wakes recover within 10–15 rotor diameters. In stable, low-turbulence conditions (common at night over cool oceans), mixing is weak and wakes can persist with measurable velocity deficits for 30–50 km downstream [12](https://businessnorway.com/articles/wake-effects-and-how-they-impact-wind-turbine-performance).

![Wake_effect](/files/Wind_farms_and_clouds_interact/wake_effect.png)
*Figure 4: Horns Rev wind farm in salt spray weather [13](https://www.mdpi.com/2077-1312/13/2/208)*

## 4.2 Wind farm array effects
In wind farms containing multiple turbine rows, wake interactions become complex. Downstream turbines operate within the wakes of upstream turbines, experiencing reduced wind speeds and altered turbulence. This leads to several important effects:

- Power losses: Downstream turbines produce less power due to lower inflow wind speeds. These wake losses typically reduce total farm output by 5–30% compared to what would be achieved if all turbines experienced undisturbed winds, with the magnitude depending on turbine spacing, wind direction relative to array layout, and atmospheric conditions [11](https://www.vectorenewables.com/en/blog/do-you-know-what-the-wake-effect-is-in-a-wind-farm)
- Cumulative wake effect: In large farms, many individual wakes merge and interact, creating a farm-scale modification to the boundary layer. The entire volume of air passing through and downwind of the farm experiences reduced mean wind speed and elevated turbulence compared to undisturbed conditions. This represents a substantial perturbation to the natural atmospheric state [12](https://docs.nrel.gov/docs/fy19osti/73183.pdf).
- Observational evidence: Satellite synthetic aperture radar (SAR) imagery provides striking visualization of these farm-scale effects. SAR sensors detect variations in sea surface roughness caused by wind speed variations. Images from operational offshore farms clearly show long streaks of reduced wind speed (smoother sea surface) extending tens of kilometers downwind, confirming that large farms create atmospheric perturbations far exceeding their physical footprint [13](https://www.sciencedirect.com/science/article/abs/pii/S0034425705002476)

# 5. How Wind Farms Affect Stratocumulus Clouds

## 5.1 Modifying Boundary Layer Turbulence

Understanding how wind farms might affect clouds requires connecting turbine wakes to cloud-relevant processes. The key link is turbulence. Wind turbines modify the turbulence field within the marine boundary layer in several specific ways:
- Momentum extraction at elevated heights: Unlike natural surface friction, which acts at the ocean surface, wind turbines extract momentum primarily at rotor height (100–150 m). This creates a momentum sink at mid-levels within the boundary layer, altering the vertical profile of wind speed and shear throughout the layer [14](https://pubs.aip.org/aip/pof/article/26/2/025101/259282/Large-eddy-simulation-of-offshore-wind-farm)
- Turbulence generation: While turbines extract mean kinetic energy for power production, they simultaneously inject turbulent kinetic energy (TKE) into the flow through multiple mechanisms: wake shear (strong velocity gradients at wake edges), breakdown of organized wake structures (tip vortices), and small-scale turbulence generated by blade passage. The magnitude of this TKE injection depends on turbine thrust coefficient, size, and operating condition [15](https://wes.copernicus.org/articles/10/1269/2025/).
- Altered spatial distribution: The turbine-generated turbulence is concentrated near rotor height and within wake regions, creating a different spatial distribution than natural boundary layer turbulence (which typically peaks near the surface from shear and at the boundary layer top from cloud-driven convection). This different vertical distribution of turbulence can affect vertical transport patterns for heat, moisture, and momentum.
- Enhanced vertical mixing: Increased turbulence generally enhances vertical mixing throughout the boundary layer. This can redistribute temperature, humidity, and momentum more efficiently, potentially modifying the boundary layer depth, the strength of the capping inversion, and the rate of entrainment at the boundary layer top [16](https://research-hub.nrel.gov/en/publications/micrometeorological-impacts-of-offshore-wind-farms-as-seen-in-obs/)

## 5.2 Potential Cloud Responses
Given these modifications to boundary layer turbulence, how might stratocumulus clouds respond? Current understanding, based primarily on idealized large eddy simulation studies, suggests that the response depends sensitively on background atmospheric conditions. Several distinct scenarios have been identified:

**Scenario 1: Cloud enhancement**

Under certain conditions, enhanced turbulent mixing from wind turbines could potentially support cloud formation. This scenario is most plausible when the capping inversion is relatively weak and the air above it is not extremely dry. In this case, the additional turbulence generated by turbines might enhance upward transport of moisture from the ocean surface toward the cloud layer, increasing moisture availability at the boundary layer top. If this enhanced moisture supply exceeds any increase in entrainment of dry air from above, the net effect could be increased cloud liquid water content, greater cloud thickness, or expanded cloud coverage [17](https://docs.nrel.gov/docs/fy19osti/73183.pdf).
​
This scenario might occur when the boundary layer is relatively shallow (allowing turbine-generated turbulence to extend throughout its depth) and when surface evaporation provides abundant moisture. It represents a situation where the turbines effectively "feed" the clouds by improving moisture delivery.

**Scenario 2: Cloud erosion**

Conversely, when a strong, dry temperature inversion caps the boundary layer, enhanced turbulence from wind turbines may primarily increase the entrainment rate of warm, dry air from the free troposphere above. In the delicate balance determining stratocumulus persistence, increasing entrainment while not proportionally increasing moisture supply shifts the system toward cloud erosion [18](https://graphsearch.epfl.ch/en/publication/264615).
​
Recent large eddy simulation studies under idealized conditions have demonstrated this effect clearly. Simulations of sufficiently large and dense wind farms beneath initially continuous stratocumulus decks show substantial reductions in cloud fraction (percentage of area covered by cloud), cloud liquid water path (vertically integrated water content), and cloud optical thickness. In extreme cases, large farms can nearly eliminate stratocumulus within and immediately downwind of the farm [19](https://ui.adsabs.harvard.edu/abs/2018AGUFM.A31J3006S/abstract).
​
The mechanism is straightforward: turbine-generated turbulence enhances mixing at the cloud top, pulling more warm, dry air downward from above the inversion. This dry air evaporates cloud droplets, reducing liquid water content. As the cloud thins, radiative cooling at the cloud top weakens (less cloud water means less efficient radiation), which reduces the cloud-driven turbulence that normally sustains the cloud. This positive feedback can lead to rapid cloud dissipation.

**Scenario 3: Minimal impact**

When wind farms are small relative to the natural spatial variability of the boundary layer, or when atmospheric turbulence is already very strong due to other processes (strong surface winds, active convection, synoptic disturbances), the additional perturbation from turbines may be negligible compared to natural fluctuations. In such cases, cloud properties might show no systematic response to wind farm presence [20](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2014JD022939).

## 5.3 Regime Dependence
The transition between these scenarios depends on multiple factors that together define different atmospheric regimes:
- Wind farm characteristics: Size (number of turbines, total area), turbine density (spacing), thrust coefficient (how much momentum each turbine extracts)
- Background wind speed: Higher winds generally increase mixing and alter the relative importance of turbine versus natural turbulence
- Boundary layer depth: Shallow boundary layers allow turbine effects to extend throughout; in deep boundary layers, turbine effects may not reach the cloud layer effectively
-Inversion strength: Strong inversions resist entrainment; weak inversions allow easier mixing between boundary layer and free troposphere
- Humidity structure: If the air above the inversion is only slightly drier than boundary layer air, entrainment effects are modest; if it's very dry, entrainment strongly erodes clouds
- Time of day: Affects radiative balance and natural turbulence levels

Comprehensively mapping this multi-dimensional parameter space to determine where each regime occurs requires extensive simulation campaigns—this is a primary objective of ongoing research.

# 6. How Clouds Affect Wind Farm Performance

The interaction between wind farms and stratocumulus is not unidirectional. Cloud presence and properties also substantially affect the atmospheric environment experienced by wind turbines, creating a feedback loop.

## 6.1 Cloud-Driven Turbulence and Stability

Stratocumulus clouds exert strong control over marine boundary layer structure through their radiative properties, which vary dramatically between day and night:

**Nighttime conditions**: At night, without solar radiation, cloud tops undergo intense longwave radiative cooling to space, with cooling rates frequently exceeding 5–10 K per hour. This creates a very cold, dense layer of air at the cloud top. The cold air sinks vigorously (it's negatively buoyant), while warmer air from below rises to replace it, establishing strong convective overturning throughout the cloud layer and often throughout the entire boundary layer depth. [21](https://acp.copernicus.org/articles/22/12241/2022/)
​
This radiatively driven turbulence creates a well-mixed boundary layer with relatively uniform potential temperature, high turbulence intensity, and efficient vertical transport of momentum. High-momentum air from above the boundary layer (or from upper portions of the boundary layer) is efficiently mixed downward toward turbine rotor heights. Similarly, the strong turbulence breaks down turbine wakes more rapidly, allowing faster wake recovery.

**Daytime conditions**: During daytime, solar radiation absorption by cloud droplets and by the ocean surface partially or fully compensates for longwave cooling at the cloud top. The net radiative cooling weakens substantially, reducing the buoyancy forcing for convection. Additionally, if the subcloud layer becomes slightly warmer than the cloud layer (due to solar heating from below or through the cloud), the boundary layer can become "decoupled"—the cloud layer maintains its own dynamics driven by weakened cloud-top cooling, while the subcloud layer becomes more stable with suppressed turbulent mixing [22](https://www.sciencedirect.com/topics/earth-and-planetary-sciences/stratocumulus-clouds).
​
In decoupled conditions, vertical transport of momentum is much less efficient. High-momentum air from aloft has difficulty reaching down to turbine heights. Turbine wakes recover more slowly due to weaker mixing.

## 6.2 Implications for Wind Profiles and Power Output
These cloud-driven changes in turbulence and stability translate directly into modifications of the vertical wind profile:

Well-mixed boundary layer (strong cloud cooling, typically nighttime): Wind speed varies relatively little with height throughout the boundary layer. Momentum from above is efficiently transported downward, maintaining strong winds at turbine hub heights.

Stable or decoupled boundary layer (weak cloud cooling or no clouds, often daytime): Stronger vertical wind shear develops. Peak wind speeds may occur above turbine heights, with weaker winds at hub height. Momentum from aloft is not efficiently mixed downward.

These profile changes affect multiple aspects of wind farm performance:

Direct wind speed effect: Changes in wind speed at hub height directly alter power production according to the cubic relationship P ∝ U^3. A 10% increase in hub-height wind speed yields approximately 33% more power.

Wake recovery effect: In conditions of strong turbulence (cloud-driven mixing), wakes recover faster. Downstream turbines experience less severe velocity deficits, producing more power. Large eddy simulations quantitatively demonstrate this: under strong cloud-top cooling, wake velocity deficits recover 20–40% faster than under cloudless conditions, leading to increases in downstream turbine power output of 10–20% [23](https://pubs.aip.org/aip/pof/article/26/2/025101/259282/Large-eddy-simulation-of-offshore-wind-farm).
​
Net farm performance: Observational studies and simulations indicate that marine stratocumulus presence can increase nighttime wind farm power output by 10–20% compared to cloudless conditions, due to both enhanced hub-height wind speeds and faster wake recovery. During daytime, when cloud-driven mixing weakens, these benefits diminish or reverse [24](https://www.osti.gov/pages/biblio/1492504).
​
## 6.3 The Feedback Loop

Combining the effects described in Sections 5 and 6 reveals the coupled nature of the system:
- Wind turbines extract momentum and generate turbulence in the marine boundary layer
- This modified turbulence affects cloud formation and maintenance (either promoting or suppressing clouds depending on conditions)
- Changes in cloud properties alter boundary layer stability and turbulence intensity
- These turbulence and stability changes modify vertical wind profiles
- Modified wind profiles change the wind speeds experienced by turbines
- This affects turbine power output and wake characteristics, closing the loop

This is not a one-way street where turbines affect clouds or clouds affect turbines—it's a bidirectional coupling where each influences the other continuously. Understanding and potentially exploiting or managing this coupling is a central goal of current research.

# 7. Large Eddy Simulation: The Primary Research Tool

# 7.1 The Simulation Challenge

Studying the coupled wind farm-cloud-boundary layer system presents significant methodological challenges due to the range of relevant scales and the complexity of interacting physical processes:

**Spatial scales**: The system involves processes from turbulent eddies of meters (blade-scale turbulence, small cloud eddies) to tens of kilometers (wind farm extent, large-scale cloud organization).

**Temporal scales**: Relevant timescales range from seconds (turbulent eddy turnover, blade rotation) to hours (cloud evolution, diurnal cycles of radiation).

**Physical processes**: Multiple coupled processes interact: fluid dynamics (three-dimensional turbulent flow), turbulent transport (momentum, heat, moisture), radiative transfer (longwave and shortwave), thermodynamics (saturation, condensation, evaporation), and turbine aerodynamics (thrust, power extraction).

This complexity means simple analytical solutions or reduced models are insufficient without first establishing fundamental understanding through detailed simulation.

Why not direct numerical simulation (DNS)? DNS resolves all scales of turbulence down to the smallest dissipative eddies (Kolmogorov scale, typically millimeters in the atmosphere). For atmospheric boundary layer flows, this would require grid spacings of millimeters and domains extending kilometers—resulting in grid sizes of trillions to quadrillions of points. Even with modern supercomputers, DNS remains computationally prohibitive for this application.

Why not traditional weather models? Numerical weather prediction models typically operate at horizontal grid spacings of 1–10 km. While appropriate for forecasting large-scale weather patterns, these models cannot resolve individual turbine wakes (which are ~100 m wide) or the fine-scale structure of boundary layer turbulence and stratocumulus clouds. These models must parameterize both turbulence and wind farm effects using simplified representations that may not accurately capture the complex interactions of interest.

## 7.2 7.2 Large Eddy Simulation as the Optimal Compromise

Large eddy simulation (LES) provides the optimal balance between physical fidelity and computational cost for this problem. The LES approach is based on a key observation: in turbulent flows, most of the kinetic energy resides in the large-scale eddies, while small-scale eddies are relatively universal and can be adequately represented by simple models.

LES explicitly resolves (calculates directly) the large, energy-containing turbulent eddies while modeling only the effects of smaller subgrid-scale turbulence. For atmospheric boundary layer applications, this allows grid spacings of 5–50 meters—fine enough to capture major turbulent structures, individual turbine wakes, detailed cloud features, and key transport processes, yet coarse enough to make simulations of domains spanning tens of kilometers feasible with modern high-performance computing resources.

## 7.3 LES Governing Equations
LES applies spatial filtering to the Navier-Stokes equations, decomposing each flow variable into a resolved (grid-scale) component and an unresolved subgrid component. For atmospheric boundary layer flows, the filtered momentum equation under the Boussinesq approximation (valid when density variations are small) takes the form:
Here's a complete .md file with the equations using $$ notation:
​

text
# Large Eddy Simulation: Momentum and Transport Equations

## Momentum Equation

$$\frac{\partial \tilde{u}_i}{\partial t} + \tilde{u}_j \frac{\partial \tilde{u}_i}{\partial x_j} = -\frac{1}{\rho_0} \frac{\partial \tilde{p}}{\partial x_i} + g \frac{\tilde{\theta}'}{\theta_0} \delta_{i3} - \frac{\partial \tau_{ij}^{\text{SGS}}}{\partial x_j} + F^{\text{turbine}} + F^{\text{other}}$$

The tilde notation $$(\tilde{\ })$$ indicates spatially filtered (resolved) quantities. The terms represent:

- **Left side:** Time evolution of resolved velocity $$\tilde{u}_i$$ plus advection by resolved flow
- **First right-hand term:** Pressure gradient force
- **Second term:** Buoyancy force (proportional to potential temperature perturbation $$\tilde{\theta}'$$; acts only in the vertical direction $$i = 3$$)
- **Third term:** Divergence of subgrid-scale (SGS) stress tensor $$\tau_{ij}^{\text{SGS}}$$
- **Fourth term:** Body forces from wind turbines
- **Fifth term:** Other forces (Coriolis, large-scale pressure gradient, etc.)

The subgrid-scale stress tensor $$\tau_{ij}^{\text{SGS}}$$ represents the effect of unresolved small-scale turbulence on the resolved scales. Since the filtered equations don't contain information about subgrid motions, this term requires modeling. Standard approaches use eddy viscosity models, most commonly the Smagorinsky model or more sophisticated dynamic models that adapt to local flow conditions.

## Temperature and Moisture Equations

Similar transport equations govern potential temperature and water vapor mixing ratio:

$$\frac{\partial \tilde{\theta}}{\partial t} + \tilde{u}_j \frac{\partial \tilde{\theta}}{\partial x_j} = -\frac{\partial q_{\theta}^{\text{SGS}}}{\partial x_j} + Q_{\theta}^{\text{rad}} + Q_{\theta}^{\text{surf}} + Q_{\theta}^{\text{phase}}$$

where $$q_{\theta}^{\text{SGS}}$$ is subgrid heat flux, $$Q_{\theta}^{\text{rad}}$$ accounts for radiative heating/cooling (critically important at cloud tops where strong longwave cooling occurs), $$Q_{\theta}^{\text{surf}}$$ represents surface heat flux, and $$Q_{\theta}^{\text{phase}}$$ accounts for latent heat release/absorption from condensation/evaporation.

Cloud microphysics: LES for stratocumulus typically employs simplified bulk microphysical schemes. The simplest approach assumes instantaneous adjustment to saturation: if a grid cell's water vapor exceeds saturation mixing ratio, the excess immediately condenses to liquid cloud water; if cloud water exists in a subsaturated cell, it immediately evaporates. More sophisticated schemes include prognostic equations for cloud droplet number concentration, but simplified approaches often suffice for studying stratocumulus dynamics and radiative effects.

Radiative transfer: Accurately representing longwave radiative cooling at cloud tops is essential for realistic stratocumulus simulation. LES codes incorporate radiative transfer schemes that compute heating/cooling rates based on the vertical distribution of temperature, water vapor, and cloud liquid water. These schemes capture the key physics—efficient upward emission by cloud droplets, weak downward emission from dry air above—while remaining computationally tractable for high-resolution simulations.

## 7.4 Typical LES Configuration
A representative LES setup for studying offshore wind farm interaction with marine stratocumulus includes:

**Domain configuration**:

- Horizontal extent: 30–50 km in the streamwise (along-wind) direction, 10–20 km in the spanwise (cross-wind) direction
- Vertical extent: 2–3 km, sufficient to fully contain the boundary layer and lower portion of free troposphere
- Boundary conditions: Periodic or cyclic conditions in horizontal directions can represent an infinite farm or a farm embedded within a larger flow field; alternatively, open or radiation boundary conditions provide more realistic representation of finite farms with well-defined inflow and outflow regions
​
**Grid resolution**:
- Horizontal grid spacing: 5–15 m provides adequate resolution of large turbulent eddies and individual turbine wakes while remaining computationally tractable
- Vertical grid spacing: Typically varies with height, with finest resolution (2–5 m) in the boundary layer where vertical gradients and shear are strongest, gradually stretching to coarser spacing (20–50 m) in the free troposphere where resolution requirements are lower
- Total grid sizes: Tens of millions to billions of computational cells depending on domain size and resolution choices
​

**Wind farm specification**:
- Number of turbines: Typically 50–200 turbines arranged in regular arrays
- Turbine spacing: Commonly 5–9 rotor diameters between turbines (both streamwise and spanwise spacing)
- Turbine characteristics: Modern offshore turbines have rotor diameters of 150–240 m and hub heights of 100–150 m
- Operating conditions: Thrust and power coefficients specified based on manufacturer data or representative values for the wind speed regime being simulated
​
**Initial and boundary conditions**:
- Atmospheric state: Initial profiles of wind, potential temperature, and humidity representative of marine boundary layer conditions, including a stratocumulus cloud layer near the boundary layer top and a capping temperature inversion
- Large-scale forcing: Specified geostrophic wind (provides mean flow), large-scale subsidence (representing synoptic-scale descent common in stratocumulus regions), and time-varying solar and longwave radiation appropriate for the latitude and time of year
​

**Simulation duration**:
- Simulations typically run for 24–48 hours of physical time to allow the system to reach quasi-equilibrium and to capture complete diurnal cycles
- The first several hours constitute a spin-up period during which the initial conditions adjust to the turbine forcing and prescribed boundary conditions
- Statistical analysis uses data from the quasi-equilibrium period after spin-u
