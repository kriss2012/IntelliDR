"""
IntelliDR Offline OpenStreetMap Road Network Engine
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
Team: Logic Legend2 (Team ID: 170889)

Provides completely offline road topology and spatial index:
- Road segments with Polyline coordinates, road name, type, speed limit, one-way flag
- Fast spatial bounding-box / KD-Tree indexing
- Offline loading from GeoJSON, JSON, or bundled urban test networks
"""

import json
import math
import os
from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np

from .coordinates import (
    geodetic_to_enu,
    enu_to_geodetic,
    haversine_distance,
    calculate_bearing,
)


@dataclass
class RoadSegment:
    """Directed road segment between two topological waypoints."""
    segment_id: str
    road_name: str
    road_type: str            # 'primary', 'secondary', 'residential', 'motorway'
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    length_m: float
    heading_deg: float
    speed_limit_kmh: float = 50.0
    is_oneway: bool = False
    
    # ENU coordinates relative to local reference
    start_enu: Optional[np.ndarray] = None
    end_enu: Optional[np.ndarray] = None


class OfflineMapProvider:
    """Manages offline road graphs and spatial indexing for map matching."""

    def __init__(self, ref_lat: float = 19.0760, ref_lon: float = 72.8777, ref_alt: float = 14.0):
        self.ref_lat = ref_lat
        self.ref_lon = ref_lon
        self.ref_alt = ref_alt
        self.segments: List[RoadSegment] = []

    def set_reference_origin(self, lat: float, lon: float, alt: float = 0.0):
        """Set local ENU projection origin."""
        self.ref_lat = lat
        self.ref_lon = lon
        self.ref_alt = alt
        self._recompute_enu_coordinates()

    def add_segment(self, segment: RoadSegment):
        """Add and project a road segment into ENU."""
        e1, n1, u1 = geodetic_to_enu(segment.start_lat, segment.start_lon, self.ref_alt, self.ref_lat, self.ref_lon, self.ref_alt)
        e2, n2, u2 = geodetic_to_enu(segment.end_lat, segment.end_lon, self.ref_alt, self.ref_lat, self.ref_lon, self.ref_alt)
        segment.start_enu = np.array([e1, n1, u1])
        segment.end_enu = np.array([e2, n2, u2])
        self.segments.append(segment)

    def _recompute_enu_coordinates(self):
        for seg in self.segments:
            e1, n1, u1 = geodetic_to_enu(seg.start_lat, seg.start_lon, self.ref_alt, self.ref_lat, self.ref_lon, self.ref_alt)
            e2, n2, u2 = geodetic_to_enu(seg.end_lat, seg.end_lon, self.ref_alt, self.ref_lat, self.ref_lon, self.ref_alt)
            seg.start_enu = np.array([e1, n1, u1])
            seg.end_enu = np.array([e2, n2, u2])

    def load_from_geojson(self, file_path: str) -> int:
        """Load road features from standard OSM GeoJSON extract."""
        if not os.path.exists(file_path):
            return 0

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        count = 0
        for feature in data.get("features", []):
            geom = feature.get("geometry", {})
            props = feature.get("properties", {})
            if geom.get("type") == "LineString":
                coords = geom.get("coordinates", [])
                name = props.get("name", "Unnamed Road")
                rtype = props.get("highway", "primary")
                speed = float(props.get("maxspeed", 50.0) if str(props.get("maxspeed", "")).replace(".","").isdigit() else 50.0)

                for i in range(len(coords) - 1):
                    lon1, lat1 = coords[i][0], coords[i][1]
                    lon2, lat2 = coords[i + 1][0], coords[i + 1][1]
                    length = haversine_distance(lat1, lon1, lat2, lon2)
                    bearing = calculate_bearing(lat1, lon1, lat2, lon2)
                    seg_id = f"{props.get('id', 'way')}_{i}"

                    seg = RoadSegment(
                        segment_id=seg_id,
                        road_name=name,
                        road_type=rtype,
                        start_lat=lat1,
                        start_lon=lon1,
                        end_lat=lat2,
                        end_lon=lon2,
                        length_m=length,
                        heading_deg=bearing,
                        speed_limit_kmh=speed,
                    )
                    self.add_segment(seg)
                    count += 1
        return count

    def generate_synthetic_urban_grid(self, center_lat: float, center_lon: float, grid_size: int = 5, spacing_m: float = 200.0):
        """Generates a realistic urban arterial/grid road network for offline testing & demos."""
        self.set_reference_origin(center_lat, center_lon, 10.0)
        self.segments.clear()

        # Generate horizontal (East-West) and vertical (North-South) roads
        extent = (grid_size // 2) * spacing_m
        
        # East-West streets
        for i, row in enumerate(range(-grid_size // 2, grid_size // 2 + 1)):
            n = row * spacing_m
            name = f"East-West Arterial {i+1}"
            e_start, e_end = -extent, extent
            lat1, lon1, _ = enu_to_geodetic(e_start, n, 0.0, center_lat, center_lon, 10.0)
            lat2, lon2, _ = enu_to_geodetic(e_end, n, 0.0, center_lat, center_lon, 10.0)
            
            # Segment forward
            seg_fwd = RoadSegment(
                segment_id=f"ew_{i}_fwd",
                road_name=name,
                road_type="primary" if abs(row) <= 1 else "secondary",
                start_lat=lat1,
                start_lon=lon1,
                end_lat=lat2,
                end_lon=lon2,
                length_m=extent * 2,
                heading_deg=90.0,
                speed_limit_kmh=60.0,
            )
            # Segment backward
            seg_bwd = RoadSegment(
                segment_id=f"ew_{i}_bwd",
                road_name=name,
                road_type="primary" if abs(row) <= 1 else "secondary",
                start_lat=lat2,
                start_lon=lon2,
                end_lat=lat1,
                end_lon=lon1,
                length_m=extent * 2,
                heading_deg=270.0,
                speed_limit_kmh=60.0,
            )
            self.add_segment(seg_fwd)
            self.add_segment(seg_bwd)

        # North-South avenues
        for j, col in enumerate(range(-grid_size // 2, grid_size // 2 + 1)):
            e = col * spacing_m
            name = f"North-South Avenue {j+1}"
            n_start, n_end = -extent, extent
            lat1, lon1, _ = enu_to_geodetic(e, n_start, 0.0, center_lat, center_lon, 10.0)
            lat2, lon2, _ = enu_to_geodetic(e, n_end, 0.0, center_lat, center_lon, 10.0)

            seg_fwd = RoadSegment(
                segment_id=f"ns_{j}_fwd",
                road_name=name,
                road_type="primary" if abs(col) <= 1 else "secondary",
                start_lat=lat1,
                start_lon=lon1,
                end_lat=lat2,
                end_lon=lon2,
                length_m=extent * 2,
                heading_deg=0.0,
                speed_limit_kmh=50.0,
            )
            seg_bwd = RoadSegment(
                segment_id=f"ns_{j}_bwd",
                road_name=name,
                road_type="primary" if abs(col) <= 1 else "secondary",
                start_lat=lat2,
                start_lon=lon2,
                end_lat=lat1,
                end_lon=lon1,
                length_m=extent * 2,
                heading_deg=180.0,
                speed_limit_kmh=50.0,
            )
            self.add_segment(seg_fwd)
            self.add_segment(seg_bwd)
