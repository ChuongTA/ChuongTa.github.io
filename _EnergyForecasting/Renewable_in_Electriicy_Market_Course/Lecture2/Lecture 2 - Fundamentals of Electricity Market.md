
Objectives:
- Identify the key factors in the electricity market.
- Describe the different types of markets in the power sector.
- Compare and contrast the current practices in European and U.S. electricity markets.
- Formulate the market-clearing procedure as a linear optimization problem, excluding the transmission network.

# Outline
- Various market actors
- Various types of electricity market
- European vs U.S.electricity markets
- Market-clearing as a linear optimisation problem

## 1. Market actors
- Also referred to as “market players” or “market participants”
- ! Which market actors have we identified so far?

### Power demands: 
- Large consumers, e.g., industrial plants  
- Retailers: Buy and resell electricity to smaller consumers.
A retailer is an intermediate market actor (or trader) who purchases electricity in bulk from electricity markets and sells it to a large number of small-scale consumers, e.g., households.

Examples in Denmark:![[Pasted image 20260814131639.png]]
### Market operator
A non-profit entity that receives all offers from producers and bids from consumers - clears the market by maximizing social welfare, and ultimately distributes the market-clearing outcomes, including prices and quantities.
![[Pasted image 20260814131811.png]]

### System operator
- Transmission System Operator (TSO): Responsible for the safe operation of the underlying power grid at the high-voltage transmission level (typically a meshed grid), ensuring supply security, real-time power supply and demand balance, and system stability.
	- Example in Denmark:
	- ![[Pasted image 20260814132009.png]]
- In Europe: **ENTSO-E (European Network of Transmission System Operators for Electricity)** coordinates all European TSOs to run the high-voltage grid, set common rules, and coordinate cross-border electricity markets.![[Pasted image 20260814132023.png]]
- Distribution System Operator (DSO): Responsible for the safe operation of the underlying power grid at the medium- and low-voltage distribution level (typically a radial grid).
	- A **radial grid** is a **tree-like distribution network** where electricity flows in **one direction** from the substation to consumers, with **no loops**.
	- TSO transmission grids are **meshed** (many loops), whereas distribution grids are **radial** (one path).
	- ![[Pasted image 20260814132420.png]]
- Market Regulator: Responsible for monitoring market performance in both the short and long run, as well as designing appropriate market regulations and policies.
- ![[Pasted image 20260814132541.png]]
- Other market actors: 
	- Traders (both physical and purely financial), 
	- Balancing Responsible Parties (BRPs), 
	- Flexibility Aggregators, 
	- and other relevant market actors will be introduced throughout the course as needed.

## 2. Various types of electricity market
Three main markets with different products are:
- Capacity markets
- Energy markets
- Ancillary service markets

### 2.1 Capacity markets
- Designed to ensure that **sufficient** generation capacity (measured in MW) is available to maintain supply security and support reliable system operation.
- Any producer submitting an offer to the electricity market—regardless of whether it is accepted or rejected—is eligible for compensation based on their availability (measured in EUR/MW).
- Capacity payments serve as an incentive for power producers to invest in new generation assets over the long term.
- Who pays the bill: The final consumer.
However, this course will not cover capacity markets.

### 2.2 Energy market
A central marketplace for exchanging energy (in MWh):
- **1) Futures markets**:
	- Long-term financial contracts (with a time span of up to 6 years)
	- Purpose: Price hedging and risk management for buyers and sellers
	- Example: NASDAQ Commodities in Scandinavian countries
	- Note: This topic will not be covered in this course.
- **2) Day-ahead market**:
	- Also known as the "spot market"
	- Timing: Cleared 12–36 hours before the actual delivery time
	- Example: Nord Pool Elspot, which is cleared at noon on day D-1 for energy exchange during each hour of day D (from midnight to midnight), resulting in different market prices and quantities for each hour.
- **3) Intra-day market**:
	- This market provides an opportunity to "modify" day-ahead schedules in case of updated forecasts, asset failures, or trading purposes. It operates as a continuous and/or discrete auction-based trading platform between the day-ahead market and real-time.
	- Previously it was just a continuous market: A **continuous market** is a trading system where **orders are matched instantly and continuously** whenever a buy and sell order meet—with **no fixed auction time**, trading 24/7, no gate closure, or market clearing.
	- Example: It starts at 3 PM on D-1 and ends 1 hour before real-time. Three discrete auction-based sessions (ID-A) and a continuous platform (ID-C) are available. The current time resolution is 1 hour, but it will shift to 15 minutes soon.
