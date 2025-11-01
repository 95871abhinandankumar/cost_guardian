// frontend/src/components/NivoCharts/CostAllocationChart.tsx

import React from 'react';
import { ResponsiveSunburst } from '@nivo/sunburst';
import { Box, Typography, useTheme } from '@mui/material';

interface CostAllocationChartProps {
    data: Array<{
        id: string;
        value: number;
        children: Array<{
            id: string;
            value: number;
            owner: string;
            service: string;
        }>;
    }>;
}

const CostAllocationChart: React.FC<CostAllocationChartProps> = ({ data }) => {
    const theme = useTheme();

    // Transform data for sunburst chart
    const sunburstData = {
        id: 'root',
        children: data.map(service => ({
            id: service.id,
            value: service.value,
            children: service.children.map(child => ({
                id: child.id,
                value: child.value,
                owner: child.owner,
                service: child.service
            }))
        }))
    };

    return (
        <Box sx={{ width: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
                Cost Allocation by Service & Owner
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Hierarchical view of spending by service and billing owner
            </Typography>
            <Box sx={{ height: 400, width: '100%' }}>
                <ResponsiveSunburst
                        data={sunburstData}
                        margin={{ top: 40, right: 40, bottom: 40, left: 40 }}
                        id="id"
                        value="value"
                        cornerRadius={2}
                        borderWidth={1}
                        borderColor={{ theme: 'background' }}
                        colors={{ scheme: 'nivo' }}
                        childColor={{ from: 'color', modifiers: [['brighter', 0.4]] }}
                        enableArcLabels={true}
                        arcLabel={(d) => `$${d.value.toFixed(0)}`}
                        arcLabelsRadiusOffset={0.5}
                        arcLabelsSkipAngle={10}
                        arcLabelsTextColor={{ theme: 'background' }}
                        animate={true}
                        motionConfig="wobbly"
                        transitionMode="pushIn"
                        tooltip={({ id, value, data }) => {
                            const nodeData = data as any;
                            return (
                                <Box sx={{ 
                                    p: 1, 
                                    bgcolor: theme.palette.background.paper, 
                                    borderRadius: 1,
                                    boxShadow: theme.shadows[3]
                                }}>
                                    <Typography variant="body2" fontWeight="bold">
                                        {nodeData.owner ? `${nodeData.owner}` : id}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        {nodeData.service || 'Service'}
                                    </Typography>
                                    <Typography variant="body2" fontWeight="bold">
                                        ${value.toFixed(0)}/month
                                    </Typography>
                                </Box>
                            );
                        }}
                        theme={{
                            background: 'transparent',
                            text: {
                                fontSize: 11,
                                fill: theme.palette.text.primary,
                                outlineWidth: 0,
                                outlineColor: 'transparent'
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
            <Box sx={{ mt: 2 }}>
                <Typography variant="caption" color="text.secondary">
                    💡 Click on segments to drill down into specific cost centers
                </Typography>
            </Box>
        </Box>
    );
};

export default CostAllocationChart;
