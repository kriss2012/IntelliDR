"""
Unit & Integration Tests for GNSS Outage Transition, Map Matching & Benchmarks
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
"""

import math
import numpy as np
import pytest

from intellidr_core.outage_manager import GNSSOutageManager
from intellidr_core.sensor_types import GNSSSample, OutageState
from intellidr_core.offline_map import OfflineMapProvider, RoadSegment
from intellidr_core.map_matcher import MapMatcher
from benchmark.evaluate_drift import DriftEvaluator


def test_gnss_outage_lifecycle():
    mgr = GNSSOutageManager(timeout_degraded_s=1.0, timeout_lost_s=2.0)

    # 1. Healthy sample
    sample = GNSSSample(timestamp=10.0, latitude=19.0760, longitude=72.8777, horizontal_accuracy_m=3.0)
    state, usable = mgr.evaluate_gnss_sample(sample)
    assert state == OutageState.GNSS_AVAILABLE
    assert usable

    # 2. Timeout to degraded
    state = mgr.check_timeout(11.2)
    assert state == OutageState.GNSS_DEGRADED

    # 3. Timeout to lost / dead reckoning
    state = mgr.check_timeout(12.5)
    assert state == OutageState.DEAD_RECKONING

    # 4. Recovery
    rec_sample = GNSSSample(timestamp=13.0, latitude=19.0761, longitude=72.8778, horizontal_accuracy_m=3.5)
    state, usable = mgr.evaluate_gnss_sample(rec_sample)
    assert state == OutageState.GNSS_RECOVERING


def test_map_matching_orthogonal_projection():
    provider = OfflineMapProvider(19.0760, 72.8777, 10.0)
    # Add East-West arterial road segment along North = 0 from East = 0 to 500m
    seg = RoadSegment(
        segment_id="test_road_1",
        road_name="Test Expressway",
        road_type="primary",
        start_lat=19.0760,
        start_lon=72.8777,
        end_lat=19.0760,
        end_lon=72.8820,
        length_m=450.0,
        heading_deg=90.0
    )
    provider.add_segment(seg)

    matcher = MapMatcher(provider, search_radius_m=30.0)

    # Test point offset 8 meters North of road centerline
    test_enu = np.array([100.0, 8.0, 0.0])
    match_result = matcher.match(test_enu, heading_deg=90.0, speed_mps=15.0)

    assert match_result.is_matched
    assert match_result.confidence > 0.70
    assert abs(match_result.lateral_offset_m - 8.0) < 0.5


def test_drift_benchmark_threshold_compliance():
    evaluator = DriftEvaluator(target_drift_threshold_pct=10.0)

    # 500 meters traveled ground truth
    n_points = 500
    t = np.linspace(0, 500, n_points)
    gt = np.column_stack([t, np.zeros(n_points), np.zeros(n_points)])

    # Estimated trajectory with 12m drift at end (12 / 500 = 2.4%)
    drift_ramp = np.linspace(0, 12, n_points)
    est = np.column_stack([t, drift_ramp, np.zeros(n_points)])

    res = evaluator.compute_metrics(
        scenario_name="500m Outage Test",
        outage_duration_s=35.0,
        ground_truth_enu=gt,
        estimated_enu=est
    )

    assert res.distance_traveled_m >= 499.0
    assert abs(res.absolute_drift_m - 12.0) < 0.1
    assert abs(res.percentage_drift - 2.4) < 0.1
    assert res.passed_sih_benchmark  # 2.4% strictly < 10.0%
