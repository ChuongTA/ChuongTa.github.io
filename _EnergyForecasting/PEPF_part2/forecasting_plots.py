"""
Plotting functions for the QR / QRF walk-forward pipeline.

Kept separate from main_pipeline.py on purpose: nothing in this file
touches data loading, feature engineering, or model fitting. Every
function here takes already-computed arrays/DataFrames and produces
one figure.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless-safe backend; avoids Tk errors with no display
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches


def plot_split_diagram(fold_boundaries, out_path):
    """
    Gantt-style chart showing the Train / Validate / Test window for
    every walk-forward fold, stacked one row per fold. This is the
    diagram that answers "what does the cross-validation actually
    look like" at a glance.
    """
    colors = {"Train": "#37474F", "Validate": "#FF9100", "Test": "#E91E63"}

    fig, ax = plt.subplots(figsize=(11, 1.2 + 0.6 * len(fold_boundaries)))

    for i, fold in enumerate(fold_boundaries):
        y = len(fold_boundaries) - i  # fold 1 on top
        segments = [
            ("Train", fold["train_start"], fold["train_end"]),
            ("Validate", fold["val_start"], fold["val_end"]),
            ("Test", fold["test_start"], fold["test_end"]),
        ]
        for label, start, end in segments:
            width_days = (end - start).total_seconds() / 86400
            ax.barh(
                y, width_days, left=start, height=0.6,
                color=colors[label], edgecolor="white", linewidth=0.5,
            )
        ax.text(fold["train_start"], y, f"  Fold {fold['fold']}", va="center", ha="right",
                fontsize=9, fontweight="bold", color="#263238")

    ax.set_yticks([])
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.set_xlabel("Date", fontsize=11, fontweight="bold", color="#37474F")
    ax.set_title("Walk-Forward Train / Validate / Test Split", fontsize=13,
                 fontweight="bold", pad=14, color="#263238")

    handles = [mpatches.Patch(color=c, label=label) for label, c in colors.items()]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0, -0.15), ncol=3,
              frameon=False, fontsize=10)

    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.grid(True, axis="x", alpha=0.2, linestyle="--", color="#90A4AE")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved split diagram to: {out_path}")


def plot_forecast_fan(dates, y_true, preds_by_model, lead_time_hours, fold_label, out_path):
    """
    QR vs QRF forecast fan chart (median + 80%/95% intervals) side by
    side, for one fold's test window.
    """
    fig, axes = plt.subplots(1, len(preds_by_model), figsize=(8 * len(preds_by_model), 5.5), sharey=True)
    if len(preds_by_model) == 1:
        axes = [axes]
    colors = {"QR": "#1976D2", "QRF": "#00796B"}

    for ax, (name, preds) in zip(axes, preds_by_model.items()):
        ax.fill_between(dates, preds[0.025], preds[0.975], alpha=0.20,
                         color=colors.get(name, "#1976D2"), label="95% Prediction Interval")
        ax.fill_between(dates, preds[0.10], preds[0.90], alpha=0.40,
                         color=colors.get(name, "#1976D2"), label="80% Prediction Interval")
        ax.plot(dates, y_true, color="#E91E63", lw=1.4, label="Actual Price", zorder=4)
        ax.plot(dates, preds[0.50], color="#37474F", lw=1.6, linestyle="--",
                label="Median Forecast", zorder=3)

        ax.axhline(0, color="#78909C", lw=0.8, linestyle=":")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        ax.set_xlabel("Date (UTC)", fontsize=11, fontweight="bold", color="#37474F")
        ax.set_title(f"{name} — {lead_time_hours}h ahead ({fold_label})", fontsize=12,
                     fontweight="bold", color="#263238")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#CFD8DC")
        ax.spines["bottom"].set_color("#CFD8DC")
        ax.legend(fontsize=9, loc="upper right", frameon=True, facecolor="white", edgecolor="#ECEFF1")
        ax.grid(True, alpha=0.2, linestyle="--", color="#90A4AE")

    axes[0].set_ylabel("DK1 Spot Price (EUR/MWh)", fontsize=11, fontweight="bold", color="#37474F")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved forecast fan chart to: {out_path}")


def plot_timing_comparison(timing_rows, out_path):
    """
    timing_rows: list of dicts with keys {method, mean_ms, std_ms},
    one bar per method, log-scaled y-axis since the gap between
    bootstrapping and conformal prediction is usually large.
    """
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = {"Bootstrap": "#FF9100", "Conformal": "#00796B"}
    names = [r["method"] for r in timing_rows]
    means = [r["mean_ms"] for r in timing_rows]
    stds = [r["std_ms"] for r in timing_rows]
    bar_colors = [colors.get(n, "#607D8B") for n in names]

    ax.bar(names, means, yerr=stds, color=bar_colors, capsize=6)
    ax.set_yscale("log")
    ax.set_ylabel("Time per fold (ms, log scale)", fontsize=11, fontweight="bold", color="#37474F")
    ax.set_title("Bootstrap vs Conformal: Prediction Time\nAveraged across walk-forward folds", fontsize=13,
                 fontweight="bold", pad=12, color="#263238")
    for i, (m, s) in enumerate(zip(means, stds)):
        ax.text(i, m * 1.15, f"{m:.1f} ms", ha="center", fontsize=10, fontweight="bold", color="#263238")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CFD8DC")
    ax.spines["bottom"].set_color("#CFD8DC")
    ax.grid(True, axis="y", alpha=0.2, linestyle="--", color="#90A4AE")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved timing comparison to: {out_path}")


def plot_reliability_diagram(reliability_rows, out_path):
    """
    reliability_rows: list of dicts with keys
        lead_time, model, nominal_coverage, empirical_coverage
    already averaged across folds.
    """
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    ax.plot([0, 1], [0, 1], color="#37474F", linestyle="--", lw=1.5, alpha=0.7,
            label="Perfect Calibration (Ideal)")

    colors = {1: "#2979FF", 6: "#00E676", 12: "#FF9100", 24: "#FF1744"}
    line_style_cycle = ["-", "--", ":", "-."]

    lead_times = sorted({r["lead_time"] for r in reliability_rows})
    models = sorted({r["model"] for r in reliability_rows})
    line_styles = {name: line_style_cycle[i % len(line_style_cycle)] for i, name in enumerate(models)}

    for lt in lead_times:
        for name in models:
            rows = [r for r in reliability_rows if r["lead_time"] == lt and r["model"] == name]
            rows = sorted(rows, key=lambda r: r["nominal_coverage"])
            noms = [r["nominal_coverage"] for r in rows]
            covs = [r["empirical_coverage"] for r in rows]
            ax.plot(noms, covs, marker="o", markersize=5, lw=2, linestyle=line_styles[name],
                    color=colors.get(lt, "#000000"), label=f"{name}, {lt}h ahead")

    ax.set_xlabel("Nominal Coverage", fontsize=12, fontweight="bold", color="#37474F")
    ax.set_ylabel("Empirical Coverage (avg. across folds)", fontsize=12, fontweight="bold", color="#37474F")
    ax.set_title("Reliability Diagram\nAveraged Across Walk-Forward Folds", fontsize=13,
                 fontweight="bold", pad=12, color="#263238")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CFD8DC")
    ax.spines["bottom"].set_color("#CFD8DC")
    ax.legend(fontsize=8, loc="lower right", frameon=True, facecolor="white", edgecolor="#ECEFF1", ncol=2)
    ax.grid(True, alpha=0.2, linestyle="--", color="#90A4AE")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved reliability diagram to: {out_path}")
