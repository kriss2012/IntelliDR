# IntelliDR System Architecture & Engineering Blueprint
**Smart India Hackathon 2026 | Problem Statement: SIH26168**  
**Theme:** Smart Vehicles | **Category:** Software  
**Organization:** Indian Space Research Organisation (ISRO)  
**Team:** Logic Legend2 (Team ID: 170889)  

---

## 1. High-Level Architecture Overview

IntelliDR replaces the catastrophic failure mode of consumer GPS during signal outages with a multi-stage, physics-informed, AI-enhanced Dead Reckoning pipeline.

```
+-----------------------------------------------------------------------+
|                              SENSOR LAYER                             |
|  - Smartphone IMU (100 Hz)             - External / Industrial IMU    |
|  - GNSS / NavIC Receiver (1 Hz)        - UDP / Serial / CAN Stream    |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                     SYNCHRONIZATION & NORMALIZATION                   |
|  - Monotonic Timestamp Alignment       - Gap Interpolation (Linear)   |
|  - Outlier & Shock Spike Suppression   - Sensor Health Monitor (Hz)   |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                      PHONE-TO-VEHICLE ALIGNMENT                       |
|  - Static Gravity Vector Lock (Z-axis) - Longitudinal Accel Alignment |
|  - Gram-Schmidt Orthogonalization      - Continuous Tracking (R_p2v)  |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                        AI MOTION INTELLIGENCE                         |
|  - 16-D Spectral / Temporal Features   - Vibration & Noise Filtering  |
|  - Vertical Jerk Pothole Rejection     - 1D-CNN Zero-OBD Velocity Net |
|  - Kinematic Auto-Fallback Safety      - Motion State Classification  |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                    15-STATE ERROR-STATE EKF FUSION                    |
|  - INS Mechanization (Quaternion)      - Gravity Subtraction (ENU)    |
|  - State: [Pos, Vel, Attitude, Ba, Bg] - Process Noise Q & Cov P      |
|  - GNSS Measurement Update (Pos, Vel)  - AI Longitudinal Speed Update |
|  - Non-Holonomic Constraints (NHC)     - Zero Velocity Update (ZUPT)  |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                         OUTAGE STATE MANAGER                          |
|  - Multi-Metric Outage Detection       - Innovation Gating (Multipath)|
|  - Immediate Dead Reckoning Handoff    - Hermite Smoothstep Recovery  |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                     OFFLINE MAP MATCHING ENGINE                       |
|  - Local OSM GeoJSON Road Network      - Polyline Orthogonal Project  |
|  - Multi-Hypothesis Candidate Scoring  - Road Centerline Constraint   |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                       NAVIGATION USER INTERFACE                       |
|  - Native Android (Jetpack Compose)    - Standalone Edge Web / CLI    |
|  - SIH Judge Demo Screen               - One-Touch Outage Simulation  |
|  - Real-Time Telemetry HUD             - 4-Way Ablation Trajectories  |
+-----------------------------------------------------------------------+
```

---

## 2. Coordinate Systems & Conventions

1. **Smartphone Body Frame ($P$)**:
   - $X_p$: Right along screen width
   - $Y_p$: Up along screen length
   - $Z_p$: Out of screen toward user
2. **Vehicle Body Frame ($V$)**:
   - $X_v$: Forward along vehicle longitudinal axis
   - $Y_v$: Right along lateral axis
   - $Z_v$: Down toward ground
3. **Local Navigation Frame ($N$)**:
   - East-North-Up (ENU) right-handed Cartesian frame centered at session origin $(lat_0, lon_0, alt_0)$.
4. **Earth Frame (WGS84 / ECEF)**:
   - Geodetic coordinates (Latitude, Longitude, Altitude) mapped via WGS84 ellipsoidal transformations.
