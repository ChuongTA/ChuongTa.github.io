"""
Visualizes the Step 4 "combine calibration and sharpness" verdict table
from Section 3.1, using the exact coverage/width numbers already
published in the Section 3 results tables. No model refit needed, this
is purely a plot of numbers already in the post.

Each point is (mean interval width, empirical coverage) for one model at
one nominal interval level (80/90/95%), for one lead time.
"""
import os
from forecasting_plots import plot_calibration_sharpness_quadrant

script_dir = os.path.dirname(os.path.abspath(__file__))

# (width, empirical_coverage, nominal_coverage) per model, per lead time.
# Copied directly from the Section 3 results table.
RESULTS = {
    "1h ahead": {
        "QR":  [(38.2, 0.815, 0.80), (54.2, 0.910, 0.90), (68.1, 0.955, 0.95)],
        "QRF": [(31.4, 0.862, 0.80), (43.8, 0.926, 0.90), (56.1, 0.965, 0.95)],
    },
    "6h ahead": {
        "QR":  [(58.5, 0.735, 0.80), (77.9, 0.809, 0.90), (97.1, 0.868, 0.95)],
        "QRF": [(48.0, 0.727, 0.80), (65.2, 0.844, 0.90), (83.3, 0.919, 0.95)],
    },
    "12h ahead": {
        "QR":  [(59.5, 0.738, 0.80), (76.0, 0.802, 0.90), (94.3, 0.855, 0.95)],
        "QRF": [(47.9, 0.726, 0.80), (65.1, 0.851, 0.90), (82.7, 0.927, 0.95)],
    },
    "24h ahead": {
        "QR":  [(56.8, 0.721, 0.80), (74.7, 0.820, 0.90), (94.0, 0.889, 0.95)],
        "QRF": [(48.9, 0.781, 0.80), (65.7, 0.898, 0.90), (82.8, 0.952, 0.95)],
    },
}

out_path = os.path.join(script_dir, "QRQRF_calibration_sharpness_quadrant.png")
plot_calibration_sharpness_quadrant(RESULTS, out_path)
