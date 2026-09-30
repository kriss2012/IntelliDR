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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.logiclegend2.intellidr.model.BenchmarkItem
import com.logiclegend2.intellidr.ui.theme.IntelliDRColors
import com.logiclegend2.intellidr.ui.theme.IntelliDRSpacing
import com.logiclegend2.intellidr.ui.theme.IntelliDRTypography

@Composable
fun BenchmarkCard(
    benchmark: BenchmarkItem,
    isExpandedLayout: Boolean = false,
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
            // Header: Scenario title and resilient status badge
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = benchmark.scenario,
                    style = IntelliDRTypography.CardTitle,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.weight(1f, fill = false)
                )

                Spacer(modifier = Modifier.width(IntelliDRSpacing.md))

                StatusBadge(
                    text = if (benchmark.passed) "PASSED (<10%)" else "FAILED (>10%)",
                    style = if (benchmark.passed) BadgeStyle.SUCCESS else BadgeStyle.DANGER
                )
            }

            Spacer(modifier = Modifier.height(IntelliDRSpacing.md))

            // Metrics Display: 4 columns on expanded/tablets, 2x2 grid on compact phones
            if (isExpandedLayout) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    BenchmarkMetricItem(
                        label = "Outage Duration",
                        value = "${benchmark.outageS.toInt()} sec",
                        modifier = Modifier.weight(1f)
                    )
                    BenchmarkMetricItem(
                        label = "Distance Traveled",
                        value = "${benchmark.distanceM.toInt()} m",
                        modifier = Modifier.weight(1f)
                    )
                    BenchmarkMetricItem(
                        label = "Absolute Drift",
                        value = "%.2f m".format(benchmark.driftM),
                        modifier = Modifier.weight(1f)
                    )
                    BenchmarkMetricItem(
                        label = "Relative Drift",
                        value = "%.2f%%".format(benchmark.driftPct),
                        highlightColor = IntelliDRColors.Success,
                        subtext = "Allowed: <10.0%",
                        modifier = Modifier.weight(1f)
                    )
                }
            } else {
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    verticalArrangement = Arrangement.spacedBy(IntelliDRSpacing.sm)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(IntelliDRSpacing.sm)
                    ) {
                        BenchmarkMetricItem(
                            label = "Outage Duration",
                            value = "${benchmark.outageS.toInt()} sec",
                            modifier = Modifier.weight(1f)
                        )
                        BenchmarkMetricItem(
                            label = "Distance Traveled",
                            value = "${benchmark.distanceM.toInt()} m",
                            modifier = Modifier.weight(1f)
                        )
                    }
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(IntelliDRSpacing.sm)
                    ) {
                        BenchmarkMetricItem(
                            label = "Absolute Drift",
                            value = "%.2f m".format(benchmark.driftM),
                            modifier = Modifier.weight(1f)
                        )
                        BenchmarkMetricItem(
                            label = "Relative Drift",
                            value = "%.2f%%".format(benchmark.driftPct),
                            highlightColor = IntelliDRColors.Success,
                            subtext = "Allowed: <10.0%",
                            modifier = Modifier.weight(1f)
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun BenchmarkMetricItem(
    label: String,
    value: String,
    modifier: Modifier = Modifier,
    highlightColor: Color? = null,
    subtext: String? = null
) {
    Column(modifier = modifier) {
        Text(
            text = label,
            style = IntelliDRTypography.MetricLabel,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis
        )
        Spacer(modifier = Modifier.height(2.dp))
        Text(
            text = value,
            style = IntelliDRTypography.MetricValueSmall,
            color = highlightColor ?: IntelliDRColors.TextPrimary,
            maxLines = 1
        )
        if (subtext != null) {
            Text(
                text = subtext,
                style = IntelliDRTypography.Subtitle,
                color = IntelliDRColors.TextMuted,
                maxLines = 1
            )
        }
    }
}
