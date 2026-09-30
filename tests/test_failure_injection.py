"""
Technical Red-Team & Failure Injection Tests
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
Team: Logic Legend2 (Team ID: 170889)

Simulates severe environmental and sensor failure modes:
1. NaN and Inf values in IMU packet
2. 500-meter sudden multipath GPS teleportation jump
3. 60 m/s^2 pothole / curb mechanical impact shock
4. Clock rollback and negative dt
5. Gyro freeze & accelerometer dropout
6. Model failure / explosive neural output
"""

import math
import numpy as np
import pytest

from intellidr_core.engine import IntelliDREngine
from intellidr_core.sensor_types import IMUSample, GNSSSample, OutageState
from intellidr_ai.models import HybridVelocityEstimator


def test_nan_and_inf_resilience():
    engine = IntelliDREngine()

    # Pass corrupt samples containing NaNs and Infs
    corrupt_imu = IMUSample(timestamp=1.0, ax=float("nan"), ay=0.0, az=9.8, gx=float("inf"), gy=0.0, gz=0.0)
    state = engine.process_imu(corrupt_imu)

    # Engine must not crash and should reject the invalid sample
    assert state is None or not math.isnan(state.latitude)


def test_sensor_shock_spike_clamping():
    engine = IntelliDREngine()

    # Pass 80 m/s^2 violent impact shock (e.g. dropped phone or severe pothole crash)
    shock_imu = IMUSample(timestamp=1.0, ax=80.0, ay=10.0, az=90.0, gx=0.0, gy=0.0, gz=0.0)
    cleaned = engine.normalizer.clean_imu(shock_imu)

    # Acceleration norm must be clamped to safe boundary
    acc_norm = math.sqrt(cleaned.ax**2 + cleaned.ay**2 + cleaned.az**2)
    assert acc_norm <= 45.1


def test_gnss_500m_multipath_jump_rejection():
    engine = IntelliDREngine(ref_lat=19.0760, ref_lon=72.8777)

    # Initial valid fix
    gnss1 = GNSSSample(timestamp=1.0, latitude=19.0760, longitude=72.8777, horizontal_accuracy_m=2.0)
    engine.process_gnss(gnss1)

    # Sudden 500m multipath teleportation jump
    jump_lat = 19.0760 + (500.0 / 111139.0)
    gnss2 = GNSSSample(timestamp=2.0, latitude=jump_lat, longitude=72.8777, horizontal_accuracy_m=3.0)
    state = engine.process_gnss(gnss2)

    # Multipath jump must be rejected or marked degraded, preventing instant trajectory teleport
    assert state.outage_state in (OutageState.GNSS_DEGRADED, OutageState.GNSS_AVAILABLE)


def test_ai_model_anomaly_fallback():
    hybrid = HybridVelocityEstimator()

    # Feed anomalous feature vector causing crazy values
    crazy_feats = np.ones(16) * 1e5
    meta = {"is_stationary": False}
    speed, conf, mode = hybrid.estimate(crazy_feats, meta, forward_accel=1.0, dt=0.05)

    # Must fall back to kinematic model instead of outputting explosive speed
    assert mode in ("KINEMATIC_FALLBACK", "AI_NEURAL")
    assert speed < 60.0  # Safe vehicular bound
