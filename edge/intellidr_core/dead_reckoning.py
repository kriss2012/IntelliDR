"""
IntelliDR Dead Reckoning Propagation Engine
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
Team: Logic Legend2 (Team ID: 170889)

Physics-Informed Inertial Dead Reckoning with:
- Calibrated 3D vehicle frame transformation
- Gravity compensation in Navigation (ENU) frame
- Longitudinal AI-assisted speed fusion
- Non-Holonomic Constraints (NHC) arresting lateral and vertical velocity drift
- Drift estimation & numerical sanity bounds
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
from .sensor_types import IMUSample, AlignmentState, FusionMode


class DeadReckoningEngine:
    """Pure and AI-assisted Dead Reckoning inertial solver."""

    def __init__(self):
        # Navigation state in ENU meters & m/s
        self.p_enu = np.zeros(3, dtype=np.float64)
        self.v_enu = np.zeros(3, dtype=np.float64)
        self.q = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)
        
        # Biases
        self.accel_bias = np.zeros(3, dtype=np.float64)
        self.gyro_bias = np.zeros(3, dtype=np.float64)

        # Odometry
        self.distance_traveled_m: float = 0.0
        self.estimated_drift_m: float = 0.0
        self.last_ts: Optional[float] = None
        self.forward_speed_mps: float = 0.0

        # Constraints
        self.nhc_damping: float = 0.85  # Damping factor on lateral/vertical slip

    def reset_state(self, p_enu: np.ndarray, v_enu: np.ndarray, q: np.ndarray):
        """Re-align DR state to filter state."""
        self.p_enu = np.array(p_enu, dtype=np.float64)
        self.v_enu = np.array(v_enu, dtype=np.float64)
        self.q = np.array(q, dtype=np.float64)
        self.forward_speed_mps = float(np.linalg.norm(self.v_enu[0:2]))

    def propagate(
        self,
        imu: IMUSample,
        alignment: AlignmentState,
        ai_speed_mps: Optional[float] = None,
        use_nhc: bool = True,
    ) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Step dead reckoning forward using IMU sample, alignment, and optional AI speed.
        Returns: (p_enu, v_enu, heading_deg)
        """
        ts = imu.timestamp
        if self.last_ts is None:
            self.last_ts = ts
            return self.p_enu, self.v_enu, 0.0

        dt = ts - self.last_ts
        self.last_ts = ts

        # Reject unreasonable dt
        if dt <= 0.0 or dt > 0.5:
            return self.p_enu, self.v_enu, 0.0

        # 1. Transform raw phone IMU to vehicle body frame [X=forward, Y=right, Z=down]
        accel_raw = imu.accel_vector()
        gyro_raw = imu.gyro_vector()

        if alignment.is_calibrated:
            accel_veh = alignment.r_phone_to_vehicle @ accel_raw
            gyro_veh = alignment.r_phone_to_vehicle @ gyro_raw
        else:
            accel_veh = accel_raw
            gyro_veh = gyro_raw

        # Subtract gyro bias
        w_b = gyro_veh - self.gyro_bias

        # 2. Propagate attitude quaternion
        angle = np.linalg.norm(w_b * dt)
        if angle > 1e-12:
            half = angle * 0.5
            s = math.sin(half) / angle
            dq = np.array([math.cos(half), w_b[0] * dt * s, w_b[1] * dt * s, w_b[2] * dt * s])
        else:
            dq = np.array([1.0, 0.0, 0.0, 0.0])
        self.q = quaternion_multiply(self.q, dq)
        self.q /= np.linalg.norm(self.q)

        # 3. Attitude rotation matrix R_b2n
        r_b2n = quaternion_to_rotation_matrix(self.q)
        roll, pitch, yaw = rotation_matrix_to_euler(r_b2n)
        heading_deg = (math.degrees(yaw) + 360.0) % 360.0

        # 4. Velocity computation:
        # If AI speed is available, use AI forward velocity directly to govern magnitude
        # and vehicle forward heading vector to govern direction, drastically suppressing double-integration drift.
        if ai_speed_mps is not None and ai_speed_mps >= 0.0:
            self.forward_speed_mps = ai_speed_mps
            # Vehicle forward unit vector in ENU frame:
            # Vehicle X axis is [1, 0, 0] in body frame -> R_b2n @ [1, 0, 0] = first column of R_b2n
            forward_unit_enu = r_b2n[:, 0]
            
            # Ground projection (horizontal unit vector)
            horiz_forward = np.array([forward_unit_enu[0], forward_unit_enu[1], 0.0])
            norm = np.linalg.norm(horiz_forward)
            if norm > 1e-6:
                horiz_forward /= norm
            else:
                horiz_forward = np.array([math.cos(yaw), math.sin(yaw), 0.0])

            self.v_enu = horiz_forward * self.forward_speed_mps
            self.v_enu[2] = 0.0  # Vertical ground constraint
        else:
            # Mechanization integration:
            # Correct accel bias
            f_b = accel_veh - self.accel_bias
            f_n = r_b2n @ f_b
            a_nav = f_n + np.array([0.0, 0.0, -9.80665])

            # Integrate velocity
            self.v_enu += a_nav * dt

            # Apply Non-Holonomic Constraints (NHC) in body frame
            if use_nhc:
                v_b = r_b2n.T @ self.v_enu
                # Suppress lateral and vertical velocity
                v_b[1] *= (1.0 - self.nhc_damping)
                v_b[2] *= (1.0 - self.nhc_damping)
                self.v_enu = r_b2n @ v_b
                self.forward_speed_mps = max(0.0, v_b[0])

        # 5. Position displacement
        step_disp = self.v_enu * dt
        self.p_enu += step_disp
        
        step_distance = float(np.linalg.norm(step_disp[0:2]))
        self.distance_traveled_m += step_distance

        return self.p_enu, self.v_enu, heading_deg
