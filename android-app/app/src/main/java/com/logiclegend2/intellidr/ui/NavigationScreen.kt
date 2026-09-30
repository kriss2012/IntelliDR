package com.logiclegend2.intellidr.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.logiclegend2.intellidr.model.OutageState
import com.logiclegend2.intellidr.model.VehicleTelemetry
import kotlin.math.*

/**
 * Primary Real-Time Navigation Screen
 * Displays dark vehicular map view, heading compass, speed HUD, and live telemetry.
 */
@Composable
fun NavigationScreen(
    telemetry: VehicleTelemetry,
    isSimulatingOutage: Boolean,
    onToggleOutage: () -> Unit,
    onOpenJudgeMode: () -> Unit
) {
    val darkBg = Color(0xFF090D16)
    val cardBg = Color(0xFF1E293B)

    val statusColor = when (telemetry.outageState) {
        OutageState.GNSS_AVAILABLE -> Color(0xFF10B981)
        OutageState.GNSS_RECOVERING -> Color(0xFF3B82F6)
        OutageState.GNSS_DEGRADED -> Color(0xFFF59E0B)
        OutageState.DEAD_RECKONING, OutageState.GNSS_LOST -> Color(0xFFEF4444)
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(darkBg)
    ) {
        // Center: Interactive Navigation Map Canvas
        Canvas(modifier = Modifier.fillMaxSize()) {
            val center = Offset(size.width / 2f, size.height / 2f)

            // Draw road grid lines
            drawLine(
                color = Color(0xFF334155),
                start = Offset(center.x, 0f),
                end = Offset(center.x, size.height),
                strokeWidth = 24.dp.toPx()
            )
            drawLine(
                color = Color(0xFF1E293B),
                start = Offset(0f, center.y),
                end = Offset(size.width, center.y),
                strokeWidth = 16.dp.toPx()
            )

            // Draw dashed center lane line
            val dashHeight = 20.dp.toPx()
            val dashSpace = 15.dp.toPx()
            var y = 0f
            while (y < size.height) {
                drawLine(
                    color = Color(0xFFFBBF24),
                    start = Offset(center.x, y),
                    end = Offset(center.x, y + dashHeight),
                    strokeWidth = 3.dp.toPx()
                )
                y += dashHeight + dashSpace
            }

            // Draw Vehicle Marker (Directional Chevron) rotated by heading
            val headRad = Math.toRadians((telemetry.headingDeg).toDouble())
            val markerSize = 22.dp.toPx()
            val tipX = center.x + markerSize * sin(headRad).toFloat()
            val tipY = center.y - markerSize * cos(headRad).toFloat()
            val leftX = center.x + (markerSize * 0.7f) * sin(headRad + 2.5).toFloat()
            val leftY = center.y - (markerSize * 0.7f) * cos(headRad + 2.5).toFloat()
            val rightX = center.x + (markerSize * 0.7f) * sin(headRad - 2.5).toFloat()
            val rightY = center.y - (markerSize * 0.7f) * cos(headRad - 2.5).toFloat()

            val markerPath = Path().apply {
                moveTo(tipX, tipY)
                lineTo(leftX, leftY)
                lineTo(center.x, center.y)
                lineTo(rightX, rightY)
                close()
            }
            drawPath(markerPath, color = Color(0xFF38BDF8))

            // Accuracy bubble
            drawCircle(
                color = statusColor.copy(alpha = 0.15f),
                radius = 35.dp.toPx(),
                center = center
            )
        }

        // Top HUD Overlay
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
                .align(Alignment.TopCenter)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Status pill
                Surface(
                    shape = RoundedCornerShape(20.dp),
                    color = statusColor.copy(alpha = 0.2f),
                    border = androidx.compose.foundation.BorderStroke(1.dp, statusColor)
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .size(8.dp)
                                .background(statusColor, CircleShape)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = telemetry.outageState.label,
                            color = statusColor,
                            fontWeight = FontWeight.Bold,
                            fontSize = 11.sp
                        )
                    }
                }

                // SIH Judge Mode button
                Button(
                    onClick = onOpenJudgeMode,
                    shape = RoundedCornerShape(20.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF3B82F6)),
                    contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                ) {
                    Text("SIH JUDGE MODE", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Road Name Banner
            Card(
                shape = RoundedCornerShape(10.dp),
                colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A).copy(alpha = 0.90f)),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 10.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Column {
                        Text("CURRENT ROAD (OFFLINE MAP)", color = Color(0xFF94A3B8), fontSize = 10.sp, fontWeight = FontWeight.Bold)
                        Text(telemetry.matchedRoadName, color = Color.White, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    }
                    Text("50 km/h", color = Color(0xFFFBBF24), fontWeight = FontWeight.Black, fontSize = 14.sp)
                }
            }
        }

        // Bottom Cockpit HUD Card
        Card(
            shape = RoundedCornerShape(topStart = 20.dp, topEnd = 20.dp),
            colors = CardDefaults.cardColors(containerColor = cardBg),
            modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.BottomCenter)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Speedometer
                    Row(verticalAlignment = Alignment.Bottom) {
                        Text(
                            text = "${telemetry.speedKmh.toInt()}",
                            color = Color.White,
                            fontSize = 42.sp,
                            fontWeight = FontWeight.Black,
                            fontFamily = FontFamily.Monospace
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "km/h",
                            color = Color(0xFF94A3B8),
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(bottom = 8.dp)
                        )
                    }

                    // Heading and Mode
                    Column(horizontalAlignment = Alignment.End) {
                        Text(
                            text = "HEADING: ${telemetry.headingDeg.toInt()}°",
                            color = Color(0xFF38BDF8),
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            fontFamily = FontFamily.Monospace
                        )
                        Text(
                            text = telemetry.fusionMode.label,
                            color = statusColor,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "Drift: %.1fm (%.1f%%)".format(telemetry.driftM, telemetry.driftPct),
                            color = Color(0xFF94A3B8),
                            fontSize = 11.sp
                        )
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))

                // Outage Action Button
                Button(
                    onClick = onToggleOutage,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (isSimulatingOutage) Color(0xFF10B981) else Color(0xFFEF4444)
                    ),
                    shape = RoundedCornerShape(10.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(48.dp)
                ) {
                    Text(
                        text = if (isSimulatingOutage) "RESTORE GNSS SIGNAL" else "SIMULATE GNSS OUTAGE (TUNNEL ENTRY)",
                        fontWeight = FontWeight.Bold,
                        fontSize = 13.sp
                    )
                }
            }
        }
    }
}
