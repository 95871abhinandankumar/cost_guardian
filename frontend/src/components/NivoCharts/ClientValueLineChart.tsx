// frontend/src/components/NivoCharts/ClientValueLineChart.tsx

import React from 'react';
import { ResponsiveLine } from '@nivo/line';
import { Typography, useTheme, Box } from '@mui/material';

interface SavingsDataPoint {
    x: string; // Month/Date
    y: number; // Cumulative Savings Amount
}

interface SavingsTrendData {
    id: string;
    data: SavingsDataPoint[];
}

interface ClientValueLineChartProps {
    data: SavingsTrendData[];
    totalSavings: number;
}

const ClientValueLineChart: React.FC<ClientValueLineChartProps> = ({ data, totalSavings }) => {
    const theme = useTheme();
    const formattedSavings = `$${totalSavings.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ",")}`; // Format as $X,XXX

    return (
        <Box sx={{ width: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h5" sx={{ mb: 1 }}>
                Cumulative Value Trend
            </Typography>
            <Typography variant="h4" color="success.main" fontWeight="bold" sx={{ mb: 2 }}>
                {formattedSavings}
            </Typography>

            <Box sx={{ height: 300, width: '100%' }}>
                <ResponsiveLine
                    data={data}
                    margin={{ top: 10, right: 20, bottom: 50, left: 60 }}
                    xScale={{ type: 'point' }}
                    yScale={{ type: 'linear', min: 0, max: 'auto' }}
                    curve="monotoneX"

                    // Style integration for Dark/Light mode
                    theme={{
                        background: theme.palette.background.paper,
                        axis: { ticks: { text: { fill: theme.palette.text.secondary } } },
                        grid: { line: { stroke: theme.palette.divider } },
                    }}

                    // --- Aesthetic Teal/Success Color ---
                    colors={[theme.palette.success.main]}

                    // Fill the area beneath the line to show accumulation
                    areaBaselineValue={0}
                    enableArea={true}
                    areaOpacity={0.4}

                    lineWidth={3}
                    pointSize={6}
                    useMesh={true}
                    enableGridX={false}

                    axisBottom={{
                        legend: 'Months',
                        legendOffset: 36,
                        legendPosition: 'middle',
                    }}
                    axisLeft={{
                        legend: 'Total Savings (USD)',
                        legendOffset: -50,
                        legendPosition: 'middle',
                        format: (v: number) => `$${v / 1000}K`, // Format for thousands
                    }}

                    // Agentic Hook: Annotation for final value delivered
                    // NOTE: Tooltip will show final cumulative value.
                    markers={[
                        {
                            axis: 'y',
                            value: totalSavings,
                            lineStyle: { stroke: theme.palette.success.main, strokeWidth: 1, strokeDasharray: '4 4' },
                            legend: 'Current Value',
                            legendOrientation: 'horizontal',
                        }
                    ]}
                />
            </Box>
        </Box>
    );
};

export default ClientValueLineChart;