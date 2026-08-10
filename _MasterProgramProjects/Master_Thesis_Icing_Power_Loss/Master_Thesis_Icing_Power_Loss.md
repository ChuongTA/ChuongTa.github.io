---
title: "Master Thesis: Icing Power Loss Forecasting for Wind Farms in Cold Climates Using Machine Learning"
category: densys
excerpt: "MSc thesis at rebase.energy (Stockholm): forecasting wind turbine icing power losses at 1-36 hour lead times using SCADA and ERA5-Land data, an extended IEA Wind Task 19 framework, and a two-stage LightGBM classifier-regressor."
layout: single
author_profile: true
permalink: /MasterProgramProjects/Master_Thesis_Icing_Power_Loss/
date: 2026-07-29
image: "/MasterProgramProjects/Master_Thesis_Icing_Power_Loss/Graphical_Abstract.png"
---

**Master Thesis, DENSYS Erasmus Mundus Joint Master Degree**
Presented to the DENSYS committee in Barcelona, July 2026.

Carried out at [rebase.energy](https://www.rebase.energy/), Stockholm, Sweden, under industrial supervision from Sebastian Haglund (CEO & Co-Founder) and Ilias Dimoulkas (Data Scientist), and academic supervision from Dr. Giuseppe Giorgi at Politecnico di Torino.

## Abstract

Atmospheric turbine icing in cold climates causes aerodynamic degradation, structural standstills, energy losses, and operational uncertainty. This thesis forecasts wind power icing loss at 1- to 36-hour lead times using multi-year Swedish turbine SCADA and ERA5-Land data. Icing labels are established using an extended IEA Wind Task 19 Sigmoid Performance Ratio framework. Data investigation reveals inter-annual non-stationarity and wind speed–temperature overlap between icing and non-icing events. Biases between SCADA and ERA5-Land inputs are corrected using Quantile Mapping and LightGBM. From numerous candidate features across multiple physical groups, Spearman and SHAP screening remove unstable predictors. A two-stage LightGBM classifier-regressor is trained using walk-forward cross-validation over multiple winters.

Evaluation on a blind winter test set spans several scenarios: Persistence, Oracle, Realistic NWP, and SCADA-only. Persistence yields high short-term accuracy but collapses rapidly as lead time increases. Oracle (using weather observations) defines the performance ceiling. Realistic NWP tracks the Oracle classifier but suffers a regression penalty from forecast errors. SCADA-only (no weather forecasts) collapses beyond the near term. Thus, local SCADA signals dominate near-term forecasts, but meteorological forecasts are essential for longer horizons.

## What I Did

- **Icing Detection & Feature Engineering:** Established icing labels on multi-year Swedish turbine SCADA data using an extended IEA Wind Task 19 Sigmoid Performance Ratio framework. Diagnosed inter-annual non-stationarity and wind speed-temperature overlap between icing and non-icing regimes, and corrected SCADA-ERA5-Land biases via Quantile Mapping and LightGBM. Applied Spearman correlation and SHAP screening across multiple physical feature groups to remove unstable predictors.
- **Icing Power-Loss Forecasting:** Built a two-stage LightGBM classifier-regressor, trained with walk-forward cross-validation over multiple winters, to forecast wind power icing losses at 1-36 hour lead times.
- **Scenario Benchmarking:** Compared Persistence, Oracle, Realistic NWP, and SCADA-only scenarios on a blind winter test set, showing local SCADA signals dominate near-term skill while NWP forecasts are essential for longer horizons — a key trade-off for operational resilience under changing conditions.

## Documentation

- [Download partial thesis (PDF)](/MasterProgramProjects/Master_Thesis_Icing_Power_Loss/Partial_Ms_thesis_compressed.pdf)
- [LinkedIn announcement post](https://www.linkedin.com/posts/chuongta_icingabrpowerabrloss-machineabrlearning-densys-ugcPost-7478380902612525057-Be_d/)

## Next Steps

This thesis is planned to be developed into a publication — stay tuned.

## Acknowledgements

Thank you to my two industrial supervisors at rebase.energy, Sebastian Haglund (CEO & Co-Founder) and Ilias Dimoulkas (Data Scientist), for their invaluable guidance and continuous feedback, and to all my colleagues at rebase.energy for a great working environment and everything I learned along the way.

I am also grateful to my academic supervisor, Dr. Giuseppe Giorgi at Politecnico di Torino, for his comments and support throughout my thesis.

To the DENSYS consortium — Fabrice Lemoine, Heathcliff Demaie, Marta Gandiglio, Samira Daghmous Menouar — and all the friends I've met through two years together, thank you.
