"""
IntelliDR Core Navigation and Sensor Fusion Engine
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
Team: Logic Legend2 (Team ID: 170889)
"""

from .coordinates import (
    geodetic_to_ecef,
    ecef_to_geodetic,
    geodetic_to_enu,
    enu_to_geodetic,
    haversine_distance,
    calculate_bearing,
    euler_to_rotation_matrix,
    quaternion_to_rotation_matrix,
    rotation_matrix_to_euler,
    euler_to_quaternion,
    quaternion_multiply,
)
from .sensor_types import (
    IMUSample,
    GNSSSample,
    VehicleState,
    AlignmentState,
    OutageState,
    FusionMode,
    MapMatchResult,
)

__all__ = [
    "geodetic_to_ecef",
    "ecef_to_geodetic",
    "geodetic_to_enu",
    "enu_to_geodetic",
    "haversine_distance",
    "calculate_bearing",
    "euler_to_rotation_matrix",
    "quaternion_to_rotation_matrix",
    "rotation_matrix_to_euler",
    "euler_to_quaternion",
    "quaternion_multiply",
    "IMUSample",
    "GNSSSample",
    "VehicleState",
    "AlignmentState",
    "OutageState",
    "FusionMode",
    "MapMatchResult",
]
