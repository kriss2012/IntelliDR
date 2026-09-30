"""
Unit Tests for Phone-to-Vehicle Alignment & Calibration Engine
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
"""

import math
import numpy as np
import pytest

from intellidr_core.alignment import AlignmentEngine
from intellidr_core.sensor_types import IMUSample


def test_gravity_alignment_lock():
    engine = AlignmentEngine(min_calibration_samples=50)

    # Simulate phone sitting flat on dashboard: gravity down along phone Z (9.81 m/s^2)
    for i in range(70):
        t = i * 0.01
        imu = IMUSample(timestamp=t, ax=0.01, ay=0.02, az=9.81, gx=0.001, gy=0.001, gz=0.001)
        state = engine.update(imu)

    assert state.confidence >= 0.40
    # Gravity unit vector points along Z
    assert abs(engine.v_z_phone[2] - (-1.0)) < 0.1 or abs(engine.v_z_phone[2] - 1.0) < 0.1


def test_forward_acceleration_calibration():
    engine = AlignmentEngine(min_calibration_samples=50)

    # 1. First lock gravity
    for i in range(60):
        imu = IMUSample(timestamp=i * 0.01, ax=0.0, ay=0.0, az=9.81, gx=0.0, gy=0.0, gz=0.0)
        engine.update(imu)

    # 2. Vehicle accelerates forward along phone X (1.5 m/s^2)
    for i in range(60, 150):
        imu = IMUSample(timestamp=i * 0.01, ax=1.5, ay=0.0, az=9.81, gx=0.0, gy=0.0, gz=0.0)
        state = engine.update(imu, gnss_speed_mps=10.0)

    assert state.confidence >= 0.80
    assert state.is_calibrated
