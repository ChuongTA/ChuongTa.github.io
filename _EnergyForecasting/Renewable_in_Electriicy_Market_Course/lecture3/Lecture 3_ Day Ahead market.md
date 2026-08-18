
Obj:
- explain the fundamentals of the day-ahead market
- Describe the concept of day-ahead market coupling in Europe
- Analyse the network effrects in the market-clearing proble,
- Formulate the nodal and zonal day-ahead market-clearing optimisation problems
- Understand the cocnept of flow-based market coupling.

Outline
- Fundamentals of Day-Ahead Market Clearing
- Single Day-Ahead Coupling (SDAC) in Europe
- Network effects on Market-Clearing Outcomes
- Power-Flow Equations
- Market-Clearing Optimisation Problem: Nodal vs Zonal
- Flow-Based Market Coupling in Europe.

# 1.Fundamentals of Day-Ahead Market Clearing
## Day-ahead market in Nord Pool
![[Pasted image 20260816162657.png]]

Why go from 1h interval -> 15-minute intervals is good?
- Because the Renewable energy is a factor, RE is very intermittent.
New forecasting is better for 15 mins instead of 1h
- Have more service will join, for example battery.

## Day-ahead market: Why?

Discussion:
Why is a day-ahead market necessary? Why not wait until real-time (or closer to real-time) to clear the electricity market instead?

- Oprational reasons: Many conventional generation units, such as nuclear and coal plants, are slow and inflexible -> they have various operational constraints and require advance scheduling to operate efficiently
- Economic reasons: Economic studies, e.g., show that forward financial markets, any market cleared before real-time operation, enhacne market competitivenes, and reduce market power (strategic bidding). this prevents market participants from manipuluating maret-clearing outcomes for their own benefit.

In future 100% renewable-based power systems with massive integration of distributed energy resources, day-ahead markets may not be necessary. Instead, long-term futures markets and near real-time operational markets might be sufficient. 

Alternatively, could “electricity as a service” be the solution?

What is the service market: Internet server (pay for the capacity)

# 2. Single Day-Ahead Coupling (SDAC) in Europe
## Single Day-ahead Coupling (SDAC) in Europe

It it better to go 5 separated zone markets or just one market?
- One market for everything is better in terms of resource atribution
- SDAC Launched in February 2014
- ![[Pasted image 20260817151143.png]]
> In SDAC, increasing liquidity means enlarging the volume and diversity of bids/offers in the day-ahead market, making trading more efficient, competitive, and stable across Europe.

Liquidity is also competition.

Involved Parties:![[Pasted image 20260817151701.png]]


## How does SDAC work?

Pan_European Hybrid Electricity Market Integration Algorithm (EUPHOMIA)

> Is an algorithm developed to couple all different market rules, to calcuate electricity prices across Europe, and to allocate corss-border capacity on a day-ahead basis.

- Day-ahead market
Question: Is Nordpool the one who clear the market or EUPHOMIA clear the market for whole Europe and Nordic?
NTC: Net Transfer Capacity
NEMO: A **Nominated Electricity Market Operator (NEMO)** is ==a power exchange or entity designated by national regulatory authorities in European Union member states to run integrated wholesale day-ahead and intraday electricity markets==

Nord Pool: Bid, offer, collector -> put all the bid offer in the same place to EUPHOMIA
-> therefore, EUPHOMIA clear the market
![[Pasted image 20260817152603.png]]


SYS : System Price: The market clearing price (in Euro/MWh) assuming no transmisson grid constraints (copper-plate system)

| Feature | Copper‑plate (System Price) | Real SDAC (Zonal Prices) |
|--------|------------------------------|---------------------------|
| Price outcome | One single European price | Different prices per bidding zone |
| Grid constraints | Ignores all transmission limits | Transmission constraints fully considered |
| Cross‑border flows | Assumed infinite capacity | Limited by ATC / FB capacities |
| Dispatch logic | Pure economic dispatch | Constrained dispatch respecting grid limits |
| Drivers of price | Only supply & demand curves | Supply, demand + congestion + network limits |
| Congestion | No congestion possible | Congestion creates price differences |
| Algorithm behavior | Ideal unconstrained solution | EUPHEMIA computes feasible zonal prices |
| Interpretation | “What price would be if grid was perfect?” | “Actual market price given real grid bottlenecks” |


