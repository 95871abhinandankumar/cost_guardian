// frontend/src/components/NivoCharts/UtilizationLineChart.tsx

import React from 'react';
import { ResponsiveLine } from '@nivo/line';
import { Card, Typography, useTheme, Box } from '@mui/material';

// Interfaces remain the same
interface UtilizationTrendPoint {
    x: string; // Date
    y: number; // Utilization Percentage
}

interface UtilizationTrendData {
    id: string;
    // NOTE: Removed 'color: string' from interface, as Nivo uses the 'colors' prop logic.
    // The main color will be passed via the data preparation function (ITDashboard.tsx).
    data: UtilizationTrendPoint[];
}

interface UtilizationLineChartProps {
    data: UtilizationTrendData[];
}

const UtilizationLineChart: React.FC<UtilizationLineChartProps> = ({ data }) => {
    const theme = useTheme();

    return (
        // Added dynamic background color from theme
        <Card elevation={6} sx={{ height: '100%', minHeight: 300, p: 2, bgcolor: theme.palette.background.paper }}>
            <Typography variant="h6" sx={{ mb: 1 }}>Avg. Utilization Trend (Last 30 Days)</Typography>
            <Box sx={{ height: 250 }}>
                <ResponsiveLine
                    data={data}
                    // --- Nivo Theming (CRITICAL for Light/Dark Mode text) ---
                    theme={{
                        background: theme.palette.background.paper,
                        axis: {
                            // Ensure axis text uses primary text color
                            legend: { text: { fill: theme.palette.text.primary } },
                            ticks: { text: { fill: theme.palette.text.secondary } },
                        },
                        grid: {
                            // Use neutral secondary text color for grid lines
                            line: { stroke: theme.palette.divider },
                        }
                    }}
                    margin={{ top: 20, right: 20, bottom: 40, left: 40 }}
                    xScale={{ type: 'point' }}
                    yScale={{ type: 'linear', min: 0, max: 100 }}
                    curve="monotoneX"
                    axisTop={null}
                    axisRight={null}

                    // --- AXES CONFIGURATION ---
                    axisBottom={{
                        tickSize: 5,
                        tickPadding: 5,
                        legend: 'Time',
                        legendOffset: 36,
                        legendPosition: 'middle',
                    }}
                    axisLeft={{
                        tickSize: 5,
                        tickPadding: 5,
                        legend: 'Utilization (%)',
                        legendOffset: -35,
                        legendPosition: 'middle',
                    }}

                    // --- COLOR AND STYLE ---
                    // Nivo will automatically use the series color defined in ITDashboard.tsx
                    // If multiple series are passed, Nivo's default color scheme will apply,
                    // but since ITDashboard passes the theme primary color, that will be used.
                    colors={[theme.palette.primary.main]}

                    pointSize={8} // Slightly larger points for visual clarity
                    pointColor={{ theme: 'background' }}
                    pointBorderWidth={2}
                    pointBorderColor={{ from: 'serieColor' }}
                    enableGridX={false} // Clean up grid clutter
                    useMesh={true}

                    // --- AGENTIC HOOK: Idle Threshold Marker ---
                    // Uses Warning color for the "below target" zone
                    markers={[
                        {
                            axis: 'y',
                            value: 40,
                            lineStyle: {
                                stroke: theme.palette.warning.main,
                                strokeWidth: 1.5, // Slightly thicker line
                                strokeDasharray: '4 4'
                            },
                            legend: 'Target Min 40%',
                            legendOrientation: 'horizontal',
                        }
                    ]}
                />
            </Box>
        </Card>
    );
};

export default UtilizationLineChart;