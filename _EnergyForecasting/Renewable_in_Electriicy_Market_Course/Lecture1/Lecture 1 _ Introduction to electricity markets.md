---
title: "Lecture 1: Introduction to electricity markets"
excerpt: "Study notes on centralized vs. decentralized power systems, game theory, market clearing, social welfare, and uniform pricing."
layout: single
author_profile: true
permalink: /EnergyForecasting/Renewable_in_Electriicy_Market_Course/Lecture1/Introduction/
usemathjax: true
date: 2026-08-12
categories:
  - "Electricity Market"
---

![[Pasted image 20260812135339.png]]

Electric power systems include: generators (producers) + tranmission system + Demands

- Centralised power system (no market): A single entity, such as the system operator, is responsible for making all **operational** and **planning** decisions (e.g: tranmission line planning example) for the entire power system.
	- Goal of system operator when making operational + planning decisions: To meet the entire demand by dispatching power generators across the network in a **feasible** and **cost-effective** manner.
	- Example in Denmark: independent state-owned company that owns and operates Danish energy infrastructure.
	- Example about security: n-1 problem. If 1 generator outs -> can we sastify the demand or not
- Electricity market
- ![[Pasted image 20260812140503.png]]
- Now every power plant is belongs to different producer
	- Producers in Denmark:  Vattenfall (major wind farm operator), European Energy A/S (better Energy A/s), Eurowind Energy, Orsted A/S, Eurowind Energy
	- Each producer: aims to maximise their own profit by making optimal operatiuonal and planning decisions
	- Unlike centrelised systems -> there multiple decision-makers involved

> # 🎯 **What is game theory in electricity markets?**

Game theory is used when **multiple market participants make strategic decisions**, and the outcome depends on how they interact.
In electricity markets, this means:
- Generators choose **offer prices** and **quantities**
- Consumers choose **bid prices**
- Aggregators choose **flexibility strategies**
- Wind producers choose **risk‑based offering strategies**
- Balancing providers choose **reserve bids**
Each player wants to **maximize profit**, but their decisions affect the market price and each other.
This is a **game**.

![[Pasted image 20260812140952.png]]

![[Pasted image 20260812141138.png]]

![[Pasted image 20260812141224.png]]
3 sellers and 3 buyers

Utility: **Utility = how much satisfaction or benefit someone gets from buying something.** Super short, with the apple example.
### 🍎 Example 

- Buyer A pays **$6** for 1 apple → their **utility is high** (they really want it).
- Buyer C pays **$4** for each apple → their **utility is lower** (they want apples, but not as much).

![[Pasted image 20260812141433.png]]

Market-clearing price: It is the price at which the quantity supplied = quantity demanded in the market
- **Nord Pool** → Scandinavian operator (Norway, Sweden, Finland, Denmark)
- **EPEX SPOT** → French operator that also runs markets in Denmark

>Note: Why does a French company operate in Denmark?
Because Europe uses **market coupling**, meaning countries share:
- common auction algorithms (EUPHEMIA)
- common price zones
- cross-border trading
So multiple exchanges can operate in the same country.
![[Pasted image 20260812141743.png]]

Why does the market operator want to maximise social welfare?

because the market operator is non-profit entity whose job is to clear the market in the way that:
- Maximises total value for consumers (their willingness to pay)
- Minimise total cost for suppliers (their offer prices)
-> this creates the large possible gap betwen:
- What buyers are willing to pay
- What sellers are willing to accept
-> the gap is called social welfare (or surplus)

![[Pasted image 20260812142429.png]]![[Pasted image 20260812142441.png]]


Beautiful Mind - John Nash 
Nash equilibrium point: The point is everyone okay with that

Question: Based on uniform pricing, does any buyer (or seller) necessarily pay (or receive) the price they submitted to the market?

The answer is **No**: In **uniform pricing**, buyers and sellers **do NOT pay or receive the price they submitted**. They all settle at **one single price**: the **market‑clearing price (MCP)**.
Uniform pricing means:
- Buyers submit **bid prices** (their willingness to pay)
- Sellers submit **offer prices** (their minimum acceptable price)
- The market operator finds the **intersection** → the MCP
- **Everyone trades at that MCP**, not at their submitted price
![[Pasted image 20260812144057.png]]


Electricity market
- Quantity: MWh
- Price: Euro/MWh or DKK/MWh
- ![[Pasted image 20260812144222.png]]
- There are some generator bidding at 0 Euros/MWh -> who are they? -> could be Renewable generator, or even negative (like -5 Euros/MWh - Tariff, )
- Bid at very high price -> who are they? Could be gas power plant -> cause the gas price is high

![[Pasted image 20260812144232.png]]


Discussion: 
What aspect of an electricity market differentiate it ffrom markets for other commodities, such as the apple market?
- Apple can be stored, but electricity can not be stored (at very very large scale)
- Electricity demand is typically highly inelastic to price, though this is changing
- the electricity market-clearing algorith miuust take into accoutn the physical laws of electricity netwroks (Kirffschoff Law)
![[Pasted image 20260812145825.png]]

Further constraints: line constraints, mathematical programs

Kahoot:
1. What is "social welfare"?: the area between the supply and demand curves
2. At the equilibrium point, the social welare is maximised
3. Which suppliers have an accepted bid in the market?
![[Pasted image 20260812150318.png]]
 - Red + Green, Blue is outside
 3.Under uniform pricing, at what prices are the REd and Green suppliers paid, respectively? 30 and 30 -> we pay people at the same price. In **uniform pricing**, buyers and sellers **do NOT pay or receive the price they submitted**. They all settle at **one single price**: the **market‑clearing price (MCP)**
1. Under uniform pricing, what is the "payment" to the green supplier? and what is tis profit (revenue minus cost)
	1. 30 Euro x 20 = 600 revenue
	2. Cost = (60 - 40) x 20 = 400
	3. Profit = 600 - 20
2. What is the social welfare?
	1. 2700 Euros = Total area under demand - generation cost 
3. At what price is the green supplier paid under the uniform and pay-as-bid pricing schemes, respectively?
	1. 30 Euros/ Mwh and 20 Euros/Mwh
4. Under uniform pricing, which of the following statements about the Orange supplier is incorrect?
![[Pasted image 20260812151519.png]]

Incorrect: For consummers, it is indifferent at what price Orange is offering. => they are different

5. Multiple choice: Which statements are correct? (There maybe more than once correct answer). if relevant, it is uniform pircing.
![[Pasted image 20260812151708.png]]

Except blue one, other answer is correct