- **4) Balancing market**:
	- Also known as the "imbalance" market or the "real-time" market.
	- This market operates close to real-time system operations.
	- Purpose: To ensure power supply-demand balance and the safe operation of the system.![[Pasted image 20260814134855.png]]

### 2.3 Ancillary service markets

These markets allow the system operator to procure services necessary for the secure and reliable operation of the system.
E.g.: 
- Primary reserves
- Secondary reserves
- Tertiary reserves
- Black-start capability
- Reactive and voltage-control reserves
- And more.![[Pasted image 20260814135029.png]]
>⚡ FCR, aFRR, mFRR 

- **FCR – Frequency Containment Reserve** _Instant, automatic response_ to stabilize frequency after a disturbance (first seconds).
- **aFRR – Automatic Frequency Restoration Reserve** _Automatic ramping_ to restore frequency and relieve FCR (seconds → minutes).
- **mFRR – Manual Frequency Restoration Reserve** _Manually activated_ reserve (TSO triggers) to restore balance and replace aFRR (minutes → 15 min).

![[Pasted image 20260814135814.png]]


# 3. European vs U.S.electricity markets
![[Pasted image 20260814140150.png]]

Europe: 6 nodes (for example) -> split 2 zones 

In terms of market and system operation: 
- In Europe: Market operators and system operators are separate entities (e.g., Nord Pool as the market operator and Energinet as the TSO).
- In the U.S.: An Independent System Operator (ISO) is responsible for both clearing the market and operating the system (e.g., CAISO and PJM).

In terms of network modeling for market clearing:
- In Europe: The transmission network is modeled in a simplified manner (using zonal representation) within the day-ahead and intraday market-clearing process. There is no detailed network modeling within each bidding zone.
- In the U.S.: The transmission network is fully modeled using a nodal representation and a linearized power flow model in all market-clearing problems.

In terms of energy and reserve markets:
- In Europe: The reserve markets are cleared separately by the TSOs (e.g., Energinet) before the day-ahead energy market is cleared by the market operator.
- In the U.S.: A joint energy and reserve market exists in the day-ahead time stage, cleared by the ISO, resulting in an energy and reserve dispatch co-optimization problem.

European vs U.S. electricity markets
Regarding complex offers versus complex market clearing:
- **In Europe:** Market actors, such as power producers, are responsible for ensuring their offers/bids adhere to their technical constraints (e.g., ramp limits, minimum production limits, and minimum up/down time limits for conventional generators). Market actors internalize their technical limits within their own offers/bids: They offer/bid for their entire portfolio within a bidding zone (not per asset). This results in complex orders (bids and offers), while the market-clearing process remains relatively simple.


## 3. Market-clearing as a linear optimization problem

An illustrative problem

![[Pasted image 20260814192638.png]]

Inelastic demand: Consumers buy the same amount no matter the price.
-> the price does NOT affect demand - demand is fixed

The market‑clearing price is determined **only by generator offers**, because demand does **not change** when price changes.

**Example:** Demand = 40 MW (inelastic) Even if price is €10, €20, or €100 → demand stays **40 MW**.

Primal variables:
$$
p_{W1},\; p_{G1},\; p_{G2}
$$
$$
\min\; C = 0 \cdot p_{W1} + 20 \cdot p_{G1} + 30 \cdot p_{G2}
$$
$$
0 \le p_{W1} \le 20
$$
$$
0 \le p_{G1} \le 50
$$
$$
0 \le p_{G2} \le 100
$$
Power balance (inelastic demand):
$$
p_{W1} + p_{G1} + p_{G2} = D
$$
Dual variables:
$$
\lambda = \text{market-clearing price}
$$
Numerical example ($D = 40$ MW):
$$
p_{W1} = 20,\quad p_{G1} = 20,\quad p_{G2} = 0
$$
Market-clearing price:
$$
\lambda = 20\ \text{€/MWh}
$$
A **dual variable** is the **shadow price** of a constraint — it tells you **how much the objective would improve if you relax that constraint by 1 unit**.

In electricity markets:
- The **dual variable of the power-balance constraint** = **market-clearing price**
- It represents the **value of one extra MW of demand**
- If demand increases by 1 MW, the objective cost increases by $\lambda$ (the dual)

Example constraint:
$$
p_{W1} + p_{G1} + p_{G2} = D
$$
Dual variable:
$$
\lambda = 20\ \text{€/MWh}
$$

Meaning: If demand increases by **1 MW**, total system cost increases by **€20** → that’s the **market price**.

$\mu$: The dual variable for an inequality constraint. It measures the **shadow price** of relaxing that constraint by **1 unit**.

