---
title: "Electricity Markets: Fundamentals"
excerpt: "Introduction to electricity market design, demand/supply curves, marginal utility, equilibrium pricing, and social surplus."
layout: single
author_profile: true
permalink: /EnergyForecasting/Structure_of_Electricity_Market/Electricity_Market_Part1_Fundamentals/
usemathjax: true
date: 2026-08-12
categories:
  - "Electricity Market"
image: "/EnergyForecasting/Structure_of_Electricity_Market/Electricity_market_part1/Images/Fig1.png"
---

This post is the first in a series on the fundamentals of electricity markets in Europe. The contents are synthesized from two main lecture courses at [Politecnico di Torino (PoliTo)](https://www.polito.it/) and the [KTH Royal Institute of Technology](https://www.kth.se/). Specific source documents are hyperlinked in the [Sources](#sources) section below.

*   **Part 1 (This post) covers:** Fundamental economic and physical concepts, including power system layers, average vs. marginal costs, demand and supply curves, equilibrium clearing, social surplus, strategic bidding, electricity's unique properties as a commodity, and market liberalization levels.
*   **Part 2 (Next post) will cover:**
    *   Electricity market structures: pool model vs. bilateral model
    *   Day-Ahead Markets
    *   Intraday Markets
    *   Balancing Markets 
    *   Ancillary Service Markets
    *   Impact of Renewable Energy on Electricity Markets

# Electricity Markets

An electricity market is a system that enables the transfer of electric energy from producers to consumers, relying on a dedicated infrastructure - the power system.

![Power system](/EnergyForecasting/Structure_of_Electricity_Market/Electricity_market_part1/Images/Fig1.png)

*Fig 1: Power system*

A **power system** is the physical network that generates electrical energy, transmits it over long distances, distributes it locally, and delivers it to consumers while maintaining stability, reliability, and quality. It includes:
- **Generation**: power plants (thermal, hydro, wind, solar, etc.) that produce electricity.
- **Transmission**: high‑voltage lines (HV, EHV) that move bulk power across long distances.
- **Distribution**: medium‑ and low‑voltage networks (MV, LV) that deliver electricity to cities, neighborhoods, and buildings.
- **Utilization**: all end‑user equipment that consumes electricity (homes, industries, commercial loads).


## Recall Math - Average vs Marginal

<div style="display: flex; gap: 20px; align-items: center; flex-wrap: wrap; margin: 1em auto;">
  <div style="flex: 1; min-width: 250px;">
    The function $f(x)$ gives the value of a quantity $y$ as a function of the variable $x$. For a specific point $x_1$ with corresponding value $y_1=f(x_1)$, we define:
    $$A(x_1) = \frac{f(x_1)}{x_1}$$
    This represents the slope of the line connecting the origin to $(x_1, y_1)$.
    For a small increase of the variable $x$, from $x_1$ to $x_1+\Delta x$, the quantity $y$ increases from $y_1$ to $y_1+\Delta y$. In the limit, the marginal value is defined as:
    $$M(x_1) = \lim_{\Delta x \to 0} \frac{\Delta y}{\Delta x} = f'(x_1)$$
    This represents the slope of the function $f(x)$ at $x=x_1$.
  </div>
  <div style="text-align: center; flex-shrink: 0;">
    <img src="/EnergyForecasting/Structure_of_Electricity_Market/Electricity_market_part1/Images/Fig2.png" alt="Average vs Marginal" style="width: 300px; height: auto;">
  </div>
</div>

## Scarcity & Marginal Utility

| Concept | Scarcity | Law of Diminishing Marginal Utility |
|--------|----------|--------------------------------------|
| **Definition** | Resources are limited relative to demand. | Each additional unit consumed gives less added satisfaction (utility). |
| **Core Idea** | Not enough supply to satisfy all wants. | Utility gained from consuming extra units decreases. |
| **Cause** | Physical, economic, or technical limits (e.g., limited generation capacity). | Human behavior: satisfaction decreases as consumption increases. |
| **Effect on Prices** | Scarcity increases prices because demand > supply. | Consumers are willing to pay less for each additional unit. |
| **Role in Markets** | Drives competition and allocation of limited electricity. | Shapes demand curve and bidding behavior. |
| **Example** | Peak hours: limited generation → high prices. | First kWh is very valuable; the 100th kWh adds little extra benefit. |


## Demand curves

• Utility always increases with the consumed quantity, but the **utility of the last consumed unit** decreases (marginal utility decreases). 
• The utility is reflected by the **price** the consumer is willing to pay. 
• Therefore, the **demand curve** represents the **marginal utility** of the good. 
• The demand curve $d(p)$ is a **decreasing function**, expressing the price buyers are willing to pay as a function of the quantity demanded:
$$\nu = d(p)$$
• The **inverse demand curve** expresses the quantity buyers demand as a function of the price:
$$p = g(\nu)$$

<div style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin: 1em auto;">
  <img src="/EnergyForecasting/Structure_of_Electricity_Market/Electricity_market_part1/Images/Fig3.png" alt="Demand Curve 1" style="max-width: 317px; height: auto;">
  <img src="/EnergyForecasting/Structure_of_Electricity_Market/Electricity_market_part1/Images/Fig4.png" alt="Demand Curve 2" style="max-width: 368px; height: auto;">
</div>

*Fig 3 and 4: Demand curves*

## Costs

• **Fixed cost** $c_F$: cost that does not depend on the production quantity (land, machines, taxes…).
• **Variable cost** $c_V(p)$: cost that depends on the production quantity (labor, fuel, electricity…).
• **Total cost** $c(p)$: sum of fixed and variable costs:
$$c(p) = c_F + c_V(p)$$

• **Average cost**: cost per unit at production level $p$:
$$\bar{c}(p) = \frac{c(p)}{p}$$

• **Average variable cost**:
$$\bar{c}_v(p) = \frac{c_V(p)}{p}$$

• **Marginal cost** $c_m(p)$: derivative of the total cost with respect to quantity:
$$c_m(p) = \frac{dc(p)}{dp}$$

## Law of diminishing marginal returns and supply curve

<div style="display: flex; gap: 20px; align-items: center; flex-wrap: wrap; margin: 1em auto;">
  <div style="flex: 1; min-width: 250px;">
    An increase in variable inputs relative to fixed inputs raises total output, but after a certain point the extra output from the same input increase becomes smaller.
    <br><br>
    • As production grows, producers must use increasingly costly resources.<br>
    • Since marginal cost rises with output, the supply curve is upward‑sloping.
  </div>
  <div style="text-align: center; flex-shrink: 0;">
    <img src="/EnergyForecasting/Structure_of_Electricity_Market/Electricity_market_part1/Images/Fig5.png" alt="Diminishing marginal returns" style="width: 320px; height: auto;">
    <br>
    <small style="color: var(--global-text-color-light);"><em>Fig 5: Diminishing marginal returns</em></small>
  </div>
</div>

## Cost, Price, and Profit

• **Cost**: the total economic expenditure a firm must undertake to produce a given quantity of a good. It includes all resources used in production. 
• **Price**: the monetary value assigned to one unit of the good in the market; it reflects consumers’ willingness to pay and producers’ willingness to sell. 
• **Profit**: the financial gain obtained by a firm, equal to the difference between the revenue from selling the good and the total cost of producing it. A rational firm aims to maximize profit.

## Equilibrium and Market Clearing Price

<div style="display: flex; gap: 20px; align-items: center; flex-wrap: wrap; margin: 1em auto;">
  <div style="flex: 1; min-width: 250px;">
    • **Equilibrium**: the condition in which the quantity offered by sellers equals the quantity demanded by buyers at a specific price. 
    <br><br>
    - When price is higher than $\lambda$ ($v_2$), more quantity is produced but less quantity is demanded, prompting producers to decrease the price.<br>
    - When price is lower than $\lambda$ ($v_1$), more quantity is demanded but less quantity is produced, prompting buyers to increase their bids, raising the price.<br><br>
    • **Market Clearing Price (MCP)**: the unique price at which supply and demand are exactly equal, ensuring that all offered quantity is sold and all demanded quantity (Market Clearing Quantity (MCQ)) is purchased.
  </div>
  <div style="text-align: center; flex-shrink: 0;">
    <img src="/EnergyForecasting/Structure_of_Electricity_Market/Electricity_market_part1/Images/Fig6.png" alt="Equilibrium and Market Clearing Price" style="width: 320px; height: auto;">
    <br>
    <small style="color: var(--global-text-color-light);"><em>Fig 6: Equilibrium and Market Clearing Price</em></small>
  </div>
</div>

## Consumer Surplus, Producer Surplus, and Social Surplus

| Concept | Definition |
|--------|------------|
| **Consumer Surplus** | The economic benefit consumers receive when they pay a market price lower than the maximum they were willing to pay. |
| **Producer Surplus** | The economic benefit producers receive when the market price is higher than the minimum price at which they were willing to supply the good. |
| **Social Surplus** | The total economic benefit created in the market, equal to the sum of consumer surplus and producer surplus. |

![Consumer Surplus, Producer Surplus, and Social Surplus](/EnergyForecasting/Structure_of_Electricity_Market/Electricity_market_part1/Images/Fig7.png)

*Fig 7: Consumer Surplus, Producer Surplus, and Social Surplus*

## Strategic Bidding Behavior of Producers

In a perfectly competitive market, producers offer electricity at their true marginal cost. This keeps the market‑clearing price low and ensures the market operates efficiently, maximizing social surplus. Consumers pay a fair price, producers earn normal profit, and the market clears at the socially optimal point where supply equals demand. **In the diagram**, this is shown on the left side: the demand curve intersects the marginal cost curve at the competitive equilibrium. The blue area represents consumer surplus, the orange area represents producer surplus, and together they form the total social surplus, which is maximized.

In a market where producers have market power, they can bid strategically by offering electricity at a higher price than their real cost. This pushes the market‑clearing price upward, increasing producer surplus but reducing consumer surplus and overall social welfare. For example, if a generator’s true marginal cost is €40/MWh but it submits an offer at €60/MWh, the market price may rise to €60/MWh instead of €40/MWh. Producers earn more, consumers pay more, and the market clears at a less efficient point that benefits producers at the expense of society. 

**In the diagram**, this appears on the right side: the strategic offer curve lies above the marginal cost curve, leading to a higher price and lower quantity. The red triangle shows the deadweight loss - the lost social welfare caused by strategic bidding.

![Demand diagram showing strategic bidding behavior of producers](/EnergyForecasting/Structure_of_Electricity_Market/Electricity_market_part1/Images/Fig8.png)

*Fig 8: Demand diagram showing strategic bidding behavior of producers*


## Electricity as a commodity

Electricity is fungible, like gold, oil, or copper - one unit is interchangeable with another, and price is the only thing that tells two offers apart. But unlike those commodities, there are several factors making electricity different:
- **No large-scale storage:** Production has to equal consumption instantly, everywhere on the grid. Hydro reservoirs are about the only large-scale option, and even they lose energy round-trip (~74% efficiency). France, for example, has ~250 GW of subscribed consumption capacity vs only ~128 GW installed.
- **Delivery quality matters:** Power has to stay within tight bounds on frequency, voltage, and harmonics; reactive power is needed to deliver real power even though it does no useful work itself.
- **Flows ≠ contracts:** Where electricity actually goes is decided by the grid's physics, not by who bought it from whom (e.g., Kirchhoff's Laws).
- **Consequence:** An unresolved imbalance shows up as a frequency deviation, and left uncorrected, cascades into a blackout.
- **TSO reserves** exist to cover exactly this: primary (<20s, automatic), secondary (<3min), tertiary (<15min, manual).


