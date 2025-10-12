// frontend/src/components/NivoCharts/GovernanceDonutChart.tsx

import React from 'react';
import { ResponsivePie } from '@nivo/pie';
import { Card, Typography, useTheme, Box } from '@mui/material';

// Interfaces remain the same
interface GovernanceData {
    id: string; // "Tagged" or "Untagged"
    label: string;
    value: number; // Spend amount (Percentage value for the chart)
    color: string; // This property is often ignored when using the Nivo 'colors' prop array
}

interface GovernanceDonutChartProps {
    data: GovernanceData[];
}

const GovernanceDonutChart: React.FC<GovernanceDonutChartProps> = ({ data }) => {
    const theme = useTheme();

    // Nivo requires the data points to have a color property if using the default color setup.
    // However, since we are calculating colors dynamically via a function, we will define the
    // color array explicitly for Nivo's 'colors' prop.
    const colorScheme = [
        theme.palette.success.main, // Tagged (Green)
        theme.palette.error.main,   // Untagged (Red)
    ];

    // --- Data Derivation ---
    // const totalValue = data.reduce((sum, d) => sum + d.value, 0);
    const untaggedItem = data.find(d => d.id === 'Untagged');
    // We already have the percentage in the data value, assuming ITDashboard calculates it correctly.
    const untaggedPercent = untaggedItem ? untaggedItem.value : 0;

    // --- Custom Nivo Layer Text Props ---
    // Nivo requires explicit typing for its function parameters (TS7031)
    const renderCenterText = ({ centerX, centerY }: { centerX: number, centerY: number }) => (
        <text
            x={centerX}
            y={centerY}
            textAnchor="middle"
            dominantBaseline="central"
            style={{
                fontSize: '18px', // Slightly larger font
                fontWeight: 'bold',
                fill: theme.palette.text.primary,
            }}
        >
            {untaggedPercent.toFixed(1)}% WASTE
        </text>
    );

    return (
        <Card elevation={6} sx={{ height: '100%', minHeight: 300, p: 2, bgcolor: theme.palette.background.paper }}>
            <Typography variant="h6" sx={{ mb: 1 }}>Resource Governance Health</Typography>

            {/* Displaying the critical number outside the chart for clear visibility */}
            <Typography color="text.secondary">
                Total Untagged Spend:
                <Typography
                    component="span"
                    fontWeight="bold"
                    // Use error.main for red contrast
                    color={theme.palette.error.main}
                    sx={{ ml: 0.5 }}
                >
                    {untaggedPercent.toFixed(1)}%
                </Typography>
            </Typography>

            <Box sx={{ height: 250 }}>
                <ResponsivePie
                    data={data}
                    // --- Nivo Theming (CRITICAL for Light/Dark Mode text) ---
                    theme={{
                        background: theme.palette.background.paper,
                        axis: {
                            legend: { text: { fill: theme.palette.text.primary } },
                            ticks: { text: { fill: theme.palette.text.secondary } },
                        },
                        legends: {
                            text: { fill: theme.palette.text.primary },
                        },
                    }}
                    margin={{ top: 20, right: 80, bottom: 20, left: 80 }}
                    innerRadius={0.7}
                    padAngle={0.7}
                    cornerRadius={3}
                    // Use our explicitly defined scheme
                    colors={colorScheme}
                    borderWidth={1}
                    borderColor={{ from: 'color', modifiers: [['darker', 0.2]] }}
                    enableArcLinkLabels={false}

                    // FIX: Explicitly type parameter 'e' to avoid TS7006 error
                    arcLabel={(e: any) => `${e.value.toFixed(0)}%`}

                    // Custom Tooltip
                    tooltip={({ datum }) => (
                        <Card elevation={10} sx={{ p: 1, bgcolor: theme.palette.background.paper, border: '1px solid grey' }}>
                            <strong>{datum.id}:</strong> {datum.value.toFixed(1)}%
                        </Card>
                    )}

                    // Custom center text layer
                    layers={['arcs', 'arcLabels', 'legends', renderCenterText]}
                />
            </Box>
        </Card>
    );
};

export default GovernanceDonutChart;