![[Pasted image 20260817152953.png]]

To answer the question why they have different zonal price and identical pricesm, it happens because of the transmission limit

# 3. Network effects on Market-Clearing Outcomes

Bus: Power system term 
Node: Graph
![[Pasted image 20260817153851.png]]

Since any 1 MW change in Demand (at either bus) result in a 30 change in the social welfare of the system
What happens if demand increases by 1 MW?
If demand goes from 90 → 91 MW:
- W1 is already full (20 MW)
- G1 is already full (50 MW)
- So the **next MW must come from G2**, at **€30/MWh**
The system gains **€40** of value (because demand is willing to pay 40 €/MWh) but loses **€30** of cost (because G2 costs 30 €/MWh).
So the **net social welfare change** is:
$$ΔSW=40−30=10 €/MW$$
But the **marginal cost** is **€30**, and that is what sets the price.

![[Pasted image 20260817155354.png]]Since any 1 MW change in demand at bus 1 causes a €20 change in the social welfare of the system, while the same change at bus 2 results in a €30 change.

![[Pasted image 20260817155628.png]]

Congestion rent
![[Pasted image 20260817155657.png]]![[Pasted image 20260817160355.png]]**No, the TSO is not for‑profit.** **Congestion revenue exists, but it must be reinvested into the grid or used to reduce tariffs.** **It cannot be kept as profit**.

TSOs are _regulated_, _non‑profit_ entities

In Europe (ENTSO‑E countries):
- TSOs **cannot** keep congestion revenue as profit
- TSOs **cannot** distribute it to shareholders
- TSOs **must** use it for regulated purposes
They are legally required to use congestion income for:
**1. Maintaining or increasing cross‑border capacity**
(Upgrading lines, reinforcing transformers, improving stability)

**2. Ensuring secure grid operation**
(Reserve procurement, redispatch costs, remedial actions)

**3. Reducing tariffs for consumers**
(If there is surplus after covering grid costs)
This is written in EU Regulation 2019/943 (Electricity Regulation).

Possible Ms thesis: Arguing who's gonna invest transmisison line

TAG: 
![[Pasted image 20260817213500.png]]

== Market Clearing as an Optimisation (with Network)
p 1 ->2: New primal variable: Power flow (in MW) from bus 1 to bus

![[Pasted image 20260817215423.png]]
![[Pasted image 20260817215345.png]]
Why first term p1-2 is positive but 2nd is negative?

Because G1 and G2 send power p1-2 to bus 2
And next that power + pG2 send to the demand
![[Pasted image 20260817215608.png]]

## Power Flow Equations
![[Pasted image 20260817215912.png]]

**AC power flow** is the full, physics‑accurate set of equations that describe how **real (P)** and **reactive (Q)** power move through an electrical network. It’s exactly what your Lecture 3 PDF is referring to when it says:

**AC power flow = the nonlinear equations that compute voltages, angles, and power flows in an AC grid, based on Kirchhoff’s laws.** They determine _how electricity actually flows_ in real time.

Electricity in transmission grids is **alternating current (AC)**. This means every bus has:
- a **voltage magnitude** Vi
- a **voltage angle** θi

![[Pasted image 20260817220029.png]]Depending on the type of each bus 𝑖, two out of the four variables,𝐏𝐢, 𝐐𝐢, 𝐕𝐢 and teta 𝐢,are known, while the other two are unknown. 
This ensures that the number of unknown variables and equations is balanced.

These contain for the equation
- **products** of variables
- **sine** and **cosine** terms
- **nonlinear coupling** between buses

This creates a feasible region that looks like the weird shape shown in the slide (the Hiskens figure) — not a nice convex polytope.

