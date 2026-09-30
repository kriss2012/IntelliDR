"""
IntelliDR Normalized Sensor & State Data Types
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
Team: Logic Legend2 (Team ID: 170889)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple
import numpy as np


class OutageState(str, Enum):
    """GNSS availability and transition lifecycle states."""
    GNSS_AVAILABLE = "GNSS_AVAILABLE"
    GNSS_DEGRADED = "GNSS_DEGRADED"
    GNSS_LOST = "GNSS_LOST"
    DEAD_RECKONING = "DEAD_RECKONING"
    GNSS_RECOVERING = "GNSS_RECOVERING"


class FusionMode(str, Enum):
    """Active navigation state estimation mode."""
    INITIALIZING = "INITIALIZING"
    GNSS_INS = "GNSS_INS"
    DEAD_RECKONING = "DEAD_RECKONING"
    AI_DEAD_RECKONING = "AI_DEAD_RECKONING"
    MAP_CONSTRAINED = "MAP_CONSTRAINED"
    STATIONARY_ZUPT = "STATIONARY_ZUPT"


@dataclass
class IMUSample:
    """Normalized high-rate inertial measurement unit sample."""
    timestamp: float           # Monotonic epoch timestamp in seconds
    ax: float                  # Specific force X in m/s^2 (phone frame)
    ay: float                  # Specific force Y in m/s^2
    az: float                  # Specific force Z in m/s^2
    gx: float                  # Angular velocity X in rad/s (phone frame)
    gy: float                  # Angular velocity Y in rad/s
    gz: float                  # Angular velocity Z in rad/s
    mx: Optional[float] = None # Magnetic field X in microTesla (uT)
    my: Optional[float] = None # Magnetic field Y in microTesla (uT)
    mz: Optional[float] = None # Magnetic field Z in microTesla (uT)
    temperature: Optional[float] = None

    def accel_vector(self) -> np.ndarray:
        return np.array([self.ax, self.ay, self.az], dtype=np.float64)

    def gyro_vector(self) -> np.ndarray:
        return np.array([self.gx, self.gy, self.gz], dtype=np.float64)

    def mag_vector(self) -> Optional[np.ndarray]:
        if self.mx is not None and self.my is not None and self.mz is not None:
            return np.array([self.mx, self.my, self.mz], dtype=np.float64)
        return None


@dataclass
class GNSSSample:
    """Normalized GNSS fix sample."""
    timestamp: float                     # Monotonic epoch timestamp in seconds
    latitude: float                      # WGS84 Latitude in degrees
    longitude: float                     # WGS84 Longitude in degrees
    altitude: float = 0.0                # Ellipsoidal / MSL altitude in meters
    speed_mps: float = 0.0               # Ground speed in m/s
    bearing_deg: float = 0.0             # Ground track / azimuth in degrees [0, 360)
    horizontal_accuracy_m: float = 5.0   # 1-sigma estimated horizontal error in meters
    vertical_accuracy_m: float = 10.0    # 1-sigma estimated vertical error in meters
    speed_accuracy_mps: float = 0.5      # Speed error estimate in m/s
    num_satellites: int = 8              # Satellites used in fix
    fix_type: int = 3                    # 0=None, 2=2D, 3=3D, 4=DGPS/RTK
    is_valid: bool = True                # Flag for healthy fix


@dataclass
class AlignmentState:
    """Phone-to-vehicle mounting frame orientation calibration state."""
    roll_deg: float = 0.0             # Roll offset in degrees
    pitch_deg: float = 0.0            # Pitch offset in degrees
    yaw_offset_deg: float = 0.0       # Azimuth heading offset between phone Y/X and vehicle X (forward)
    confidence: float = 0.0           # Calibration confidence [0.0, 1.0]
    is_calibrated: bool = False       # True once alignment converges
    r_phone_to_vehicle: np.ndarray = field(
        default_factory=lambda: np.eye(3, dtype=np.float64)
    )


@dataclass
class MapMatchResult:
    """Offline map matching evaluation on local road network graph."""
    is_matched: bool = False
    road_id: str = ""
    road_name: str = ""
    road_type: str = ""
    matched_latitude: float = 0.0
    matched_longitude: float = 0.0
    matched_heading_deg: float = 0.0
    lateral_offset_m: float = 0.0
    confidence: float = 0.0           # [0.0, 1.0]
    speed_limit_kmh: float = 50.0


@dataclass
class VehicleState:
    """Complete estimated real-time navigation and dead reckoning state."""
    timestamp: float
    latitude: float
    longitude: float
    altitude: float
    e_m: float = 0.0                  # East position in meters relative to session origin
    n_m: float = 0.0                  # North position in meters relative to session origin
    u_m: float = 0.0                  # Up position in meters relative to session origin
    ve_mps: float = 0.0               # Velocity East
    vn_mps: float = 0.0               # Velocity North
    vu_mps: float = 0.0               # Velocity Up
    forward_speed_mps: float = 0.0    # Body forward speed
    heading_deg: float = 0.0          # Navigation heading in degrees [0, 360)
    roll_deg: float = 0.0
    pitch_deg: float = 0.0
    quaternion: np.ndarray = field(
        default_factory=lambda: np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)
    )
    accel_bias: np.ndarray = field(
        default_factory=lambda: np.zeros(3, dtype=np.float64)
    )
    gyro_bias: np.ndarray = field(
        default_factory=lambda: np.zeros(3, dtype=np.float64)
    )
    horizontal_accuracy_m: float = 5.0
    fusion_mode: FusionMode = FusionMode.INITIALIZING
    outage_state: OutageState = OutageState.GNSS_AVAILABLE
    position_confidence: float = 1.0
    drift_distance_m: float = 0.0     # Total accumulated drift from ground truth / reference
    drift_percentage: float = 0.0     # Drift as percentage of distance traveled
    distance_traveled_m: float = 0.0
    outage_duration_s: float = 0.0
    ai_velocity_mps: float = 0.0
    ai_velocity_confidence: float = 0.0
    map_match: Optional[MapMatchResult] = None