## From monopoly to competition: liberalization levels

- **Level 0**: Monopoly, fully bundled, regulated
- **Level 1**: Purchasing agency, competition only in generation
- **Level 2**: Wholesale competition, retailers/large customers choose supplier
- **Level 3**: Retail competition, everyone chooses supplier

<div style="display: flex; flex-direction: column; gap: 15px; align-items: center; margin: 1.5em auto;">
  <img src="/EnergyForecasting/Structure_of_Electricity_Market/Electricity_market_part1/Images/Fig9.png" alt="liberalization ladder Level 0" style="max-width: 100%; height: auto;">
  <img src="/EnergyForecasting/Structure_of_Electricity_Market/Electricity_market_part1/Images/Fig10.png" alt="liberalization ladder Level 1" style="max-width: 100%; height: auto;">
  <img src="/EnergyForecasting/Structure_of_Electricity_Market/Electricity_market_part1/Images/Fig11.png" alt="liberalization ladder Level 2" style="max-width: 100%; height: auto;">
  <img src="/EnergyForecasting/Structure_of_Electricity_Market/Electricity_market_part1/Images/Fig12.png" alt="liberalization ladder Level 3" style="max-width: 100%; height: auto;">
</div>

*Fig 9 to 12: liberalization ladder 0–3*


