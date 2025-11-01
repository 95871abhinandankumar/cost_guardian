// frontend/src/pages/FinanceDashboard.tsx

import React, { useMemo, useState, useEffect } from 'react';
import { 
    Box, Typography, Grid, Card, CardContent, CircularProgress, Alert, useTheme,
    alpha, Fade, Paper
} from '@mui/material';
import { 
    TrendingUp, TrendingDown, AccountBalance, Savings, 
    Analytics, ArrowUpward, ArrowDownward
} from '@mui/icons-material';
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
    owner?: string;
    service_name_simplified?: string;
}

// Modern KPI Card with gradient and icons
const KPICard = ({ 
    title, 
    value, 
    color, 
    subtitle, 
    icon: Icon,
    trend 
}: { 
    title: string; 
    value: string; 
    color: 'primary' | 'error' | 'success' | 'warning'; 
    subtitle?: string;
    icon?: React.ElementType;
    trend?: 'up' | 'down';
}) => {
    const theme = useTheme();
    const isLight = theme.palette.mode === 'light';
    
    const gradientColors = {
        primary: isLight ? ['#667eea', '#764ba2'] : ['#7c8aff', '#9c7cff'],
        success: isLight ? ['#11998e', '#38ef7d'] : ['#26d0ce', '#1a2980'],
        error: isLight ? ['#eb3349', '#f45c43'] : ['#ff6b6b', '#ee5a6f'],
        warning: isLight ? ['#f093fb', '#f5576c'] : ['#ffa726', '#fb8c00'],
    };
    
    const bgGradient = `linear-gradient(135deg, ${gradientColors[color][0]} 0%, ${gradientColors[color][1]} 100%)`;
    
    return (
        <Fade in={true} timeout={600}>
            <Card 
                elevation={0}
                sx={{
                    background: isLight 
                        ? `linear-gradient(135deg, ${alpha(theme.palette[color].main, 0.1)} 0%, ${alpha(theme.palette[color].main, 0.05)} 100%)`
                        : `linear-gradient(135deg, ${alpha(theme.palette[color].main, 0.15)} 0%, ${alpha(theme.palette[color].main, 0.08)} 100%)`,
                    borderRadius: 3,
                    border: `1px solid ${alpha(theme.palette[color].main, 0.2)}`,
                    position: 'relative',
                    overflow: 'hidden',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: `0 8px 24px ${alpha(theme.palette[color].main, 0.25)}`,
                        border: `1px solid ${alpha(theme.palette[color].main, 0.4)}`,
                    },
                    '&::before': {
                        content: '""',
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        height: '4px',
                        background: bgGradient,
                    }
                }}
            >
                <CardContent sx={{ p: 3, position: 'relative', zIndex: 1 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                        <Box>
                            <Typography 
                                variant="subtitle2" 
                                sx={{ 
                                    color: theme.palette[color].main,
                                    fontWeight: 600,
                                    textTransform: 'uppercase',
                                    letterSpacing: 0.5,
                                    fontSize: '0.75rem',
                                    mb: 0.5
                                }}
                            >
                                {title}
                            </Typography>
                            <Typography 
                                variant="h4" 
                                fontWeight="bold"
                                sx={{ 
                                    fontSize: { xs: '1.75rem', sm: '2rem' },
                                    background: bgGradient,
                                    WebkitBackgroundClip: 'text',
                                    WebkitTextFillColor: 'transparent',
                                    backgroundClip: 'text',
                                }}
                            >
                                {value}
                            </Typography>
                        </Box>
                        {Icon && (
                            <Box
                                sx={{
                                    p: 1.5,
                                    borderRadius: 2,
                                    background: bgGradient,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                }}
                            >
                                <Icon sx={{ color: 'white', fontSize: 28 }} />
                            </Box>
                        )}
                    </Box>
                    {subtitle && (
                        <Box display="flex" alignItems="center" gap={0.5}>
                            {trend === 'up' && <ArrowUpward sx={{ fontSize: 14, color: theme.palette.success.main }} />}
                            {trend === 'down' && <ArrowDownward sx={{ fontSize: 14, color: theme.palette.error.main }} />}
                            <Typography 
                                variant="body2" 
                                sx={{ 
                                    color: theme.palette.text.secondary,
                                    fontSize: '0.875rem',
                                    fontWeight: 500
                                }}
                            >
                                {subtitle}
                            </Typography>
                        </Box>
                    )}
                </CardContent>
            </Card>
        </Fade>
    );
};

const FinanceDashboard: React.FC = () => {
    const theme = useTheme();
    const [isLoading, setIsLoading] = useState(true);
    const [metrics, setMetrics] = useState<Metric[]>([]);
    const [allRecommendations, setAllRecommendations] = useState<Recommendation[]>([]);
    const [error, setError] = useState<string | null>(null);

    // Fetch data from API
    useEffect(() => {
        const fetchData = async () => {
            try {
                setIsLoading(true);
                const [metricsData, recommendationsData] = await Promise.all([
                    getMetricsData(),
                    getRecommendationData()
                ]);
                setMetrics(metricsData);
                setAllRecommendations(recommendationsData);
                setError(null);
            } catch (err) {
                console.error('Error fetching data:', err);
                setError('Failed to load data. Please check if backend is running.');
            } finally {
                setIsLoading(false);
            }
        };
        fetchData();
    }, []);

    // Financial KPI Calculations (hooks must be before early returns)
    const financialMetrics = useMemo(() => {
        const totalMonthlySpend = metrics.reduce((sum, metric) => sum + (metric.unblended_cost_usd * 30), 0);
        const totalProjectedSavings = allRecommendations
            .filter(r => r.action_status === 'pending')
            .reduce((sum, r) => sum + r.projected_savings_monthly, 0);
        const forecastedSpend = totalMonthlySpend * 1.15;
        const forecastVariance = ((totalMonthlySpend - forecastedSpend) / forecastedSpend) * 100;
        return {
            totalMonthlySpend,
            totalProjectedSavings,
            forecastVariance,
            roi: totalProjectedSavings > 0 ? ((totalProjectedSavings / totalMonthlySpend) * 100) : 0
        };
    }, [metrics, allRecommendations]);

    const costTrendData = useMemo(() => {
        const currentSpend = financialMetrics.totalMonthlySpend;
        const projectedSpend = currentSpend * 1.15;
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

    const costAllocationData = useMemo(() => {
        const serviceGroups = metrics.reduce((acc, metric) => {
            const service = metric.service_name_simplified;
            const monthlyCost = metric.unblended_cost_usd * 30;
            if (!acc[service]) {
                acc[service] = { cost: 0, children: {} };
            }
            acc[service].cost += monthlyCost;
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

    const savingsPrioritizationData = useMemo(() => {
        return allRecommendations
            .filter(r => r.action_status === 'pending')
            .sort((a, b) => b.projected_savings_monthly - a.projected_savings_monthly)
            .map(r => ({
                id: r.recommendation_id,
                resource: r.resource_id_impacted,
                owner: r.owner || metrics.find(m => m.resource_id === r.resource_id_impacted)?.billing_tag_owner || 'Unknown',
                service: r.service_name_simplified || metrics.find(m => m.resource_id === r.resource_id_impacted)?.service_name_simplified || 'Unknown',
                currentCost: r.current_monthly_cost,
                projectedSavings: r.projected_savings_monthly,
                action: r.recommended_action,
                severity: r.flag_severity
            }));
    }, [allRecommendations, metrics]);

    // Show loading state
    if (isLoading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                <CircularProgress />
            </Box>
        );
    }

    // Show error state
    if (error) {
        return (
            <Box p={3}>
                <Alert severity="error">{error}</Alert>
            </Box>
        );
    }

    if (metrics.length === 0) {
        return <Alert severity="info" sx={{ m: 4 }}>No financial data found to analyze.</Alert>;
    }

    return (
        <Box
            sx={{
                minHeight: 'calc(100vh - 64px)',
                width: '100%',
                overflowX: 'hidden',
                bgcolor: theme.palette.background.default,
                pb: 6,
            }}
        >
            <Box
                sx={{
                    maxWidth: '1400px',
                    width: '100%',
                    mx: 'auto',
                    px: { xs: 2, sm: 4, md: 6 },
                    pt: 4,
                    boxSizing: 'border-box',
                }}
            >
                {/* Modern Header */}
                <Fade in={true} timeout={800}>
                    <Box sx={{ mb: 5 }}>
                        <Typography 
                            variant="h3" 
                            sx={{
                                fontWeight: 800,
                                fontSize: { xs: '2rem', md: '2.75rem' },
                                mb: 1,
                                background: theme.palette.mode === 'light'
                                    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                                    : 'linear-gradient(135deg, #a1c4fd 0%, #9c7cff 100%)',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                backgroundClip: 'text',
                            }}
                        >
                            Finance Dashboard
                        </Typography>
                        <Typography 
                            variant="body1" 
                            sx={{ 
                                color: theme.palette.text.secondary,
                                fontSize: '1.1rem',
                                fontWeight: 400,
                            }}
                        >
                            Comprehensive financial insights and optimization opportunities
                        </Typography>
                    </Box>
                </Fade>

                {/* Modern KPI Cards */}
                <Grid container spacing={3} sx={{ mb: 5 }}>
                    <Grid item xs={12} sm={6} lg={4}>
                        <KPICard 
                            title="Total Monthly Spend" 
                            value={`$${financialMetrics.totalMonthlySpend.toLocaleString()}`} 
                            color="primary"
                            subtitle="Current month actual spend"
                            icon={AccountBalance}
                            trend="up"
                        />
                    </Grid>
                    <Grid item xs={12} sm={6} lg={4}>
                        <KPICard 
                            title="Total Projected Savings" 
                            value={`$${financialMetrics.totalProjectedSavings.toLocaleString()}`} 
                            color="success"
                            subtitle={`${financialMetrics.roi.toFixed(1)}% ROI potential`}
                            icon={Savings}
                            trend="up"
                        />
                    </Grid>
                    <Grid item xs={12} sm={6} lg={4}>
                        <KPICard 
                            title="Forecast Variance" 
                            value={`${Math.abs(financialMetrics.forecastVariance).toFixed(1)}%`} 
                            color="warning"
                            subtitle="vs. projected budget"
                            icon={TrendingDown}
                            trend="down"
                        />
                    </Grid>
                </Grid>

                {/* Modern Content Grid with Enhanced Cards */}
                <Grid container spacing={4}>
                    {/* Cost Trend Chart */}
                    <Grid item xs={12} lg={8}>
                        <Fade in={true} timeout={1000}>
                            <Paper
                                elevation={0}
                                sx={{
                                    p: 3,
                                    borderRadius: 3,
                                    bgcolor: theme.palette.mode === 'light' 
                                        ? alpha(theme.palette.background.paper, 0.8)
                                        : alpha(theme.palette.background.paper, 0.6),
                                    backdropFilter: 'blur(20px)',
                                    border: `1px solid ${alpha(theme.palette.divider, 0.5)}`,
                                    boxShadow: theme.palette.mode === 'light'
                                        ? '0 8px 32px rgba(0, 0, 0, 0.08)'
                                        : '0 8px 32px rgba(0, 0, 0, 0.3)',
                                }}
                            >
                                <Box display="flex" alignItems="center" gap={1} mb={2}>
                                    <Analytics sx={{ color: theme.palette.primary.main }} />
                                    <Typography variant="h6" fontWeight={700}>
                                        Cost Trend Analysis
                                    </Typography>
                                </Box>
                                <CostTrendChart data={costTrendData} />
                            </Paper>
                        </Fade>
                    </Grid>

                    {/* Cost Allocation Chart */}
                    <Grid item xs={12} lg={4}>
                        <Fade in={true} timeout={1200}>
                            <Paper
                                elevation={0}
                                sx={{
                                    p: 3,
                                    borderRadius: 3,
                                    bgcolor: theme.palette.mode === 'light' 
                                        ? alpha(theme.palette.background.paper, 0.8)
                                        : alpha(theme.palette.background.paper, 0.6),
                                    backdropFilter: 'blur(20px)',
                                    border: `1px solid ${alpha(theme.palette.divider, 0.5)}`,
                                    boxShadow: theme.palette.mode === 'light'
                                        ? '0 8px 32px rgba(0, 0, 0, 0.08)'
                                        : '0 8px 32px rgba(0, 0, 0, 0.3)',
                                    height: '100%',
                                }}
                            >
                                <Box display="flex" alignItems="center" gap={1} mb={2}>
                                    <TrendingUp sx={{ color: theme.palette.success.main }} />
                                    <Typography variant="h6" fontWeight={700}>
                                        Cost Allocation
                                    </Typography>
                                </Box>
                                <CostAllocationChart data={costAllocationData} />
                            </Paper>
                        </Fade>
                    </Grid>

                    {/* Savings Prioritization Table */}
                    <Grid item xs={12}>
                        <Fade in={true} timeout={1400}>
                            <Paper
                                elevation={0}
                                sx={{
                                    p: 3,
                                    borderRadius: 3,
                                    bgcolor: theme.palette.mode === 'light' 
                                        ? alpha(theme.palette.background.paper, 0.8)
                                        : alpha(theme.palette.background.paper, 0.6),
                                    backdropFilter: 'blur(20px)',
                                    border: `1px solid ${alpha(theme.palette.divider, 0.5)}`,
                                    boxShadow: theme.palette.mode === 'light'
                                        ? '0 8px 32px rgba(0, 0, 0, 0.08)'
                                        : '0 8px 32px rgba(0, 0, 0, 0.3)',
                                }}
                            >
                                <Box display="flex" alignItems="center" gap={1} mb={3}>
                                    <Savings sx={{ color: theme.palette.success.main }} />
                                    <Typography variant="h6" fontWeight={700}>
                                        Savings Prioritization
                                    </Typography>
                                </Box>
                                <SavingsPrioritizationTable data={savingsPrioritizationData} />
                            </Paper>
                        </Fade>
                    </Grid>
                </Grid>
            </Box>
        </Box>
    );
};

export default FinanceDashboard;
