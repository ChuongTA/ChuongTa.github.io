"""
Plotting functions for the QR / QRF walk-forward pipeline.

Kept separate from main_pipeline.py on purpose: nothing in this file
touches data loading, feature engineering, or model fitting. Every
function here takes already-computed arrays/DataFrames and produces
one figure.
"""
import os
import numpy as np
import pandas as pd
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


def plot_local_exceedance_rate(dates, y_true, preds_by_model, tau, out_path, window_hours=48):
    """
    Rolling local exceedance rate at a single upper quantile tau (e.g. 0.95):
    the fraction of actual prices above the predicted tau-quantile, inside a
    rolling window. A well-calibrated tau quantile should hover near 1 - tau.
    """
    colors = {"QR": "#1976D2", "QRF": "#00796B"}
    dates = pd.to_datetime(dates)
    fig, ax = plt.subplots(figsize=(9, 5))

    for name, preds in preds_by_model.items():
        exceed = (y_true > preds[tau]).astype(float)
        rolling = pd.Series(exceed, index=dates).rolling(f"{window_hours}h", min_periods=window_hours // 2).mean()
        ax.plot(rolling.index, rolling.values, color=colors.get(name, "#607D8B"), lw=2, label=name)

    ax.axhline(1 - tau, color="#37474F", linestyle="--", lw=1.5, label=f"Nominal ({1 - tau:.0%})")
    ax.set_ylim(-0.02, max(0.4, ax.get_ylim()[1]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax.set_xlabel("Date (UTC)", fontsize=11, fontweight="bold", color="#37474F")
    ax.set_ylabel(f"Local exceedance rate, {window_hours}h rolling", fontsize=11, fontweight="bold", color="#37474F")
    ax.set_title(f"Local exceedance rate at $\\tau={tau}$, Fold 4", fontsize=13,
                 fontweight="bold", pad=12, color="#263238")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CFD8DC")
    ax.spines["bottom"].set_color("#CFD8DC")
    ax.legend(fontsize=9, loc="upper right", frameon=True, facecolor="white", edgecolor="#ECEFF1")
    ax.grid(True, alpha=0.2, linestyle="--", color="#90A4AE")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved local exceedance rate plot to: {out_path}")


def plot_interval_width_over_time(dates, y_true, preds_by_model, lo_a, hi_a, out_path, spike_z=2.0):
    """
    Interval width (hi_a - lo_a quantile) over time for each model, with
    price-spike timestamps (z-score of y_true above spike_z) marked.
    """
    colors = {"QR": "#1976D2", "QRF": "#00796B"}
    dates = pd.to_datetime(dates)
    fig, ax = plt.subplots(figsize=(9, 5))

    for name, preds in preds_by_model.items():
        width = preds[hi_a] - preds[lo_a]
        ax.plot(dates, width, color=colors.get(name, "#607D8B"), lw=2, label=f"{name} width")

    z = (y_true - np.mean(y_true)) / np.std(y_true)
    spike_mask = z > spike_z
    for spike_date in np.asarray(dates)[spike_mask]:
        ax.axvline(spike_date, color="#E91E63", lw=0.8, alpha=0.35, zorder=1)
    if spike_mask.any():
        ax.axvline(np.asarray(dates)[spike_mask][0], color="#E91E63", lw=0.8, alpha=0.35,
                   zorder=1, label="Price spike")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax.set_xlabel("Date (UTC)", fontsize=11, fontweight="bold", color="#37474F")
    ax.set_ylabel(f"Interval width ({int(hi_a * 100 - lo_a * 100)}%), EUR/MWh", fontsize=11,
                  fontweight="bold", color="#37474F")
    ax.set_title("95% Interval Width Over Time, Fold 4", fontsize=13,
                 fontweight="bold", pad=12, color="#263238")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CFD8DC")
    ax.spines["bottom"].set_color("#CFD8DC")
    ax.legend(fontsize=9, loc="upper right", frameon=True, facecolor="white", edgecolor="#ECEFF1")
    ax.grid(True, alpha=0.2, linestyle="--", color="#90A4AE")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved interval width over time plot to: {out_path}")


def plot_calibration_sharpness_quadrant(results, out_path):
    """
    Four panels, one per lead time. Each plots width (x) vs. coverage
    deviation, empirical - nominal (y), for both models at the 80/90/95%
    intervals, shaded into the four Step-4 verdict quadrants: narrow vs.
    wide is split at that panel's own median width, matches-nominal is a
    band around y = 0.

    results: {lead_time_label: {"QR": [(width, cov, nominal), ...],
                                 "QRF": [(width, cov, nominal), ...]}}
    """
    colors = {"QR": "#1976D2", "QRF": "#00796B"}
    markers = {80: "o", 90: "s", 95: "^"}
    match_band = 0.02  # +/- 2 points counts as "matches nominal"

    fig, axes = plt.subplots(2, 2, figsize=(11, 9.6))
    axes = axes.ravel()

    for ax, (lead_label, by_model) in zip(axes, results.items()):
        all_widths = [w for pts in by_model.values() for (w, _, _) in pts]
        x_split = (min(all_widths) + max(all_widths)) / 2

        x_lo, x_hi = min(all_widths) - 8, max(all_widths) + 8
        y_vals = [cov - nom for pts in by_model.values() for (_, cov, nom) in pts]
        y_lo, y_hi = min(y_vals + [-match_band]) - 0.03, max(y_vals + [match_band]) + 0.03

        # Quadrant shading: narrow/wide split at x_split, matches-band around y=0
        ax.axhspan(-match_band, match_band, color="#B0BEC5", alpha=0.25, zorder=0)
        ax.fill_betweenx([y_lo, -match_band], x_lo, x_split, color="#EF9A9A", alpha=0.25, zorder=0)
        ax.fill_betweenx([match_band, y_hi], x_lo, x_split, color="#A5D6A7", alpha=0.25, zorder=0)
        ax.fill_betweenx([match_band, y_hi], x_split, x_hi, color="#FFE082", alpha=0.25, zorder=0)
        ax.fill_betweenx([-match_band, match_band], x_split, x_hi, color="#90CAF9", alpha=0.25, zorder=0)

        ax.axhline(0, color="#37474F", lw=1, linestyle="--", zorder=1)
        ax.axvline(x_split, color="#37474F", lw=1, linestyle="--", zorder=1)

        for name, pts in by_model.items():
            for w, cov, nom in pts:
                nom_pct = int(round(nom * 100))
                ax.scatter(w, cov - nom, color=colors.get(name, "#607D8B"),
                           marker=markers.get(nom_pct, "o"), s=90, zorder=3,
                           edgecolor="white", linewidth=0.8)
            ws = [w for w, _, _ in pts]
            covs = [cov - nom for w, cov, nom in pts]
            order = np.argsort(ws)
            ax.plot(np.array(ws)[order], np.array(covs)[order], color=colors.get(name, "#607D8B"),
                    lw=1.2, alpha=0.6, zorder=2)

        ax.set_xlim(x_lo, x_hi)
        ax.set_ylim(y_lo, y_hi)
        ax.set_title(lead_label, fontsize=12, fontweight="bold", color="#263238")
        ax.set_xlabel("Mean interval width (EUR/MWh)", fontsize=10, fontweight="bold", color="#37474F")
        ax.set_ylabel("Coverage - nominal", fontsize=10, fontweight="bold", color="#37474F")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#CFD8DC")
        ax.spines["bottom"].set_color("#CFD8DC")

    # Shared legend: model colors + interval markers + quadrant labels
    model_handles = [plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=9, label=n)
                      for n, c in colors.items()]
    marker_handles = [plt.Line2D([0], [0], marker=m, color="w", markerfacecolor="#607D8B", markersize=8,
                                  label=f"{p}% interval") for p, m in markers.items()]
    fig.legend(handles=model_handles + marker_handles, loc="lower center", ncol=5,
               frameon=False, fontsize=10, bbox_to_anchor=(0.5, 0.005))

    fig.suptitle("Calibration vs. Sharpness Quadrants, by Lead Time\n"
                 "(narrow/wide split at each panel's own median width; grey band = within 2 points of nominal)",
                 fontsize=13, fontweight="bold", y=0.98, color="#263238")

    for ax, corner_labels in zip(
        axes,
        [dict(overconfident=(0.02, 0.04), excellent=(0.02, 0.96),
              underconfident=(0.98, 0.96), conservative=(0.98, 0.04))] * 4,
    ):
        ax.text(*corner_labels["overconfident"], "Overconfident", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=8, color="#B71C1C", fontweight="bold")
        ax.text(*corner_labels["excellent"], "Excellent", transform=ax.transAxes,
                ha="left", va="top", fontsize=8, color="#1B5E20", fontweight="bold")
        ax.text(*corner_labels["underconfident"], "Underconfident", transform=ax.transAxes,
                ha="right", va="top", fontsize=8, color="#E65100", fontweight="bold")
        ax.text(*corner_labels["conservative"], "Conservative", transform=ax.transAxes,
                ha="right", va="bottom", fontsize=8, color="#0D47A1", fontweight="bold")

    plt.subplots_adjust(top=0.86, bottom=0.13, hspace=0.35, wspace=0.28)
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved calibration/sharpness quadrant plot to: {out_path}")
