---
title: "Self-Directed Learning: Electricity Markets & Renewables"
excerpt: "Study notes on market structures, pricing mechanisms, day-ahead clearing, intraday trading, balancing markets, and the Nordic market model."
layout: single
author_profile: true
permalink: /EnergyForecasting/Electricity_Market/
usemathjax: true
date: 2026-08-12
categories:
  - "Energy Markets"
---

# Self-Directed Learning: Electricity Markets

This page compiles my notes and study materials on electricity market design, clearing mechanisms, and deregulated operations. A primary resource for this study is the DTU course **Renewables in Electricity Markets (46755)** (available via [DTU Course Catalog](https://kurser.dtu.dk/course/46755) and [YouTube Lecture Playlist](https://www.youtube.com/watch?v=QmdBpKUP4Ek&list=PLe7H9pun_r8bsWrLZ483DhVt8zvU4jv8P)).

---

# The Nordic electricity market

The electricity market in the Nordic countries operates as a deregulated, liberalized system. Unlike vertically integrated systems where a single utility controls production, transmission, and retail, the Nordic model uses a bilateral structure. Market players trade electric energy freely through centralized power pools or direct contracts, while independent entities manage the physical grid.

## Core characteristics of electricity

The design of the Nordic market is shaped by two physical characteristics of electric energy:

- **Non-storability:** Electricity must be produced and consumed at the same moment. The system requires continuous balance to maintain frequency.
- **Transport constraints:** Electric power flows according to physical laws, not contract paths. Grid congestion limits how much power can travel between regions.

These two properties explain almost every institutional feature described below: because energy cannot be stockpiled, someone must be responsible, minute by minute, for keeping production and consumption in balance; and because power cannot be routed like a parcel, the market must account for where energy physically enters and leaves the grid.

## The power system

Trading electricity requires a physical infrastructure to carry it from producers to consumers. This infrastructure — the power system — is organized in three layers:

- **Transmission grid:** The national or international backbone. Carries large amounts of power over long distances at high voltage.
- **Sub-transmission grid:** Regional grids that step down from the transmission level.
- **Distribution grid:** Connects the majority of end consumers, typically split into high- and low-voltage segments.

Transmission and distribution are natural monopolies — it is not economically sensible to build parallel grids — so grid ownership is kept separate from the competitive parts of the market (production, retail, trading) and is subject to regulation.

## Market participants

Several distinct functions exist in the electricity market. The same company can hold more than one of these roles at once (for example, a producer that is also a balance responsible player), but the functions themselves are conceptually separate:

- **Producers:** Own and operate power plants. Economies of scale mean the production side tends toward a smaller number of larger players.
- **Consumers:** End-users of electricity, ranging enormously in size, from households to industrial loads.
- **Retailers and traders:** Buy from producers (or other retailers) and sell to consumers (or other retailers). They can offer consumers price insurance and increase competition in the market, but they also carry significant financial risk since they are exposed to price movements between purchase and sale.
- **Grid owners:** Build, operate, and maintain the transmission, sub-transmission, and distribution grids. As natural monopolists, they are also responsible for power quality and metering, and must sometimes buy electricity themselves to cover losses in the grid.
- **System operator:** Technically responsible for the real-time balance between generation and consumption. Because this role must be neutral toward all commercial players, it is often called an Independent System Operator (ISO); when the same entity also owns the transmission grid, it is called a Transmission System Operator (TSO), which is the Nordic model.
- **Balance responsible players:** Financially responsible for the balance between generation and consumption on behalf of a producer, consumer, or trader. Every market participant must either be balance responsible itself or contract with someone else who takes on that responsibility — a balance responsible player does not need to produce or consume electricity itself.

## Grid tariffs

There is no electricity market without a grid, and someone has to pay for building, operating, and maintaining it. Grid tariffs generally combine several components:

- **Energy fee:** Covers losses in the grid.
- **Congestion fee:** Applies when temporary transmission limitations restrict flow.
- **Capacity fee:** Recovers the underlying investment cost of the grid.

Because grids are monopolies, tariffs are regulated rather than left to competition, typically under one of two regimes:

- **Cost-based regulation:** The tariff reflects what it actually costs the grid company to build, operate, and maintain the network.
- **Performance-based regulation:** The tariff reflects the service level the grid company delivers, giving it an incentive to operate efficiently rather than simply pass costs through.

## Market timeline and trading sequence

Trading follows a sequence that starts years in advance and ends with real-time operations. The whole sequence exists to solve one problem: producers cannot know in advance exactly when and how much their customers will consume, so the market needs a structured way to firm up positions as delivery approaches, and to settle whatever gap remains afterward.

### Forward market
The forward market allows producers and retailers to secure prices and manage risk up to several years before delivery. These financial contracts do not involve physical delivery of power — they function purely as price insurance. Typical instruments include futures and options: for example, in an option contract one party pays a premium so that if the spot price later exceeds an agreed strike price, the counterparty compensates the difference.

### Day-ahead market (Spot market)
The day-ahead market is the primary venue for physical trading. On exchanges like Nord Pool Elspot, buyers and sellers submit bids by 12:00 the day before delivery.

- **Bids:** Participants submit quantity and price pairs for each hour — a sell bid states a quantity and a minimum acceptable price, a purchase bid a quantity and a maximum acceptable price. Beyond simple hourly bids, exchanges also support **block bids** (which must be accepted across a set of consecutive hours as a single unit), **convertible block bids** (which convert into ordinary single-hour bids if the price is favourable enough), and **conditional bids** (valid only if another specified bid is also accepted).
- **Pricing:** The pool clears the market using a price cross, where the supply and demand curves intersect. This sets a single clearing price for each hour if there are no grid bottlenecks.

### Intraday market
The intraday market (such as Nord Pool Elbas) operates closer to the delivery hour. It lets participants adjust their positions when wind forecasts change, outages occur, or consumption drifts. Trading is continuous, with buyers and sellers matching bids directly at individual transaction prices — unlike the day-ahead auction, every trade can settle at its own price rather than a single system-wide clearing price.

### Real-time balancing market
During the delivery hour, the transmission system operator (TSO) maintains grid balance. TSOs run balancing markets where generators bid to increase or decrease production:

- **Up-regulation bids:** The bidder offers to sell additional energy to the system operator — producers raising output or consumers cutting consumption — specifying a maximum volume (MW) and a minimum acceptable price.
- **Down-regulation bids:** The bidder offers to buy energy from the system operator — producers cutting output or consumers raising consumption — specifying a maximum volume (MW) and a maximum acceptable price.

The TSO calls on these bids based on cost: the cheapest available up-regulation bid or the best-paying down-regulation bid is activated first. Activated bids can be settled either **pay-as-bid** (each accepted bid is paid its own requested price) or under **uniform pricing** (all activated up-regulation bids receive the price of the most expensive one used, and all activated down-regulation bids receive the price of the least expensive one used).

An alternative to a balancing market is **central dispatch**, where the system operator solves a short-term optimization problem directly from the bids submitted in the ahead market and dispatches the system according to that solution; real-time prices then fall out of the same optimization rather than from a separate bid-and-activate process.

### Imbalance settlement
After delivery, the TSO calculates the difference between traded volumes and actual production or consumption for each balance responsible player, typically as:

```
balance = generation + purchase − consumption − sales
```

(counting both ahead-market and real-time positions). A **positive balance** means the player fed more energy into the system than it withdrew, and it must sell the surplus to the system operator; a **negative balance** means it withdrew more than it fed in, and it must buy the shortfall.

The price used for this settlement matters a great deal, and two conventions dominate:

- **Single-price system:** The system operator buys and sells imbalance power at the same price (the relevant regulation price), regardless of whether the imbalance happened to help or hurt overall system balance.
- **Two-price system:** The system operator uses one price for imbalances that work against the system's needs and the ordinary day-ahead system price for imbalances that happen to help it. This gives balance responsible players a stronger incentive to forecast accurately and avoid imbalances, since only "unhelpful" deviations are penalized relative to the ahead-market price.

Some markets soften this incentive with a **mixed price system** (helpful imbalances are paid a price between the system price and the harmful-imbalance price) or a **dead-band** (small deviations are settled at the system price regardless of direction, so only large imbalances face a worse price).

## Congestion management and bidding zones

The Nordic region uses bidding zones to manage transmission constraints.

When the grid cannot carry all the desired power from cheap production zones to high-demand zones, the market splits. TSOs calculate the available transfer capacity between areas. The market clearing process incorporates these constraints:

- **No grid bottlenecks:** A single system price clears the entire market.
- **Grid bottlenecks:** Prices diverge between areas. Cheap zones experience lower prices due to surplus power, while import-constrained zones face higher prices.

## Models for organizing ahead trading

Beyond the specific Nordic implementation, three broad models exist for how the ahead market can be structured, and it is useful to see where the Nordic model sits among them:

- **Vertically integrated market:** Consumers must buy from their local power company, which itself combines the roles of producer, retailer, grid owner, and balance responsible player. Power companies may still trade freely with each other.
- **Centralized market (power pool):** All producers sell to a central pool and all consumers buy from it. The pool is usually operated by the system operator, who then also functions as trader, retailer, and balance responsible party for consumers.
- **Bilateral market:** All players may trade freely with each other, whether directly or through one or more competing pools. The Nordic market is of this type — Nord Pool operates as one (of potentially several) trading venues, but producers, retailers, and consumers are free to also contract directly.
