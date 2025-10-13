// frontend/src/pages/MSPDashboard.tsx (Final Compiled Version)

import React, { useMemo } from 'react';
import { Box, Typography, Grid, Card, CardContent, useTheme } from '@mui/material';
// Imports for the MSP Dashboard components
import ClientValueLineChart from '../components/NivoCharts/ClientValueLineChart';
import GovernanceDonutChart from '../components/NivoCharts/GovernanceDonutChart';
import ClientPrioritizationTable from '../components/ClientPrioritizationTable';

// Imports for data access (assume interfaces are defined or imported)
import { getMetricsData, getRecommendationData } from '../services/dataService';

// KpiCard helper (UPDATED to include 'warning' color)
const KpiCard = ({ title, value, color }: { title: string; value: string; color: 'primary' | 'error' | 'success' | 'warning' }) => (
    <Card elevation={6}>
        <CardContent>
            <Typography color={`${color}.main`} variant="h6">{title}</Typography>
            <Typography variant="h4" fontWeight="bold">{value}</Typography>
        </CardContent>
    </Card>
);

const MSPDashboard: React.FC = () => {
    const theme = useTheme();

    // Data Access (Simulated) - Assuming Metric and Recommendation interfaces are globally available
    const metrics: any[] = getMetricsData();
    const allRecommendations: any[] = getRecommendationData();

    // --- DATA AGGREGATION & KPI CALCULATION ---

    // Total Savings Delivered (Scaled up for visual effect on the chart)
    const totalSavingsDelivered = useMemo(() =>
        allRecommendations.reduce((sum: number, r: any) => sum + r.projected_savings_monthly, 0) * 100
    , [allRecommendations]);

    // Mock Client KPIs
    const totalClientsManaged = 48;

    // 1. Prepare Data for Cumulative Value Trend Chart
    const cumulativeValueData = useMemo(() => {
        return [{
            id: 'Total Savings',
            data: [
                { x: "Jan", y: totalSavingsDelivered * 0.10 },
                { x: "Feb", y: totalSavingsDelivered * 0.35 },
                { x: "Mar", y: totalSavingsDelivered * 0.60 },
                { x: "Apr", y: totalSavingsDelivered * 0.85 },
                { x: "May", y: totalSavingsDelivered },
            ]
        }];
    }, [totalSavingsDelivered]);

    // 2. Prepare Data for Governance Donut Chart
    const governanceData = useMemo(() => {
        const totalMonthlyCost = metrics.reduce((sum: number, m: any) => sum + m.unblended_cost_usd, 0) * 30;
        const untaggedSpend = metrics.filter(d => d.billing_tag_owner === 'owner:unknown')
                                     .reduce((sum: number, d: any) => sum + d.unblended_cost_usd, 0) * 30;

        const complianceRate = totalMonthlyCost > 0 ? ((totalMonthlyCost - untaggedSpend) / totalMonthlyCost) * 100 : 0;

        return {
            complianceRate: complianceRate,
            data: [
                { id: "Tagged Spend", label: "Tagged Spend", value: totalMonthlyCost - untaggedSpend, color: theme.palette.success.main },
                // Use a muted color for the slice to fit the aesthetic
                { id: "Untagged Waste", label: "Untagged Waste", value: untaggedSpend, color: theme.palette.secondary.dark },
            ],
        };
    }, [metrics, theme.palette.success.main, theme.palette.secondary.dark]);

    // 3. Prepare Data for Client Prioritization Table (Mock Data)
    const clientSummaryData = useMemo(() => {
        return [
            { client_name: "Client Alpha", total_spend: 8500, total_potential_savings: 550, tagging_compliance: 95 },
            { client_name: "Client Beta", total_spend: 2100, total_potential_savings: 45, tagging_compliance: 75 },
            { client_name: "Client Gamma", total_spend: 12000, total_potential_savings: 1200, tagging_compliance: 88 },
        ].sort((a, b) => b.total_potential_savings - a.total_potential_savings);
    }, []);


    // --- RENDER ---
    return (
        <Box sx={{ p: 4, bgcolor: theme.palette.background.default, color: theme.palette.text.primary }}>
            <Typography variant="h3" gutterBottom>
                MSP Operations Dashboard
            </Typography>

            {/* 1. KPI BAR - Highlighting Value */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={4}>
                    <KpiCard title="Total Clients Managed" value={String(totalClientsManaged)} color="primary" />
                </Grid>
                <Grid item xs={12} sm={4}>
                    <KpiCard
                        title="Total Savings Delivered"
                        value={`$${(totalSavingsDelivered / 1000).toFixed(1)}M+`}
                        color="success"
                    />
                </Grid>
                <Grid item xs={12} sm={4}>
                    <KpiCard
                        title="Avg. Tagging Compliance"
                        value={`${governanceData.complianceRate.toFixed(1)}%`}
                        // FIX: Logic is now valid due to updated KpiCard type definition
                        color={governanceData.complianceRate < 85 ? 'warning' : 'primary'}
                    />
                </Grid>
            </Grid>

            {/* 2. MAIN CONTENT GRID */}
            <Grid container spacing={4}>

                {/* LEFT: CUMULATIVE VALUE TREND (Line Chart) - 2/3 width */}
                <Grid item xs={12} md={8}>
                    <ClientValueLineChart data={cumulativeValueData} totalSavings={totalSavingsDelivered} />
                </Grid>

                {/* RIGHT: GOVERNANCE SPEND (Donut Chart) - 1/3 width */}
                <Grid item xs={12} md={4}>
                    <GovernanceDonutChart
                        data={governanceData.data}
                    />
                </Grid>

                {/* BOTTOM: CLIENT PRIORITIZATION TABLE */}
                <Grid item xs={12}>
                    <ClientPrioritizationTable data={clientSummaryData} />
                </Grid>
            </Grid>
        </Box>
    );
};

export default MSPDashboard;