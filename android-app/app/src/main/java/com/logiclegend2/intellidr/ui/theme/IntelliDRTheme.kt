package com.logiclegend2.intellidr.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable

private val DarkColorScheme = darkColorScheme(
    primary = IntelliDRColors.Primary,
    onPrimary = IntelliDRColors.Background,
    primaryContainer = IntelliDRColors.PrimaryMuted,
    onPrimaryContainer = IntelliDRColors.TextPrimary,
    secondary = IntelliDRColors.Secondary,
    onSecondary = IntelliDRColors.Background,
    background = IntelliDRColors.Background,
    onBackground = IntelliDRColors.TextPrimary,
    surface = IntelliDRColors.Surface,
    onSurface = IntelliDRColors.TextPrimary,
    surfaceVariant = IntelliDRColors.SurfaceCard,
    onSurfaceVariant = IntelliDRColors.TextSecondary,
    error = IntelliDRColors.Danger,
    onError = IntelliDRColors.TextPrimary
)

@Composable
fun IntelliDRTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = DarkColorScheme,
        content = content
    )
}
