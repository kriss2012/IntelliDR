package com.logiclegend2.intellidr.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.logiclegend2.intellidr.ui.theme.IntelliDRColors
import com.logiclegend2.intellidr.ui.theme.IntelliDRSpacing
import com.logiclegend2.intellidr.ui.theme.IntelliDRTypography

@Composable
fun AblationCard(
    tier: String,
    driftM: String,
    driftPct: String,
    status: String,
    badgeStyle: BadgeStyle,
    driftColor: Color,
    description: String,
    aiContribution: String,
    modifier: Modifier = Modifier
) {
    Card(
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = IntelliDRColors.SurfaceCard),
        border = BorderStroke(1.dp, IntelliDRColors.SurfaceBorder),
        modifier = modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(IntelliDRSpacing.standardCardPadding)
        ) {
            // Header: Tier title + Status Badge
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = tier,
                    style = IntelliDRTypography.CardTitle,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.weight(1f, fill = false)
                )

                Spacer(modifier = Modifier.width(IntelliDRSpacing.sm))

                StatusBadge(
                    text = status,
                    style = badgeStyle
                )
            }

            Spacer(modifier = Modifier.height(IntelliDRSpacing.sm))

            // Drift Metrics
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(IntelliDRSpacing.xl)
            ) {
                Column {
                    Text(
                        text = "ABSOLUTE DRIFT",
                        style = IntelliDRTypography.MetricLabel
                    )
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = driftM,
                        style = IntelliDRTypography.MetricValueMedium
                    )
                }

                Column {
                    Text(
                        text = "RELATIVE DRIFT",
                        style = IntelliDRTypography.MetricLabel
                    )
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = driftPct,
                        style = IntelliDRTypography.MetricValueMedium,
                        color = driftColor
                    )
                }
            }

            Spacer(modifier = Modifier.height(IntelliDRSpacing.sm))

            Text(
                text = description,
                style = IntelliDRTypography.Body,
                color = IntelliDRColors.TextSecondary
            )

            Spacer(modifier = Modifier.height(IntelliDRSpacing.sm))

            Text(
                text = "⚡ AI Role: $aiContribution",
                style = IntelliDRTypography.CodeFootnote
            )
        }
    }
}
