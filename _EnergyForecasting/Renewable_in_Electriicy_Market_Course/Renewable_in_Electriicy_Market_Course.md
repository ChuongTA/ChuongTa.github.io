---
title: "Self-Directed Learning: Renewables in Electricity Markets"
excerpt: "Study notes on market structures, pricing mechanisms, day-ahead clearing, intraday trading, balancing markets, and offering strategies."
layout: single
author_profile: true
permalink: /EnergyForecasting/Renewable_in_Electriicy_Market_Course/
usemathjax: true
date: 2026-08-12
categories:
  - "Electricity Market"
image: "/EnergyForecasting/Renewable_in_Electriicy_Market_Course/1_Intro/Introduction_graphical_abstract.png"
---
# Self-Directed Learning: Renewables in Electricity Markets

This page compiles my notes, study materials, and practical projects on electricity market design, clearing mechanisms, and deregulated operations. A primary resource for this study is the DTU course **Renewables in Electricity Markets (46755)** taught by [**Prof. Jalal Kazempour**](https://www.jalalkazempour.com/home) in the **Spring semester of 2025** at DTU (available via the [DTU Course Catalog](https://kurser.dtu.dk/course/46755) and the [YouTube Lecture Playlist](https://www.youtube.com/watch?v=QmdBpKUP4Ek&list=PLe7H9pun_r8bsWrLZ483DhVt8zvU4jv8P)).

<figure style="display: block; margin: 1.5em auto; text-align: center;">
  <img src="/EnergyForecasting/Renewable_in_Electriicy_Market_Course/1_Intro/Introduction_graphical_abstract.png" alt="Graphical Abstract - Electricity Market Structure" style="max-width: 100%; height: auto; border-radius: 8px; border: 1px solid var(--global-border-color);">
  <figcaption style="margin-top: 0.5em; font-size: 0.9em; color: var(--global-text-color-light);">Graphical abstract: Structural overview of electricity markets and clearing mechanisms.</figcaption>
</figure>

*Status: In Progress (Completed Lectures 0 to 3. Below links will direct to detailed notes and projects as they are completed).*

---

This course provides a comprehensive overview of electricity markets, covering both system-level and market participant perspectives. The curriculum includes:

## I. System and Market Perspective

### Lecture 0: Introduction of the Course *(Completed)*
- [Lecture Slides (PDF)](/EnergyForecasting/Renewable_in_Electriicy_Market_Course/1_Intro/46755%20%E2%80%93%20Renewables%20in%20Electricity%20Markets%20Lecture%200-compressed.pdf)
- [Study Notes (Markdown)](/EnergyForecasting/Renewable_in_Electriicy_Market_Course/1_Intro/Introduction%20of%20renewable%20in%20electricity%20market.md)
- 8 Objectives of learning the course
- Introduction of 2 assignments

### Lecture 1: Introduction to electricity markets *(Completed)*
- [Lecture Slides (PDF)](/EnergyForecasting/Renewable_in_Electriicy_Market_Course/Lecture1/46755%20%E2%80%93%20Renewables%20in%20Electricity%20Markets%20Lecture%201.pdf)
- [Study Notes (Markdown)](/EnergyForecasting/Renewable_in_Electriicy_Market_Course/Lecture1/Lecture%201%20_%20Introduction%20to%20electricity%20markets.md)
- [Study Notes (PDF)](/EnergyForecasting/Renewable_in_Electriicy_Market_Course/Lecture1/Lecture%201%20_%20Introduction%20to%20electricity%20markets.pdf)
- **Quick Summary:**
  - Learned about shifting from centralized TSO dispatch to decentralized power markets (modeled using Game Theory).
  - Covered uniform pricing (settling at the Market Clearing Price) vs. pay-as-bid schemes.
  - Explored what makes electricity markets unique (non-storability, inelastic demand, grid constraints).
  - Played a super fun 🎮 Kahoot quiz on calculating social welfare and supplier profits (still Notworking! 😜)

### Lecture 2: Fundamentals of Electricity Market *(Completed)*
- [Lecture Slides (PDF)](/EnergyForecasting/Renewable_in_Electriicy_Market_Course/Lecture2/46755%20%E2%80%93%20Renewables%20in%20Electricity%20Markets%20Lecture%202.pdf)
- [Study Notes (Markdown)](/EnergyForecasting/Renewable_in_Electriicy_Market_Course/Lecture2/Lecture%202%20-%20Fundamentals%20of%20Electricity%20Market.md)
- [Study Notes (PDF)](/EnergyForecasting/Renewable_in_Electriicy_Market_Course/Lecture2/Lecture%202%20-%20Fundamentals%20of%20Electricity%20Market.pdf)
- **Quick Summary:**
  - Classified power market actors (consumers, retailers, market operators, TSOs, DSOs, regulators, BRPs, and flexibility aggregators).
  - Explored energy market timelines (futures, day-ahead/spot, intraday, and balancing) and ancillary services (FCR, aFRR, mFRR).
  - Compared European (TSO/MO separation, zonal, sequential clearing) vs. U.S. markets (ISO, nodal, joint co-optimization).
  - Formulated market clearing mathematically as a linear optimization problem, using the Lagrangian function and KKT optimality conditions to verify market prices.

### Market Clearing: Optimization vs. Equilibrium *(To be updated)*

- Market clearing as an optimization problem
- Market clearing as a competitive equilibrium problem
- Definitions of Nash equilibrium and mixed complementarity problems

### Lecture 3: Day-Ahead Market *(Completed)*
- [Lecture Slides (PDF)](/EnergyForecasting/Renewable_in_Electriicy_Market_Course/lecture3/46755%20%E2%80%93%20Renewables%20in%20Electricity%20Markets%20Lecture%203.pdf)
- [Study Notes (Markdown)](/EnergyForecasting/Renewable_in_Electriicy_Market_Course/lecture3/Lecture%203_%20Day%20Ahead%20market.md)
- [Study Notes (PDF)](/EnergyForecasting/Renewable_in_Electriicy_Market_Course/lecture3/Lecture%203_%20Day%20Ahead%20market.pdf)
- **Quick Summary:**
  - Explored Single Day-Ahead Coupling (SDAC) in Europe using the EUPHEMIA hybrid market integration algorithm.
  - Analyzed network effects on clearing outcomes, price distribution, and congestion rent collection.
  - Formulated the mathematical differences between Nodal (LMP-based, e.g., US ISOs) and Zonal (European) market-clearing models.
  - Studied linear DC power-flow approximations used to maintain convex, globally solvable optimization problems.
  - Evaluated Flow-Based Market Coupling as a more grid-reflective alternative to traditional Net Transfer Capacity (NTC) zonal models.

### Intraday Markets *(To be updated)*

- Market structure and practical implementation (focus on European markets)
- Continuous intraday trading
- Auction-based intraday markets

### Balancing Markets *(To be updated)*

- Practical implementation (focus on European markets)
- Market-clearing problem formulated as an optimization problem
- One-price vs. two-price balancing settlements

### Ancillary Service Markets *(To be updated)*

- Overview of ancillary service markets (focus on European and Nordic markets: mFRR, aFRR, FCR)
- Market-clearing problem formulated as an optimization problem
- Ongoing European initiatives for balancing

### Impacts of Renewable Energy on Electricity Markets *(To be updated)*

---

## II. Market Participant Perspective

### Offering Strategy of a Price-Taker Wind Power Producer *(To be updated)*

- Price-taker vs. price-maker
- Offering strategy as a newsvendor problem
- Stochastic programming for decision-making under uncertainty
- Risk considerations
- Decision quality analysis: Ex-post out-of-sample validation and cross-validation

### Offering Strategy of a Flexibility Aggregator in Ancillary Service Markets *(To be updated)*

- Pre-qualification requirements for bidding in ancillary service markets
- Chance-constrained programming and solution techniques
- Chance-constrained optimization model for offering strategies
