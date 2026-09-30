package com.logiclegend2.intellidr

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.*
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.logiclegend2.intellidr.engine.OnDeviceNavigationEngine
import com.logiclegend2.intellidr.model.VehicleTelemetry
import com.logiclegend2.intellidr.sensor.SensorCollector
import com.logiclegend2.intellidr.service.NavigationForegroundService
import com.logiclegend2.intellidr.ui.*
import com.logiclegend2.intellidr.ui.theme.IntelliDRTheme
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch

enum class AppScreen {
    NAVIGATION,
    JUDGE_MODE,
    COMPARISON,
    HEALTH,
    METRICS
}

class MainActivity : ComponentActivity() {

    private lateinit var engine: OnDeviceNavigationEngine
    private lateinit var sensorCollector: SensorCollector

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { perms ->
        val fineLocationGranted = perms[Manifest.permission.ACCESS_FINE_LOCATION] ?: false
        if (fineLocationGranted) {
            startNavigation()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        engine = OnDeviceNavigationEngine()
        sensorCollector = SensorCollector(this)

        checkAndRequestPermissions()

        setContent {
            IntelliDRTheme {
                var currentScreen by remember { mutableStateOf(AppScreen.JUDGE_MODE) }
                var telemetry by remember { mutableStateOf(engine.telemetry) }
                var isOutageSim by remember { mutableStateOf(false) }

                // System back button handler
                BackHandler(enabled = currentScreen != AppScreen.JUDGE_MODE) {
                    currentScreen = AppScreen.JUDGE_MODE
                }

                // Collect sensor updates in Compose
                LaunchedEffect(Unit) {
                    lifecycleScope.launch {
                        sensorCollector.imuFlow.collectLatest { imu ->
                            telemetry = engine.processIMU(imu)
                        }
                    }
                    lifecycleScope.launch {
                        sensorCollector.gnssFlow.collectLatest { gnss ->
                            telemetry = engine.processGNSS(gnss)
                        }
                    }
                }

                val toggleOutage: () -> Unit = {
                    isOutageSim = !isOutageSim
                    engine.triggerSimulatedOutage(isOutageSim)
                    telemetry = engine.telemetry
                }

                when (currentScreen) {
                    AppScreen.NAVIGATION -> {
                        NavigationScreen(
                            telemetry = telemetry,
                            isSimulatingOutage = isOutageSim,
                            onToggleOutage = toggleOutage,
                            onOpenJudgeMode = { currentScreen = AppScreen.JUDGE_MODE }
                        )
                    }
                    AppScreen.JUDGE_MODE -> {
                        SihJudgeScreen(
                            telemetry = telemetry,
                            isSimulatingOutage = isOutageSim,
                            onToggleOutage = toggleOutage,
                            onStartLiveTest = {
                                startNavigation()
                                currentScreen = AppScreen.NAVIGATION
                            },
                            onOpenComparison = { currentScreen = AppScreen.COMPARISON },
                            onOpenHealth = { currentScreen = AppScreen.HEALTH },
                            onOpenMetrics = { currentScreen = AppScreen.METRICS }
                        )
                    }
                    AppScreen.COMPARISON -> {
                        ComparisonScreen(onBack = { currentScreen = AppScreen.JUDGE_MODE })
                    }
                    AppScreen.HEALTH -> {
                        SensorHealthScreen(onBack = { currentScreen = AppScreen.JUDGE_MODE })
                    }
                    AppScreen.METRICS -> {
                        MetricsDashboardScreen(onBack = { currentScreen = AppScreen.JUDGE_MODE })
                    }
                }
            }
        }
    }

    private fun checkAndRequestPermissions() {
        val permissions = mutableListOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.POST_NOTIFICATIONS)
        }

        val allGranted = permissions.all {
            ContextCompat.checkSelfPermission(this, it) == PackageManager.PERMISSION_GRANTED
        }

        if (allGranted) {
            startNavigation()
        } else {
            permissionLauncher.launch(permissions.toTypedArray())
        }
    }

    private fun startNavigation() {
        sensorCollector.start()
        val intent = Intent(this, NavigationForegroundService::class.java).apply {
            action = NavigationForegroundService.ACTION_START
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        sensorCollector.stop()
    }
}
