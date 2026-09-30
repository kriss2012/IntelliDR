"""
IntelliDR Coordinate Transformations & Geodetic Utilities
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
Team: Logic Legend2 (Team ID: 170889)

Provides high-precision transformations between:
- Geodetic (WGS84 Latitude, Longitude, Altitude)
- Earth-Centered, Earth-Fixed (ECEF)
- Local East-North-Up (ENU) navigation frame
- North-East-Down (NED) navigation frame
- Body (B) and Vehicle (V) coordinate frames via Quaternions / DCM
"""

import math
from typing import Tuple, Union
import numpy as np

# WGS84 Ellipsoid Constants
WGS84_A = 6378137.0          # Semi-major axis in meters
WGS84_F = 1.0 / 298.257223563 # Flattening
WGS84_B = WGS84_A * (1.0 - WGS84_F) # Semi-minor axis in meters
WGS84_E2 = 2.0 * WGS84_F - (WGS84_F ** 2) # First eccentricity squared
WGS84_E_PRIME2 = (WGS84_A**2 - WGS84_B**2) / (WGS84_B**2) # Second eccentricity squared


def geodetic_to_ecef(lat_deg: float, lon_deg: float, alt_m: float = 0.0) -> Tuple[float, float, float]:
    """Convert WGS84 Geodetic coordinates (lat, lon, alt) to ECEF (X, Y, Z) in meters."""
    phi = math.radians(lat_deg)
    lam = math.radians(lon_deg)
    
    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)
    sin_lam = math.sin(lam)
    cos_lam = math.cos(lam)
    
    # Prime vertical radius of curvature
    n = WGS84_A / math.sqrt(1.0 - WGS84_E2 * (sin_phi ** 2))
    
    x = (n + alt_m) * cos_phi * cos_lam
    y = (n + alt_m) * cos_phi * sin_lam
    z = (n * (1.0 - WGS84_E2) + alt_m) * sin_phi
    return x, y, z


def ecef_to_geodetic(x: float, y: float, z: float) -> Tuple[float, float, float]:
    """Convert ECEF (X, Y, Z) coordinates in meters to WGS84 Geodetic (lat, lon, alt)."""
    p = math.hypot(x, y)
    if p < 1e-6:
        # Near poles
        lat = 90.0 if z > 0 else -90.0
        alt = abs(z) - WGS84_B
        return lat, 0.0, alt

    theta = math.atan2(z * WGS84_A, p * WGS84_B)
    sin_theta = math.sin(theta)
    cos_theta = math.cos(theta)
    
    phi = math.atan2(
        z + WGS84_E_PRIME2 * WGS84_B * (sin_theta ** 3),
        p - WGS84_E2 * WGS84_A * (cos_theta ** 3)
    )
    lam = math.atan2(y, x)
    
    sin_phi = math.sin(phi)
    n = WGS84_A / math.sqrt(1.0 - WGS84_E2 * (sin_phi ** 2))
    alt = (p / math.cos(phi)) - n
    
    return math.degrees(phi), math.degrees(lam), alt


def geodetic_to_enu(
    lat_deg: float, lon_deg: float, alt_m: float,
    ref_lat_deg: float, ref_lon_deg: float, ref_alt_m: float
) -> Tuple[float, float, float]:
    """Convert WGS84 geodetic position to local East-North-Up (ENU) frame relative to reference origin."""
    x, y, z = geodetic_to_ecef(lat_deg, lon_deg, alt_m)
    x0, y0, z0 = geodetic_to_ecef(ref_lat_deg, ref_lon_deg, ref_alt_m)
    
    dx = x - x0
    dy = y - y0
    dz = z - z0
    
    phi = math.radians(ref_lat_deg)
    lam = math.radians(ref_lon_deg)
    
    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)
    sin_lam = math.sin(lam)
    cos_lam = math.cos(lam)
    
    # Rotation matrix from ECEF to local ENU
    e = -sin_lam * dx + cos_lam * dy
    n = -sin_phi * cos_lam * dx - sin_phi * sin_lam * dy + cos_phi * dz
    u = cos_phi * cos_lam * dx + cos_phi * sin_lam * dy + sin_phi * dz
    return e, n, u


