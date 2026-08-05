"""
Plotting functions for the bootstrap-residuals deep-dive (in-sample vs
out-sample vs binned/conditional residuals), mirroring the plots used in
the skforecast bootstrapped-residuals tutorial, generated for real from
this project's own DK1 results rather than reused as-is.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_prediction_interval(dates, y_true, lower, upper, pred, title, out_path,
                              ylabel="Value", color="#607D8B"):
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.fill_between(dates, lower, upper, color=color, alpha=0.3, label="Prediction interval", zorder=1)
    ax.plot(dates, y_true, color="#E91E63", lw=1.3, label="Actual", zorder=3)
    ax.plot(dates, pred, color="#37474F", lw=1.3, linestyle="--", label="Point forecast", zorder=2)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax.set_xlabel("Date (UTC)", fontsize=10, fontweight="bold", color="#37474F")
    ax.set_ylabel(ylabel, fontsize=10, fontweight="bold", color="#37474F")
    ax.set_title(title, fontsize=12, fontweight="bold", color="#263238")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CFD8DC")
    ax.spines["bottom"].set_color("#CFD8DC")
    ax.legend(fontsize=9, loc="upper right", frameon=True, facecolor="white", edgecolor="#ECEFF1")
    ax.grid(True, alpha=0.2, linestyle="--", color="#90A4AE")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved prediction interval plot to: {out_path}")


def plot_residuals_by_bin(bin_labels, residuals_by_bin, out_path, ylabel="Residual"):
    fig, ax = plt.subplots(figsize=(10, 4.5))
    data = [residuals_by_bin[b] for b in bin_labels]
    bp = ax.boxplot(data, tick_labels=[str(b) for b in bin_labels], patch_artist=True, showfliers=False)
    for patch in bp["boxes"]:
        patch.set_facecolor("#90CAF9")
        patch.set_alpha(0.7)
    ax.axhline(0, color="#37474F", lw=1, linestyle="--")
    ax.set_xlabel("Bin (by predicted value, low to high)", fontsize=10, fontweight="bold", color="#37474F")
    ax.set_ylabel(ylabel, fontsize=10, fontweight="bold", color="#37474F")
    ax.set_title("Validation Residuals by Predicted-Value Bin", fontsize=12, fontweight="bold", color="#263238")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CFD8DC")
    ax.spines["bottom"].set_color("#CFD8DC")
    ax.grid(True, axis="y", alpha=0.2, linestyle="--", color="#90A4AE")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved residuals-by-bin plot to: {out_path}")


def plot_method_comparison(dates, y_true, methods, out_path, ylabel="Value"):
    """methods: dict of name -> (lower, upper, pred, color)"""
    fig, axes = plt.subplots(len(methods), 1, figsize=(10, 3.6 * len(methods)), sharex=True)
    if len(methods) == 1:
        axes = [axes]
    for ax, (name, (lower, upper, pred, color)) in zip(axes, methods.items()):
        ax.fill_between(dates, lower, upper, color=color, alpha=0.3, label="80% interval", zorder=1)
        ax.plot(dates, y_true, color="#E91E63", lw=1.2, label="Actual", zorder=3)
        ax.plot(dates, pred, color="#37474F", lw=1.2, linestyle="--", label="Point forecast", zorder=2)
        ax.set_title(name, fontsize=11, fontweight="bold", color="#263238")
        ax.set_ylabel(ylabel, fontsize=9, fontweight="bold", color="#37474F")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#CFD8DC")
        ax.spines["bottom"].set_color("#CFD8DC")
        ax.legend(fontsize=8, loc="upper right", frameon=True, facecolor="white", edgecolor="#ECEFF1")
        ax.grid(True, alpha=0.2, linestyle="--", color="#90A4AE")
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    axes[-1].xaxis.set_major_locator(mdates.DayLocator(interval=2))
    axes[-1].set_xlabel("Date (UTC)", fontsize=10, fontweight="bold", color="#37474F")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved method comparison plot to: {out_path}")


def plot_multiple_intervals_coverage(nominal, empirical, out_path):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot([0, 1], [0, 1], color="#37474F", linestyle="--", lw=1.5, alpha=0.7, label="Perfect calibration")
    ax.plot(nominal, empirical, marker="o", color="#7B1FA2", lw=2, label="Binned bootstrap")
    ax.set_xlabel("Nominal coverage", fontsize=10, fontweight="bold", color="#37474F")
    ax.set_ylabel("Empirical coverage", fontsize=10, fontweight="bold", color="#37474F")
    ax.set_title("Coverage Across Multiple Interval Levels", fontsize=12, fontweight="bold", color="#263238")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CFD8DC")
    ax.spines["bottom"].set_color("#CFD8DC")
    ax.legend(fontsize=9, loc="lower right", frameon=True, facecolor="white", edgecolor="#ECEFF1")
    ax.grid(True, alpha=0.2, linestyle="--", color="#90A4AE")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved multiple-intervals coverage plot to: {out_path}")
