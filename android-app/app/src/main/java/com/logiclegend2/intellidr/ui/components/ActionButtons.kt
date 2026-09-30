package com.logiclegend2.intellidr.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Assessment
import androidx.compose.material.icons.filled.Compare
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Sensors
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.logiclegend2.intellidr.ui.theme.IntelliDRColors
import com.logiclegend2.intellidr.ui.theme.IntelliDRSpacing

@Composable
fun PrimaryActionButton(
    isSimulatingOutage: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val bgColor = if (isSimulatingOutage) IntelliDRColors.Success else IntelliDRColors.Danger
    val btnText = if (isSimulatingOutage) {
        "RESTORE GNSS (RECOVERY DEMO)"
    } else {
        "SIMULATE GNSS OUTAGE (TUNNEL ENTRY)"
    }

    Button(
        onClick = onClick,
        colors = ButtonDefaults.buttonColors(containerColor = bgColor),
        shape = RoundedCornerShape(10.dp),
        modifier = modifier
            .fillMaxWidth()
            .height(IntelliDRSpacing.primaryButtonHeight)
    ) {
        Text(
            text = btnText,
            color = Color.White,
            fontWeight = FontWeight.Bold,
            fontSize = 13.sp,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis
        )
    }
}

@Composable
fun SecondaryActionGroup(
    onOpenComparison: () -> Unit,
    onOpenBenchmarks: () -> Unit,
    onOpenHealth: () -> Unit,
    onStartLiveTest: () -> Unit,
    isExpanded: Boolean = false,
    isNarrow: Boolean = false,
    modifier: Modifier = Modifier
) {
    if (isExpanded) {
        // Single row with 4 buttons on tablet / desktop
        Row(
            modifier = modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(IntelliDRSpacing.sm)
        ) {
            SecondaryActionButton(
                icon = Icons.Default.Compare,
                text = "ABLATION",
                onClick = onOpenComparison,
                modifier = Modifier.weight(1f)
            )
            SecondaryActionButton(
                icon = Icons.Default.Assessment,
                text = "BENCHMARKS",
                onClick = onOpenBenchmarks,
                modifier = Modifier.weight(1f)
            )
            SecondaryActionButton(
                icon = Icons.Default.Sensors,
                text = "SENSOR HEALTH",
                onClick = onOpenHealth,
                modifier = Modifier.weight(1f)
            )
            SecondaryActionButton(
                icon = Icons.Default.PlayArrow,
                text = "LIVE TEST",
                onClick = onStartLiveTest,
                isAccent = true,
                modifier = Modifier.weight(1f)
            )
        }
    } else if (isNarrow) {
        // Vertical stack for very narrow screens (<340dp)
        Column(
            modifier = modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(IntelliDRSpacing.xs)
        ) {
            SecondaryActionButton(
                icon = Icons.Default.Compare,
                text = "ABLATION STUDY",
                onClick = onOpenComparison
            )
            SecondaryActionButton(
                icon = Icons.Default.Assessment,
                text = "BENCHMARKS (<10%)",
                onClick = onOpenBenchmarks
            )
            SecondaryActionButton(
                icon = Icons.Default.Sensors,
                text = "SENSOR HEALTH",
                onClick = onOpenHealth
            )
            SecondaryActionButton(
                icon = Icons.Default.PlayArrow,
                text = "START LIVE TEST",
                onClick = onStartLiveTest,
                isAccent = true
            )
        }
    } else {
        // 2x2 grid for standard compact phones
        Column(
            modifier = modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(IntelliDRSpacing.xs)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(IntelliDRSpacing.sm)
            ) {
                SecondaryActionButton(
                    icon = Icons.Default.Compare,
                    text = "ABLATION",
                    onClick = onOpenComparison,
                    modifier = Modifier.weight(1f)
                )
                SecondaryActionButton(
                    icon = Icons.Default.Assessment,
                    text = "BENCHMARKS",
                    onClick = onOpenBenchmarks,
                    modifier = Modifier.weight(1f)
                )
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(IntelliDRSpacing.sm)
            ) {
                SecondaryActionButton(
                    icon = Icons.Default.Sensors,
                    text = "SENSOR HEALTH",
                    onClick = onOpenHealth,
                    modifier = Modifier.weight(1f)
                )
                SecondaryActionButton(
                    icon = Icons.Default.PlayArrow,
                    text = "START LIVE TEST",
                    onClick = onStartLiveTest,
                    isAccent = true,
                    modifier = Modifier.weight(1f)
                )
            }
        }
    }
}

@Composable
fun SecondaryActionButton(
    icon: ImageVector,
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    isAccent: Boolean = false
) {
    OutlinedButton(
        onClick = onClick,
        shape = RoundedCornerShape(8.dp),
        colors = ButtonDefaults.outlinedButtonColors(
            containerColor = if (isAccent) IntelliDRColors.PrimaryMuted.copy(alpha = 0.2f) else IntelliDRColors.SurfaceCard,
            contentColor = if (isAccent) IntelliDRColors.Primary else IntelliDRColors.TextPrimary
        ),
        border = BorderStroke(
            1.dp,
            if (isAccent) IntelliDRColors.Primary else IntelliDRColors.SurfaceBorder
        ),
        contentPadding = PaddingValues(horizontal = 8.dp, vertical = 6.dp),
        modifier = modifier
            .fillMaxWidth()
            .height(IntelliDRSpacing.secondaryButtonHeight)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier.size(16.dp),
            tint = if (isAccent) IntelliDRColors.Primary else IntelliDRColors.TextSecondary
        )
        Spacer(modifier = Modifier.width(6.dp))
        Text(
            text = text,
            fontSize = 11.sp,
            fontWeight = FontWeight.SemiBold,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis
        )
    }
}
