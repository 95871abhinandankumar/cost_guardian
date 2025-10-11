// frontend/src/pages/ITDashboard.tsx

import React, { useMemo, useState } from 'react';
import { Box, Typography, Grid, Card, CardContent, CircularProgress, Alert, useTheme } from '@mui/material';
import AnomalyScatterPlot from '../components/NivoCharts/AnomalyScatterPlot';
import ActionQueueList from '../components/ActionQueue/ActionQueueList';
import UtilizationLineChart from '../components/NivoCharts/UtilizationLineChart';
import GovernanceDonutChart from '../components/NivoCharts/GovernanceDonutChart';
import { getMetricsData, getRecommendationData } from '../services/dataService';
import { RecommendationType } from '../components/ActionQueue/ActionButton';

// --- INTERFACE DEFINITIONS (Centralized for this component) ---
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
    recommendation_type: RecommendationType;
    current_monthly_cost: number;
    projected_savings_monthly: number;
    recommended_action: string;
    action_status: string;
}

// KPI Card helper
const KPI_Card = ({ title, value, color }: { title: string; value: string; color: 'primary' | 'error' | 'success' }) => (
    <Card elevation={3}>
        <CardContent>
            <Typography color={`${color}.main`} variant="h6">{title}</Typography>
            <Typography variant="h4" fontWeight="bold">{value}</Typography>
        </CardContent>
    </Card>
);

const ITDashboard: React.FC = () => {
    const theme = useTheme();
    const [isLoading] = useState(false);

    // Data Access (Simulated)
    const metrics: Metric[] = getMetricsData();
    const allRecommendations: Recommendation[] = getRecommendationData() as Recommendation[];

    // Data Processing Logic (Memoized KPI Calculations)
    const computeMetrics = useMemo(() => metrics.filter((d) => d.resource_type === 'compute'), [metrics]);
    const pendingCritical = useMemo(
        () => allRecommendations.filter(
            (r) => (r.flag_severity === 'Critical' || r.flag_severity === 'High') && r.action_status === 'pending'
        ),
        [allRecommendations]
    );
    const totalPotentialSavings = pendingCritical.reduce((sum: number, r: Recommendation) => sum + r.projected_savings_monthly, 0);
    const totalUtilization = useMemo(() => {
        if (computeMetrics.length === 0) return 0;
        const sumUtil: number = computeMetrics.reduce((sum, d) => sum + d.utilization_score, 0);
        return (sumUtil / computeMetrics.length) * 100;
    }, [computeMetrics]);

    // Prepare scatter plot data
    const scatterData = useMemo(() => {
        const anomalyResourceIds = new Set(pendingCritical.map((r) => r.resource_id_impacted));
        return [
            {
                id: 'Compute Resources',
                data: computeMetrics.map((d) => {
                    const monthlyCost = Math.max(0, d.unblended_cost_usd * 30);
                    return {
                        x: d.utilization_score * 100,
                        y: monthlyCost,
                        id: d.resource_id,
                        severity: anomalyResourceIds.has(d.resource_id) ? 'Critical' : 'Healthy',
                        owner: d.billing_tag_owner,
                    };
                }),
            },
        ];
    }, [computeMetrics, pendingCritical]);

    // Prepare Utilization Trend Line Chart
    const trendData = useMemo(() => {
        return [{
            id: 'Avg Utilization',
            color: theme.palette.primary.main, // Uses the aesthetic violet/blue line color
            data: [
                { x: "Sept 10", y: 30 },
                { x: "Sept 20", y: 45 },
                { x: "Sept 30", y: 55 },
                { x: "Oct 08", y: Number(totalUtilization.toFixed(0)) },
            ]
        }]
    }, [theme.palette.primary.main, totalUtilization]);

    // Prepare Governance Donut Chart
    const governanceData = useMemo(() => {
        const taggedCost = metrics.filter(d => d.billing_tag_owner !== 'owner:unknown').reduce((sum: number, d: Metric) => sum + d.unblended_cost_usd, 0) * 30;
        const untaggedCost = metrics.filter(d => d.billing_tag_owner === 'owner:unknown').reduce((sum: number, d: Metric) => sum + d.unblended_cost_usd, 0) * 30;
        const totalCost = taggedCost + untaggedCost;

        const taggedPercent = totalCost > 0 ? (taggedCost / totalCost) * 100 : 0;
        const untaggedPercent = totalCost > 0 ? (untaggedCost / totalCost) * 100 : 0;

        return [
            { id: "Tagged", label: "Tagged Spend", value: taggedPercent, color: theme.palette.success.main },
            { id: "Untagged", label: "Untagged Spend", value: untaggedPercent, color: theme.palette.error.main },
        ];
    }, [metrics, theme.palette.success.main, theme.palette.error.main]);

    const handleActionCompleted = () => {
        console.log('Dashboard Refresh Triggered (Simulated).');
    };

    if (isLoading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 10 }}>
                <CircularProgress />
                <Typography sx={{ ml: 2 }}>Loading AI Data...</Typography>
            </Box>
        );
    }
    if (computeMetrics.length === 0) {
        return <Alert severity="info" sx={{ m: 4 }}>No compute resources found in the current dataset to analyze.</Alert>;
    }

    return (
        <Box
            sx={{
                p: 4,
                // This forces the dynamic background color, overriding light theme defaults
                bgcolor: theme.palette.background.default
            }}
        >
            <Typography variant="h3" gutterBottom>
                IT Operations Dashboard
            </Typography>

            {/* 1. KPI BAR */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={4}>
                    <KPI_Card title="Critical Actions Pending" value={String(pendingCritical.length)} color="error" />
                </Grid>
                <Grid item xs={12} sm={4}>
                    <KPI_Card title="Avg. System Utilization" value={`${totalUtilization.toFixed(1)}%`} color="primary" />
                </Grid>
                <Grid item xs={12} sm={4}>
                    <KPI_Card
                        title="Potential Monthly Waste"
                        value={`$${totalPotentialSavings.toFixed(0)}`}
                        color="success"
                    />
                </Grid>
            </Grid>

            {/* 2. MAIN CONTENT GRID */}
            <Grid container spacing={4}>
                <Grid item xs={12} md={8}>
                    <AnomalyScatterPlot data={scatterData} />
                </Grid>
                <Grid item xs={12} md={4}>
                    <ActionQueueList data={allRecommendations} onActionCompleted={handleActionCompleted} />
                </Grid>

                {/* NEW BOTTOM ROW FOR CONTEXT */}
                <Grid item xs={12} md={6}>
                    <UtilizationLineChart data={trendData} />
                </Grid>

                <Grid item xs={12} md={6}>
                    <GovernanceDonutChart data={governanceData} />
                </Grid>
            </Grid>
        </Box>
    );
};

export default ITDashboard;