**$\mu$ is the dual variable for an inequality constraint.** It tells you whether a limit is **active (binding)**.
- If the limit **binds** → $\mu > 0$
- If the limit **does NOT bind** → $\mu = 0$

Example constraint:
$$
p_{G1} \le 50
$$
- If $p_{G1} = 50$ → limit is active → $\mu > 0$
- If $p_{G1} < 50$ → limit is not active → $\mu = 0$

In your numerical example, G1 produces **20**, so the limit is not binding:
$$
\mu = 0
$$


The **Lagrange equation** (Lagrangian) is what you get when you combine:
- the **objective function**, and
- all the **constraints**,
- multiplied by their **dual variables** ($\lambda, \mu$).

**Goal:** To combine the **objective** and **all constraints** into **one single function** so we can apply the **KKT conditions** and find the **optimal solution + optimal prices (dual variables)**.

KKT: Karush-Kuhn-Tucker conditions

![[Pasted image 20260814194952.png]]

Objective:
$$
\min C = 0p_{W1} + 20p_{G1} + 30p_{G2}
$$

Constraints:
$$
p_{W1} + p_{G1} + p_{G2} = D \quad (\lambda)
$$
$$
0 \le p_i \le \overline{p}_i \quad (\mu_i^{low},\; \mu_i^{up})
$$

### **Lagrangian Function**
$$
L = 0p_{W1} + 20p_{G1} + 30p_{G2} + \lambda(D - p_{W1} - p_{G1} - p_{G2}) + \mu_{W1}^{up}(p_{W1} - 20) + \mu_{G1}^{up}(p_{G1} - 50) + \mu_{G2}^{up}(p_{G2} - 100)
$$
*(Note: Usually, bounds are written as $p_i - p_i^{up} \le 0$, so we add $\mu_i^{up}(p_i - p_i^{up})$).*

That’s the **Lagrange equation**: **objective + duals × constraints**.

![[Pasted image 20260814194531.png]]

![[Pasted image 20260814194909.png|327]]

> $\bar{\mu}$

**$\bar{\mu}$ is the dual variable for the** _**upper bound**_ **of an inequality constraint.**
- Every variable has **two limits**: 
  - **lower limit** → $\mu^{low}$ (or $\underline{\mu}$)
  - **upper limit** → $\mu^{up}$ (or $\overline{\mu}$)
So:
- If the **upper limit is binding** → $\overline{\mu} > 0$
- If the **upper limit is NOT binding** → $\overline{\mu} = 0$

![[Pasted image 20260814195033.png]]![[Pasted image 20260814195118.png]]

KKT Conditions of the market-clearing optimization problem:
![[Pasted image 20260814195316.png]]

KTT Conditions of the market-clearing optimisation 
![[Pasted image 20260814195629.png]]

How to verify the market-clearing price by the KKT conditions
![[Pasted image 20260814200043.png]]


Example with different demand

First, if the demand is 0
![[Pasted image 20260814200132.png]]

What is the price in here, if the demand quantity is around 80 MW
![[Pasted image 20260814200223.png]]

What is the price in here, if the demand is 70

The right and left hand side if we decrease and increase the demand a bit -> the price will vary -> therefore, it will be in the range of [20,30]
![[Pasted image 20260814200239.png]]


## An Illustrative example: Price-elastic demand 

Now the demand will be affected by the price

![[Pasted image 20260814200512.png]]


## Market clearing with price-elastic demand

![[Pasted image 20260815112928.png]]


## Market clearing as a linear optimisation problem
![[Pasted image 20260815112959.png]]

SW: Social welfare


## Electricity price in DK

![[Pasted image 20260815113452.png]]

## Kahoot

- Q1: A retailer: Buys power from the market in bulk and sells it to small consumers.
- Q2: Which of following choices include only market operators? 
	- Nord Pool, EPEX, EEX (a leading international commodity exchange based in Leipizig, Germany)
	- EPEX: European Power Exchange (a major pan-European marketplace where short-term electricity contracts are brought and sold).
- Q3: A transmission system operator (TSO): operates the high-voltage transmisison grid.
- Q4: The Nordic TSOs are Energinet, Svenska Krafnat, Stattnet, Fingrid
- Q5: Nord Pool clears Day a head, intraday
	- It doesn't  reserve, and balancing markets
		- In Denmark:
		- **Energinet** clears:
		    - FCR (primary reserves)
		    - aFRR (secondary reserves)
		    - mFRR (manual reserves)
		    - Balancing market (real‑time)
		In Finland:
		- **Fingrid** clears the same types of reserve and balancing markets.
- Q6: Which entities coordinate national TSOs and regulators, respectively, at the European Level?
	- ENTSO-e and ACER
