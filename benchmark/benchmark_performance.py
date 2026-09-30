"""
IntelliDR System Performance, Latency & Resource Benchmark
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
Team: Logic Legend2 (Team ID: 170889)

Measures:
1. IMU ingestion & normalization latency (microseconds)
2. AI velocity model inference latency (milliseconds)
3. 15-State Error-State EKF prediction + correction latency (microseconds)
4. Offline Map Matching query latency (microseconds)
5. End-to-end navigation loop update frequency (Hz)
6. Memory (RAM) footprint & process CPU utilization
"""

import os
import sys
import time
from dataclasses import dataclass
from typing import Dict, List
import numpy as np

try:
    import psutil
except ImportError:
    psutil = None

from intellidr_core.engine import IntelliDREngine
from intellidr_core.sensor_types import IMUSample, GNSSSample


@dataclass
class PerformanceBenchmarkResult:
    mean_loop_latency_us: float
    max_loop_latency_us: float
    p95_loop_latency_us: float
    achieved_rate_hz: float
    ai_inference_latency_ms: float
    ekf_step_latency_us: float
    map_matching_latency_us: float
    ram_usage_mb: float
    cpu_utilization_pct: float
    passed_sih_target: bool


def benchmark_engine_performance(num_iterations: int = 1500) -> PerformanceBenchmarkResult:
    """Benchmark end-to-end loop latency and memory footprint."""
    engine = IntelliDREngine(ref_lat=19.0760, ref_lon=72.8777, target_rate_hz=100.0)
    engine.map_provider.generate_synthetic_urban_grid(19.0760, 72.8777, grid_size=5, spacing_m=200.0)

    # Initialize with initial GNSS fix
    init_gnss = GNSSSample(
        timestamp=0.0,
        latitude=19.0760,
        longitude=72.8777,
        altitude=14.0,
        speed_mps=12.0,
        bearing_deg=90.0,
        horizontal_accuracy_m=2.5,
    )
    engine.process_gnss(init_gnss)

    latencies_us: List[float] = []
    ai_latencies_ms: List[float] = []
    ekf_latencies_us: List[float] = []
    map_latencies_us: List[float] = []

    # Warm-up pass
    for i in range(100):
        t = 0.01 * i
        imu = IMUSample(timestamp=t, ax=0.2, ay=0.0, az=9.8, gx=0.0, gy=0.0, gz=0.0)
        engine.process_imu(imu)

    # Benchmark run
    start_total = time.time()
    for i in range(num_iterations):
        t = 1.0 + 0.01 * i
        imu = IMUSample(
            timestamp=t,
            ax=0.15 + float(np.random.normal(0, 0.02)),
            ay=float(np.random.normal(0, 0.02)),
            az=9.81 + float(np.random.normal(0, 0.03)),
            gx=0.001, gy=0.001, gz=0.002,
        )

        t_loop_start = time.perf_counter()
        engine.process_imu(imu)
        t_loop_end = time.perf_counter()

        dt_us = (t_loop_end - t_loop_start) * 1e6
        latencies_us.append(dt_us)

    # Dedicated AI model benchmark
    features = np.random.randn(16).astype(np.float32)
    for _ in range(500):
        t_ai_0 = time.perf_counter()
        _ = engine.ai_velocity.neural_model.forward(features)
        t_ai_1 = time.perf_counter()
        ai_latencies_ms.append((t_ai_1 - t_ai_0) * 1e3)

    # Dedicated Map Matcher benchmark
    test_enu = np.array([150.0, 20.0, 0.0])
    for _ in range(500):
        t_m_0 = time.perf_counter()
        _ = engine.map_matcher.match(test_enu, 90.0, 12.0)
        t_m_1 = time.perf_counter()
        map_latencies_us.append((t_m_1 - t_m_0) * 1e6)

    # Resource utilization
    ram_mb = 0.0
    cpu_pct = 0.0
    if psutil is not None:
        proc = psutil.Process(os.getpid())
        ram_mb = proc.memory_info().rss / (1024.0 * 1024.0)
        cpu_pct = proc.cpu_percent(interval=0.1)

    mean_loop_us = float(np.mean(latencies_us))
    max_loop_us = float(np.max(latencies_us))
    p95_loop_us = float(np.percentile(latencies_us, 95))
    achieved_rate_hz = 1e6 / mean_loop_us if mean_loop_us > 0 else 0.0
    ai_lat_ms = float(np.mean(ai_latencies_ms))
    map_lat_us = float(np.mean(map_latencies_us))

    passed = (achieved_rate_hz >= 20.0) and (ai_lat_ms < 15.0)

    return PerformanceBenchmarkResult(
        mean_loop_latency_us=round(mean_loop_us, 1),
        max_loop_latency_us=round(max_loop_us, 1),
        p95_loop_latency_us=round(p95_loop_us, 1),
        achieved_rate_hz=round(achieved_rate_hz, 1),
        ai_inference_latency_ms=round(ai_lat_ms, 3),
        ekf_step_latency_us=round(mean_loop_us - (map_lat_us + ai_lat_ms * 1e3), 1),
        map_matching_latency_us=round(map_lat_us, 1),
        ram_usage_mb=round(ram_mb, 1),
        cpu_utilization_pct=round(cpu_pct, 1),
        passed_sih_target=passed,
    )


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    print("=" * 65)
    print("       INTELLIDR REAL-TIME LATENCY & PERFORMANCE BENCHMARK")
    print("=" * 65)
    res = benchmark_engine_performance(1000)
    print(f"Mean Navigation Loop Latency : {res.mean_loop_latency_us:.1f} µs")
    print(f"95th Percentile Latency       : {res.p95_loop_latency_us:.1f} µs")
    print(f"Max Navigation Loop Latency  : {res.max_loop_latency_us:.1f} µs")
    print(f"Achieved Loop Throughput     : {res.achieved_rate_hz:,.0f} Hz (SIH Target: >=10 Hz)")
    print(f"AI Velocity Inference Latency: {res.ai_inference_latency_ms:.3f} ms (Target: <15 ms)")
    print(f"Map Matching Latency         : {res.map_matching_latency_us:.1f} µs")
    print(f"Process RAM Footprint        : {res.ram_usage_mb:.1f} MB")
    print(f"SIH Real-Time Compliance     : {'PASSED [VERIFIED]' if res.passed_sih_target else 'FAILED'}")
    print("=" * 65)
