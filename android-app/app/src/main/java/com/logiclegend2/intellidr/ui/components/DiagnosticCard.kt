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
fun DiagnosticCard(
    title: String,
    specs: String,
    isPass: Boolean,
    note: String,
    modifier: Modifier = Modifier
) {
    Card(
        shape = RoundedCornerShape(10.dp),
        colors = CardDefaults.cardColors(containerColor = IntelliDRColors.SurfaceCard),
        border = BorderStroke(1.dp, if (isPass) IntelliDRColors.SurfaceBorder else IntelliDRColors.DangerBorder),
        modifier = modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(IntelliDRSpacing.standardCardPadding),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(
                modifier = Modifier
                    .weight(1f)
                    .padding(end = IntelliDRSpacing.md)
            ) {
                Text(
                    text = title,
                    style = IntelliDRTypography.CardTitle,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )

                Spacer(modifier = Modifier.height(IntelliDRSpacing.xs))

                Text(
                    text = specs,
                    style = IntelliDRTypography.Subtitle,
                    color = IntelliDRColors.Primary,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )

                Spacer(modifier = Modifier.height(IntelliDRSpacing.xs))

                Text(
                    text = note,
                    style = IntelliDRTypography.Body,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
                )
            }

            StatusBadge(
                text = if (isPass) "PASS" else "FAIL",
                style = if (isPass) BadgeStyle.SUCCESS else BadgeStyle.DANGER
            )
        }
    }
}
