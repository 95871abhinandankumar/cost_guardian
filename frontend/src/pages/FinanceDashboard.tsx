// frontend/src/pages/FinanceDashboard.tsx

import React, { useMemo, useState } from 'react';
import { Box, Typography, Grid, Card, CardContent, CircularProgress, Alert, useTheme } from '@mui/material';
import { getMetricsData, getRecommendationData } from '../services/dataService';
import CostTrendChart from '../components/NivoCharts/CostTrendChart';
import CostAllocationChart from '../components/NivoCharts/CostAllocationChart';
import SavingsPrioritizationTable from '../components/SavingsPrioritizationTable';

// --- INTERFACE DEFINITIONS ---
interface Metric {
    resource_id: string;
    resource_type: string;
    unblended_cost_usd: number;
    utilization_score: number;
    billing_tag_owner: string;
    timestamp_day: string;
    service_name_simplified: string;
}

interface Recommendation {
    recommendation_id: string;
    resource_id_impacted: string;
    resource_type: string;
    flag_severity: string;
    recommendation_type: string;
    current_monthly_cost: number;
    projected_savings_monthly: number;
    recommended_action: string;
    action_status: string;
    client_name: string;
}

// KPI Card helper component
const KPICard = ({ title, value, color, subtitle }: { 
    title: string; 
    value: string; 
    color: 'primary' | 'error' | 'success'; 
    subtitle?: string;
}) => (
    <Card elevation={3}>
        <CardContent>
            <Typography color={`${color}.main`} variant="h6">{title}</Typography>
            <Typography variant="h4" fontWeight="bold">{value}</Typography>
            {subtitle && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {subtitle}
                </Typography>
            )}
        </CardContent>
    </Card>
);

