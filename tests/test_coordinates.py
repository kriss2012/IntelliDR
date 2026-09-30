"""
Unit Tests for Geodetic and Attitude Transformations
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
"""

import math
import numpy as np
import pytest

from intellidr_core.coordinates import (
    geodetic_to_ecef,
    ecef_to_geodetic,
    geodetic_to_enu,
    enu_to_geodetic,
    haversine_distance,
    calculate_bearing,
    euler_to_quaternion,
    quaternion_to_rotation_matrix,
    rotation_matrix_to_euler,
    quaternion_multiply,
)


def test_geodetic_ecef_roundtrip():
    lat, lon, alt = 19.0760, 72.8777, 14.5
    x, y, z = geodetic_to_ecef(lat, lon, alt)
    r_lat, r_lon, r_alt = ecef_to_geodetic(x, y, z)

    assert abs(r_lat - lat) < 1e-6
    assert abs(r_lon - lon) < 1e-6
    assert abs(r_alt - alt) < 1e-2


def test_enu_roundtrip():
    ref_lat, ref_lon, ref_alt = 19.0760, 72.8777, 10.0
    target_lat = ref_lat + 0.005  # ~555m North
    target_lon = ref_lon + 0.005  # ~525m East
    target_alt = 15.0

    e, n, u = geodetic_to_enu(target_lat, target_lon, target_alt, ref_lat, ref_lon, ref_alt)
    r_lat, r_lon, r_alt = enu_to_geodetic(e, n, u, ref_lat, ref_lon, ref_alt)

    assert abs(r_lat - target_lat) < 1e-6
    assert abs(r_lon - target_lon) < 1e-6
    assert abs(r_alt - target_alt) < 1e-2
    assert e > 0
    assert n > 0


def test_haversine_and_bearing():
    # Mumbai to Pune
    lat1, lon1 = 19.0760, 72.8777
    lat2, lon2 = 18.5204, 73.8567
    dist = haversine_distance(lat1, lon1, lat2, lon2)
    bearing = calculate_bearing(lat1, lon1, lat2, lon2)

    assert 115000 < dist < 125000  # ~120 km
    assert 110 < bearing < 130    # Southeast direction


def test_attitude_conversions():
    roll = math.radians(12.0)
    pitch = math.radians(-8.0)
    yaw = math.radians(45.0)

    q = euler_to_quaternion(roll, pitch, yaw)
    assert abs(np.linalg.norm(q) - 1.0) < 1e-6

    R = quaternion_to_rotation_matrix(q)
    assert np.allclose(R @ R.T, np.eye(3), atol=1e-6)

    r_roll, r_pitch, r_yaw = rotation_matrix_to_euler(R)
    assert abs(r_roll - roll) < 1e-4
    assert abs(r_pitch - pitch) < 1e-4
    assert abs(r_yaw - yaw) < 1e-4
