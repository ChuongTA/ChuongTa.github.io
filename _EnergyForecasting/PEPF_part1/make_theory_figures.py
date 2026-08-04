import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# ── Paths and Directories ──────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(os.path.dirname(script_dir), "Results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# ── Synthetic Data for Methodology Illustration ─────────────────────────────
# Keep it deliberately simple and independent of actual CSV data
quantiles = [10, 20, 30, 40, 50, 60, 70, 80, 90]
quantile_vals = [30.0, 38.0, 45.0, 52.0, 60.0, 68.0, 75.0, 85.0, 100.0]
actual = 82.0

# ── Create the Figure ──────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6, 8))

# Draw the vertical axis representing the quantile ladder line
x_ladder = 0.3
ax.axvline(x=x_ladder, color="#37474F", lw=2, ymin=0.05, ymax=0.95, zorder=1)

# Plot the nine horizontal tick marks and label them
for q, val in zip(quantiles, quantile_vals):
    # tick mark line
    is_median = (q == 50)
    color = "#D32F2F" if is_median else "#00796B"
    lw = 3 if is_median else 2
    
    ax.plot([x_ladder - 0.03, x_ladder + 0.03], [val, val], color=color, lw=lw, zorder=2)
    
    # text label for each quantile
    label_text = f"$q_{{{q/100:.1f}}}$ = {val:.0f}"
    ax.text(x_ladder - 0.05, val, label_text, ha="right", va="center", fontsize=10, 
            fontweight="bold" if is_median else "normal", color="#37474F")

# Overlay realized price as a distinct marker
ax.scatter([x_ladder], [actual], color="#E91E63", marker="*", s=250, zorder=5, label="Realised Price")
ax.text(x_ladder + 0.05, actual, f"Realised Price\n({actual:.0f} EUR/MWh)", color="#E91E63", 
        ha="left", va="center", fontsize=10, fontweight="bold")

# Sketch implied density to the side (Simple Normal distribution)
y_grid = np.linspace(10, 120, 200)
# A simple normal distribution centered at 60 (median) to represent the density visually
density = stats.norm.pdf(y_grid, loc=60, scale=25)
# Scale density for visualization on the right side of the ladder
density_scaled = x_ladder + (density / max(density)) * 0.45

ax.plot(density_scaled, y_grid, color="#4DB6AC", lw=2, zorder=3)
ax.fill_betweenx(y_grid, x_ladder, density_scaled, color="#B2DFDB", alpha=0.4, zorder=2, label="Implied Density")

# Formatting & Styling
ax.set_ylabel("Electricity Price (EUR/MWh)", fontsize=12, fontweight="bold", color="#37474F")
ax.set_title("What a quantile ladder looks like for a single hour", fontsize=12, fontweight="bold", pad=15, color="#263238")

# Adjust limits and hide horizontal axis elements
ax.set_xlim(-0.05, 0.9)
ax.set_ylim(15, 115)
ax.get_xaxis().set_visible(False)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.spines["left"].set_color("#CFD8DC")

# Add a simple legend
ax.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="#ECEFF1")
ax.grid(True, axis="y", alpha=0.15, linestyle="--", color="#90A4AE")

plt.tight_layout()
output_path = os.path.join(RESULTS_DIR, "quantile_ladder.png")
plt.savefig(output_path, dpi=150)
plt.close()
print(f"Successfully saved quantile ladder plot to: {output_path}")

# ── Figure 6 — The shape of the pinball loss ───────────────────────────────
actual_price = 96.0
predictions = np.linspace(40, 150, 500)
taus = [0.1, 0.5, 0.9]

fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

for i, tau in enumerate(taus):
    ax = axes[i]
    
    # Calculate pinball loss
    errors = actual_price - predictions
    loss = np.where(errors >= 0, tau * errors, (tau - 1) * errors)
    
    # Plot loss curve
    ax.plot(predictions, loss, color="#00796B", lw=2.5, label=f"Pinball Loss")
    
    # Vertical dotted line at the actual price
    ax.axvline(x=actual_price, color="#E91E63", linestyle="--", lw=1.5)
    ax.text(actual_price + 2, max(loss) * 0.8, f"Actual Price\n({actual_price:.0f} EUR/MWh)", 
            color="#E91E63", fontsize=9, fontweight="bold")
    
    # Formatting panel
    ax.set_title(f"$\\tau = {tau}$", fontsize=14, fontweight="bold", color="#263238", pad=12)
    ax.set_xlabel("Predicted Value (EUR/MWh)", fontsize=11, fontweight="bold", color="#37474F")
    if i == 0:
        ax.set_ylabel("Loss", fontsize=11, fontweight="bold", color="#37474F")
        
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CFD8DC")
    ax.spines["bottom"].set_color("#CFD8DC")
    ax.grid(True, alpha=0.15, linestyle="--", color="#90A4AE")
    ax.set_xlim(35, 155)
    ax.set_ylim(-2, max(loss) + 5)

plt.suptitle("The shape of the pinball loss for different quantiles", fontsize=14, fontweight="bold", color="#263238", y=1.02)
plt.tight_layout()
output_path_pinball = os.path.join(RESULTS_DIR, "pinball_loss_shape.png")
plt.savefig(output_path_pinball, dpi=150, bbox_inches="tight")
plt.close()
print(f"Successfully saved pinball loss shape plot to: {output_path_pinball}")

