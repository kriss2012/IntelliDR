package com.logiclegend2.intellidr.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.os.PowerManager
import androidx.core.app.NotificationCompat
import com.logiclegend2.intellidr.sensor.SensorCollector
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel

/**
 * Foreground Service guaranteeing non-stop high-rate IMU polling and navigation
 * even when the mobile app is in the background or screen is turned off.
 */
class NavigationForegroundService : Service() {

    private val serviceScope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    private var wakeLock: PowerManager.WakeLock? = null
    private lateinit var sensorCollector: SensorCollector

    companion object {
        const val CHANNEL_ID = "intellidr_nav_channel"
        const val NOTIFICATION_ID = 26168
        const val ACTION_START = "ACTION_START_NAVIGATION"
        const val ACTION_STOP = "ACTION_STOP_NAVIGATION"
    }

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        sensorCollector = SensorCollector(this)

        val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
        wakeLock = powerManager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "IntelliDR:NavWakeLock").apply {
            setReferenceCounted(false)
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> {
                startForeground(NOTIFICATION_ID, buildNotification("IntelliDR Navigation Active", "Tracking GNSS+INS @ 100 Hz"))
                wakeLock?.acquire(12 * 60 * 60 * 1000L) // 12 hours max
                sensorCollector.start()
            }
            ACTION_STOP -> {
                sensorCollector.stop()
                if (wakeLock?.isHeld == true) wakeLock?.release()
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
        }
        return START_STICKY
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "IntelliDR Navigation Service",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Continuous background inertial navigation and dead reckoning"
            }
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }

    private fun buildNotification(title: String, text: String): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(title)
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_dialog_map)
            .setOngoing(true)
            .build()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        sensorCollector.stop()
        if (wakeLock?.isHeld == true) wakeLock?.release()
        serviceScope.cancel()
    }
}
