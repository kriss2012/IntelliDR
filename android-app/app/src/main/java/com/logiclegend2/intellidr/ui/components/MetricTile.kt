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
fun MetricTile(
    title: String,
    value: String,
    unit: String,
    modifier: Modifier = Modifier,
    highlightColor: Color? = null,
    isLarge: Boolean = false
) {
    Card(
        shape = RoundedCornerShape(10.dp),
        colors = CardDefaults.cardColors(containerColor = IntelliDRColors.SurfaceCard),
        border = BorderStroke(1.dp, IntelliDRColors.SurfaceBorderSubtle),
        modifier = modifier
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = IntelliDRSpacing.md, vertical = IntelliDRSpacing.sm)
        ) {
            Text(
                text = title,
                style = IntelliDRTypography.MetricLabel,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )

            Spacer(modifier = Modifier.height(IntelliDRSpacing.xs))

            Row(
                verticalAlignment = Alignment.Bottom,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = value,
                    style = if (isLarge) IntelliDRTypography.MetricValueLarge else IntelliDRTypography.MetricValueMedium,
                    color = highlightColor ?: IntelliDRColors.TextPrimary,
                    maxLines = 1,
                    overflow = TextOverflow.Clip,
                    modifier = Modifier.weight(1f, fill = false)
                )

                Spacer(modifier = Modifier.width(IntelliDRSpacing.xs))

                Text(
                    text = unit,
                    style = IntelliDRTypography.MetricUnit,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.padding(bottom = 2.dp)
                )
            }
        }
    }
}
