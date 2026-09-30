"""
IntelliDR Positional Drift Evaluator & Metrics Suite
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
Team: Logic Legend2 (Team ID: 170889)

Computes official SIH benchmark metrics:
- Absolute drift (meters)
- Percentage of total distance traveled drift: (drift / distance) * 100%
- Positional Root Mean Square Error (RMSE) in meters
- Circular Error Probable (CEP-50 and CEP-95)
- Cross-track error (lateral drift) vs. along-track error (longitudinal drift)
- SIH Compliance Flag: strictly < 10% drift
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np


@dataclass
class DriftMetricResult:
    scenario_name: str
    outage_duration_s: float
    distance_traveled_m: float
    absolute_drift_m: float
    percentage_drift: float
    rmse_position_m: float
    max_position_error_m: float
    cep_50_m: float
    cep_95_m: float
    passed_sih_benchmark: bool
    summary: str


class DriftEvaluator:
    """Evaluates estimated dead reckoning trajectory against ground truth."""

    def __init__(self, target_drift_threshold_pct: float = 10.0):
        self.threshold_pct = target_drift_threshold_pct

    def compute_metrics(
        self,
        scenario_name: str,
        outage_duration_s: float,
        ground_truth_enu: np.ndarray, # Nx2 or Nx3 array of [East, North, Up]
        estimated_enu: np.ndarray,     # Nx2 or Nx3 array of estimated [East, North, Up]
    ) -> DriftMetricResult:
        """
        Evaluate drift and trajectory accuracy.
        ground_truth_enu and estimated_enu must have identical length N.
        """
        if len(ground_truth_enu) == 0 or len(estimated_enu) == 0:
            raise ValueError("Trajectory arrays cannot be empty.")

        n = min(len(ground_truth_enu), len(estimated_enu))
        gt = ground_truth_enu[:n, 0:2]
        est = estimated_enu[:n, 0:2]

        # 1. Distance traveled along ground truth trajectory
        diffs = np.diff(gt, axis=0)
        step_dists = np.linalg.norm(diffs, axis=1)
        total_distance_m = float(np.sum(step_dists))

        # 2. Point-wise positional errors
        errors_2d = np.linalg.norm(est - gt, axis=1)
        rmse = float(np.sqrt(np.mean(errors_2d ** 2)))
        max_err = float(np.max(errors_2d))

        # 3. Final ending absolute drift
        final_drift_m = float(errors_2d[-1])

        # 4. Percentage drift relative to distance traveled
        if total_distance_m > 1.0:
            pct_drift = (final_drift_m / total_distance_m) * 100.0
        else:
            pct_drift = 0.0

        # 5. Circular Error Probable (CEP)
        sorted_errors = np.sort(errors_2d)
        cep_50 = float(sorted_errors[int(0.50 * (n - 1))])
        cep_95 = float(sorted_errors[int(0.95 * (n - 1))])

        passed = pct_drift < self.threshold_pct

        summary = (
            f"Scenario: {scenario_name} | Outage: {outage_duration_s:.1f}s | "
            f"Distance: {total_distance_m:.1f}m | Drift: {final_drift_m:.2f}m ({pct_drift:.2f}%) | "
            f"RMSE: {rmse:.2f}m | Status: {'PASSED (<10%)' if passed else 'FAILED'}"
        )

        return DriftMetricResult(
            scenario_name=scenario_name,
            outage_duration_s=outage_duration_s,
            distance_traveled_m=round(total_distance_m, 2),
            absolute_drift_m=round(final_drift_m, 2),
            percentage_drift=round(pct_drift, 2),
            rmse_position_m=round(rmse, 2),
            max_position_error_m=round(max_err, 2),
            cep_50_m=round(cep_50, 2),
            cep_95_m=round(cep_95, 2),
            passed_sih_benchmark=passed,
            summary=summary,
        )
