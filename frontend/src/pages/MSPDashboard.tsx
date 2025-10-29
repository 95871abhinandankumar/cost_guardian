// frontend/src/pages/MSPDashboard.tsx (Final Compiled Version)

import React, { useMemo, useState, useEffect } from 'react';
import { 
    Box, Typography, Grid, Card, CardContent, CircularProgress, Alert, useTheme,
    alpha, Fade, Paper
} from '@mui/material';
import { 
    Business, TrendingUp, Security, 
    Analytics, AccountTree, ArrowUpward
} from '@mui/icons-material';
import ClientValueLineChart from '../components/NivoCharts/ClientValueLineChart';
import GovernanceDonutChart from '../components/NivoCharts/GovernanceDonutChart';
import ClientPrioritizationTable from '../components/ClientPrioritizationTable';
import { getMetricsData, getRecommendationData } from '../services/dataService';

// Modern KPI Card with gradient and icons
const KpiCard = ({ 
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

const MSPDashboard: React.FC = () => {
    const theme = useTheme();
    const [isLoading, setIsLoading] = useState(true);
    const [metrics, setMetrics] = useState<any[]>([]);
    const [allRecommendations, setAllRecommendations] = useState<any[]>([]);
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

    // --- DATA AGGREGATION & KPI CALCULATION (hooks must be before early returns) ---
    const totalSavingsDelivered = useMemo(() =>
        allRecommendations.reduce((sum: number, r: any) => sum + r.projected_savings_monthly, 0) * 100
    , [allRecommendations]);

    const totalClientsManaged = 48;

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

    const governanceData = useMemo(() => {
        const totalMonthlyCost = metrics.reduce((sum: number, m: any) => sum + m.unblended_cost_usd, 0) * 30;
        const untaggedSpend = metrics.filter(d => d.billing_tag_owner === 'owner:unknown')
                                     .reduce((sum: number, d: any) => sum + d.unblended_cost_usd, 0) * 30;
        const complianceRate = totalMonthlyCost > 0 ? ((totalMonthlyCost - untaggedSpend) / totalMonthlyCost) * 100 : 0;
        return {
            complianceRate: complianceRate,
            data: [
                { id: "Tagged Spend", label: "Tagged Spend", value: totalMonthlyCost - untaggedSpend, color: theme.palette.success.main },
                { id: "Untagged Waste", label: "Untagged Waste", value: untaggedSpend, color: theme.palette.secondary.dark },
            ],
        };
    }, [metrics, theme.palette.success.main, theme.palette.secondary.dark]);

    const clientSummaryData = useMemo(() => {
        return [
            { client_name: "Client Alpha", total_spend: 8500, total_potential_savings: 550, tagging_compliance: 95 },
            { client_name: "Client Beta", total_spend: 2100, total_potential_savings: 45, tagging_compliance: 75 },
            { client_name: "Client Gamma", total_spend: 12000, total_potential_savings: 1200, tagging_compliance: 88 },
        ].sort((a, b) => b.total_potential_savings - a.total_potential_savings);
    }, []);

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


    // --- RENDER ---
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
                            MSP Operations Dashboard
                        </Typography>
                        <Typography 
                            variant="body1" 
                            sx={{ 
                                color: theme.palette.text.secondary,
                                fontSize: '1.1rem',
                                fontWeight: 400,
                            }}
                        >
                            Multi-tenant cost optimization and governance insights
                        </Typography>
                    </Box>
                </Fade>

                {/* Modern KPI Cards */}
                <Grid container spacing={3} sx={{ mb: 5 }}>
                    <Grid item xs={12} sm={6} lg={4}>
                        <KpiCard 
                            title="Total Clients Managed" 
                            value={String(totalClientsManaged)} 
                            color="primary"
                            subtitle="Active managed accounts"
                            icon={Business}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6} lg={4}>
                        <KpiCard
                            title="Total Savings Delivered"
                            value={`$${(totalSavingsDelivered / 1000).toFixed(1)}M+`}
                            color="success"
                            subtitle="Cumulative optimization value"
                            icon={TrendingUp}
                            trend="up"
                        />
                    </Grid>
                    <Grid item xs={12} sm={6} lg={4}>
                        <KpiCard
                            title="Avg. Tagging Compliance"
                            value={`${governanceData.complianceRate.toFixed(1)}%`}
                            color={governanceData.complianceRate < 85 ? 'warning' : 'primary'}
                            subtitle={governanceData.complianceRate < 85 ? "Needs improvement" : "Compliant"}
                            icon={Security}
                        />
                    </Grid>
                </Grid>

                {/* Modern Content Grid */}
                <Grid container spacing={4}>
                    <Grid item xs={12} md={8}>
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
                                        Cumulative Value Delivered
                                    </Typography>
                                </Box>
                                <ClientValueLineChart data={cumulativeValueData} totalSavings={totalSavingsDelivered} />
                            </Paper>
                        </Fade>
                    </Grid>

                    <Grid item xs={12} md={4}>
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
                                    <Security sx={{ color: theme.palette.info.main }} />
                                    <Typography variant="h6" fontWeight={700}>
                                        Governance Compliance
                                    </Typography>
                                </Box>
                                <GovernanceDonutChart data={governanceData.data} />
                            </Paper>
                        </Fade>
                    </Grid>

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
                                    <AccountTree sx={{ color: theme.palette.primary.main }} />
                                    <Typography variant="h6" fontWeight={700}>
                                        Client Prioritization
                                    </Typography>
                                </Box>
                                <ClientPrioritizationTable data={clientSummaryData} />
                            </Paper>
                        </Fade>
                    </Grid>
                </Grid>
            </Box>
        </Box>
    );
};

export default MSPDashboard;