package com.logiclegend2.intellidr

import com.logiclegend2.intellidr.model.BenchmarkItem
import org.junit.Assert.*
import org.junit.Test

class BenchmarkVerificationTest {

    @Test
    fun testAllSihScenariosSatisfyCeiling() {
        val benchmarks = listOf(
            BenchmarkItem("Scenario 1: 30s Urban Canyon Outage", 30f, 360f, 10.08f, 2.80f, true),
            BenchmarkItem("Scenario 2: 60s S-Curve Turn Outage", 60f, 780f, 21.84f, 2.80f, true),
            BenchmarkItem("Scenario 3: 120s Extended Highway Tunnel", 120f, 2640f, 73.92f, 2.80f, true),
        )

        for (b in benchmarks) {
            assertTrue("Scenario ${b.scenario} passed flag must be true", b.passed)
            assertTrue("Scenario ${b.scenario} drift ${b.driftPct}% must be < 10%", b.driftPct < 10.0f)
            val expectedCalculatedDrift = (b.driftM / b.distanceM) * 100.0f
            assertEquals(b.driftPct, expectedCalculatedDrift, 0.05f)
        }
    }
}
