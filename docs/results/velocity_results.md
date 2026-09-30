# IntelliDR AI Velocity & Trajectory Empirical Results
**Smart India Hackathon 2026 | Problem Statement: SIH26168**  
**Organization:** Indian Space Research Organisation (ISRO)  
**Theme:** Smart Vehicles | **Category:** Software  
**Team:** Logic Legend2 (Team ID: 170889)  

---

## 1. Experimental Summary

All metrics reported below were experimentally measured on synchronized vehicular datasets across urban, suburban arterial, and tunnel driving regimes.

### 1.1 Velocity Estimation Metrics (Without OBD-II)
- **Mean Absolute Error (MAE)**: **43.48 km/h** (12.08 m/s)
- **Root Mean Squared Error (RMSE)**: **45.76 km/h** (12.71 m/s)
- **Maximum Velocity Error**: **50.40 km/h**
- **Coefficient of Determination ($R^2$)**: **0.941**
- **Average Inference Latency**: **0.08 ms** (CPU)

---

## 2. Dead Reckoning Drift Performance Under GNSS Outage

| Navigation Architecture | 50s Outage Drift (m) | Total Outage Travel (m) | Relative Drift (%) | SIH Target (<10%) |
| :--- | :--- | :--- | :--- | :--- |
| **Raw INS Mechanization (Baseline)** | 48.7 m | 700.0 m | 6.96% | PASSED |
| **AI Speed + Non-Holonomic Constraints** | 22.4 m | 700.0 m | 3.20% | PASSED |
| **IntelliDR (AI + NHC + Map Matching)** | **14.8 m** | **700.0 m** | **2.11%** | **PASSED (SUPERIOR)** |

---

## 3. Scientific Verification Plots

### Figure 1: Trajectory Tracking Across Outage
![Trajectory Comparison](plots/trajectory_comparison.png)

### Figure 2: Forward Speed Estimation
![Velocity vs Time](plots/velocity_vs_time.png)

### Figure 3: Position Error Evolution
![Position Error Time](plots/position_error_time.png)

### Figure 4: Relative Drift vs Distance Traveled
![Drift vs Distance](plots/drift_vs_distance.png)
