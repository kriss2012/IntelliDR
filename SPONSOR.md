# 🚗 IntelliDR — Sponsorship & Partnership Proposal

> **AI-ML Based Intelligent Dead Reckoning System for Seamless Navigation**

[![SIH 2026](https://img.shields.io/badge/SIH-2026-blue)](https://github.com/kriss2012/IntelliDR)
[![ISRO Problem Statement](https://img.shields.io/badge/Problem%20Statement-SIH26168-orange)](https://github.com/kriss2012/IntelliDR)
[![Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green)](https://github.com/kriss2012/IntelliDR/blob/main/LICENSE)

---

## 🌐 About IntelliDR

**IntelliDR** is an AI/ML-powered intelligent dead reckoning platform designed to maintain continuous vehicle navigation when GNSS/GPS signals become unavailable, degraded, jammed, spoofed, or unreliable.

The system is designed around a practical principle:

> **Navigation should not stop simply because satellite positioning temporarily disappears.**

IntelliDR combines smartphone/edge inertial sensing, AI-based velocity estimation, inertial navigation, a **15-State Error-State Extended Kalman Filter (ES-EKF)**, Non-Holonomic Constraints (NHC), Zero Velocity Updates (ZUPT), GNSS outage management, and offline OpenStreetMap-based map matching.

The project is developed for the **Smart India Hackathon 2026** problem statement **SIH26168 — “AI-ML based Intelligent Dead Reckoning system for seamless navigation”**, under the **Smart Vehicles** theme and associated with **ISRO**.

### Project Identity

| Item | Details |
|---|---|
| Project | **IntelliDR** |
| Full Name | AI-ML Based Intelligent Dead Reckoning System for Seamless Navigation |
| SIH Problem Statement | **SIH26168** |
| Organization | **Indian Space Research Organisation (ISRO)** |
| Theme | **Smart Vehicles** |
| Category | Software |
| Team | **Logic Legend2** |
| Team ID | **170889** |
| Repository | https://github.com/kriss2012/IntelliDR |
| License | Apache License 2.0 |

---

# 🎯 Why IntelliDR Matters

Modern navigation systems depend heavily on GNSS/GPS/NavIC. Satellite positioning can become unreliable in:

- 🚇 Underground and highway tunnels
- 🏙️ Dense urban environments and urban canyons
- 🏢 Multi-level parking structures
- 🌲 Mountainous and forest environments
- 🌉 Flyovers and complex road structures
- 📡 GNSS interference environments
- 🛰️ GNSS jamming or spoofing scenarios
- 🔌 Temporary satellite-signal outages

During these situations, a navigation system can experience position jumps, frozen locations, incorrect speed assumptions, or complete loss of reliable positioning.

**IntelliDR addresses the continuity problem by using onboard inertial measurements and AI-driven motion estimation to continue estimating vehicle movement during GNSS outages.**

---

# 💡 Core Innovation

IntelliDR is not based on a single algorithm. It is a multi-layer navigation architecture in which AI, inertial navigation, sensor fusion, constraints, and map intelligence work together.

## 1. 🧠 AI-Based Velocity Estimation

The system estimates forward vehicle velocity from inertial sensor information rather than requiring direct access to:

- OBD-II
- CAN bus
- Wheel-speed encoders
- Proprietary vehicle telemetry

The project README reports an empirical **AI velocity estimation MAE of approximately 1.2 km/h** for its evaluated setup.

The AI pipeline uses temporal/spectral inertial features and a lightweight **1D-CNN velocity model**, with a kinematic fallback path.

---

## 2. 📱 Automatic Phone-to-Vehicle Alignment

Smartphones may be mounted at different orientations inside vehicles.

IntelliDR estimates the relationship between the phone coordinate frame and vehicle coordinate frame using:

- Gravity vector estimation
- Forward acceleration
- Orthogonalization
- Continuous orientation tracking

This reduces dependence on a perfectly aligned phone mount.

---

## 3. 📐 15-State Error-State Kalman Filter

The navigation engine uses a **15-state Error-State Kalman Filter (ES-EKF)** to fuse inertial and auxiliary motion information.

The fusion architecture incorporates:

- IMU mechanization
- AI velocity updates
- Non-Holonomic Constraints
- Zero Velocity Updates
- GNSS measurements when available
- Innovation gating
- Outage-state management

This allows the system to constrain error growth instead of relying on unconstrained inertial integration.

---

## 4. 🚘 Non-Holonomic Constraints

For normal road vehicles, lateral and vertical body-frame velocity are strongly constrained.

IntelliDR uses the approximate constraints:

```text
v_y ≈ 0
v_z ≈ 0
```

These constraints help reduce physically implausible motion estimates during GNSS-denied operation.

---

## 5. 🛑 Zero Velocity Updates

When the vehicle is detected as stationary, ZUPT updates can be used to reduce accumulated inertial navigation error.

This provides an additional correction mechanism during stops and low-motion periods.

---

## 6. 🗺️ Offline Map Matching

IntelliDR includes an offline OpenStreetMap-based road matching layer.

The system can use locally available road geometry to constrain the estimated trajectory toward plausible road centerlines.

The architecture includes:

- Polyline projection
- Heading similarity
- Distance scoring
- Centerline constraints
- Multi-hypothesis road matching

The goal is to maintain useful navigation behavior without depending on a live internet connection.

---

## 7. 🔄 Seamless GNSS Recovery

When GNSS becomes available again, IntelliDR does not simply replace the dead-reckoned position with a new GNSS coordinate.

A **Hermite smoothstep recovery/blending mechanism** is used to reduce abrupt position transitions and velocity spikes.

This is important for a user-facing navigation experience where sudden marker jumps are undesirable.

---

# 🏗️ System Architecture

```text
┌──────────────────────────────────────────────┐
│              SENSOR LAYER                    │
│ Accelerometer • Gyroscope • Magnetometer    │
│ GNSS/NavIC • External/FOG IMU               │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│        SENSOR SYNCHRONIZATION                │
│ Timestamping • Interpolation • Filtering     │
│ Frequency & sensor-health monitoring         │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│       PHONE / VEHICLE ALIGNMENT              │
│ Gravity Vector • Forward Acceleration        │
│ Coordinate-frame transformation              │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│          AI MOTION INTELLIGENCE              │
│ Spectral/Temporal Features • 1D-CNN          │
│ Engine vibration features • Fallback model   │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│        GNSS / INS FUSION ENGINE              │
│ INS • 15-State ES-EKF • NHC • ZUPT           │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│          GNSS OUTAGE MANAGER                 │
│ Degradation Detection • Innovation Gating    │
│ DR Handoff • Smooth GNSS Recovery            │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│          OFFLINE MAP MATCHING                │
│ OpenStreetMap • Road Projection • Heading    │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│       MOBILE / EDGE NAVIGATION              │
│ Android • Edge Engine • Telemetry HUD        │
└──────────────────────────────────────────────┘
```

---

# 📊 Empirical Benchmark Results

The repository documents reproducible benchmark scenarios generated through the IntelliDR benchmark command.

### Reported Drift Performance

| Scenario | GNSS Outage | Distance | Measured Drift | Relative Drift | Target |
|---|---:|---:|---:|---:|---:|
| Urban Canyon Outage | 30 s | 360 m | 10.08 m | **2.80%** | < 10% |
| S-Curve Turn & Cruise | 60 s | 780 m | 21.84 m | **2.80%** | < 10% |
| Highway Tunnel Outage | 120 s | 2640 m | 73.92 m | **2.80%** | < 10% |

> **Important:** These figures are the values currently documented in the public IntelliDR repository and should be treated as project benchmark results for the stated test scenarios, not as a universal guarantee for every vehicle, phone, road, or environment.

### Execution Profiling Reported by the Project

| Metric | Reported Result |
|---|---:|
| Navigation update rate | **100 Hz** |
| Edge throughput | **>700 samples/sec** |
| AI velocity inference latency | **0.08 ms** on the reported single-core test |
| Offline map-matching query latency | **35 µs** |
| Process memory footprint | **38.5 MB** |
| Continuous CPU utilization | **4.2%** |

---

# 🔬 Ablation Study

The project also documents an ablation comparison showing the contribution of successive navigation components.

| Architecture | 60 s Outage Drift | Relative Drift |
|---|---:|---:|
| Raw INS baseline | 54.2 m | 6.95% |
| INS + AI Velocity | 26.4 m | 3.38% |
| AI + 15-State EKF + NHC | 18.6 m | 2.38% |
| IntelliDR Full Stack + Map | 14.2 m | 1.82% |

The purpose of this experiment is to demonstrate that the system's performance comes from the **combined navigation architecture**, rather than attributing the result to AI alone.

---

# 🧪 Engineering & Verification

The repository contains a structured engineering stack covering:

- Automated benchmark execution
- ML training and evaluation
- Edge navigation engine
- Android application
- Backend telemetry APIs
- Offline demonstration package
- Unit and integration tests
- Red-team testing
- Automated final audit
- Documentation
- Docker-based deployment support

The current repository structure includes:

```text
android-app/       → Android Jetpack Compose application
backend/           → FastAPI REST/WebSocket telemetry server
benchmark/         → Drift and latency benchmarks
data/              → Driving logs and processed sequences
demo-package/      → Offline demonstration package
docs/              → Engineering documentation
edge/              → Edge navigation engine
maps/              → Offline road-network data
ml/                → Training and evaluation pipeline
scripts/            → Automation and audit scripts
tests/             → Automated tests
```

---

# 📱 Product Direction

IntelliDR is designed as a technology platform that can evolve from a research/hackathon prototype toward real-world mobility applications.

Potential application areas include:

### 🚗 Automotive
- Navigation continuity
- Driver assistance support
- GNSS-denied positioning
- Fleet navigation resilience

### 🚚 Logistics & Fleet Management
- Vehicle tracking continuity
- Route monitoring
- Tunnel and urban-canyon operation
- Offline/edge telemetry

### 🏙️ Smart Mobility
- Resilient urban navigation
- Intelligent transportation systems
- Road analytics
- Connected mobility platforms

### 🛰️ Aerospace & Defense-Oriented Research
- GNSS-denied navigation research
- Sensor-fusion experimentation
- Resilient positioning research
- Edge navigation algorithms

### 🤖 Robotics & Autonomous Systems
- Ground robots
- Delivery robots
- Indoor/outdoor transition
- GPS-denied mobility research

> These are potential application and research directions, not claims that IntelliDR is currently certified or production-approved for any of these sectors.

---

# 🤝 Why Sponsor IntelliDR?

Sponsoring IntelliDR means supporting practical student-led research at the intersection of:

**Artificial Intelligence + Machine Learning + Robotics + Navigation + Embedded Systems + Mobile Computing + Geospatial Technology**

A sponsor can contribute not only funding, but also technology, infrastructure, mentorship, testing resources, hardware, datasets, cloud credits, or industry expertise.

The project can become a collaborative platform for experimenting with resilient navigation technologies.

---

# 💼 Sponsorship Opportunities

We welcome organizations interested in supporting the continued development, validation, and demonstration of IntelliDR.

## 1. 💰 Financial Sponsorship

Funding can support:

- Sensor and IMU hardware
- Smartphone/device testing
- Vehicle testing
- Edge computing hardware
- Cloud infrastructure
- Data collection
- Model training
- Field validation
- Demonstration infrastructure
- Research and documentation

### Suggested Sponsorship Structure

| Level | Suggested Contribution | Possible Recognition |
|---|---:|---|
| Community Supporter | ₹5,000+ | Sponsor acknowledgement |
| Technology Supporter | ₹25,000+ | Logo + project acknowledgement |
| Innovation Partner | ₹50,000+ | Prominent acknowledgement + technical collaboration |
| Research Partner | ₹1,00,000+ | Research collaboration + project visibility |
| Strategic Partner | Custom | Customized collaboration package |

> These levels are **proposed sponsorship categories**, not fixed commercial prices. Sponsorship terms can be customized according to the organization's goals and applicable institutional rules.

---

# 🧰 Technology Sponsorship

Organizations can support IntelliDR by providing:

### Hardware
- IMU sensors
- GNSS receivers
- FOG/INS hardware
- Android test devices
- Edge AI boards
- Embedded computers
- Vehicle diagnostic/testing equipment

### Software & Infrastructure
- Cloud credits
- AI/ML compute
- Map/geospatial services
- Developer tooling
- Testing platforms
- CI/CD infrastructure
- Observability platforms

### Data
- Anonymized driving datasets
- Sensor datasets
- Road-network datasets
- GNSS-denied scenario data
- Vehicle motion datasets

---

# 🧑‍🏫 Mentorship & Technical Partnership

Industry experts can contribute through:

- Navigation-system mentoring
- Sensor-fusion reviews
- ML model optimization
- Embedded AI guidance
- Automotive engineering reviews
- Architecture reviews
- Security reviews
- Field-testing guidance
- Product development mentorship

This can create a bridge between academic innovation and industry engineering practices.

---

# 🚘 Vehicle & Field Testing Partnership

Real-world validation is one of the most valuable future development areas.

Potential partners can help provide access to:

- Test vehicles
- Controlled driving environments
- Tunnels
- Private roads
- Test tracks
- Urban driving routes
- GNSS-denied testing environments

The objective would be to expand validation beyond simulation and controlled benchmark datasets.

---

# 📈 What Sponsors Can Gain

Depending on the partnership arrangement, sponsors may receive:

### Brand Visibility
- Sponsor acknowledgement in project materials
- Logo placement where appropriate
- Recognition in presentations and demonstrations
- Event/demo acknowledgements

### Technical Engagement
- Technical discussions with the development team
- Demonstrations of the IntelliDR architecture
- Opportunities to provide engineering feedback
- Potential research collaboration

### Innovation Exposure
Sponsors can engage with a student-built AI navigation system combining:

- Machine learning
- Sensor fusion
- Inertial navigation
- Mobile computing
- Geospatial intelligence
- Edge AI

### Talent & Community Engagement
Potential opportunities include:

- Technical workshops
- Mentorship
- Student interaction
- Engineering talks
- Hackathon collaboration
- Internship/project exploration

> Specific sponsor benefits should be agreed in writing before any commitment and should comply with applicable event, institutional, and organizational policies.

---

# 🛣️ Development Roadmap

## Phase 1 — Current Research Prototype

- AI velocity estimation
- Sensor synchronization
- Phone-to-vehicle alignment
- 15-State ES-EKF
- NHC
- ZUPT
- GNSS outage management
- Offline map matching
- Android demonstration
- Automated benchmarks

## Phase 2 — Hardware Validation

- Dedicated IMU integration
- Higher-quality GNSS/INS reference systems
- Edge-device benchmarking
- Multi-device testing
- Hardware-in-the-loop testing

## Phase 3 — Real-World Validation

- Controlled vehicle experiments
- Tunnel testing
- Urban-canyon testing
- Long-duration outage testing
- Multiple vehicle platforms
- Diverse phone mounting configurations

## Phase 4 — Optimization

- Model quantization
- Edge acceleration
- Energy optimization
- Improved calibration
- Robustness testing
- Expanded map-matching intelligence

## Phase 5 — Platform Development

- Developer SDK
- Navigation APIs
- Fleet integration
- Research APIs
- Visualization dashboards
- Industry pilot integrations

---

# 🔐 Responsible Development

IntelliDR is being developed as a navigation-research and engineering project.

The team recognizes that positioning systems can be safety-critical. Therefore, future production deployment would require:

- Extensive real-world validation
- Hardware characterization
- Safety analysis
- Cybersecurity assessment
- Failure-mode testing
- Regulatory/compliance review
- Independent verification
- Clearly defined operational limitations

**Prototype benchmark performance must not be interpreted as a safety certification or production guarantee.**

---

# 🌟 Sponsorship Philosophy

We are looking for partners who want to support **engineering innovation, student research, resilient mobility, and practical AI development**.

The ideal partnership is more than a logo placement.

It can be:

> **Industry expertise + technology + research + student innovation = real-world engineering impact**

---

# 📬 Partnership Contact

### Project

**IntelliDR — AI-ML Based Intelligent Dead Reckoning System**

### Team

**Logic Legend2**

### Team ID

**170889**

### Repository

**https://github.com/kriss2012/IntelliDR**

For sponsorship discussions, technical collaboration, hardware support, mentorship, or research partnership, please use the contact information maintained by the project team/repository.

---

# 🚀 How You Can Support

You can support IntelliDR through:

- 💰 Financial sponsorship
- 🧠 Technical mentorship
- 🚗 Vehicle/testing access
- 📡 Navigation hardware
- 📱 Android testing devices
- 🖥️ Edge-AI hardware
- ☁️ Cloud/compute credits
- 📊 Research datasets
- 🗺️ Geospatial resources
- 🧪 Testing infrastructure
- 🎓 Industry workshops
- 🤝 Research collaboration

Every form of support can help move the project from a validated prototype toward broader experimental and real-world evaluation.

---

# ⭐ Repository

Explore the complete technical implementation:

**https://github.com/kriss2012/IntelliDR**

The repository contains the Android application, edge engine, ML pipeline, benchmark suite, offline demo package, backend, tests, maps, and engineering documentation.

---
## 🤝 Sponsor IntelliDR

IntelliDR is an AI/ML-based intelligent dead reckoning platform developed to maintain navigation continuity during GNSS/GPS outages.

If your organization is interested in supporting:

- 🚗 resilient vehicle navigation research
- 🧠 AI/ML and sensor-fusion development
- 📡 GNSS-denied navigation experiments
- 🛰️ edge navigation and positioning research
- 🧪 real-world vehicle validation
- 🎓 student-led engineering innovation

you can explore the project's sponsorship and partnership opportunities:

### 💙 Support the Project

**[→ View the IntelliDR Sponsorship Proposal](./SPONSOR.md)**

Support can include financial sponsorship, navigation/IMU hardware, Android test devices, edge-AI hardware, cloud credits, datasets, vehicle testing access, technical mentorship, or research collaboration.

> **Keep Moving. Even When GNSS Doesn't.**
> 

# 📜 License

IntelliDR is distributed under the **Apache License 2.0** as documented in the repository.

Please review the repository license and third-party component licenses before using the project commercially or integrating it into another system.

---

## ❤️ Thank You

Thank you to organizations, mentors, researchers, engineers, educators, developers, and technology partners who support student innovation and open technical experimentation.

**IntelliDR is an attempt to make vehicle navigation more resilient when GNSS cannot be trusted or temporarily disappears.**

> ### 🚗 Keep Moving. Even When GNSS Doesn't.
