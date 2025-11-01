// frontend/src/components/NivoCharts/AnomalyScatterPlot.tsx

import React from 'react';
import { ResponsiveScatterPlot } from '@nivo/scatterplot';
import { useTheme, Typography, Box, Card } from '@mui/material';

interface ScatterDataPoint {
    x: number; // Utilization Score * 100 (0-100)
    y: number; // Monthly Cost (USD)
    id: string;
    severity: string;
    owner: string;
}

interface ScatterSeries {
    id: string;
    data: ScatterDataPoint[];
}

interface AnomalyScatterPlotProps {
    data: ScatterSeries[];
}

const AnomalyScatterPlot: React.FC<AnomalyScatterPlotProps> = ({ data }) => {
    const theme = useTheme();

    // --- FINAL AESTHETIC COLOR MAPPING ---
    const getColor = (node: any) => {
        const severity = node.data?.severity || 'Healthy';

        switch (severity) {
            case 'Critical':
                return theme.palette.error.main;   // Electric Pink/Red
            case 'High':
                return theme.palette.warning.main; // Warning Amber
            case 'Medium':
                return theme.palette.info.main;    // Standard Blue
            case 'Low':
            case 'Healthy':
                return theme.palette.success.main; // Vibrant Neon Green
            default:
                return theme.palette.secondary.main;
        }
    };

    // Custom Tooltip for Agentic Insight
    const CustomTooltip = ({ node }: { node: { data: ScatterDataPoint } }) => (
        <Card elevation={10} sx={{
            p: 1,
            bgcolor: theme.palette.background.paper,
            border: `1px solid ${getColor(node)}`
        }}>
            <Typography variant="body2" fontWeight="bold" color={getColor(node)}>
                {node.data.severity === 'Critical' ? 'CRITICAL ANOMALY' : 'Resource Details'}
            </Typography>
            <Typography variant="caption" color={theme.palette.text.secondary}>
                ID: {node.data.id} <br />
                Owner: {node.data.owner} <br />
                Cost: ${node.data.y.toFixed(2)}/mo <br />
                Utilization: {node.data.x.toFixed(1)}%
            </Typography>
        </Card>
    );

    return (
        <Box sx={{ width: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h5" sx={{ mb: 2 }}>Resource Utilization Anomaly Target</Typography>
            <Box sx={{ height: 400, width: '100%' }}>
                <ResponsiveScatterPlot
                    data={data}
                    xScale={{ type: 'linear', min: 0, max: 100 }}
                    yScale={{ type: 'linear', min: 0, max: 'auto' }}

                    // AXES Styling
                    axisBottom={{
                        legend: 'Average Utilization (%)',
                        legendOffset: 46,
                        legendPosition: 'middle',
                    }}
                    axisLeft={{
                        legend: 'Estimated Monthly Cost (USD)',
                        legendOffset: -60,
                        format: (v: number) => `$${v.toFixed(0)}`,
                        legendPosition: 'middle',
                    }}

                    // AGENTIC HOOK: Idle Threshold Marker (Uses Error Dark for high contrast line)
                    markers={[
                        {
                            axis: 'x',
                            value: 10,
                            lineStyle: {
                                stroke: theme.palette.error.dark,
                                strokeWidth: 2,
                                strokeDasharray: '6 6'
                            },
                            legend: '10% Idle Threshold',
                            legendOrientation: 'horizontal',
                        }
                    ]}

                    // Styling and Interactions (Ensures axis text is readable in Dark Mode)
                    theme={{
                        background: theme.palette.background.paper,
                        axis: {
                            legend: { text: { fill: theme.palette.text.primary } },
                            ticks: { text: { fill: theme.palette.text.secondary } },
                        },
                        grid: {
                            line: { stroke: theme.palette.divider },
                        }
                    }}
                    colors={getColor}
                    nodeSize={12}
                    useMesh={true}
                    tooltip={CustomTooltip}
                />
            </Box>
        </Box>
    );
};

export default AnomalyScatterPlot;