- Q7: A residental customer at a certain addres can choose her [...] among various options
	- Retailer: A residential customer **can choose her electricity retailer** because retailers are **competitive companies**. They offer different:
		- prices (fixed/variable)
		- contract types
		- green energy options
		Retailers buy electricity from markets (day‑ahead, intraday) and sell it to households. So customers are free to switch between them
		- **2. TSO/DSO = no choice**
		A customer **cannot choose** the **TSO** or **DSO** because:
	- They are **natural monopolies** tied to the physical grid.
	- The **TSO** runs the national transmission grid (e.g., Energinet, Fingrid).
	- The **DSO** runs the local distribution grid (e.g., Radius, Cerius).
	- They are **regulated**, not competitive.
	- They **do not sell electricity** — they only transport it and ensure reliability.
- Q8: Which choice correctly represents the chronological order of market clearing?
	- Future, day-ahead, intraday, balancing
- Q9: How many zone exists in the following countries, respectively: Denmark, Norway, Sweden, Finland, Germany and France?
	- 2, 5, 4, 1,1,1
- Q10: Which of the following is correct about European electricity markets?
	- The network is simplistically represented in a zone setup.
- Q11: Which of the following is NOT correct about US electricity market?
	- ISO clears the reserve market after the energy market
	- Correct:
		- **1. ISO = both market operator AND system operator**
			U.S. ISOs/RTOs (e.g., CAISO, PJM) **clear the market AND operate the grid**. This is different from Europe, where Nord Pool ≠ Energinet.
	- **2. Network is fully modeled (nodal)**
		- U.S. markets use **nodal pricing** with a **linearized power‑flow model** in all clearing problems.
	- **3. Joint energy + reserve co‑optimization**
		In the U.S., **day‑ahead energy and reserve markets are cleared together** by the ISO.
	- **4. Simple bids, complex clearing**:
		- Producers submit **technical constraints** (ramp limits, min up/down times, etc.). This makes the clearing problem a **unit commitment** with binary variables.
	- NOT Correct: In the **U.S. ISO/RTO markets**, the **day‑ahead energy market and reserve market are cleared** _**together**_ in **one single co‑optimization**. From here
		- **Nodal model**
		- **Joint clearing of energy + reserves**
		- **Unit commitment with binary variables**
- Q12: Which of the following is the correct formulation of the Lagrangian function?
	- ![[Pasted image 20260815120157.png]]
- Q13: Which does this complementary slackness condition entail?
	- ![[Pasted image 20260815120259.png]]
Q14: What is the objective function for the market-clearing optimisation problem?
	![[Pasted image 20260815120355.png]]
	Correct answer: D - Elastic Demand -M maximise the objective function

Q15: What is the market-clearing price (in euros/MWh)
![[Pasted image 20260815120445.png]]
Any price between 30 and 40

Q16: Which of the following statements about the KKT conditions are correct (there maybe multiple correct answers)![[Pasted image 20260815120559.png]]
-  **1. The dual variable of an equality constraint can take any real value**

	✅ Correct
	- Equality constraints h(x)=0 have **no sign restriction** on their dual variable λ.
	- It can be **positive, negative, or zero**, depending on whether relaxing the constraint increases or decreases the objective.
	- In contrast, inequality constraints g(x)≤0 have **non‑negative** duals μ≥0.
- **2. The KKT conditions can be used to verify the market‑clearing price*
	✅ Correct
	- In electricity markets, the **dual variable of the power‑balance constraint** equals the **market‑clearing price**.
	- Solving the KKT system gives both **optimal dispatch (primal)** and **prices (dual)**.
	- Hence, checking the KKT conditions confirms that the computed price satisfies optimality.
-  **3. The KKT conditions can be solved as a system of equations**

	✅ Correct
	- The KKT conditions combine
	    - **Stationarity** (gradient equations),
	    - **Primal feasibility** (constraints),
	    - **Dual feasibility** (sign restrictions),
	    - **Complementary slackness** (products = 0).
	- Together, they form a **system of equations and inequalities** that can be solved numerically.
    
    **4. Complementary condition includes the product of a primal and a dual variable**
	✅ Correct
	- For each inequality constraint gi(x)≤0, the KKT condition requires:
	$$μi⋅gi(x)=0$$
	- This means either the constraint is **active** (gi(x)=0,μi>0) or **inactive** (gi(x)<0,μi=0).
	- That product term is the **complementary slackness condition**.

- Q17:  What is the common range of electricity prices typial residental consumers in Denmark (in Euro/KWh, including Tax)?
	- 0.2 - 0.5 