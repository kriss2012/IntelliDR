package com.logiclegend2.intellidr

import com.logiclegend2.intellidr.engine.OnDeviceNavigationEngine
import com.logiclegend2.intellidr.model.FusionMode
import com.logiclegend2.intellidr.model.IMUReading
import com.logiclegend2.intellidr.model.OutageState
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

class OnDeviceNavigationEngineTest {

    private lateinit var engine: OnDeviceNavigationEngine

    @Before
    fun setUp() {
        engine = OnDeviceNavigationEngine()
    }

    @Test
    fun testInitialEngineState() {
        val initialTelemetry = engine.telemetry
        assertEquals(OutageState.GNSS_AVAILABLE, initialTelemetry.outageState)
        assertEquals(FusionMode.GNSS_INS, initialTelemetry.fusionMode)
        assertEquals(0.0f, initialTelemetry.driftPct, 0.001f)
    }

    @Test
    fun testOutageSimulationTrigger() {
        // Trigger outage
        engine.triggerSimulatedOutage(true)
        val outageTelemetry = engine.telemetry
        assertEquals(OutageState.DEAD_RECKONING, outageTelemetry.outageState)
        assertEquals(FusionMode.AI_DEAD_RECKONING, outageTelemetry.fusionMode)

        // Trigger recovery
        engine.triggerSimulatedOutage(false)
        val recoveredTelemetry = engine.telemetry
        assertEquals(OutageState.GNSS_RECOVERING, recoveredTelemetry.outageState)
    }

    @Test
    fun testProcessIMUDuringDeadReckoning() {
        engine.triggerSimulatedOutage(true)
        val initialHeading = engine.telemetry.headingDeg

        val reading = IMUReading(
            timestampNs = System.nanoTime(),
            ax = 1.2f,
            ay = 0.0f,
            az = 9.81f,
            gx = 0.0f,
            gy = 0.0f,
            gz = 0.05f
        )
        val updated = engine.processIMU(reading)
        assertNotNull(updated)
        assertTrue(updated.driftPct < 10.0f)
    }
}
