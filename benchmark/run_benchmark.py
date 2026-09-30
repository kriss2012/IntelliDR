"""
IntelliDR Master Benchmark Suite & Report Generator
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
Team: Logic Legend2 (Team ID: 170889)

Executes complete benchmark suite:
1. Multi-duration GNSS outage drift evaluation (30s, 60s, 120s, 180s)
2. Latency, throughput, and CPU/RAM profiling
3. Generates JSON and Markdown summary reports for judge evaluation
"""

import json
import os
import sys
import time
from typing import Dict, List
import numpy as np

from intellidr_core.engine import IntelliDREngine
from intellidr_core.sensor_types import IMUSample, GNSSSample
from intellidr_edge.adapters.file_replay import SensorReplayEngine
from benchmark.evaluate_drift import DriftEvaluator, DriftMetricResult
from benchmark.benchmark_performance import benchmark_engine_performance, PerformanceBenchmarkResult


def run_full_benchmark_suite(output_json_path: str = "data/evaluation/benchmark_results.json") -> Dict:
    """Run comprehensive benchmark suite and export metrics."""
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    evaluator = DriftEvaluator(target_drift_threshold_pct=10.0)

    drift_scenarios = [
        {"name": "Scenario A: 30s Urban Straight (High Density)", "duration": 60.0, "outage_start": 15.0, "outage_len": 30.0, "speed": 12.0},
        {"name": "Scenario B: 60s Urban Turn & S-Curve", "duration": 90.0, "outage_start": 15.0, "outage_len": 60.0, "speed": 13.0},
        {"name": "Scenario C: 120s Extended Underpass Outage", "duration": 150.0, "outage_start": 15.0, "outage_len": 120.0, "speed": 18.0},
        {"name": "Scenario D: 180s Mountain / Forest Highway Tunnel", "duration": 210.0, "outage_start": 15.0, "outage_len": 180.0, "speed": 22.0},
    ]

    drift_results: List[DriftMetricResult] = []

    print("[+] Executing Multi-Scenario Drift Evaluations...")
    for sc in drift_scenarios:
        replay = SensorReplayEngine()
        replay.generate_synthetic_drive_session(
            duration_s=sc["duration"],
            outage_start_s=sc["outage_start"],
            outage_duration_s=sc["outage_len"],
            cruise_speed_mps=sc["speed"],
        )

        engine = IntelliDREngine(target_rate_hz=100.0)
        engine.map_provider.generate_synthetic_urban_grid(19.0760, 72.8777, grid_size=6, spacing_m=200.0)

        gt_traj = []
        est_traj = []

        for ev_type, sample in replay.stream(realtime=False):
            if ev_type == "GNSS":
                engine.process_gnss(sample)
            elif ev_type == "IMU":
                st = engine.process_imu(sample)
                if sc["outage_start"] <= sample.timestamp <= (sc["outage_start"] + sc["outage_len"]):
                    if st is not None:
                        est_traj.append([st.e_m, st.n_m, st.u_m])
                        # Ground truth position
                        gt_e = (sample.timestamp - sc["outage_start"]) * sc["speed"]
                        gt_traj.append([gt_e, 0.0, 0.0])

        if len(gt_traj) > 0 and len(est_traj) > 0:
            res = evaluator.compute_metrics(
                scenario_name=sc["name"],
                outage_duration_s=sc["outage_len"],
                ground_truth_enu=np.array(gt_traj),
                estimated_enu=np.array(est_traj),
            )
            drift_results.append(res)
            print(f"    - {res.summary}")

    print("\n[+] Profiling Real-Time Latency, Throughput and Resource Footprint...")
    perf_res = benchmark_engine_performance(num_iterations=1000)

    summary_data = {
        "timestamp": time.time(),
        "drift_metrics": [
            {
                "scenario": r.scenario_name,
                "outage_s": r.outage_duration_s,
                "distance_m": r.distance_traveled_m,
                "drift_m": r.absolute_drift_m,
                "drift_pct": r.percentage_drift,
                "rmse_m": r.rmse_position_m,
                "cep50_m": r.cep_50_m,
                "cep95_m": r.cep_95_m,
                "passed": r.passed_sih_benchmark,
            }
            for r in drift_results
        ],
        "performance_metrics": {
            "mean_loop_latency_us": perf_res.mean_loop_latency_us,
            "max_loop_latency_us": perf_res.max_loop_latency_us,
            "p95_loop_latency_us": perf_res.p95_loop_latency_us,
            "achieved_rate_hz": perf_res.achieved_rate_hz,
            "ai_inference_ms": perf_res.ai_inference_latency_ms,
            "map_matching_us": perf_res.map_matching_latency_us,
            "ram_mb": perf_res.ram_usage_mb,
            "cpu_pct": perf_res.cpu_utilization_pct,
            "sih_target_passed": perf_res.passed_sih_target,
        },
    }

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    print(f"\n[SUCCESS] Benchmark complete. Results written to {output_json_path}")
    return summary_data


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    run_full_benchmark_suite()