# ── Figure 7 — CRPS Illustration for Three Distributions ────────────────────
def get_crps(mu, sigma, y_obs):
    # Numerical integration of (CDF(z) - H(z - y_obs))^2
    z_vals = np.linspace(-4, 4, 1000)
    cdf_vals = stats.norm.cdf(z_vals, loc=mu, scale=sigma)
    heaviside_vals = np.where(z_vals >= y_obs, 1.0, 0.0)
    squared_diff = (cdf_vals - heaviside_vals)**2
    # Simple rectangular integration to avoid version-dependent np.trapz / trapezoid
    crps_val = np.sum(squared_diff) * (z_vals[1] - z_vals[0])
    return crps_val

def plot_crps_panel(ax, mu, sigma, y_obs, title_suffix):
    z_grid = np.linspace(-3.5, 3.5, 500)
    cdf = stats.norm.cdf(z_grid, loc=mu, scale=sigma)
    heaviside = np.where(z_grid >= y_obs, 1.0, 0.0)
    crps_val = get_crps(mu, sigma, y_obs)
    
    # Plot curves using raw string for LaTeX symbols
    ax.plot(z_grid, cdf, color="#1976D2", lw=2, label=r"Forecast CDF: $\hat{F}(z)$")
    # For Heaviside, draw step function cleanly
    ax.step(z_grid, heaviside, where="post", color="#F57C00", lw=2, label=r"Heaviside CDF: $H(z-y)$")
    
    # Shading the CRPS area
    mask_before = z_grid < y_obs
    ax.fill_between(z_grid[mask_before], 0, cdf[mask_before], color="#1976D2", alpha=0.35, label="CRPS Area")
    mask_after = z_grid >= y_obs
    ax.fill_between(z_grid[mask_after], cdf[mask_after], 1, color="#1976D2", alpha=0.35)
    
    # Vertical line/marker at y
    ax.axvline(x=y_obs, color="#B0BEC5", linestyle="--", lw=1.2)
    ax.text(y_obs, -0.07, "$y$", ha="center", va="top", fontsize=11, fontweight="bold", color="#37474F")
    
    # Formatting
    ax.set_ylim(-0.1, 1.05)
    ax.set_xlabel("$z$", fontsize=11, color="#37474F")
    ax.set_title(f"{title_suffix}\nCRPS value: {crps_val:.2f}", fontsize=11, fontweight="bold", pad=10, color="#263238")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CFD8DC")
    ax.spines["bottom"].set_color("#CFD8DC")
    ax.legend(loc="upper left", fontsize=8, frameon=True, facecolor="white", edgecolor="#ECEFF1")

fig_crps, axes_crps = plt.subplots(1, 3, figsize=(15, 4.8), sharey=True)

# (a) Calibrated, High Variance
plot_crps_panel(axes_crps[0], mu=0.0, sigma=0.83, y_obs=0.0, 
                title_suffix="(a) Calibrated\n(aligns mean with observed)")

# (b) Not Calibrated, Low Variance
plot_crps_panel(axes_crps[1], mu=-0.5, sigma=0.4, y_obs=0.0, 
                title_suffix="(b) Not calibrated\nbut has a smaller variance")

# (c) Calibrated, Low Variance
plot_crps_panel(axes_crps[2], mu=0.0, sigma=0.4, y_obs=0.0, 
                title_suffix="(c) Calibrated and\nhas a smaller variance")

plt.tight_layout()
output_path_crps = os.path.join(RESULTS_DIR, "crps_illustration.png")
plt.savefig(output_path_crps, dpi=150, bbox_inches="tight")
plt.close()
print(f"Successfully saved CRPS illustration plot to: {output_path_crps}")


# ── Figure 8 — PIT Histograms ───────────────────────────────────────────────
fig_pit, axes_pit = plt.subplots(2, 2, figsize=(12, 10), sharey=True, sharex=True)
rng = np.random.default_rng(42)

# Generate synthetic PIT values
pit_data = {
    "Well Calibrated": rng.uniform(0.0, 1.0, 1500),
    "Underdispersed": rng.beta(0.4, 0.4, 1500),
    "Overdispersed": rng.beta(2.5, 2.5, 1500),
    "Biased Forecast": rng.beta(1.5, 3.5, 1500)
}

plot_configs = [
    (0, 0, "Well Calibrated"),
    (0, 1, "Underdispersed"),
    (1, 0, "Overdispersed"),
    (1, 1, "Biased Forecast")
]

for row, col, key in plot_configs:
    ax = axes_pit[row, col]
    data = pit_data[key]
    
    # Plot histogram with probability density
    ax.hist(data, bins=20, density=True, color="#90CAF9", edgecolor="#1E88E5", alpha=0.85)
    
    ax.set_title(key, fontsize=12, fontweight="bold", color="#263238")
    ax.set_xlabel("PIT Value", fontsize=10, color="#37474F")
    if col == 0:
        ax.set_ylabel("Density", fontsize=10, color="#37474F")
        
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CFD8DC")
    ax.spines["bottom"].set_color("#CFD8DC")
    ax.grid(True, alpha=0.15, linestyle="--", color="#90A4AE")
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 3.0)

plt.tight_layout()
output_path_pit = os.path.join(RESULTS_DIR, "pit_histograms.png")
plt.savefig(output_path_pit, dpi=150, bbox_inches="tight")
plt.close()
print(f"Successfully saved PIT histograms plot to: {output_path_pit}")


