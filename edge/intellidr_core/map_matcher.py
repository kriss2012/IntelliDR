"""
IntelliDR Advanced Offline Map Matching Engine
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
Team: Logic Legend2 (Team ID: 170889)

Geometric and Topological Map Matcher:
- Multi-hypothesis road segment candidate generation
- Orthogonal projection onto road vector polylines
- Composite scoring:
    Score = w_dist * exp(-d^2 / 2*sigma_d^2) + w_heading * cos(delta_theta)
- Confidence-gated projection: prevents snapping when vehicle is off-road or turning
- Map-assisted dead reckoning cross-track drift elimination
"""

import math
from typing import List, Optional, Tuple
import numpy as np

from .coordinates import (
    geodetic_to_enu,
    enu_to_geodetic,
    haversine_distance,
)
from .sensor_types import MapMatchResult
from .offline_map import OfflineMapProvider, RoadSegment


class MapMatcher:
    """Offline topological road-network matcher for dead reckoning constraint."""

    def __init__(
        self,
        map_provider: OfflineMapProvider,
        search_radius_m: float = 35.0,
        sigma_dist_m: float = 12.0,
        min_confidence_threshold: float = 0.60,
    ):
        self.map_provider = map_provider
        self.search_radius = search_radius_m
        self.sigma_dist = sigma_dist_m
        self.min_confidence = min_confidence_threshold
        self.active_segment_id: Optional[str] = None

    def match(
        self,
        current_enu: np.ndarray,
        heading_deg: float,
        speed_mps: float,
    ) -> MapMatchResult:
        """
        Evaluate candidate road segments for given vehicle state in local ENU.
        Returns MapMatchResult with confidence and projected coordinate.
        """
        p = current_enu[0:2]  # [East, North]
        candidates = []

        for seg in self.map_provider.segments:
            if seg.start_enu is None or seg.end_enu is None:
                continue

            a = seg.start_enu[0:2]
            b = seg.end_enu[0:2]
            u = b - a
            u_len_sq = np.dot(u, u)

            if u_len_sq < 1e-6:
                continue

            # Orthogonal projection parameter t in [0, 1]
            v = p - a
            t = np.clip(np.dot(v, u) / u_len_sq, 0.0, 1.0)
            proj = a + t * u
            dist = float(np.linalg.norm(p - proj))

            if dist > self.search_radius:
                continue

            # Heading difference in degrees [-180, 180]
            d_heading = (heading_deg - seg.heading_deg + 180.0) % 360.0 - 180.0
            heading_diff_deg = abs(d_heading)

            # Distance score [0, 1]
            s_dist = math.exp(-(dist ** 2) / (2.0 * (self.sigma_dist ** 2)))

            # Heading score: cosine similarity, penalize opposite direction
            if speed_mps > 1.5:  # Heading is reliable when moving
                s_head = max(0.0, math.cos(math.radians(heading_diff_deg)))
            else:
                s_head = 0.7  # Neutral when stationary / slow

            # Composite score with continuity bonus for previously matched road
            score = 0.55 * s_dist + 0.45 * s_head
            if seg.segment_id == self.active_segment_id:
                score = min(1.0, score + 0.10)  # Hysteresis bonus

            candidates.append((score, seg, proj, dist, t))

        if not candidates:
            return MapMatchResult(is_matched=False, confidence=0.0)

        # Sort descending by score
        candidates.sort(key=lambda x: x[0], reverse=True)
        best_score, best_seg, best_proj, best_dist, best_t = candidates[0]

        if best_score < self.min_confidence:
            return MapMatchResult(
                is_matched=False,
                road_id=best_seg.segment_id,
                road_name=best_seg.road_name,
                lateral_offset_m=best_dist,
                confidence=best_score,
            )

        self.active_segment_id = best_seg.segment_id

        # Convert projected ENU back to geodetic
        proj_lat, proj_lon, _ = enu_to_geodetic(
            best_proj[0], best_proj[1], 0.0,
            self.map_provider.ref_lat, self.map_provider.ref_lon, self.map_provider.ref_alt
        )

        return MapMatchResult(
            is_matched=True,
            road_id=best_seg.segment_id,
            road_name=best_seg.road_name,
            road_type=best_seg.road_type,
            matched_latitude=proj_lat,
            matched_longitude=proj_lon,
            matched_heading_deg=best_seg.heading_deg,
            lateral_offset_m=best_dist,
            confidence=best_score,
            speed_limit_kmh=best_seg.speed_limit_kmh,
        )

    def constrain_position(
        self,
        current_enu: np.ndarray,
        match_result: MapMatchResult,
        blend_factor: float = 0.65,
    ) -> np.ndarray:
        """
        Gently constrain estimated dead reckoning position towards the road centerline.
        Eliminates unbounded cross-track drift during prolonged GNSS outages.
        """
        if not match_result.is_matched or match_result.confidence < self.min_confidence:
            return current_enu

        # Find projected ENU point
        e_proj, n_proj, _ = geodetic_to_enu(
            match_result.matched_latitude,
            match_result.matched_longitude,
            0.0,
            self.map_provider.ref_lat,
            self.map_provider.ref_lon,
            self.map_provider.ref_alt,
        )

        constrained = np.array(current_enu, dtype=np.float64)
        # Apply smooth partial pull towards centerline
        weight = blend_factor * match_result.confidence
        constrained[0] = (1.0 - weight) * current_enu[0] + weight * e_proj
        constrained[1] = (1.0 - weight) * current_enu[1] + weight * n_proj
        return constrained
