---
title: "Machine Learning-Enhanced Life Cycle Assessment of Offshore Wind Farms ♻️💻"
category: densys
excerpt: "Integrated LCA-ML framework achieving 12,600× computational acceleration for rapid environmental optimization of North Sea offshore wind turbines."
layout: single
author_profile: true
permalink: /projects/project4.md/
---

![Offshore Wind LCA Framework](/files/LCA_offshore_wind/LCA_picture.png)

**Academic Research Project — Politecnico di Torino**

This research was completed as part of the Resources and Environmental Sustainability course (04OULND), DENSYS Master's program, Academic Year 2025/26.

---

## Executive Summary

This study integrates Life Cycle Assessment (LCA) with Machine Learning to achieve **12,600× computational acceleration** for offshore wind environmental optimization (R²=98.5%, RMSE=18.5 kg CO₂-eq) [file:66]. Analysis of 333 design scenarios reveals that **European manufacturing achieves 52% lower GWP** (2.5 vs 3.8 g CO₂-eq/kWh) than Asian sourcing, while **Operation & Maintenance contributes 43% of lifecycle emissions** despite representing only 6-7 years of operational span [file:66]. Feature importance analysis identifies five parameters explaining 73.5% of environmental variance: turbine capacity (21.4%), capacity factor (18.7%), foundation mass (12.8%), manufacturing grid carbon intensity (11.2%), and operational lifetime (9.4%) [file:66].

Pareto frontier analysis identifies 47 non-dominated configurations, revealing that **environmental optimum (26.2 g CO₂-eq/kWh) requires 40% CAPEX premium** versus economic optimum, which incurs 47% GWP penalty [file:66]. **EU Taxonomy threshold (30 g) eliminates 68% of design space**, while carbon pricing (€80/tonne) narrows economic advantage from 30% to 22% [file:66]. Decarbonization modeling confirms **2050 climate targets are achievable** through coordinated grid decarbonization (35%), recycling infrastructure (15%), material innovation (10%), and autonomous maintenance (5%) [file:66].

---

## What We Did

- **Comprehensive LCA:** Evaluated 333 scenarios across turbine scales (8-15 MW), foundation types (monopile/jacket/floating), and global supply chains following ISO 14040/14044 standards [file:66]
- **Machine Learning:** Trained Random Forest, Gradient Boosting, XGBoost, and LightGBM achieving 98.5% prediction accuracy with SHAP explainable AI [file:66]
- **Multi-Objective Optimization:** Applied NSGA-II genetic algorithm identifying 47 Pareto-optimal designs balancing environmental, energy, and economic objectives [file:66]
- **Sensitivity Analysis:** Quantified ±48% GWP variation (21.4-47.8 g CO₂-eq/kWh) driven by capacity factor, foundation mass, and manufacturing location [file:66]
- **Policy Assessment:** Analyzed EU Taxonomy compliance and carbon pricing impacts on design selection [file:66]

---

## Key Findings

**Manufacturing location dominates:** European sourcing achieves 52% GWP reduction vs Asian supply chains  
**Site selection is critical:** Capacity factor (SI=-1.18) yields 23.6% GWP reduction for 20% improvement  
**Floating platforms outperform:** Concrete semi-submersible achieves 31.7% lower GWP than monopile  
**O&M requires attention:** 43% lifecycle contribution identifies autonomous systems as decarbonization lever  
**Climate targets feasible:** 61% total reduction achievable by 2050 through coordinated interventions  

---

## Documentation

- [Download Full Report (PDF)](/files/LCA_offshore_wind/LCA_report_2.pdf)
- [View Graphical Abstract](/files/LCA_offshore_wind/LCA_picture.png)

**Note:** Code and supplementary data will be released upon peer-reviewed publication.

---

## Technologies Used

- Python (Scikit-learn, XGBoost, SHAP, Pandas, Matplotlib)
- ISO 14040/14044 Life Cycle Assessment
- ReCiPe 2016 impact assessment method
- NSGA-II multi-objective optimization
- Machine Learning: Random Forest, ensemble methods

---

## Results Highlights

| Metric | 8 MW | 12 MW | 15 MW | Improvement |
|--------|------|-------|-------|-------------|
| GWP (kg CO₂-eq/GWh) | 38,200 | 32,400 | 28,100 | -26.4% |
| EPBT (months) | 6.21 | 5.18 | 4.76 | -23.3% |
| CPBT (years) | 1.07 | 0.86 | 0.77 | -28.0% |

**Foundation Comparison (12 MW):**
- Monopile: 33,800 kg CO₂-eq/GWh (baseline)
- Floating Concrete: 23,100 kg CO₂-eq/GWh (-31.7%)
- Jacket: 40,600 kg CO₂-eq/GWh (+20.1%)

---

*This work is under development for submission to peer-reviewed journals in renewable energy systems.*

---

