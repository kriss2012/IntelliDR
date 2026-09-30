package com.logiclegend2.intellidr.sensor

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Bundle
import android.os.SystemClock
import com.logiclegend2.intellidr.model.GNSSReading
import com.logiclegend2.intellidr.model.IMUReading
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow

/**
 * Android Native Sensor Collector
 * Samples 100 Hz continuous IMU and 1 Hz GNSS using Android Location & Sensor frameworks.
 */
class SensorCollector(private val context: Context) : SensorEventListener, LocationListener {

    private val sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val locationManager = context.getSystemService(Context.LOCATION_SERVICE) as? LocationManager

    private val accel = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
    private val gyro = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)
    private val mag = sensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD)

    private val _imuFlow = MutableSharedFlow<IMUReading>(extraBufferCapacity = 200)
    val imuFlow: SharedFlow<IMUReading> = _imuFlow

    private val _gnssFlow = MutableSharedFlow<GNSSReading>(extraBufferCapacity = 10)
    val gnssFlow: SharedFlow<GNSSReading> = _gnssFlow

    private var latestAx = 0f
    private var latestAy = 0f
    private var latestAz = 9.81f
    private var latestGx = 0f
    private var latestGy = 0f
    private var latestGz = 0f
    private var latestMx: Float? = null
    private var latestMy: Float? = null
    private var latestMz: Float? = null

    var isRunning = false
        private set

    fun start() {
        if (isRunning) return
        isRunning = true

        accel?.let { sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_FASTEST) }
        gyro?.let { sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_FASTEST) }
        mag?.let { sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_GAME) }

        try {
            locationManager?.requestLocationUpdates(
                LocationManager.GPS_PROVIDER,
                1000L,
                0f,
                this
            )
        } catch (_: SecurityException) {
            // Handled via permission checks in UI
        }
    }

    fun stop() {
        if (!isRunning) return
        isRunning = false
        sensorManager.unregisterListener(this)
        locationManager?.removeUpdates(this)
    }

    override fun onSensorChanged(event: SensorEvent?) {
        if (event == null) return
        val tsNs = event.timestamp

        when (event.sensor.type) {
            Sensor.TYPE_ACCELEROMETER -> {
                latestAx = event.values[0]
                latestAy = event.values[1]
                latestAz = event.values[2]

                // Emit bundled 6-axis frame on accelerometer tick
                val reading = IMUReading(
                    timestampNs = tsNs,
                    ax = latestAx,
                    ay = latestAy,
                    az = latestAz,
                    gx = latestGx,
                    gy = latestGy,
                    gz = latestGz,
                    mx = latestMx,
                    my = latestMy,
                    mz = latestMz
                )
                _imuFlow.tryEmit(reading)
            }
            Sensor.TYPE_GYROSCOPE -> {
                latestGx = event.values[0]
                latestGy = event.values[1]
                latestGz = event.values[2]
            }
            Sensor.TYPE_MAGNETIC_FIELD -> {
                latestMx = event.values[0]
                latestMy = event.values[1]
                latestMz = event.values[2]
            }
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}

    override fun onLocationChanged(loc: Location) {
        val reading = GNSSReading(
            timestampMs = loc.time,
            latitude = loc.latitude,
            longitude = loc.longitude,
            altitude = loc.altitude,
            speedMps = if (loc.hasSpeed()) loc.speed else 0f,
            bearingDeg = if (loc.hasBearing()) loc.bearing else 0f,
            accuracyM = if (loc.hasAccuracy()) loc.accuracy else 5.0f,
            satellites = loc.extras?.getInt("satellites", 8) ?: 8,
            isValid = true
        )
        _gnssFlow.tryEmit(reading)
    }

    override fun onProviderEnabled(provider: String) {}
    override fun onProviderDisabled(provider: String) {}
    @Deprecated("Deprecated in Java")
    override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {}
}