![[Pasted image 20260817220713.png]]Non‑convex problems can have:

- multiple local optima
- saddle points
- disconnected feasible regions
So even if you run a solver:
👉 You cannot guarantee it found the _global_ optimum.

If SDAC or any day‑ahead market tried to use **full AC power flow**, the market‑clearing problem would:

- take too long
- sometimes fail to converge
- sometimes give suboptimal or inconsistent prices
- not guarantee welfare maximization
This is unacceptable for a market that must clear **Europe in 17 minutes**.
So instead:
👉 Markets use **linearized DC power flow**, which _is_ convex

This makes the optimization:
- fast
- reliable
- globally optimal
- predictable
![[Pasted image 20260817221309.png]]

Local optimisation
![[Pasted image 20260817221818.png]]![[Pasted image 20260817222022.png]]![[Pasted image 20260817222739.png]]


## 4. market optimsation Nodal vs Zonal![[Pasted image 20260817223136.png]]
In California: Each different point has different zone
![[Pasted image 20260817223456.png]]

| Feature                        | Nodal Market (e.g., PJM, CAISO – U.S.)                                | Zonal Market (Europe – SDAC)                                              | Example from  lecture                                      |
| ------------------------------ | --------------------------------------------------------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------- |
| Price granularity              | **One price per node (bus)**                                          | **One price per bidding zone**                                            | Germany = one price for entire country                     |
| Internal grid constraints      | **Fully enforced** (all line limits included in optimization)         | **Ignored** in market clearing (except some critical lines in flow-based) | Germany’s north–south congestion NOT reflected in DA price |
| Cross-border constraints       | Enforced                                                              | Enforced (NTC or flow-based)                                              | Price differences only when NTC between zones is hit       |
| Congestion visibility          | **Local congestion → local price differences**                        | **Only inter-zonal congestion → zonal price differences**                 | SE2 ≠ SE3 ≠ SE4 in your screenshot                         |
| Market-clearing model          | AC/DC OPF with full network                                           | Welfare maximization + NTC constraints                                    | EUPHEMIA uses DC + NTC/FB constraints                      |
| Efficiency                     | High (uses full physics)                                              | Lower (internal redispatch needed)                                        | Denmark redispatch due to internal bottlenecks             |
| Who fixes internal congestion? | Market (prices reflect it)                                            | **TSO after market** (redispatch)                                         | Energinet redispatches DK1–DK2 flows                       |
| When do prices differ?         | Whenever ANY line congests                                            | Only when **cross-border** line congests                                  | Germany–Denmark price split when interconnector is full    |
| Example scenario               | Line inside city congested → price difference between Bus A and Bus B | Internal line congested but ignored → same zonal price                    | DK1 & DK2 same price even if internal lines congested      |
![[Pasted image 20260817224243.png]]![[Pasted image 20260817224249.png]]![[Pasted image 20260817224301.png]]![[Pasted image 20260817224306.png]]
NTC is the input data for market clear
NTC is determined by TSO

![[Pasted image 20260817224318.png]]


![[Pasted image 20260818142803.png]]Set of primal variables: pGg, PdD, theta_n (Voltage angle of bus n)
SW: Social Welfare
Ud: Bid price of demand d, Cg: Offer price of producer g
![[Pasted image 20260818142935.png]]

More detail, check slides

# Power Flow in Zonal systems
![[Pasted image 20260818143200.png]]Disclaimer: I use the symbol ATC (Available Transfer Capacity) to represent NTC (Net Transfer Capacity), although they might differ slightly in practice. In this course, we consider both terms (NTC and ATC) identical. 112 DTU Wind, Technical University of Denmark

![[Pasted image 20260818143316.png]]

Check others in slides

![[Pasted image 20260818143359.png]]

## 5. Flow-based market coupling in Europe
- It's an alternative to the NTC-based zonal model.
- The central western european (CWE) TSOs succesfully implemented flow-based capacity calculation and allocation, with the go-live date on May 21st, 2015

