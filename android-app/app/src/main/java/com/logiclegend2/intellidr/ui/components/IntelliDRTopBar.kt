package com.logiclegend2.intellidr.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
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
fun IntelliDRTopBar(
    title: String,
    subtitle: String? = "SIH26168 | ISRO | Theme: Smart Vehicles | Team: 170889",
    onBack: (() -> Unit)? = null,
    trailingContent: (@Composable () -> Unit)? = null,
    modifier: Modifier = Modifier
) {
    Surface(
        color = IntelliDRColors.Background,
        modifier = modifier
            .fillMaxWidth()
            .windowInsetsPadding(WindowInsets.statusBars)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = IntelliDRSpacing.lg, vertical = IntelliDRSpacing.sm),
            verticalAlignment = Alignment.CenterVertically
        ) {
            if (onBack != null) {
                IconButton(
                    onClick = onBack,
                    modifier = Modifier
                        .size(IntelliDRSpacing.minTouchTarget)
                        .padding(end = IntelliDRSpacing.sm)
                ) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                        contentDescription = "Navigate back to previous screen",
                        tint = IntelliDRColors.Primary
                    )
                }
            }

            Column(
                modifier = Modifier
                    .weight(1f)
                    .padding(vertical = IntelliDRSpacing.xs)
            ) {
                Text(
                    text = title,
                    style = IntelliDRTypography.ScreenTitle,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                if (subtitle != null) {
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = subtitle,
                        style = IntelliDRTypography.Subtitle,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }
            }

            if (trailingContent != null) {
                Spacer(modifier = Modifier.width(IntelliDRSpacing.sm))
                trailingContent()
            }
        }
    }
}
