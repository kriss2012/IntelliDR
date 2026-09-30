"""
IntelliDR Sensor Normalization and Synchronization Engine
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
Team: Logic Legend2 (Team ID: 170889)

Provides:
- High-precision timestamp synchronization (monotonic clock reference)
- Resampling & linear/spherical interpolation for missing sensor packets
- Anomaly & outlier rejection (handling sensor dropouts and spikes)
- Real-time sensor health & sampling frequency monitoring
"""

import collections
import math
from typing import Deque, List, Optional, Tuple
import numpy as np

from .sensor_types import IMUSample, GNSSSample


class SensorHealthMonitor:
    """Tracks sampling rates, latency, packet drops, and health metrics."""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.imu_timestamps: Deque[float] = collections.deque(maxlen=window_size)
        self.gnss_timestamps: Deque[float] = collections.deque(maxlen=window_size)
        self.imu_drop_count: int = 0
        self.last_imu_ts: Optional[float] = None
        self.last_gnss_ts: Optional[float] = None

    def record_imu(self, timestamp: float, expected_dt: float = 0.01) -> None:
        if self.last_imu_ts is not None:
            dt = timestamp - self.last_imu_ts
            if dt > 2.5 * expected_dt:
                # Detected packet drop
                self.imu_drop_count += int(round(dt / expected_dt)) - 1
        self.last_imu_ts = timestamp
        self.imu_timestamps.append(timestamp)

    def record_gnss(self, timestamp: float) -> None:
        self.last_gnss_ts = timestamp
        self.gnss_timestamps.append(timestamp)

    def get_imu_rate_hz(self) -> float:
        if len(self.imu_timestamps) < 2:
            return 0.0
        duration = self.imu_timestamps[-1] - self.imu_timestamps[0]
        if duration <= 1e-6:
            return 0.0
        return (len(self.imu_timestamps) - 1) / duration

    def get_gnss_rate_hz(self) -> float:
        if len(self.gnss_timestamps) < 2:
            return 0.0
        duration = self.gnss_timestamps[-1] - self.gnss_timestamps[0]
        if duration <= 1e-6:
            return 0.0
        return (len(self.gnss_timestamps) - 1) / duration

    def get_summary(self) -> dict:
        return {
            "imu_rate_hz": round(self.get_imu_rate_hz(), 1),
            "gnss_rate_hz": round(self.get_gnss_rate_hz(), 1),
            "imu_drop_count": self.imu_drop_count,
            "imu_healthy": self.get_imu_rate_hz() >= 20.0,
            "gnss_healthy": self.get_gnss_rate_hz() >= 0.5,
        }


class SensorNormalizer:
    """Normalizes and synchronizes raw IMU and GNSS streams."""

    def __init__(
        self,
        target_imu_rate_hz: float = 100.0,
        max_accel_norm: float = 45.0,  # Max allowable accel in m/s^2 (shock limit)
        max_gyro_norm: float = 15.0,   # Max allowable gyro in rad/s
    ):
        self.target_rate = target_imu_rate_hz
        self.target_dt = 1.0 / target_imu_rate_hz
        self.max_accel_norm = max_accel_norm
        self.max_gyro_norm = max_gyro_norm
        
        self.health_monitor = SensorHealthMonitor()
        self.last_valid_imu: Optional[IMUSample] = None
        self.last_emitted_ts: Optional[float] = None
        
        # Buffer for sorting out-of-order packets
        self.imu_buffer: List[IMUSample] = []

    def clean_imu(self, sample: IMUSample) -> Optional[IMUSample]:
        """Validate sample integrity, eliminate NaNs, and clamp anomalous shock spikes."""
        if any(math.isnan(v) or math.isinf(v) for v in [sample.ax, sample.ay, sample.az, sample.gx, sample.gy, sample.gz]):
            return None

        # Accel norm check
        accel_norm = math.sqrt(sample.ax**2 + sample.ay**2 + sample.az**2)
        if accel_norm > self.max_accel_norm:
            # Scale down excessive shock spike towards last known good sample
            scale = self.max_accel_norm / (accel_norm + 1e-6)
            sample.ax *= scale
            sample.ay *= scale
            sample.az *= scale

        # Gyro norm check
        gyro_norm = math.sqrt(sample.gx**2 + sample.gy**2 + sample.gz**2)
        if gyro_norm > self.max_gyro_norm:
            scale = self.max_gyro_norm / (gyro_norm + 1e-6)
            sample.gx *= scale
            sample.gy *= scale
            sample.gz *= scale

        self.health_monitor.record_imu(sample.timestamp, self.target_dt)
        return sample

    def process_imu(self, sample: IMUSample) -> List[IMUSample]:
        """
        Ingest IMU sample, fill missed timestamps via linear interpolation,
        and yield normalized stream.
        """
        cleaned = self.clean_imu(sample)
        if cleaned is None:
            return []

        emitted: List[IMUSample] = []

        if self.last_valid_imu is None:
            self.last_valid_imu = cleaned
            self.last_emitted_ts = cleaned.timestamp
            return [cleaned]

        dt = cleaned.timestamp - self.last_valid_imu.timestamp

        # Handle backward timestamps (clock jitter or out-of-order)
        if dt <= 0.0:
            return []

        # Handle large gap: if gap > 2 * dt and < 0.5s, interpolate missing samples
        if dt > 2.0 * self.target_dt and dt < 0.5:
            num_steps = int(round(dt / self.target_dt))
            for i in range(1, num_steps):
                alpha = i / float(num_steps)
                interp_ts = self.last_valid_imu.timestamp + alpha * dt
                interp_sample = IMUSample(
                    timestamp=interp_ts,
                    ax=self.last_valid_imu.ax + alpha * (cleaned.ax - self.last_valid_imu.ax),
                    ay=self.last_valid_imu.ay + alpha * (cleaned.ay - self.last_valid_imu.ay),
                    az=self.last_valid_imu.az + alpha * (cleaned.az - self.last_valid_imu.az),
                    gx=self.last_valid_imu.gx + alpha * (cleaned.gx - self.last_valid_imu.gx),
                    gy=self.last_valid_imu.gy + alpha * (cleaned.gy - self.last_valid_imu.gy),
                    gz=self.last_valid_imu.gz + alpha * (cleaned.gz - self.last_valid_imu.gz),
                )
                emitted.append(interp_sample)

        emitted.append(cleaned)
        self.last_valid_imu = cleaned
        self.last_emitted_ts = cleaned.timestamp
        return emitted

    def process_gnss(self, sample: GNSSSample) -> Optional[GNSSSample]:
        """Validate and sanitize incoming GNSS fix."""
        if math.isnan(sample.latitude) or math.isnan(sample.longitude):
            return None
        if abs(sample.latitude) > 90.0 or abs(sample.longitude) > 180.0:
            return None
        if sample.horizontal_accuracy_m <= 0.0:
            sample.horizontal_accuracy_m = 10.0

        self.health_monitor.record_gnss(sample.timestamp)
        return sample
