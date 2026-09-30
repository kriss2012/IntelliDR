package com.logiclegend2.intellidr.ui.responsive

import java.util.Locale

object Formatter {
    fun velocity(speedKmh: Number): String {
        return "%.1f".format(Locale.US, speedKmh.toDouble())
    }

    fun heading(deg: Number): String {
        val norm = ((deg.toDouble() % 360.0) + 360.0) % 360.0
        return "${norm.toInt()}°"
    }

    fun distance(meters: Number): String {
        val m = meters.toDouble()
        return if (m >= 1000.0) {
            "%.2f km".format(Locale.US, m / 1000.0)
        } else {
            "%.1f m".format(Locale.US, m)
        }
    }

    fun driftPct(pct: Number): String {
        return "%.2f%%".format(Locale.US, pct.toDouble())
    }

    fun driftMeters(meters: Number): String {
        return "%.2f m".format(Locale.US, meters.toDouble())
    }

    fun durationSeconds(seconds: Number): String {
        return "${seconds.toInt()} s"
    }

    fun frequency(hz: Number): String {
        return "%.1f Hz".format(Locale.US, hz.toDouble())
    }

    fun latency(ms: Number): String {
        return "%.2f ms".format(Locale.US, ms.toDouble())
    }
}
