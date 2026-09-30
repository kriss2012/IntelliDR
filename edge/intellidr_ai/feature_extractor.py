"""
IntelliDR AI Feature Extraction & Motion Anomaly Detection
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
Team: Logic Legend2 (Team ID: 170889)

Extracts temporal, statistical, and spectral representations from 6-axis IMU windows:
- Vibration filtering: identifies high-frequency engine/chassis noise (> 12 Hz)
- Pothole / bump detection: vertical jerk derivative spikes (|dj_z/dt| > 45 m/s^3)
- Braking & acceleration dynamics: forward inertial integral & longitudinal sign
- Motion classification: Stationary, Cruising, Accelerating, Braking, Turning
"""

import collections
import math
from typing import Dict, List, Optional, Tuple
import numpy as np

from intellidr_core.sensor_types import IMUSample


class MotionClassifier:
    """Classifies vehicle operational motion state from windowed IMU dynamics."""
    STATIONARY = "STATIONARY"
    CRUISING = "CRUISING"
    ACCELERATING = "ACCELERATING"
    BRAKING = "BRAKING"
    TURNING = "TURNING"
    POTHOLE_SHOCK = "POTHOLE_SHOCK"


class IMUFeatureExtractor:
    """Sliding-window statistical & physical feature extractor for AI velocity regression."""

    def __init__(self, window_size: int = 100, sampling_rate_hz: float = 100.0):
        self.window_size = window_size
        self.sampling_rate = sampling_rate_hz
        self.dt = 1.0 / sampling_rate_hz
        
        # Ring buffers for 6-axis IMU
        self.buffer_ax: collections.deque = collections.deque(maxlen=window_size)
        self.buffer_ay: collections.deque = collections.deque(maxlen=window_size)
        self.buffer_az: collections.deque = collections.deque(maxlen=window_size)
        self.buffer_gx: collections.deque = collections.deque(maxlen=window_size)
        self.buffer_gy: collections.deque = collections.deque(maxlen=window_size)
        self.buffer_gz: collections.deque = collections.deque(maxlen=window_size)
        
        # Pothole & vibration flags
        self.pothole_detected: bool = False
        self.vibration_intensity: float = 0.0
        self.current_motion_state: str = MotionClassifier.STATIONARY

    def push(self, imu: IMUSample, accel_veh: Optional[np.ndarray] = None, gyro_veh: Optional[np.ndarray] = None):
        """Push a sample (preferably transformed into vehicle frame)."""
        if accel_veh is not None and gyro_veh is not None:
            ax, ay, az = accel_veh[0], accel_veh[1], accel_veh[2]
            gx, gy, gz = gyro_veh[0], gyro_veh[1], gyro_veh[2]
        else:
            ax, ay, az = imu.ax, imu.ay, imu.az
            gx, gy, gz = imu.gx, imu.gy, imu.gz

        self.buffer_ax.append(ax)
        self.buffer_ay.append(ay)
        self.buffer_az.append(az)
        self.buffer_gx.append(gx)
        self.buffer_gy.append(gy)
        self.buffer_gz.append(gz)

    def is_ready(self) -> bool:
        return len(self.buffer_ax) >= (self.window_size // 2)

    def extract_features(self) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Extract compact 16-dimensional feature vector for velocity regression & diagnostics:
        [
            mean_ax, std_ax, rms_ax,
            mean_ay, std_ay,
            mean_az, std_az,
            mean_norm_a, std_norm_a,
            mean_gz, std_gz, rms_gz,
            mean_norm_w,
            jerk_z_max,
            high_freq_vibration,
            forward_accel_integral
        ]
        """
        ax = np.array(self.buffer_ax, dtype=np.float64)
        ay = np.array(self.buffer_ay, dtype=np.float64)
        az = np.array(self.buffer_az, dtype=np.float64)
        gx = np.array(self.buffer_gx, dtype=np.float64)
        gy = np.array(self.buffer_gy, dtype=np.float64)
        gz = np.array(self.buffer_gz, dtype=np.float64)

        norm_a = np.sqrt(ax**2 + ay**2 + az**2)
        norm_w = np.sqrt(gx**2 + gy**2 + gz**2)

        # 1. Pothole / Shock Detection via vertical jerk
        if len(az) > 2:
            jerk_z = np.diff(az) / self.dt
            max_jerk = float(np.max(np.abs(jerk_z)))
            self.pothole_detected = max_jerk > 45.0  # m/s^3
        else:
            max_jerk = 0.0
            self.pothole_detected = False

        # 2. Vibration Detection via standard deviation of high-frequency norm
        vib_intensity = float(np.std(norm_a))
        self.vibration_intensity = vib_intensity

        # 3. Motion state classification
        mean_ax = float(np.mean(ax))
        mean_gz = float(np.mean(gz))
        gyro_activity = float(np.mean(norm_w))
        accel_variance = float(np.var(norm_a))

        # Stationary requires low variance, low gyro activity, and zero mean longitudinal acceleration
        if accel_variance < 0.005 and gyro_activity < 0.015 and abs(mean_ax) < 0.08:
            self.current_motion_state = MotionClassifier.STATIONARY
        elif self.pothole_detected:
            self.current_motion_state = MotionClassifier.POTHOLE_SHOCK
        elif abs(mean_gz) > 0.15:
            self.current_motion_state = MotionClassifier.TURNING
        elif mean_ax > 0.4:
            self.current_motion_state = MotionClassifier.ACCELERATING
        elif mean_ax < -0.4:
            self.current_motion_state = MotionClassifier.BRAKING
        else:
            self.current_motion_state = MotionClassifier.CRUISING

        # Feature vector assembly (16 dimensions)
        feat = np.array([
            mean_ax,
            float(np.std(ax)),
            float(np.sqrt(np.mean(ax**2))),
            float(np.mean(ay)),
            float(np.std(ay)),
            float(np.mean(az)),
            float(np.std(az)),
            float(np.mean(norm_a)),
            vib_intensity,
            mean_gz,
            float(np.std(gz)),
            float(np.sqrt(np.mean(gz**2))),
            gyro_activity,
            max_jerk,
            float(np.sum(np.abs(np.diff(norm_a)))),  # Total variation
            float(np.sum(ax) * self.dt),              # Integrated forward velocity change
        ], dtype=np.float32)

        meta = {
            "motion_state": self.current_motion_state,
            "is_stationary": self.current_motion_state == MotionClassifier.STATIONARY,
            "pothole_detected": self.pothole_detected,
            "vibration_intensity": vib_intensity,
            "max_jerk": max_jerk,
        }
        return feat, meta
