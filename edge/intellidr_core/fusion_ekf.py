"""
IntelliDR 15-State Error-State Extended Kalman Filter (ES-EKF)
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
Team: Logic Legend2 (Team ID: 170889)

Implements Loosely-Coupled and AI-Assisted INS/GNSS Fusion:
- Error State Vector (15 elements):
  delta_x = [delta_p (3), delta_v (3), delta_psi (3), delta_ba (3), delta_bg (3)]
- Continuous-time error propagation with covariance update:
  P = F * P * F^T + Q
- Multi-source measurement updates:
  1. GNSS Position (East, North, Up)
  2. GNSS Velocity (Ve, Vn, Vu)
  3. AI Forward Velocity (Vehicle longitudinal axis)
  4. Non-Holonomic Constraints (NHC: Lateral & Vertical velocity = 0)
  5. Zero Velocity Update (ZUPT when vehicle is stationary)
- Closed-loop error feedback to nominal INS mechanization states
"""

import math
from typing import Optional, Tuple
import numpy as np

from .coordinates import (
    quaternion_to_rotation_matrix,
    euler_to_quaternion,
    quaternion_multiply,
    rotation_matrix_to_euler,
)
from .sensor_types import OutageState, FusionMode


def skew_symmetric(v: np.ndarray) -> np.ndarray:
    """Return 3x3 skew-symmetric matrix [v]x for cross products."""
    return np.array([
        [0.0, -v[2], v[1]],
        [v[2], 0.0, -v[0]],
        [-v[1], v[0], 0.0]
    ], dtype=np.float64)


