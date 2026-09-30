package com.logiclegend2.intellidr

import androidx.compose.ui.unit.dp
import com.logiclegend2.intellidr.ui.responsive.Formatter
import com.logiclegend2.intellidr.ui.responsive.WindowHeightClass
import com.logiclegend2.intellidr.ui.responsive.WindowSizeInfo
import com.logiclegend2.intellidr.ui.responsive.WindowWidthClass
import org.junit.Assert.*
import org.junit.Test

class AdaptiveLayoutTest {

    @Test
    fun testWindowSizeClassBreakpoints() {
        // Compact Phone: 360 x 800 dp
        val compactPhone = WindowSizeInfo(
            widthClass = WindowWidthClass.Compact,
            heightClass = WindowHeightClass.Regular,
            widthDp = 360.dp,
            heightDp = 800.dp
        )
        assertTrue(compactPhone.isCompact)
        assertFalse(compactPhone.isMedium)
        assertFalse(compactPhone.isExpanded)
        assertFalse(compactPhone.isLandscapePhone)

        // Landscape Phone: 800 x 360 dp
        val landscapePhone = WindowSizeInfo(
            widthClass = WindowWidthClass.Medium,
            heightClass = WindowHeightClass.Compact,
            widthDp = 800.dp,
            heightDp = 360.dp
        )
        assertFalse(landscapePhone.isCompact)
        assertTrue(landscapePhone.isMedium)
        assertTrue(landscapePhone.isLandscapePhone)

        // Tablet Portrait: 768 x 1024 dp
        val tablet = WindowSizeInfo(
            widthClass = WindowWidthClass.Medium,
            heightClass = WindowHeightClass.Regular,
            widthDp = 768.dp,
            heightDp = 1024.dp
        )
        assertTrue(tablet.isMedium)
        assertFalse(tablet.isLandscapePhone)

        // Expanded Large Screen / Tablet Landscape: 1280 x 800 dp
        val largeScreen = WindowSizeInfo(
            widthClass = WindowWidthClass.Large,
            heightClass = WindowHeightClass.Regular,
            widthDp = 1280.dp,
            heightDp = 800.dp
        )
        assertTrue(largeScreen.isExpanded)
        assertFalse(largeScreen.isCompact)
    }

    @Test
    fun testTelemetryFormatterIntegrity() {
        assertEquals("36.0", Formatter.velocity(36.0f))
        assertEquals("0.0", Formatter.velocity(0.0))
        assertEquals("359°", Formatter.heading(359.2f))
        assertEquals("0°", Formatter.heading(360.0))
        assertEquals("10.08 m", Formatter.driftMeters(10.08f))
        assertEquals("2.80%", Formatter.driftPct(2.80f))
        assertEquals("30 s", Formatter.durationSeconds(30.0f))
        assertEquals("360.0 m", Formatter.distance(360.0f))
        assertEquals("2.64 km", Formatter.distance(2640.0f))
        assertEquals("100.0 Hz", Formatter.frequency(100.0f))
        assertEquals("0.08 ms", Formatter.latency(0.08f))
    }
}
