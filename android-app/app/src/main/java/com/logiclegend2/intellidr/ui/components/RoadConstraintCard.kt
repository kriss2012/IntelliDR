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
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.logiclegend2.intellidr.ui.theme.IntelliDRColors
import com.logiclegend2.intellidr.ui.theme.IntelliDRSpacing
import com.logiclegend2.intellidr.ui.theme.IntelliDRTypography

@Composable
fun RoadConstraintCard(
    roadName: String,
    matchPct: Int = 96,
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
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "ROAD NETWORK CONSTRAINT",
                    style = IntelliDRTypography.MetricLabel,
                    maxLines = 1
                )

                StatusBadge(
                    text = "MATCH: $matchPct%",
                    style = BadgeStyle.SUCCESS
                )
            }

            Spacer(modifier = Modifier.height(IntelliDRSpacing.xs))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = roadName,
                    style = IntelliDRTypography.CardTitle,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.weight(1f, fill = false)
                )

                Spacer(modifier = Modifier.width(IntelliDRSpacing.sm))

                Text(
                    text = "100% Offline GeoJSON",
                    style = IntelliDRTypography.Subtitle,
                    color = IntelliDRColors.AccentTeal,
                    maxLines = 1
                )
            }
        }
    }
}