const FinanceDashboard: React.FC = () => {
    const theme = useTheme();
    const [isLoading] = useState(false);

    // Data Access
    const metrics: Metric[] = getMetricsData();
    const allRecommendations: Recommendation[] = getRecommendationData() as Recommendation[];

    // Financial KPI Calculations
    const financialMetrics = useMemo(() => {
        const totalMonthlySpend = metrics.reduce((sum, metric) => sum + (metric.unblended_cost_usd * 30), 0);
        const totalProjectedSavings = allRecommendations
            .filter(r => r.action_status === 'pending')
            .reduce((sum, r) => sum + r.projected_savings_monthly, 0);
        
        // Calculate forecast variance (simplified - in real app this would come from forecasting model)
        const forecastedSpend = totalMonthlySpend * 1.15; // 15% growth assumption
        const forecastVariance = ((totalMonthlySpend - forecastedSpend) / forecastedSpend) * 100;
        
        return {
            totalMonthlySpend,
            totalProjectedSavings,
            forecastVariance,
            roi: totalProjectedSavings > 0 ? ((totalProjectedSavings / totalMonthlySpend) * 100) : 0
        };
    }, [metrics, allRecommendations]);

    // Cost trend data for line chart
    const costTrendData = useMemo(() => {
        const currentSpend = financialMetrics.totalMonthlySpend;
        const projectedSpend = currentSpend * 1.15; // 15% growth
        const postActionSpend = currentSpend - financialMetrics.totalProjectedSavings;
        
        return [
            {
                id: 'Actual Spend',
                color: theme.palette.error.main,
                data: [
                    { x: 'Sept', y: currentSpend * 0.85 },
                    { x: 'Oct', y: currentSpend * 0.92 },
                    { x: 'Nov', y: currentSpend },
                ]
            },
            {
                id: 'Forecasted Spend',
                color: theme.palette.warning.main,
                data: [
                    { x: 'Sept', y: projectedSpend * 0.85 },
                    { x: 'Oct', y: projectedSpend * 0.92 },
                    { x: 'Nov', y: projectedSpend },
                ]
            },
            {
                id: 'Post-Action Projected',
                color: theme.palette.success.main,
                data: [
                    { x: 'Sept', y: postActionSpend * 0.85 },
                    { x: 'Oct', y: postActionSpend * 0.92 },
                    { x: 'Nov', y: postActionSpend },
                ]
            }
        ];
    }, [financialMetrics, theme.palette]);

    // Cost allocation data for treemap/sunburst
    const costAllocationData = useMemo(() => {
        const serviceGroups = metrics.reduce((acc, metric) => {
            const service = metric.service_name_simplified;
            const monthlyCost = metric.unblended_cost_usd * 30;
            
            if (!acc[service]) {
                acc[service] = { cost: 0, children: {} };
            }
            acc[service].cost += monthlyCost;
            
            // Group by owner within service
            const owner = metric.billing_tag_owner;
            if (!acc[service].children[owner]) {
                acc[service].children[owner] = 0;
            }
            acc[service].children[owner] += monthlyCost;
            
            return acc;
        }, {} as Record<string, { cost: number; children: Record<string, number> }>);

        return Object.entries(serviceGroups).map(([service, data]) => ({
            id: service,
            value: data.cost,
            children: Object.entries(data.children).map(([owner, cost]) => ({
                id: `${service}-${owner}`,
                value: cost,
                owner,
                service
            }))
        }));
    }, [metrics]);

    // Savings prioritization data
    const savingsPrioritizationData = useMemo(() => {
        return allRecommendations
            .filter(r => r.action_status === 'pending')
            .sort((a, b) => b.projected_savings_monthly - a.projected_savings_monthly)
            .map(r => ({
                id: r.recommendation_id,
                resource: r.resource_id_impacted,
                owner: metrics.find(m => m.resource_id === r.resource_id_impacted)?.billing_tag_owner || 'Unknown',
                service: metrics.find(m => m.resource_id === r.resource_id_impacted)?.service_name_simplified || 'Unknown',
                currentCost: r.current_monthly_cost,
                projectedSavings: r.projected_savings_monthly,
                action: r.recommended_action,
                severity: r.flag_severity
            }));
    }, [allRecommendations, metrics]);

    if (isLoading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 10 }}>
                <CircularProgress />
                <Typography sx={{ ml: 2 }}>Loading Financial Data...</Typography>
            </Box>
        );
    }

    if (metrics.length === 0) {
        return <Alert severity="info" sx={{ m: 4 }}>No financial data found to analyze.</Alert>;
    }

    return (
        <Box
            sx={{
                p: 4,
                bgcolor: theme.palette.background.default
            }}
        >
            <Typography variant="h3" gutterBottom>
                💰 Finance Dashboard: The Value and Accountability View
            </Typography>

            {/* 1. KPI BAR */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={4}>
                    <KPICard 
                        title="Total Monthly Spend" 
                        value={`$${financialMetrics.totalMonthlySpend.toFixed(0)}`} 
                        color="primary"
                        subtitle="Current month actual spend"
                    />
                </Grid>
                <Grid item xs={12} sm={4}>
                    <KPICard 
                        title="Total Projected Savings" 
                        value={`$${financialMetrics.totalProjectedSavings.toFixed(0)}`} 
                        color="success"
                        subtitle={`${financialMetrics.roi.toFixed(1)}% ROI potential`}
                    />
                </Grid>
                <Grid item xs={12} sm={4}>
                    <KPICard 
                        title="Forecast Variance" 
                        value={`${financialMetrics.forecastVariance.toFixed(1)}%`} 
                        color="error"
                        subtitle="vs. projected budget"
                    />
                </Grid>
            </Grid>

            {/* 2. MAIN CONTENT GRID */}
            <Grid container spacing={4}>
                {/* Cost Trend & ROI Chart */}
                <Grid item xs={12} md={8}>
                    <CostTrendChart data={costTrendData} />
                </Grid>

                {/* Cost Allocation Chart */}
                <Grid item xs={12} md={4}>
                    <CostAllocationChart data={costAllocationData} />
                </Grid>

                {/* Savings Prioritization Table */}
                <Grid item xs={12}>
                    <SavingsPrioritizationTable data={savingsPrioritizationData} />
                </Grid>
            </Grid>
        </Box>
    );
};

export default FinanceDashboard;
