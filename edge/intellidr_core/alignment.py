"""
IntelliDR Phone-to-Vehicle Alignment and Dynamic Calibration Engine
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
Team: Logic Legend2 (Team ID: 170889)

Solves the arbitrary mounting problem:
Estimates the 3D rotation matrix R_p2v that transforms measurements from
the Smartphone Body Frame (P) to the Vehicle Coordinate Frame (V):
- Vehicle X: Forward (Longitudinal)
- Vehicle Y: Right (Lateral)
- Vehicle Z: Down (Vertical)

Algorithm:
1. Static / Low-dynamic Gravity Vector Estimation -> Determines Vehicle Vertical Axis (Z).
2. Longitudinal Acceleration Window Alignment -> Determines Vehicle Forward Axis (X).
3. Orthogonalization via Cross Product -> Y = Z x X.
4. Continuous low-pass Kalman tracking of alignment confidence.
"""

import math
from typing import List, Optional, Tuple
import numpy as np

from .sensor_types import IMUSample, AlignmentState
from .coordinates import rotation_matrix_to_euler


class AlignmentEngine:
    """Estimates and tracks the transformation between Smartphone frame and Vehicle frame."""

    def __init__(
        self,
        min_calibration_samples: int = 150,  # ~1.5s at 100 Hz
        straight_motion_accel_threshold: float = 0.4, # m/s^2 forward accel to detect drive
    ):
        self.min_samples = min_calibration_samples
        self.straight_accel_thresh = straight_motion_accel_threshold

        # Buffers for gravity estimation
        self.accel_history: List[np.ndarray] = []
        self.gyro_history: List[np.ndarray] = []

        # Estimated unit axes in phone frame
        self.v_z_phone = np.array([0.0, 0.0, 1.0])  # Gravity direction (down)
        self.v_x_phone = np.array([0.0, 1.0, 0.0])  # Vehicle forward direction
        self.v_y_phone = np.array([1.0, 0.0, 0.0])  # Vehicle right direction

        self.r_p2v = np.eye(3, dtype=np.float64)
        self.confidence: float = 0.0
        self.is_calibrated: bool = False
        self.status_message: str = "Calibrating..."

    def update(self, imu: IMUSample, gnss_speed_mps: Optional[float] = None) -> AlignmentState:
        """
        Process an incoming IMU sample to calibrate or refine the alignment matrix.
        Returns the updated AlignmentState.
        """
        a = imu.accel_vector()
        w = imu.gyro_vector()

        self.accel_history.append(a)
        self.gyro_history.append(w)
        if len(self.accel_history) > 500:
            self.accel_history.pop(0)
            self.gyro_history.pop(0)

        # 1. Gravity Estimation (Vehicle Z axis: Downwards)
        if len(self.accel_history) >= self.min_samples:
            accels = np.array(self.accel_history)
            gyros = np.array(self.gyro_history)

            # Check if vehicle is relatively steady (low angular rate variance)
            gyro_std = np.std(gyros, axis=0)
            if np.mean(gyro_std) < 0.2:  # rad/s - smooth driving or stationary
                mean_accel = np.mean(accels, axis=0)
                norm = np.linalg.norm(mean_accel)
                if 8.5 < norm < 11.0:
                    # Specific force points upward when resting on gravity, so down is -mean_accel
                    # In NED convention, Z is Down, so accelerometer measures -1g when stationary.
                    # Normalizing gives gravity unit vector.
                    self.v_z_phone = -mean_accel / norm
                    self.confidence = max(self.confidence, 0.4)
                    self.status_message = "Vertical gravity locked. Drive straight to calibrate forward axis."

        # 2. Longitudinal Acceleration Detection (Vehicle X axis: Forward)
        if self.confidence >= 0.4 and len(self.accel_history) >= 50:
            recent_accels = np.array(self.accel_history[-50:])
            mean_a = np.mean(recent_accels, axis=0)

            # Remove vertical gravity component
            horizontal_a = mean_a - np.dot(mean_a, self.v_z_phone) * self.v_z_phone
            horiz_norm = np.linalg.norm(horizontal_a)

            # Check for significant linear acceleration along horizontal plane
            # Correlate with GNSS speed increase if available
            speed_increasing = True
            if gnss_speed_mps is not None and gnss_speed_mps < 1.0:
                speed_increasing = False

            if horiz_norm > self.straight_accel_thresh and speed_increasing:
                estimated_forward = horizontal_a / horiz_norm
                
                # Smooth update of forward axis
                if not self.is_calibrated:
                    self.v_x_phone = estimated_forward
                else:
                    self.v_x_phone = 0.95 * self.v_x_phone + 0.05 * estimated_forward
                    self.v_x_phone /= (np.linalg.norm(self.v_x_phone) + 1e-9)

                # 3. Complete Right-Handed Coordinate System: Y = Z x X
                v_y = np.cross(self.v_z_phone, self.v_x_phone)
                y_norm = np.linalg.norm(v_y)
                if y_norm > 1e-4:
                    self.v_y_phone = v_y / y_norm
                    # Re-orthogonalize X = Y x Z
                    self.v_x_phone = np.cross(self.v_y_phone, self.v_z_phone)
                    self.v_x_phone /= np.linalg.norm(self.v_x_phone)

                    # Rotation matrix from phone to vehicle frame
                    # Rows are vehicle axes projected into phone coordinates
                    self.r_p2v = np.vstack([
                        self.v_x_phone,
                        self.v_y_phone,
                        self.v_z_phone
                    ])

                    self.confidence = min(1.0, self.confidence + 0.05)
                    if self.confidence >= 0.85:
                        self.is_calibrated = True
                        self.status_message = f"Calibration complete ({int(self.confidence * 100)}%)"

        # Compute Euler angles of phone mount
        roll_rad, pitch_rad, yaw_rad = rotation_matrix_to_euler(self.r_p2v.T)

        return AlignmentState(
            roll_deg=math.degrees(roll_rad),
            pitch_deg=math.degrees(pitch_rad),
            yaw_offset_deg=math.degrees(yaw_rad),
            confidence=self.confidence,
            is_calibrated=self.is_calibrated,
            r_phone_to_vehicle=self.r_p2v,
        )

    def transform_accel(self, accel_phone: np.ndarray) -> np.ndarray:
        """Transform specific force from Phone frame to Vehicle frame [Forward, Right, Down]."""
        return self.r_p2v @ accel_phone

    def transform_gyro(self, gyro_phone: np.ndarray) -> np.ndarray:
        """Transform angular velocity from Phone frame to Vehicle frame [Roll, Pitch, Yaw rates]."""
        return self.r_p2v @ gyro_phone
