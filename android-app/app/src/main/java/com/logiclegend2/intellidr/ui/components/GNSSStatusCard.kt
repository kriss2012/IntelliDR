package com.logiclegend2.intellidr.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.logiclegend2.intellidr.model.OutageState
import com.logiclegend2.intellidr.model.VehicleTelemetry
import com.logiclegend2.intellidr.ui.theme.IntelliDRColors
import com.logiclegend2.intellidr.ui.theme.IntelliDRSpacing
import com.logiclegend2.intellidr.ui.theme.IntelliDRTypography

@Composable
fun GNSSStatusCard(
    telemetry: VehicleTelemetry,
    modifier: Modifier = Modifier
) {
    val (statusColor, badgeStyle) = when (telemetry.outageState) {
        OutageState.GNSS_AVAILABLE -> Pair(IntelliDRColors.Success, BadgeStyle.SUCCESS)
        OutageState.GNSS_RECOVERING -> Pair(IntelliDRColors.Info, BadgeStyle.INFO)
        OutageState.GNSS_DEGRADED -> Pair(IntelliDRColors.Warning, BadgeStyle.WARNING)
        OutageState.DEAD_RECKONING, OutageState.GNSS_LOST -> Pair(IntelliDRColors.Danger, BadgeStyle.DANGER)
    }

    Card(
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = IntelliDRColors.SurfaceCard),
        border = BorderStroke(1.dp, statusColor.copy(alpha = 0.4f)),
        modifier = modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(IntelliDRSpacing.standardCardPadding)
        ) {
            // Header Row: Status Label & Fusion Mode Badge
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.weight(1f, fill = false)
                ) {
                    Box(
                        modifier = Modifier
                            .size(10.dp)
                            .background(statusColor, CircleShape)
                    )
                    Spacer(modifier = Modifier.width(IntelliDRSpacing.sm))
                    Text(
                        text = "POSITIONING STATUS",
                        style = IntelliDRTypography.MetricLabel,
                        color = IntelliDRColors.TextMuted,
                        maxLines = 1
                    )
                }

                Spacer(modifier = Modifier.width(IntelliDRSpacing.sm))

                StatusBadge(
                    text = telemetry.fusionMode.label,
                    style = badgeStyle
                )
            }

            Spacer(modifier = Modifier.height(IntelliDRSpacing.xs))

            // Main State Label
            Text(
                text = telemetry.outageState.label,
                color = statusColor,
                fontSize = 19.sp,
                fontWeight = FontWeight.Black,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )

            Spacer(modifier = Modifier.height(IntelliDRSpacing.sm))

            // Sub-status telemetry metadata
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                val satInfo = if (telemetry.outageState == OutageState.GNSS_AVAILABLE) {
                    "Satellites: 10 Fix (NavIC+GPS)"
                } else {
                    "Satellites: 0 (Outage active)"
                }

                Text(
                    text = satInfo,
                    style = IntelliDRTypography.Subtitle,
                    color = IntelliDRColors.TextSecondary,
                    maxLines = 1
                )

                Text(
                    text = "Confidence: 98.4%",
                    style = IntelliDRTypography.Subtitle,
                    color = IntelliDRColors.Primary,
                    maxLines = 1
                )
            }
        }
    }
}
