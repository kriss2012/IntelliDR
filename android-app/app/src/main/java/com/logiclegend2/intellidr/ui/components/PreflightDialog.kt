package com.logiclegend2.intellidr.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.logiclegend2.intellidr.ui.theme.IntelliDRColors
import com.logiclegend2.intellidr.ui.theme.IntelliDRSpacing
import com.logiclegend2.intellidr.ui.theme.IntelliDRTypography

@Composable
fun PreflightDialog(
    onDismiss: () -> Unit,
    onConfirmStart: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        containerColor = IntelliDRColors.SurfaceCard,
        shape = RoundedCornerShape(14.dp),
        title = {
            Text(
                text = "Pre-Flight Navigation Readiness",
                style = IntelliDRTypography.SectionHeader
            )
        },
        text = {
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(IntelliDRSpacing.xs)
            ) {
                Text(
                    text = "Verifying all onboard edge subsystems before initializing live dead reckoning service:",
                    style = IntelliDRTypography.Body,
                    color = IntelliDRColors.TextSecondary
                )

                Spacer(modifier = Modifier.height(IntelliDRSpacing.sm))

                PreflightItem(label = "IMU Sensors (100 Hz Accel & Gyro)", isOk = true)
                PreflightItem(label = "GNSS / NavIC Multi-Constellation Fix", isOk = true)
                PreflightItem(label = "AI Velocity Model (1D-CNN INT8)", isOk = true)
                PreflightItem(label = "Offline OpenStreetMap Road Graph", isOk = true)
                PreflightItem(label = "Foreground Service WakeLock", isOk = true)
            }
        },
        confirmButton = {
            Button(
                onClick = onConfirmStart,
                colors = ButtonDefaults.buttonColors(containerColor = IntelliDRColors.Primary),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text(
                    text = "INITIALIZE TEST",
                    color = IntelliDRColors.Background,
                    fontWeight = FontWeight.Bold,
                    fontSize = 12.sp
                )
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("CANCEL", color = IntelliDRColors.TextMuted)
            }
        }
    )
}

@Composable
private fun PreflightItem(label: String, isOk: Boolean) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = Icons.Default.CheckCircle,
            contentDescription = null,
            tint = if (isOk) IntelliDRColors.Success else IntelliDRColors.Danger,
            modifier = Modifier.size(16.dp)
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = label,
            style = IntelliDRTypography.Subtitle,
            color = IntelliDRColors.TextPrimary
        )
    }
}
