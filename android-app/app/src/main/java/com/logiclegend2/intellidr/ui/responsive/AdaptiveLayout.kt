package com.logiclegend2.intellidr.ui.responsive

import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

enum class WindowWidthClass {
    Compact,   // < 600dp (standard portrait phones)
    Medium,    // 600dp - 840dp (small tablets, foldables unfolded)
    Expanded,  // 840dp - 1200dp (standard tablets, desktop mode)
    Large      // 1200dp+ (large displays)
}

enum class WindowHeightClass {
    Compact,   // < 480dp (landscape phones)
    Regular    // >= 480dp
}

data class WindowSizeInfo(
    val widthClass: WindowWidthClass,
    val heightClass: WindowHeightClass,
    val widthDp: Dp,
    val heightDp: Dp
) {
    val isCompact: Boolean get() = widthClass == WindowWidthClass.Compact
    val isMedium: Boolean get() = widthClass == WindowWidthClass.Medium
    val isExpanded: Boolean get() = widthClass == WindowWidthClass.Expanded || widthClass == WindowWidthClass.Large
    val isLandscapePhone: Boolean get() = heightClass == WindowHeightClass.Compact && widthDp > heightDp
}

@Composable
fun rememberWindowSizeInfo(): WindowSizeInfo {
    val configuration = LocalConfiguration.current
    val widthDp = configuration.screenWidthDp.dp
    val heightDp = configuration.screenHeightDp.dp

    val widthClass = when {
        widthDp < 600.dp -> WindowWidthClass.Compact
        widthDp < 840.dp -> WindowWidthClass.Medium
        widthDp < 1200.dp -> WindowWidthClass.Expanded
        else -> WindowWidthClass.Large
    }

    val heightClass = when {
        heightDp < 480.dp -> WindowHeightClass.Compact
        else -> WindowHeightClass.Regular
    }

    return WindowSizeInfo(widthClass, heightClass, widthDp, heightDp)
}
