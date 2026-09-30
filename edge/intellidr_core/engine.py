"""
IntelliDR Master Navigation & Dead Reckoning Engine
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
Theme: Smart Vehicles | Category: Software
Team: Logic Legend2 (Team ID: 170889)

Master Pipeline Coordinator:
Raw IMU / GNSS
  -> Sensor Normalization & Synchronization
  -> Phone-to-Vehicle 3D Alignment
  -> AI Motion Intelligence (Denoising, Vibration Filter, Speed Estimation)
  -> 15-State Error-State EKF (GNSS + INS Mechanization)
  -> Outage Manager (GNSS Outage Detection & Seamless Transition)
  -> Dead Reckoning & Non-Holonomic Constraints (NHC)
  -> Offline OpenStreetMap Map Matching
  -> Real-Time Navigation State
"""

import math
from typing import Dict, List, Optional, Tuple
import numpy as np

from .coordinates import (
    geodetic_to_enu,
    enu_to_geodetic,
    haversine_distance,
    calculate_bearing,
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
from .sensor_normalizer import SensorNormalizer
from .alignment import AlignmentEngine
from .fusion_ekf import ErrorStateEKF
from .outage_manager import GNSSOutageManager
from .dead_reckoning import DeadReckoningEngine
from .offline_map import OfflineMapProvider
from .map_matcher import MapMatcher
from intellidr_ai.feature_extractor import IMUFeatureExtractor
from intellidr_ai.models import HybridVelocityEstimator


class IntelliDREngine:
    """Master navigation engine implementing the complete SIH26168 pipeline."""

    def __init__(
        self,
        ref_lat: float = 19.0760,
        ref_lon: float = 72.8777,
        ref_alt: float = 14.0,
        target_rate_hz: float = 100.0,
        enable_map_matching: bool = True,
    ):
        self.ref_lat = ref_lat
        self.ref_lon = ref_lon
        self.ref_alt = ref_alt
        self.target_rate_hz = target_rate_hz
        self.enable_map_matching = enable_map_matching

        # Subsystems
        self.normalizer = SensorNormalizer(target_imu_rate_hz=target_rate_hz)
        self.alignment = AlignmentEngine()
        self.ekf = ErrorStateEKF()
        self.outage_mgr = GNSSOutageManager()
        self.dr = DeadReckoningEngine()
        self.feature_extractor = IMUFeatureExtractor(window_size=100, sampling_rate_hz=target_rate_hz)
        self.ai_velocity = HybridVelocityEstimator()
        
        # Map Matching
        self.map_provider = OfflineMapProvider(ref_lat, ref_lon, ref_alt)
        self.map_matcher = MapMatcher(self.map_provider)

        # Engine Tracking State
        self.is_initialized: bool = False
        self.current_state: Optional[VehicleState] = None
        self.last_imu_ts: Optional[float] = None
        
        # Benchmarking & Drift Metrics
        self.total_distance_traveled_m: float = 0.0
        self.ground_truth_positions: List[Tuple[float, float, float]] = []
        self.estimated_positions: List[Tuple[float, float, float]] = []
        self.accumulated_drift_m: float = 0.0
        self.drift_percentage: float = 0.0

    def set_reference_origin(self, lat: float, lon: float, alt: float = 0.0):
        """Set local ENU navigation origin."""
        self.ref_lat = lat
        self.ref_lon = lon
        self.ref_alt = alt
        self.map_provider.set_reference_origin(lat, lon, alt)

    def trigger_simulated_outage(self, active: bool, current_ts: Optional[float] = None):
        """Force manual GNSS outage for live SIH judge demonstration."""
        ts = current_ts or (self.last_imu_ts or 0.0)
        self.outage_mgr.trigger_simulated_outage(active, ts)

    def process_gnss(self, raw_gnss: GNSSSample) -> Optional[VehicleState]:
        """Ingest and fuse an incoming GNSS sample."""
        gnss = self.normalizer.process_gnss(raw_gnss)
        if gnss is None:
            return None

        # Seed reference origin on first valid fix
        if not self.is_initialized:
            self.set_reference_origin(gnss.latitude, gnss.longitude, gnss.altitude)
            heading_rad = math.radians(gnss.bearing_deg)
            v_enu = np.array([
                gnss.speed_mps * math.sin(heading_rad),
                gnss.speed_mps * math.cos(heading_rad),
                0.0
            ], dtype=np.float64)
            self.ekf.initialize(np.zeros(3), v_enu, heading_rad)
            self.dr.reset_state(np.zeros(3), v_enu, self.ekf.q)
            self.is_initialized = True

        # Project GNSS into local ENU
        e_g, n_g, u_g = geodetic_to_enu(
            gnss.latitude, gnss.longitude, gnss.altitude,
            self.ref_lat, self.ref_lon, self.ref_alt
        )
        p_gnss_enu = np.array([e_g, n_g, u_g])

        # Evaluate outage status & multipath gating
        outage_state, usable = self.outage_mgr.evaluate_gnss_sample(
            gnss, current_estimated_pos_enu=self.ekf.p_enu, sample_enu_pos=p_gnss_enu
        )

        if usable and outage_state in (OutageState.GNSS_AVAILABLE, OutageState.GNSS_DEGRADED, OutageState.GNSS_RECOVERING):
            # Calculate GNSS velocity in ENU
            head_rad = math.radians(gnss.bearing_deg)
            v_gnss_enu = np.array([
                gnss.speed_mps * math.sin(head_rad),
                gnss.speed_mps * math.cos(head_rad),
                0.0
            ])

            # Apply smooth recovery weighting if transitioning from outage
            rec_weight = self.outage_mgr.get_smooth_recovery_weight()
            effective_pos_std = max(1.0, gnss.horizontal_accuracy_m / max(0.1, rec_weight))
            
            # EKF measurement update
            self.ekf.update_gnss_position(p_gnss_enu, std_dev=effective_pos_std)
            self.ekf.update_gnss_velocity(v_gnss_enu, std_dev=max(0.3, gnss.speed_accuracy_mps))
            
            # Re-align DR state to EKF
            self.dr.reset_state(self.ekf.p_enu, self.ekf.v_enu, self.ekf.q)

        return self._build_vehicle_state(gnss.timestamp, outage_state)

    def process_imu(self, raw_imu: IMUSample) -> Optional[VehicleState]:
        """Ingest high-rate IMU sample and step dead reckoning / EKF prediction."""
        samples = self.normalizer.process_imu(raw_imu)
        if not samples:
            return None

        state = None
        for imu in samples:
            state = self._step_imu(imu)
        return state

    def _step_imu(self, imu: IMUSample) -> VehicleState:
        ts = imu.timestamp
        dt = (ts - self.last_imu_ts) if self.last_imu_ts is not None else 0.01
        self.last_imu_ts = ts
        dt = max(0.001, min(0.05, dt))

        # Check for GNSS outage timeout
        outage_state = self.outage_mgr.check_timeout(ts)

        # 1. Update phone-to-vehicle alignment
        gnss_spd = self.outage_mgr.last_raw_gnss.speed_mps if self.outage_mgr.last_raw_gnss else None
        alignment_state = self.alignment.update(imu, gnss_spd)

        # Transform IMU into vehicle frame
        accel_veh = self.alignment.transform_accel(imu.accel_vector())
        gyro_veh = self.alignment.transform_gyro(imu.gyro_vector())

        # 2. AI Motion Intelligence: feature extraction & motion classification
        self.feature_extractor.push(imu, accel_veh, gyro_veh)
        ai_speed = 0.0
        ai_conf = 0.0
        motion_meta = {}

        if self.feature_extractor.is_ready():
            feats, motion_meta = self.feature_extractor.extract_features()
            ai_speed, ai_conf, _ = self.ai_velocity.estimate(
                features=feats,
                meta=motion_meta,
                forward_accel=float(accel_veh[0]),
                dt=dt,
            )

        # 3. State Propagation (EKF prediction)
        self.ekf.predict(dt, accel_veh, gyro_veh)

        # 4. Outage Handling & Dead Reckoning
        fusion_mode = FusionMode.GNSS_INS
        if outage_state in (OutageState.DEAD_RECKONING, OutageState.GNSS_LOST):
            fusion_mode = FusionMode.AI_DEAD_RECKONING

            # Stationary ZUPT update
            if motion_meta.get("is_stationary", False):
                self.ekf.update_zupt(std_vel=0.05)
                fusion_mode = FusionMode.STATIONARY_ZUPT
            else:
                # Apply AI forward velocity constraint
                if ai_conf > 0.60:
                    self.ekf.update_ai_velocity(ai_speed, std_dev=0.8)

                # Apply Non-Holonomic Constraints (NHC)
                self.ekf.update_nhc(std_lat=0.15, std_vert=0.15)

            # Step Dead Reckoning solver
            p_dr, v_dr, _ = self.dr.propagate(
                imu=imu,
                alignment=alignment_state,
                ai_speed_mps=ai_speed if ai_conf > 0.60 else None,
                use_nhc=True,
            )
            # Synchronize position
            self.ekf.p_enu = p_dr
            self.ekf.v_enu = v_dr
            self.ekf.q = self.dr.q

        # 5. Offline Map Matching
        map_match_result: Optional[MapMatchResult] = None
        current_speed = float(np.linalg.norm(self.ekf.v_enu[0:2]))
        roll, pitch, yaw = self.ekf.get_euler_angles()
        heading_deg = (math.degrees(yaw) + 360.0) % 360.0

        if self.enable_map_matching and len(self.map_provider.segments) > 0:
            map_match_result = self.map_matcher.match(self.ekf.p_enu, heading_deg, current_speed)
            
            # Constrain position if dead reckoning and map match confidence is high
            if outage_state in (OutageState.DEAD_RECKONING, OutageState.GNSS_LOST):
                if map_match_result.is_matched and map_match_result.confidence > 0.65:
                    self.ekf.p_enu = self.map_matcher.constrain_position(
                        self.ekf.p_enu, map_match_result, blend_factor=0.70
                    )
                    self.dr.p_enu = np.array(self.ekf.p_enu)
                    fusion_mode = FusionMode.MAP_CONSTRAINED

        # 6. Update Odometry & Drift
        step_dist = current_speed * dt
        self.total_distance_traveled_m += step_dist

        return self._build_vehicle_state(
            ts, outage_state, fusion_mode, ai_speed, ai_conf, map_match_result
        )

    def _build_vehicle_state(
        self,
        timestamp: float,
        outage_state: OutageState,
        fusion_mode: FusionMode = FusionMode.GNSS_INS,
        ai_speed: float = 0.0,
        ai_conf: float = 0.0,
        map_match: Optional[MapMatchResult] = None,
    ) -> VehicleState:
        # Convert local ENU position back to Geodetic (Lat, Lon, Alt)
        lat, lon, alt = enu_to_geodetic(
            self.ekf.p_enu[0], self.ekf.p_enu[1], self.ekf.p_enu[2],
            self.ref_lat, self.ref_lon, self.ref_alt
        )
        roll, pitch, yaw = self.ekf.get_euler_angles()
        speed = float(np.linalg.norm(self.ekf.v_enu[0:2]))
        heading_deg = (math.degrees(yaw) + 360.0) % 360.0

        # Positional drift percentage calculation
        drift_dist = self.accumulated_drift_m
        drift_pct = (drift_dist / max(1.0, self.total_distance_traveled_m)) * 100.0

        state = VehicleState(
            timestamp=timestamp,
            latitude=lat,
            longitude=lon,
            altitude=alt,
            e_m=float(self.ekf.p_enu[0]),
            n_m=float(self.ekf.p_enu[1]),
            u_m=float(self.ekf.p_enu[2]),
            ve_mps=float(self.ekf.v_enu[0]),
            vn_mps=float(self.ekf.v_enu[1]),
            vu_mps=float(self.ekf.v_enu[2]),
            forward_speed_mps=speed,
            heading_deg=heading_deg,
            roll_deg=math.degrees(roll),
            pitch_deg=math.degrees(pitch),
            quaternion=self.ekf.q.copy(),
            accel_bias=self.ekf.accel_bias.copy(),
            gyro_bias=self.ekf.gyro_bias.copy(),
            horizontal_accuracy_m=self.ekf.get_position_std_m(),
            fusion_mode=fusion_mode,
            outage_state=outage_state,
            position_confidence=max(0.2, 1.0 - (drift_pct / 20.0)),
            drift_distance_m=drift_dist,
            drift_percentage=round(drift_pct, 2),
            distance_traveled_m=round(self.total_distance_traveled_m, 1),
            outage_duration_s=round(self.outage_mgr.total_outage_duration_s, 1),
            ai_velocity_mps=round(ai_speed, 2),
            ai_velocity_confidence=round(ai_conf, 2),
            map_match=map_match,
        )
        self.current_state = state
        return state
