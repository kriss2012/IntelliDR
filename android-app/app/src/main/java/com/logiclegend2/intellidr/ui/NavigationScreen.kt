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
import com.logiclegend2.intellidr.ui.components.PrimaryActionButton
import com.logiclegend2.intellidr.ui.components.StatusBadge
import com.logiclegend2.intellidr.ui.components.BadgeStyle
import com.logiclegend2.intellidr.ui.responsive.Formatter
import com.logiclegend2.intellidr.ui.responsive.rememberWindowSizeInfo
import com.logiclegend2.intellidr.ui.theme.IntelliDRColors
import com.logiclegend2.intellidr.ui.theme.IntelliDRSpacing
import com.logiclegend2.intellidr.ui.theme.IntelliDRTypography
import kotlin.math.cos
import kotlin.math.sin

/**
 * Primary Real-Time Navigation Cockpit Screen
 * Displays dark vehicular map view, heading compass, speed HUD, and live telemetry.
 * Fully inset-aware and responsive across portrait, landscape, and tablets.
 */
@Composable
fun NavigationScreen(
    telemetry: VehicleTelemetry,
    isSimulatingOutage: Boolean,
    onToggleOutage: () -> Unit,
    onOpenJudgeMode: () -> Unit
) {
    val windowInfo = rememberWindowSizeInfo()
    val isTwoPane = windowInfo.isExpanded || (windowInfo.isMedium && windowInfo.isLandscapePhone)

    val (statusColor, badgeStyle) = when (telemetry.outageState) {
        OutageState.GNSS_AVAILABLE -> Pair(IntelliDRColors.Success, BadgeStyle.SUCCESS)
        OutageState.GNSS_RECOVERING -> Pair(IntelliDRColors.Info, BadgeStyle.INFO)
        OutageState.GNSS_DEGRADED -> Pair(IntelliDRColors.Warning, BadgeStyle.WARNING)
        OutageState.DEAD_RECKONING, OutageState.GNSS_LOST -> Pair(IntelliDRColors.Danger, BadgeStyle.DANGER)
    }

    if (isTwoPane) {
        // Landscape & Tablet 2-Pane Navigation Cockpit
        Scaffold(
            containerColor = IntelliDRColors.Background
        ) { innerPadding ->
            Row(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding)
                    .windowInsetsPadding(WindowInsets.safeDrawing)
            ) {
                // Left: Map Canvas
                Box(
                    modifier = Modifier
                        .weight(1.2f)
                        .fillMaxHeight()
                ) {
                    NavigationMapCanvas(telemetry = telemetry, statusColor = statusColor)

                    // Map Overlay: Road Name Pill
                    Surface(
                        shape = RoundedCornerShape(10.dp),
                        color = IntelliDRColors.SurfaceCard.copy(alpha = 0.90f),
                        border = androidx.compose.foundation.BorderStroke(1.dp, IntelliDRColors.SurfaceBorder),
                        modifier = Modifier
                            .align(Alignment.TopStart)
                            .padding(IntelliDRSpacing.md)
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "ROAD: ${telemetry.matchedRoadName}",
                                style = IntelliDRTypography.Subtitle,
                                color = IntelliDRColors.TextPrimary
                            )
                        }
                    }
                }

                // Right: Cockpit Controls & Telemetry
                Column(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxHeight()
                        .background(IntelliDRColors.Surface)
                        .padding(IntelliDRSpacing.lg),
                    verticalArrangement = Arrangement.SpaceBetween
                ) {
                    Column(verticalArrangement = Arrangement.spacedBy(IntelliDRSpacing.md)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            StatusBadge(text = telemetry.outageState.label, style = badgeStyle)
                            Button(
                                onClick = onOpenJudgeMode,
                                shape = RoundedCornerShape(8.dp),
                                colors = ButtonDefaults.buttonColors(containerColor = IntelliDRColors.PrimaryMuted),
                                contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                            ) {
                                Text("JUDGE CONTROL", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                            }
                        }

                        // Speedometer & Telemetry
                        Row(verticalAlignment = Alignment.Bottom) {
                            Text(
                                text = "${telemetry.speedKmh.toInt()}",
                                style = IntelliDRTypography.MetricValueLarge,
                                fontSize = 46.sp
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = "km/h",
                                style = IntelliDRTypography.MetricUnit,
                                fontSize = 14.sp,
                                modifier = Modifier.padding(bottom = 6.dp)
                            )
                        }

                        Text(
                            text = "HEADING: ${Formatter.heading(telemetry.headingDeg)} | AI VEL: ${Formatter.velocity(telemetry.aiSpeedKmh)} km/h",
                            style = IntelliDRTypography.Subtitle,
                            color = IntelliDRColors.Primary
                        )

                        Text(
                            text = "DRIFT: ${Formatter.driftMeters(telemetry.driftM)} (${Formatter.driftPct(telemetry.driftPct)})",
                            style = IntelliDRTypography.Subtitle,
                            color = if (telemetry.driftPct < 10.0) IntelliDRColors.Success else IntelliDRColors.Danger
                        )

                        Text(
                            text = "FUSION: ${telemetry.fusionMode.label}",
                            style = IntelliDRTypography.Subtitle,
                            color = IntelliDRColors.TextSecondary
                        )
                    }

                    PrimaryActionButton(
                        isSimulatingOutage = isSimulatingOutage,
                        onClick = onToggleOutage
                    )
                }
            }
        }
    } else {
        // Portrait Mobile Fullscreen Cockpit with Safe Insets
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(IntelliDRColors.Background)
        ) {
            // Background: Interactive Map Canvas
            NavigationMapCanvas(
                telemetry = telemetry,
                statusColor = statusColor,
                modifier = Modifier.fillMaxSize()
            )

            // Top HUD Overlay: System status & Navigation Header
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .windowInsetsPadding(WindowInsets.statusBars)
                    .padding(horizontal = IntelliDRSpacing.lg, vertical = IntelliDRSpacing.sm)
                    .align(Alignment.TopCenter)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    StatusBadge(text = telemetry.outageState.label, style = badgeStyle)

                    Button(
                        onClick = onOpenJudgeMode,
                        shape = RoundedCornerShape(20.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = IntelliDRColors.PrimaryMuted),
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                    ) {
                        Text("SIH JUDGE MODE", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    }
                }

                Spacer(modifier = Modifier.height(IntelliDRSpacing.sm))

                // Road Name Banner
                Surface(
                    shape = RoundedCornerShape(10.dp),
                    color = IntelliDRColors.SurfaceCard.copy(alpha = 0.90f),
                    border = androidx.compose.foundation.BorderStroke(1.dp, IntelliDRColors.SurfaceBorder),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 14.dp, vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text("OFFLINE ROAD GRAPH", style = IntelliDRTypography.MetricLabel)
                            Text(telemetry.matchedRoadName, style = IntelliDRTypography.CardTitle)
                        }
                        Text(
                            text = "50 km/h",
                            color = IntelliDRColors.RoadCenterline,
                            fontWeight = FontWeight.Black,
                            fontSize = 13.sp
                        )
                    }
                }
            }

            // Bottom Cockpit HUD: Speedometer, Heading, Outage Action
            Surface(
                shape = RoundedCornerShape(topStart = 20.dp, topEnd = 20.dp),
                color = IntelliDRColors.SurfaceCard,
                border = androidx.compose.foundation.BorderStroke(1.dp, IntelliDRColors.SurfaceBorder),
                modifier = Modifier
                    .fillMaxWidth()
                    .align(Alignment.BottomCenter)
                    .windowInsetsPadding(WindowInsets.navigationBars)
            ) {
                Column(modifier = Modifier.padding(IntelliDRSpacing.lg)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.Bottom) {
                            Text(
                                text = "${telemetry.speedKmh.toInt()}",
                                style = IntelliDRTypography.MetricValueLarge,
                                fontSize = 40.sp
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = "km/h",
                                style = IntelliDRTypography.MetricUnit,
                                fontSize = 13.sp,
                                modifier = Modifier.padding(bottom = 6.dp)
                            )
                        }

                        Column(horizontalAlignment = Alignment.End) {
                            Text(
                                text = "HEADING: ${Formatter.heading(telemetry.headingDeg)}",
                                style = IntelliDRTypography.Subtitle,
                                color = IntelliDRColors.Primary
                            )
                            Text(
                                text = telemetry.fusionMode.label,
                                style = IntelliDRTypography.Subtitle,
                                color = statusColor
                            )
                            Text(
                                text = "Drift: ${Formatter.driftMeters(telemetry.driftM)} (${Formatter.driftPct(telemetry.driftPct)})",
                                style = IntelliDRTypography.Subtitle,
                                color = if (telemetry.driftPct < 10.0) IntelliDRColors.Success else IntelliDRColors.Danger
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(IntelliDRSpacing.md))

                    PrimaryActionButton(
                        isSimulatingOutage = isSimulatingOutage,
                        onClick = onToggleOutage
                    )
                }
            }
        }
    }
}