def enu_to_geodetic(
    e: float, n: float, u: float,
    ref_lat_deg: float, ref_lon_deg: float, ref_alt_m: float
) -> Tuple[float, float, float]:
    """Convert local East-North-Up (ENU) coordinates to WGS84 geodetic coordinates."""
    x0, y0, z0 = geodetic_to_ecef(ref_lat_deg, ref_lon_deg, ref_alt_m)
    
    phi = math.radians(ref_lat_deg)
    lam = math.radians(ref_lon_deg)
    
    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)
    sin_lam = math.sin(lam)
    cos_lam = math.cos(lam)
    
    dx = -sin_lam * e - sin_phi * cos_lam * n + cos_phi * cos_lam * u
    dy = cos_lam * e - sin_phi * sin_lam * n + cos_phi * sin_lam * u
    dz = cos_phi * n + sin_phi * u
    
    return ecef_to_geodetic(x0 + dx, y0 + dy, z0 + dz)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two points on Earth in meters."""
    r = 6371000.0 # Earth mean radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lam = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi / 2.0) ** 2) + \
        math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lam / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate forward azimuth / bearing from point 1 to point 2 in degrees [0, 360)."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lam = math.radians(lon2 - lon1)
    
    y = math.sin(delta_lam) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lam)
    bearing = math.degrees(math.atan2(y, x))
    return (bearing + 360.0) % 360.0


# -------------------------------------------------------------
# Attitude, Quaternion and Rotation Matrix Conversions
# -------------------------------------------------------------

def euler_to_rotation_matrix(roll: float, pitch: float, yaw: float) -> np.ndarray:
    """
    Construct 3x3 rotation matrix R from Body to Navigation frame (Z-Y-X convention).
    Angles in radians: roll (phi), pitch (theta), yaw (psi).
    R_b_to_n = Rz(yaw) * Ry(pitch) * Rx(roll)
    """
    cr = math.cos(roll)
    sr = math.sin(roll)
    cp = math.cos(pitch)
    sp = math.sin(pitch)
    cy = math.cos(yaw)
    sy = math.sin(yaw)
    
    r = np.array([
        [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
        [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
        [-sp,     cp * sr,                cp * cr]
    ], dtype=np.float64)
    return r


def quaternion_to_rotation_matrix(q: np.ndarray) -> np.ndarray:
    """
    Convert unit quaternion q = [qw, qx, qy, qz] to 3x3 direction cosine matrix R.
    Maps vector from Body frame to Navigation frame: v_n = R * v_b.
    """
    qw, qx, qy, qz = q[0], q[1], q[2], q[3]
    
    # Normalization safeguard
    norm = math.sqrt(qw*qw + qx*qx + qy*qy + qz*qz)
    if norm > 1e-12:
        qw /= norm
        qx /= norm
        qy /= norm
        qz /= norm
        
    return np.array([
        [1.0 - 2.0*(qy**2 + qz**2), 2.0*(qx*qy - qz*qw),       2.0*(qx*qz + qy*qw)],
        [2.0*(qx*qy + qz*qw),       1.0 - 2.0*(qx**2 + qz**2), 2.0*(qy*qz - qx*qw)],
        [2.0*(qx*qz - qy*qw),       2.0*(qy*qz + qx*qw),       1.0 - 2.0*(qx**2 + qy**2)]
    ], dtype=np.float64)


def rotation_matrix_to_euler(r: np.ndarray) -> Tuple[float, float, float]:
    """
    Extract Euler angles (roll, pitch, yaw) in radians from rotation matrix R_b_to_n.
    Z-Y-X sequence.
    """
    pitch = -math.asin(np.clip(r[2, 0], -1.0, 1.0))
    if abs(math.cos(pitch)) > 1e-6:
        roll = math.atan2(r[2, 1], r[2, 2])
        yaw = math.atan2(r[1, 0], r[0, 0])
    else:
        # Gimbal lock at pitch = +-90 deg
        roll = 0.0
        yaw = math.atan2(-r[0, 1], r[1, 1])
    return roll, pitch, (yaw + 2.0 * math.pi) % (2.0 * math.pi)


def euler_to_quaternion(roll: float, pitch: float, yaw: float) -> np.ndarray:
    """Convert Euler angles (radians) to unit quaternion q = [qw, qx, qy, qz]."""
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    
    qw = cr * cp * cy + sr * sp * sy
    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy
    return np.array([qw, qx, qy, qz], dtype=np.float64)


def quaternion_multiply(q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
    """Hamiltonian quaternion product q = q1 * q2."""
    w1, x1, y1, z1 = q1[0], q1[1], q1[2], q1[3]
    w2, x2, y2, z2 = q2[0], q2[1], q2[2], q2[3]
    
    w = w1*w2 - x1*x2 - y1*y2 - z1*z2
    x = w1*x2 + x1*w2 + y1*z2 - z1*y2
    y = w1*y2 - x1*z2 + y1*w2 + z1*x2
    z = w1*z2 + x1*y2 - y1*x2 + z1*w2
    return np.array([w, x, y, z], dtype=np.float64)
