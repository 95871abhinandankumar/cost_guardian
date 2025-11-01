// frontend/src/components/SavingsPrioritizationTable.tsx

import React from 'react';
import {
    Box,
    Typography,
    Card,
    CardContent,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Chip,
    useTheme
} from '@mui/material';
import { TrendingUp, TrendingDown, Warning, CheckCircle } from '@mui/icons-material';

interface SavingsPrioritizationData {
    id: string;
    resource: string;
    owner: string;
    service: string;
    currentCost: number;
    projectedSavings: number;
    action: string;
    severity: string;
}

interface SavingsPrioritizationTableProps {
    data: SavingsPrioritizationData[];
}

const SavingsPrioritizationTable: React.FC<SavingsPrioritizationTableProps> = ({ data }) => {
    const theme = useTheme();

    const getSeverityColor = (severity: string) => {
        switch (severity.toLowerCase()) {
            case 'critical':
                return 'error';
            case 'high':
                return 'warning';
            case 'medium':
                return 'info';
            case 'low':
                return 'success';
            default:
                return 'default';
        }
    };

    const getSeverityIcon = (severity: string) => {
        switch (severity.toLowerCase()) {
            case 'critical':
                return <Warning />;
            case 'high':
                return <TrendingUp />;
            case 'medium':
                return <TrendingDown />;
            case 'low':
                return <CheckCircle />;
            default:
                return undefined;
        }
    };

    const totalSavings = data.reduce((sum, item) => sum + item.projectedSavings, 0);
    const totalCurrentCost = data.reduce((sum, item) => sum + item.currentCost, 0);

    return (
        <Card elevation={3}>
            <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">
                        Savings Prioritization by Dollar Value
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                            Total Potential: <strong>${totalSavings.toFixed(0)}</strong>
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            ROI: <strong>{((totalSavings / totalCurrentCost) * 100).toFixed(1)}%</strong>
                        </Typography>
                    </Box>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Recommendations sorted by projected savings value for budget approval prioritization
                </Typography>
                
                <TableContainer component={Paper} variant="outlined">
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell><strong>Priority</strong></TableCell>
                                <TableCell><strong>Resource</strong></TableCell>
                                <TableCell><strong>Owner</strong></TableCell>
                                <TableCell><strong>Service</strong></TableCell>
                                <TableCell align="right"><strong>Current Cost</strong></TableCell>
                                <TableCell align="right"><strong>Projected Savings</strong></TableCell>
                                <TableCell align="right"><strong>Savings %</strong></TableCell>
                                <TableCell><strong>Severity</strong></TableCell>
                                <TableCell><strong>Recommended Action</strong></TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {data.map((item, index) => (
                                <TableRow 
                                    key={item.id}
                                    sx={{ 
                                        '&:hover': { 
                                            backgroundColor: theme.palette.action.hover 
                                        } 
                                    }}
                                >
                                    <TableCell>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <Typography variant="body2" fontWeight="bold">
                                                #{index + 1}
                                            </Typography>
                                        </Box>
                                    </TableCell>
                                    <TableCell>
                                        <Typography variant="body2" fontFamily="monospace">
                                            {item.resource}
                                        </Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Typography variant="body2">
                                            {item.owner}
                                        </Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Typography variant="body2">
                                            {item.service}
                                        </Typography>
                                    </TableCell>
                                    <TableCell align="right">
                                        <Typography variant="body2" fontWeight="bold">
                                            ${item.currentCost.toFixed(0)}
                                        </Typography>
                                    </TableCell>
                                    <TableCell align="right">
                                        <Typography 
                                            variant="body2" 
                                            fontWeight="bold"
                                            color="success.main"
                                        >
                                            ${item.projectedSavings.toFixed(0)}
                                        </Typography>
                                    </TableCell>
                                    <TableCell align="right">
                                        <Typography 
                                            variant="body2" 
                                            fontWeight="bold"
                                            color="success.main"
                                        >
                                            {item.currentCost > 0 ? ((item.projectedSavings / item.currentCost) * 100).toFixed(1) : '0'}%
                                        </Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Chip
                                            icon={getSeverityIcon(item.severity)}
                                            label={item.severity}
                                            color={getSeverityColor(item.severity) as any}
                                            size="small"
                                            variant="outlined"
                                        />
                                    </TableCell>
                                    <TableCell>
                                        <Typography variant="body2" sx={{ maxWidth: 300 }}>
                                            {item.action}
                                        </Typography>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
                
                <Box sx={{ mt: 2, p: 2, bgcolor: theme.palette.grey[50], borderRadius: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                        💡 <strong>Finance Insight:</strong> Focus on the top 3 recommendations for maximum budget impact. 
                        These represent {totalSavings > 0 ? ((data.slice(0, 3).reduce((sum, item) => sum + item.projectedSavings, 0) / totalSavings) * 100).toFixed(0) : '0'}% 
                        of total potential savings.
                    </Typography>
                </Box>
            </CardContent>
        </Card>
    );
};

export default SavingsPrioritizationTable;