@Composable
fun NavigationMapCanvas(
    telemetry: VehicleTelemetry,
    statusColor: Color,
    modifier: Modifier = Modifier
) {
    Canvas(modifier = modifier) {
        val center = Offset(size.width / 2f, size.height / 2f)

        // Road Lines
        drawLine(
            color = IntelliDRColors.RoadAsphalt,
            start = Offset(center.x, 0f),
            end = Offset(center.x, size.height),
            strokeWidth = 24.dp.toPx()
        )
        drawLine(
            color = IntelliDRColors.SurfaceElevated,
            start = Offset(0f, center.y),
            end = Offset(size.width, center.y),
            strokeWidth = 16.dp.toPx()
        )

        // Dashed Centerline
        val dashHeight = 20.dp.toPx()
        val dashSpace = 15.dp.toPx()
        var y = 0f
        while (y < size.height) {
            drawLine(
                color = IntelliDRColors.RoadCenterline,
                start = Offset(center.x, y),
                end = Offset(center.x, y + dashHeight),
                strokeWidth = 3.dp.toPx()
            )
            y += dashHeight + dashSpace
        }

        // Vehicle Chevron Directional Marker
        val headRad = Math.toRadians(telemetry.headingDeg.toDouble())
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
        drawPath(markerPath, color = IntelliDRColors.Primary)

        // Positional uncertainty bubble
        drawCircle(
            color = statusColor.copy(alpha = 0.15f),
            radius = 35.dp.toPx(),
            center = center
        )
    }
}
