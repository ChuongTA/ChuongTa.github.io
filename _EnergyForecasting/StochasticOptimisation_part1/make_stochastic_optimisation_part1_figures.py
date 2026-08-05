"""
Generates the deterministic-vs-stochastic figure for the Stochastic
Optimisation for Energy Storage, Part 1 (theory) post.

fig_deterministic_vs_stochastic.png
   Two panels: a single known path (deterministic) vs a branching fan of
   scenarios (stochastic), for a generic uncertain quantity (price, demand,
   or generation).

The two-stage program diagram is built manually instead (see the markdown
file for the description of what it should show).
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(11)

OUT_DIR = "D:/33_Obsidian/33_Github/ChuongTa.github.io/_EnergyForecasting/StochasticOptimisation_part1"

NAVY = "#1f3b57"
LIGHT_BLUE = "#8ca0c4"

# ---------------------------------------------------------------------
# Figure 1: deterministic (single known path) vs stochastic (scenario fan)
# ---------------------------------------------------------------------
t = np.arange(13)
base = 50 + 20 * np.sin((t - 2) / 13 * 2 * np.pi)

n_scenarios = 6
scenarios = []
for i in range(n_scenarios):
    noise = np.random.normal(0, 5, size=13).cumsum() * 0.4
    scenarios.append(base + noise)

fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)

ax = axes[0]
ax.plot(t, base, color=NAVY, linewidth=2.4, zorder=3)
ax.set_title("Deterministic: one known path", fontsize=11, color=NAVY)
ax.set_xlabel("Time")
ax.set_ylabel("Uncertain quantity\n(price, demand, generation)")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax = axes[1]
for s in scenarios:
    ax.plot(t, s, color=LIGHT_BLUE, linewidth=1.2, alpha=0.85, zorder=2)
ax.plot(t, base, color=NAVY, linewidth=1.6, linestyle="--", zorder=3, label="Expected path")
ax.set_title("Stochastic: a range of possible paths", fontsize=11, color=NAVY)
ax.set_xlabel("Time")
ax.legend(loc="upper left", frameon=False, fontsize=8)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.suptitle("Deterministic vs. Stochastic Optimisation", fontsize=13, color=NAVY, y=1.02)
fig.tight_layout()
fig.savefig(f"{OUT_DIR}/fig_deterministic_vs_stochastic.png", dpi=160, bbox_inches="tight")
plt.close(fig)

print("Saved:")
print(f"{OUT_DIR}/fig_deterministic_vs_stochastic.png")
