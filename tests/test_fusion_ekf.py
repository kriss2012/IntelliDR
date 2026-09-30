"""
Unit Tests for 15-State Error-State EKF Fusion Engine
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
"""

import math
import numpy as np
import pytest

from intellidr_core.fusion_ekf import ErrorStateEKF


def test_ekf_prediction_and_covariance_growth():
    ekf = ErrorStateEKF()
    ekf.initialize(np.array([0.0, 0.0, 0.0]), np.array([10.0, 0.0, 0.0]), 0.0)

    initial_pos_var = ekf.P[0, 0]

    # Predict 50 steps
    for _ in range(50):
        ekf.predict(0.01, np.array([0.0, 0.0, 9.80665]), np.array([0.0, 0.0, 0.0]))

    # Without GNSS updates, covariance must grow
    assert ekf.P[0, 0] > initial_pos_var
    assert ekf.p_enu[0] > 0.0  # Vehicle moved forward East


def test_ekf_gnss_position_update():
    ekf = ErrorStateEKF()
    ekf.initialize(np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, 0.0]), 0.0)

    # Inject position offset
    gnss_pos = np.array([15.0, 25.0, 0.0])
    ekf.update_gnss_position(gnss_pos, std_dev=2.0)

    # Estimated position must pull towards GNSS measurement
    assert ekf.p_enu[0] > 10.0
    assert ekf.p_enu[1] > 18.0
    # Covariance must shrink
    assert ekf.P[0, 0] < 25.0


def test_ekf_nhc_and_zupt_updates():
    ekf = ErrorStateEKF()
    ekf.initialize(np.array([0.0, 0.0, 0.0]), np.array([12.0, 4.0, 2.0]), 0.0)

    # Lateral and vertical speed exist (slip anomaly)
    ekf.update_nhc(std_lat=0.10, std_vert=0.10)

    # Lateral (Y) and Vertical (Z) velocity should be suppressed
    assert abs(ekf.v_enu[1]) < 3.5
    assert abs(ekf.v_enu[2]) < 1.8

    # Apply ZUPT
    ekf.update_zupt(std_vel=0.05)
    assert np.linalg.norm(ekf.v_enu) < 1.0
