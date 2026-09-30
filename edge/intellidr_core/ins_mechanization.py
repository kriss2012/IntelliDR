"""
IntelliDR Inertial Navigation System (INS) Mechanization Engine
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
Team: Logic Legend2 (Team ID: 170889)

Implements rigorous inertial mechanization in Local East-North-Up (ENU) frame:
1. Quaternion-based attitude integration with closed-form rotational vector.
2. Gravity compensation in navigation frame (g_n = [0, 0, -9.80665] m/s^2).
3. Specific force rotation from Body to Navigation frame: f_n = R(q) * (f_b - b_a).
4. Velocity and displacement numerical integration with dt sanity limits.
"""

import math
from typing import Tuple
import numpy as np

from .coordinates import (
    quaternion_to_rotation_matrix,
    rotation_matrix_to_euler,
    quaternion_multiply,
)

# Standard terrestrial gravitational acceleration in ENU frame (m/s^2)
GRAVITY_ENU = np.array([0.0, 0.0, -9.80665], dtype=np.float64)


class INSMechanization:
    """Inertial Mechanization strapdown solver in Local ENU navigation frame."""

    def __init__(self, initial_position_enu: np.ndarray = None, initial_velocity_enu: np.ndarray = None):
        # Position in ENU [East, North, Up] in meters
        self.p_enu = np.zeros(3, dtype=np.float64) if initial_position_enu is None else np.array(initial_position_enu, dtype=np.float64)
        # Velocity in ENU [ve, vn, vu] in m/s
        self.v_enu = np.zeros(3, dtype=np.float64) if initial_velocity_enu is None else np.array(initial_velocity_enu, dtype=np.float64)
        # Unit quaternion [qw, qx, qy, qz] representing Body to ENU rotation
        self.q = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)
        
        # Sensor biases
        self.accel_bias = np.zeros(3, dtype=np.float64)
        self.gyro_bias = np.zeros(3, dtype=np.float64)

        # Stored previous acceleration in nav frame for trapezoidal integration
        self.last_a_nav = np.zeros(3, dtype=np.float64)

    def initialize_attitude(self, roll_rad: float, pitch_rad: float, yaw_rad: float):
        """Set initial attitude quaternion from known Euler angles."""
        from .coordinates import euler_to_quaternion
        self.q = euler_to_quaternion(roll_rad, pitch_rad, yaw_rad)

    def propagate(
        self,
        dt: float,
        accel_body: np.ndarray,
        gyro_body: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Step forward mechanization state over interval dt:
        - accel_body: [ax, ay, az] in m/s^2
        - gyro_body:  [gx, gy, gz] in rad/s
        Returns: (position_enu, velocity_enu, quaternion)
        """
        if dt <= 0.0 or dt > 0.5:
            # Reject anomalous dt
            return self.p_enu, self.v_enu, self.q

        # 1. Bias Correction
        f_b = accel_body - self.accel_bias
        w_b = gyro_body - self.gyro_bias

        # 2. Attitude Propagation via closed-form delta quaternion
        # Rotation vector delta_theta = w_b * dt
        delta_theta = w_b * dt
        angle = np.linalg.norm(delta_theta)

        if angle > 1e-12:
            half_angle = angle * 0.5
            sin_term = math.sin(half_angle) / angle
            dq = np.array([
                math.cos(half_angle),
                delta_theta[0] * sin_term,
                delta_theta[1] * sin_term,
                delta_theta[2] * sin_term
            ], dtype=np.float64)
        else:
            dq = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)

        # Update quaternion: q = q * dq
        self.q = quaternion_multiply(self.q, dq)
        self.q /= (np.linalg.norm(self.q) + 1e-12)

        # 3. Transform specific force to Navigation (ENU) frame
        r_b2n = quaternion_to_rotation_matrix(self.q)
        f_nav = r_b2n @ f_b

        # 4. Total Acceleration in Navigation Frame: a_nav = f_nav + g_enu
        a_nav = f_nav + GRAVITY_ENU

        # 5. Velocity and Position Integration (Trapezoidal)
        v_next = self.v_enu + 0.5 * (self.last_a_nav + a_nav) * dt
        p_next = self.p_enu + self.v_enu * dt + 0.25 * (self.last_a_nav + a_nav) * (dt ** 2)

        self.v_enu = v_next
        self.p_enu = p_next
        self.last_a_nav = a_nav

        return self.p_enu, self.v_enu, self.q

    def get_euler_angles(self) -> Tuple[float, float, float]:
        """Return (roll, pitch, yaw) in radians in navigation frame."""
        r_b2n = quaternion_to_rotation_matrix(self.q)
        return rotation_matrix_to_euler(r_b2n)
