package com.logiclegend2.intellidr.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.wrapContentWidth
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.logiclegend2.intellidr.ui.theme.IntelliDRColors
import com.logiclegend2.intellidr.ui.theme.IntelliDRSpacing
import com.logiclegend2.intellidr.ui.theme.IntelliDRTypography

enum class BadgeStyle {
    SUCCESS,
    WARNING,
    DANGER,
    INFO,
    NEUTRAL
}

@Composable
fun StatusBadge(
    text: String,
    style: BadgeStyle = BadgeStyle.SUCCESS,
    modifier: Modifier = Modifier
) {
    val (bgColor, textColor, borderColor) = when (style) {
        BadgeStyle.SUCCESS -> Triple(IntelliDRColors.SuccessBg, IntelliDRColors.Success, IntelliDRColors.SuccessBorder)
        BadgeStyle.WARNING -> Triple(IntelliDRColors.WarningBg, IntelliDRColors.Warning, IntelliDRColors.WarningBorder)
        BadgeStyle.DANGER -> Triple(IntelliDRColors.DangerBg, IntelliDRColors.Danger, IntelliDRColors.DangerBorder)
        BadgeStyle.INFO -> Triple(IntelliDRColors.InfoBg, IntelliDRColors.Primary, IntelliDRColors.PrimaryVariant)
        BadgeStyle.NEUTRAL -> Triple(IntelliDRColors.SurfaceElevated, IntelliDRColors.TextSecondary, IntelliDRColors.SurfaceBorder)
    }

    Surface(
        shape = RoundedCornerShape(6.dp),
        color = bgColor,
        border = BorderStroke(1.dp, borderColor),
        modifier = modifier
            .wrapContentWidth()
            .widthIn(min = IntelliDRSpacing.minBadgeWidth)
    ) {
        Text(
            text = text,
            color = textColor,
            style = IntelliDRTypography.BadgeText,
            textAlign = TextAlign.Center,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
        )
    }
}