## From regulation to liberalization

Electricity systems moved from one regulated monopoly controlling generation, transmission, distribution, and retail to a liberalized structure where generation and retail are opened to competition, while transmission and distribution remain regulated natural monopolies.

![From regulation to liberalization](/EnergyForecasting/Structure_of_Electricity_Market/Electricity_market_part1/Images/Fig13.png)

*Fig 13: From regulation to liberalization*


## Functions in Electricity Market
- **Producers**: Generate electricity and submit offers to the market. They decide how much to produce and at what price, aiming to maximize profit.
- **Consumers**: Use electricity and submit bids that reflect their willingness to pay. They can be households, industries, or commercial users.
- **Retailers and Traders**: Buy electricity from the wholesale market and sell it to consumers. Traders also buy and sell electricity across markets to exploit price differences.
- **Grid Owners**: Own and maintain the transmission and distribution networks. They ensure reliable physical delivery of electricity but do not participate in price competition.
- **System Operator (TSO)**: Responsible for real‑time balancing, grid stability, and secure operation of the power system. They run balancing markets and manage congestion.
- **Balance Responsible Players (BRPs)**: Entities financially responsible for keeping their production and consumption schedules balanced. If they deviate, they pay imbalance costs.

![Functions in Electricity Market](/EnergyForecasting/Structure_of_Electricity_Market/Electricity_market_part1/Images/Fig14.png)

*Fig 14: Functions in Electricity Market*

---

### Sources

- KTH "EG2050 System Planning", lecture 1 - 2 "The Structure of an electricity market", 2014 (Access via [KTH Course Catalog](https://www.kth.se/student/kurser/kurs/EG2050?l=en))
- PoliTo "Smart Electricity Systems", *Market for electricity* lecture slides, A.Y. 2025-2026, taught by [Prof. Tao HUANG](https://www.polito.it/en/staff?p=tao.huang)
- Gemini generated AI pictures for Fig 7 and 8