![[Pasted image 20260818151101.png]]
# 6. Kahoot

- Q1: Which of the following statements about the day-ahead arket in Nordpool is incorrecw?
	B: The market time unit is currently set to 30-minute intervals (1 hour in the time lecture deliver 2025)
- Q2: Which of the following statements about SDAC (single day-ahead coupling) is incorrect?
	- It takes around 5 hours to solve the market clearing optimisation problem  (it took around 16 minutes)
- The system price is 102.32 Euros/MWh, What does this mean.
	- The unconstrained market-clearing price (if there were no grid limits)
- Which of the following statement is incorrect?
	![[Pasted image 20260818144409.png]]
Incorrect: If there were not network limits, the price in SE2 would likely decrease.
- SE2 price is low 40.78 due to congestion, if there is no congestion, the generator can transfer power to other zones -> then the price in SE2 will be higher.

Q3: ![[Pasted image 20260818144733.png]]
C: 35, 35, 0
It is not congested. Price different is 0

Q4: The line capacity is 70 MW now, same question 
![[Pasted image 20260818144920.png]] B: 30, 35, 35 = 7 x 5 = Euros

Q5: Which of the following statements is correct regarding grid-constrained market clearing under a uniform pricing scheme?
-Correct: The grid owener is compensated in the event of congestion
- Red is incorrect, it should be: Total payment by demand = Congestion rent + Total payment to producers
- Blue: It is budge balance.

Q6: A system has 3 nodes 3 lines, & 4 producers. How many nodal balancees must be enforcecd in the optimisation problem.
A system with:
- **3 nodes**
- **3 lines**
- **4 producers**
requires **one nodal power balance equation per node**.

Number of nodal balances=3

Q7: A system has 3 nodes 3 lines, & 4 producers. How many LMPs (nodal prices) are there as dual variables?
1 LMP per node -> 3 LMPs, doesn't matter how many producers

Q8: ![[Pasted image 20260818145741.png]]
Blue is correct: It becomes non-convex.
Green is wrong: We can not obtain the optimal solution because we don't know it is either local or global

Q9: When obtaining the lineared DC power flow approximation from the AC equations, what approximation is not considered?
![[Pasted image 20260818145954.png]]

A is wrong , bik = 0


Q10: If the market-clearing optimisation problem (linear) is constrained by the linearized (DC) power flow equations,...
Its solution is guaranteed to be globally optimal.

Q11: What does the NTC-based model enforce for each bidding zone?
![[Pasted image 20260818150251.png]]Red is wrong, when we use NTC-based zonal, we ignore everything inside the zone.
- Capacity of all the domestive is not the same

Q12: Order the models in terms of their need for re-dispatch to restore grid feasibility, from lowest to highest magnitude:

![[Pasted image 20260818150603.png]]
Nodal AC, Nodal DC, Zonal flow-based coupling, Zonal NTC-based.

- Nodal AC: Respect power flow equation
- Nodal DC: Uses **linearized DC power flow**, Simple than AC, need a bit redispatch
- Zonal flow-based coupling: Don't see nodal structure at all, but try to add ritical constraints using PTDF. Need more moderate redispatch
- **Zonal NTC‑Based — highest redispatch**
- Only enforces **cross‑border limits**.
- Completely ignores **internal grid constraints**.
- Market result often infeasible → TSOs must fix everything afterward.

**Dispatch = the amount of power each generator is instructed to produce in a given hour (or 15‑minute interval) to meet demand.**

It is the **physical implementation** of the market result.

- **Day‑ahead market clears** → gives _scheduled_ production for each generator.
- **Dispatch** → the TSO ensures generators actually produce those quantities in real time.
- **Redispatch** → corrections made by the TSO if the market schedule violates grid constraints. (_adjustments_ made afterward to fix congestion or maintain grid feasibility.)

Q13: Which of the following statements about flow-based market coupling are correct (multiple chocie)![[Pasted image 20260818151133.png]]
- There is still one price for every zone
- It reflects the capacity limit of critical domestic lines to some extent.