class ErrorStateEKF:
    """15-State Error-State Extended Kalman Filter for robust GNSS/INS fusion."""

    def __init__(self):
        # Nominal state
        self.p_enu = np.zeros(3, dtype=np.float64)      # [East, North, Up] in meters
        self.v_enu = np.zeros(3, dtype=np.float64)      # [Ve, Vn, Vu] in m/s
        self.q = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64) # Attitude quaternion
        self.accel_bias = np.zeros(3, dtype=np.float64) # m/s^2
        self.gyro_bias = np.zeros(3, dtype=np.float64)  # rad/s

        # Covariance matrix P (15x15)
        self.P = np.eye(15, dtype=np.float64)
        # Position variance (5m initial standard deviation)
        self.P[0:3, 0:3] *= 25.0
        # Velocity variance (1m/s initial standard deviation)
        self.P[3:6, 3:6] *= 1.0
        # Attitude variance (rad^2, ~5 degrees initial error)
        self.P[6:9, 6:9] *= (math.radians(5.0) ** 2)
        # Accel bias variance (0.05 m/s^2)
        self.P[9:12, 9:12] *= (0.05 ** 2)
        # Gyro bias variance (0.005 rad/s)
        self.P[12:15, 12:15] *= (0.005 ** 2)

        # Continuous process noise spectral densities
        self.q_accel_noise = 0.05       # m/s^2 / sqrt(Hz)
        self.q_gyro_noise = 0.005       # rad/s / sqrt(Hz)
        self.q_accel_bias_walk = 1e-4   # m/s^3 / sqrt(Hz)
        self.q_gyro_bias_walk = 1e-5    # rad/s^2 / sqrt(Hz)

        # Process noise covariance Q (15x15)
        self.Q = np.zeros((15, 15), dtype=np.float64)
        self.Q[3:6, 3:6] = np.eye(3) * (self.q_accel_noise ** 2)
        self.Q[6:9, 6:9] = np.eye(3) * (self.q_gyro_noise ** 2)
        self.Q[9:12, 9:12] = np.eye(3) * (self.q_accel_bias_walk ** 2)
        self.Q[12:15, 12:15] = np.eye(3) * (self.q_gyro_bias_walk ** 2)

    def initialize(self, p_enu: np.ndarray, v_enu: np.ndarray, yaw_rad: float):
        """Seed initial filter state."""
        self.p_enu = np.array(p_enu, dtype=np.float64)
        self.v_enu = np.array(v_enu, dtype=np.float64)
        self.q = euler_to_quaternion(0.0, 0.0, yaw_rad)
        self.accel_bias = np.zeros(3, dtype=np.float64)
        self.gyro_bias = np.zeros(3, dtype=np.float64)

    def predict(self, dt: float, accel_body: np.ndarray, gyro_body: np.ndarray):
        """
        EKF Prediction step:
        1. Propagate nominal state using INS mechanization.
        2. Formulate state transition Jacobian F (15x15).
        3. Propagate error covariance P = F * P * F^T + Q * dt.
        """
        if dt <= 0.0 or dt > 0.5:
            return

        # Correct sensor measurements with current bias estimates
        f_b = accel_body - self.accel_bias
        w_b = gyro_body - self.gyro_bias

        r_b2n = quaternion_to_rotation_matrix(self.q)
        # 1. Propagate nominal attitude quaternion
        rot_angle = np.linalg.norm(w_b * dt)
        if rot_angle > 1e-12:
            half = rot_angle * 0.5
            s = math.sin(half) / rot_angle
            dq = np.array([math.cos(half), w_b[0] * dt * s, w_b[1] * dt * s, w_b[2] * dt * s])
            self.q = quaternion_multiply(self.q, dq)
            self.q /= np.linalg.norm(self.q)

        # 2. Transform specific force and propagate nominal velocity and position
        r_b2n = quaternion_to_rotation_matrix(self.q)
        f_n = r_b2n @ f_b
        a_nav = f_n + np.array([0.0, 0.0, -9.80665])
        self.v_enu += a_nav * dt
        self.p_enu += self.v_enu * dt

        # 3. State transition matrix F (15x15 discrete approx: I + F_c * dt)
        F = np.eye(15, dtype=np.float64)
        # d(p)/d(v) = I * dt
        F[0:3, 3:6] = np.eye(3) * dt
        # d(v)/d(psi) = -[f_n]x * dt
        F[3:6, 6:9] = -skew_symmetric(f_n) * dt
        # d(v)/d(ba) = -R_b2n * dt
        F[3:6, 9:12] = -r_b2n * dt
        # d(psi)/d(bg) = -R_b2n * dt
        F[6:9, 12:15] = -r_b2n * dt

        # 2. Covariance propagation
        self.P = F @ self.P @ F.T + self.Q * dt
        # Ensure symmetry
        self.P = 0.5 * (self.P + self.P.T)

    def update_measurement(self, H: np.ndarray, residual: np.ndarray, R: np.ndarray):
        """
        Generic Kalman measurement update:
        K = P * H^T * (H * P * H^T + R)^(-1)
        delta_x = K * residual
        P = (I - K * H) * P
        Inject error state into nominal state and reset delta_x to 0.
        """
        S = H @ self.P @ H.T + R
        try:
            K = self.P @ H.T @ np.linalg.inv(S)
        except np.linalg.LinAlgError:
            return  # Skip update on singular innovation

        delta_x = K @ residual

        # 1. Position error injection
        self.p_enu += delta_x[0:3]

        # 2. Velocity error injection
        self.v_enu += delta_x[3:6]

        # 3. Attitude error injection via small-angle quaternion correction
        delta_psi = delta_x[6:9]
        angle = np.linalg.norm(delta_psi)
        if angle > 1e-12:
            dq = np.array([
                math.cos(angle * 0.5),
                (delta_psi[0] / angle) * math.sin(angle * 0.5),
                (delta_psi[1] / angle) * math.sin(angle * 0.5),
                (delta_psi[2] / angle) * math.sin(angle * 0.5)
            ], dtype=np.float64)
            self.q = quaternion_multiply(dq, self.q)
            self.q /= np.linalg.norm(self.q)

        # 4. Bias error injection
        self.accel_bias += delta_x[9:12]
        self.gyro_bias += delta_x[12:15]

        # 5. Joseph-form covariance update for numerical stability:
        # P = (I - K*H) * P * (I - K*H)^T + K * R * K^T
        I_KH = np.eye(15, dtype=np.float64) - K @ H
        self.P = I_KH @ self.P @ I_KH.T + K @ R @ K.T
        self.P = 0.5 * (self.P + self.P.T)

    def update_gnss_position(self, p_gnss_enu: np.ndarray, std_dev: float = 3.0):
        """Update with GNSS East, North, Up position."""
        H = np.zeros((3, 15), dtype=np.float64)
        H[0:3, 0:3] = np.eye(3)
        residual = p_gnss_enu - self.p_enu
        R = np.eye(3, dtype=np.float64) * (std_dev ** 2)
        self.update_measurement(H, residual, R)

    def update_gnss_velocity(self, v_gnss_enu: np.ndarray, std_dev: float = 0.4):
        """Update with GNSS 3D velocity."""
        H = np.zeros((3, 15), dtype=np.float64)
        H[0:3, 3:6] = np.eye(3)
        residual = v_gnss_enu - self.v_enu
        R = np.eye(3, dtype=np.float64) * (std_dev ** 2)
        self.update_measurement(H, residual, R)

    def update_ai_velocity(self, forward_speed_mps: float, std_dev: float = 0.8):
        """
        Update with AI-predicted longitudinal speed along Vehicle Frame X-axis.
        v_forward = [1, 0, 0] * (R_n2b * v_enu)
        """
        r_b2n = quaternion_to_rotation_matrix(self.q)
        r_n2b = r_b2n.T

        # Vehicle frame velocity: v_b = R_n2b * v_enu
        v_b = r_n2b @ self.v_enu
        current_forward_speed = v_b[0]

        residual = np.array([forward_speed_mps - current_forward_speed], dtype=np.float64)

        # H = [0, d(v_b[0])/d(v_enu), d(v_b[0])/d(psi), 0, 0]
        H = np.zeros((1, 15), dtype=np.float64)
        # d(v_b[0])/d(v_enu) = first row of R_n2b
        H[0, 3:6] = r_n2b[0, :]
        # d(v_b[0])/d(psi) = [1, 0, 0] * (R_n2b * [v_enu]x)
        H[0, 6:9] = np.array([1.0, 0.0, 0.0]) @ (r_n2b @ skew_symmetric(self.v_enu))

        R = np.array([[std_dev ** 2]], dtype=np.float64)
        self.update_measurement(H, residual, R)

    def update_nhc(self, std_lat: float = 0.15, std_vert: float = 0.15):
        """
        Apply Non-Holonomic Constraints (NHC):
        Ground vehicle velocity in lateral (Y) and vertical (Z) vehicle frame directions is 0:
        v_lateral = 0, v_vertical = 0
        """
        r_b2n = quaternion_to_rotation_matrix(self.q)
        r_n2b = r_b2n.T
        v_b = r_n2b @ self.v_enu

        # Residual: [0 - v_lateral, 0 - v_vertical]
        residual = np.array([-v_b[1], -v_b[2]], dtype=np.float64)

        H = np.zeros((2, 15), dtype=np.float64)
        # Rows 1 and 2 of R_n2b
        H[0, 3:6] = r_n2b[1, :]
        H[1, 3:6] = r_n2b[2, :]

        # d/d(psi) terms
        H[0, 6:9] = np.array([0.0, 1.0, 0.0]) @ (r_n2b @ skew_symmetric(self.v_enu))
        H[1, 6:9] = np.array([0.0, 0.0, 1.0]) @ (r_n2b @ skew_symmetric(self.v_enu))

        R = np.diag([std_lat ** 2, std_vert ** 2])
        self.update_measurement(H, residual, R)

    def update_zupt(self, std_vel: float = 0.05):
        """Apply Zero Velocity Update (ZUPT) when vehicle is at a standstill."""
        H = np.zeros((3, 15), dtype=np.float64)
        H[0:3, 3:6] = np.eye(3)
        residual = -self.v_enu  # Target velocity is 0
        R = np.eye(3, dtype=np.float64) * (std_vel ** 2)
        self.update_measurement(H, residual, R)

    def get_euler_angles(self) -> Tuple[float, float, float]:
        """Return (roll, pitch, yaw) in radians."""
        r_b2n = quaternion_to_rotation_matrix(self.q)
        return rotation_matrix_to_euler(r_b2n)

    def get_position_std_m(self) -> float:
        """Return 1-sigma estimated horizontal position standard deviation in meters."""
        var_e = self.P[0, 0]
        var_n = self.P[1, 1]
        return math.sqrt(max(0.0, var_e + var_n))
