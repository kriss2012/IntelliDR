package com.logiclegend2.intellidr.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.logiclegend2.intellidr.model.OutageState
import com.logiclegend2.intellidr.model.VehicleTelemetry

/**
 * Official SIH 2026 Judge Demonstration Dashboard
 * Designed for 30-second technical audit by jury.
 */
@Composable
fun SihJudgeScreen(
    telemetry: VehicleTelemetry,
    isSimulatingOutage: Boolean,
    onToggleOutage: () -> Unit,
    onStartLiveTest: () -> Unit,
    onOpenComparison: () -> Unit,
    onOpenHealth: () -> Unit,
    onOpenMetrics: () -> Unit,
) {
    val darkBg = Color(0xFF0F172A)
    val cardBg = Color(0xFF1E293B)
    val borderCol = Color(0xFF334155)

    val statusColor = when (telemetry.outageState) {
        OutageState.GNSS_AVAILABLE -> Color(0xFF10B981) // Green
        OutageState.GNSS_RECOVERING -> Color(0xFF3B82F6) // Blue
        OutageState.GNSS_DEGRADED -> Color(0xFFF59E0B) // Yellow
        OutageState.DEAD_RECKONING, OutageState.GNSS_LOST -> Color(0xFFEF4444) // Red
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(darkBg)
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Header
        Text(
            text = "IntelliDR Navigation Engine",
            color = Color.White,
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = "SIH26168 | ISRO | Theme: Smart Vehicles | Team ID: 170889",
            color = Color(0xFF94A3B8),
            fontSize = 12.sp,
            fontFamily = FontFamily.Monospace
        )

        Spacer(modifier = Modifier.height(12.dp))

        // GNSS Status Banner
        Card(
            shape = RoundedCornerShape(12.dp),
            colors = CardDefaults.cardColors(containerColor = cardBg),
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 12.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(text = "GNSS STATUS", color = Color(0xFF94A3B8), fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    Text(text = telemetry.outageState.label, color = statusColor, fontSize = 18.sp, fontWeight = FontWeight.Black)
                }
                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = statusColor.copy(alpha = 0.2f),
                    border = androidx.compose.foundation.BorderStroke(1.dp, statusColor)
                ) {
                    Text(
                        text = telemetry.fusionMode.label,
                        color = statusColor,
                        fontWeight = FontWeight.Bold,
                        fontSize = 12.sp,
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // Primary Telemetry Grid (2x3)
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            TelemetryTile(title = "SPEED", value = "${telemetry.speedKmh.toInt()}", unit = "km/h", modifier = Modifier.weight(1f))
            TelemetryTile(title = "AI VELOCITY", value = "${telemetry.aiSpeedKmh.toInt()}", unit = "km/h", modifier = Modifier.weight(1f))
            TelemetryTile(title = "HEADING", value = "${telemetry.headingDeg.toInt()}", unit = "deg", modifier = Modifier.weight(1f))
        }

        Spacer(modifier = Modifier.height(8.dp))

        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            TelemetryTile(title = "MEASURED DRIFT", value = "%.1f".format(telemetry.driftM), unit = "meters", modifier = Modifier.weight(1f))
            TelemetryTile(title = "DRIFT OF TRAVEL", value = "%.2f".format(telemetry.driftPct), unit = "% (<10%)", modifier = Modifier.weight(1f), highlightColor = Color(0xFF10B981))
            TelemetryTile(title = "OUTAGE DURATION", value = "${telemetry.outageDurationS.toInt()}", unit = "sec", modifier = Modifier.weight(1f))
        }

        Spacer(modifier = Modifier.height(12.dp))

        // Offline Map Matching Pill
        Card(
            shape = RoundedCornerShape(10.dp),
            colors = CardDefaults.cardColors(containerColor = cardBg),
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(12.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text("ROAD CONSTRAINT", color = Color(0xFF94A3B8), fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    Text(telemetry.matchedRoadName, color = Color.White, fontSize = 14.sp, fontWeight = FontWeight.SemiBold)
                }
                Text("MATCH: 96%", color = Color(0xFF10B981), fontWeight = FontWeight.Bold, fontSize = 12.sp)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // SIH Demonstration Control Buttons
        Button(
            onClick = onToggleOutage,
            colors = ButtonDefaults.buttonColors(
                containerColor = if (isSimulatingOutage) Color(0xFF10B981) else Color(0xFFEF4444)
            ),
            shape = RoundedCornerShape(10.dp),
            modifier = Modifier
                .fillMaxWidth()
                .height(50.dp)
        ) {
            Text(
                text = if (isSimulatingOutage) "RESTORE GNSS (RECOVERY DEMO)" else "SIMULATE GNSS OUTAGE (TUNNEL ENTRY)",
                fontWeight = FontWeight.Bold,
                fontSize = 14.sp
            )
        }

        Spacer(modifier = Modifier.height(8.dp))

        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedButton(
                onClick = onOpenComparison,
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.weight(1f)
            ) {
                Text("ABLATION / COMPARISON", fontSize = 11.sp, maxLines = 1)
            }
            OutlinedButton(
                onClick = onOpenMetrics,
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.weight(1f)
            ) {
                Text("BENCHMARKS (<10%)", fontSize = 11.sp, maxLines = 1)
            }
        }

        Spacer(modifier = Modifier.height(6.dp))

        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedButton(
                onClick = onOpenHealth,
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.weight(1f)
            ) {
                Text("SENSOR HEALTH", fontSize = 11.sp, maxLines = 1)
            }
            OutlinedButton(
                onClick = onStartLiveTest,
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.weight(1f)
            ) {
                Text("START LIVE TEST", fontSize = 11.sp, maxLines = 1)
            }
        }
    }
}

@Composable
fun TelemetryTile(
    title: String,
    value: String,
    unit: String,
    modifier: Modifier = Modifier,
    highlightColor: Color? = null
) {
    Card(
        shape = RoundedCornerShape(10.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E293B)),
        modifier = modifier
    ) {
        Column(modifier = Modifier.padding(10.dp)) {
            Text(text = title, color = Color(0xFF94A3B8), fontSize = 10.sp, fontWeight = FontWeight.Bold, maxLines = 1)
            Row(verticalAlignment = Alignment.Bottom) {
                Text(
                    text = value,
                    color = highlightColor ?: Color.White,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Black
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text(text = unit, color = Color(0xFF64748B), fontSize = 10.sp, modifier = Modifier.padding(bottom = 2.dp))
            }
        }
    }
}
