// frontend/src/components/NivoCharts/CostTrendChart.tsx

import React from 'react';
import { ResponsiveLine } from '@nivo/line';
import { Box, Typography, useTheme } from '@mui/material';

interface CostTrendChartProps {
    data: Array<{
        id: string;
        color: string;
        data: Array<{
            x: string;
            y: number;
        }>;
    }>;
}

const CostTrendChart: React.FC<CostTrendChartProps> = ({ data }) => {
    const theme = useTheme();

    return (
        <Box sx={{ width: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
                Cost Trend & ROI Simulation
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Visual demonstration of cost trajectory after agent's actions are applied
            </Typography>
            <Box sx={{ height: 400, width: '100%' }}>
                <ResponsiveLine
                        data={data}
                        margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
                        xScale={{ type: 'point' }}
                        yScale={{
                            type: 'linear',
                            min: 'auto',
                            max: 'auto',
                            stacked: false,
                            reverse: false
                        }}
                        yFormat=" >-.2f"
                        axisTop={null}
                        axisRight={null}
                        axisBottom={{
                            tickSize: 5,
                            tickPadding: 5,
                            tickRotation: 0,
                            legend: 'Month',
                            legendOffset: 36,
                            legendPosition: 'middle'
                        }}
                        axisLeft={{
                            tickSize: 5,
                            tickPadding: 5,
                            tickRotation: 0,
                            legend: 'Monthly Cost ($)',
                            legendOffset: -50,
                            legendPosition: 'middle',
                            format: (value) => `$${value.toFixed(0)}`
                        }}
                        pointSize={8}
                        pointColor={{ theme: 'background' }}
                        pointBorderWidth={2}
                        pointBorderColor={{ from: 'serieColor' }}
                        pointLabelYOffset={-12}
                        useMesh={true}
                        legends={[
                            {
                                anchor: 'bottom-right',
                                direction: 'column',
                                justify: false,
                                translateX: 100,
                                translateY: 0,
                                itemsSpacing: 0,
                                itemDirection: 'left-to-right',
                                itemWidth: 80,
                                itemHeight: 20,
                                itemOpacity: 0.75,
                                symbolSize: 12,
                                symbolShape: 'circle',
                                symbolBorderColor: 'rgba(0, 0, 0, .5)',
                                effects: [
                                    {
                                        on: 'hover',
                                        style: {
                                            itemBackground: 'rgba(0, 0, 0, .03)',
                                            itemOpacity: 1
                                        }
                                    }
                                ]
                            }
                        ]}
                        theme={{
                            background: 'transparent',
                            text: {
                                fontSize: 11,
                                fill: theme.palette.text.primary,
                                outlineWidth: 0,
                                outlineColor: 'transparent'
                            },
                            axis: {
                                domain: {
                                    line: {
                                        stroke: theme.palette.divider,
                                        strokeWidth: 1
                                    }
                                },
                                legend: {
                                    text: {
                                        fontSize: 12,
                                        fill: theme.palette.text.secondary,
                                        outlineWidth: 0,
                                        outlineColor: 'transparent'
                                    }
                                },
                                ticks: {
                                    line: {
                                        stroke: theme.palette.divider,
                                        strokeWidth: 1
                                    },
                                    text: {
                                        fontSize: 11,
                                        fill: theme.palette.text.secondary,
                                        outlineWidth: 0,
                                        outlineColor: 'transparent'
                                    }
                                }
                            },
                            grid: {
                                line: {
                                    stroke: theme.palette.divider,
                                    strokeWidth: 1
                                }
                            },
                            legends: {
                                title: {
                                    text: {
                                        fontSize: 11,
                                        fill: theme.palette.text.secondary,
                                        outlineWidth: 0,
                                        outlineColor: 'transparent'
                                    }
                                },
                                text: {
                                    fontSize: 11,
                                    fill: theme.palette.text.secondary,
                                    outlineWidth: 0,
                                    outlineColor: 'transparent'
                                },
                                ticks: {
                                    line: {},
                                    text: {
                                        fontSize: 10,
                                        fill: theme.palette.text.secondary,
                                        outlineWidth: 0,
                                        outlineColor: 'transparent'
                                    }
                                }
                            },
                            tooltip: {
                                container: {
                                    background: theme.palette.background.paper,
                                    color: theme.palette.text.primary,
                                    fontSize: 12,
                                    borderRadius: 4,
                                    boxShadow: theme.shadows[3]
                                }
                            }
                        }}
                    />
                </Box>
        </Box>
    );
};

export default CostTrendChart;
