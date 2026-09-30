package com.logiclegend2.intellidr.model

/**
 * IntelliDR Navigation Data Models
 * SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
 * Team: Logic Legend2 (Team ID: 170889)
 */

enum class OutageState(val label: String) {
    GNSS_AVAILABLE("GNSS AVAILABLE"),
    GNSS_DEGRADED("GNSS DEGRADED"),
    GNSS_LOST("GNSS LOST"),
    DEAD_RECKONING("DEAD RECKONING"),
    GNSS_RECOVERING("GNSS RECOVERING")
}

enum class FusionMode(val label: String) {
    INITIALIZING("INITIALIZING"),
    GNSS_INS("GNSS + INS"),
    AI_DEAD_RECKONING("AI DEAD RECKONING"),
    MAP_CONSTRAINED("MAP CONSTRAINED"),
    STATIONARY_ZUPT("STATIONARY ZUPT")
}

data class IMUReading(
    val timestampNs: Long,
    val ax: Float,
    val ay: Float,
    val az: Float,
    val gx: Float,
    val gy: Float,
    val gz: Float,
    val mx: Float? = null,
    val my: Float? = null,
    val mz: Float? = null
)

data class GNSSReading(
    val timestampMs: Long,
    val latitude: Double,
    val longitude: Double,
    val altitude: Double,
    val speedMps: Float,
    val bearingDeg: Float,
    val accuracyM: Float,
    val satellites: Int = 8,
    val isValid: Boolean = true
)

data class VehicleTelemetry(
    val timestamp: Long = System.currentTimeMillis(),
    val latitude: Double = 19.0760,
    val longitude: Double = 72.8777,
    val altitude: Double = 14.0,
    val speedKmh: Float = 0.0f,
    val aiSpeedKmh: Float = 0.0f,
    val headingDeg: Float = 0.0f,
    val rollDeg: Float = 0.0f,
    val pitchDeg: Float = 0.0f,
    val accuracyM: Float = 2.5f,
    val driftM: Float = 0.0f,
    val driftPct: Float = 0.0f,
    val distanceTraveledM: Float = 0.0f,
    val outageDurationS: Float = 0.0f,
    val outageState: OutageState = OutageState.GNSS_AVAILABLE,
    val fusionMode: FusionMode = FusionMode.GNSS_INS,
    val isMapMatched: Boolean = false,
    val matchedRoadName: String = "ISRO Space Highway"
)

data class SensorHealth(
    val imuRateHz: Float = 100.0f,
    val gnssRateHz: Float = 1.0f,
    val isAccelHealthy: Boolean = true,
    val isGyroHealthy: Boolean = true,
    val isMagHealthy: Boolean = true,
    val isGnssHealthy: Boolean = true,
    val isModelLoaded: Boolean = true,
    val isOfflineMapReady: Boolean = true,
    val cpuUsagePct: Float = 4.2f,
    val ramUsageMb: Float = 38.5f,
    val modelSizeBytes: Long = 1843200L
)

data class BenchmarkItem(
    val scenario: String,
    val outageS: Float,
    val distanceM: Float,
    val driftM: Float,
    val driftPct: Float,
    val passed: Boolean
)
