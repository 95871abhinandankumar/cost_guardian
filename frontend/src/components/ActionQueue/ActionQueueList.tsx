// frontend/src/components/ActionQueue/ActionQueueList.tsx
import React from 'react';
import { 
    Box, Typography, Chip, Divider, useTheme, alpha 
} from '@mui/material';
import { Error as ErrorIcon } from '@mui/icons-material';
import ActionButton, { RecommendationType } from './ActionButton';

// Interfaces
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

interface ActionQueueListProps {
    data: Recommendation[];
    onActionCompleted?: () => void;
}

const ActionQueueList: React.FC<ActionQueueListProps> = ({ data, onActionCompleted }) => {
    const theme = useTheme();
    // Filter critical/high actions
    const criticalActions = data.filter(r => r.flag_severity === 'Critical' || r.flag_severity === 'High');

    if (criticalActions.length === 0) {
        return (
            <Box sx={{ textAlign: 'center', py: 4, color: theme.palette.text.secondary }}>
                <Typography variant="body2">No critical actions pending</Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ width: '100%', overflow: 'hidden' }}>
            {criticalActions.map((r, index) => (
                <Box key={r.recommendation_id}>
                    <Box
                        sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            gap: 1,
                            p: 2,
                            mb: index < criticalActions.length - 1 ? 1 : 0,
                            borderRadius: 2,
                            bgcolor: r.flag_severity === 'Critical' 
                                ? alpha(theme.palette.error.main, 0.05)
                                : alpha(theme.palette.warning.main, 0.05),
                            border: `1px solid ${alpha(
                                r.flag_severity === 'Critical' ? theme.palette.error.main : theme.palette.warning.main,
                                0.2
                            )}`,
                            transition: 'background-color 0.2s ease',
                            width: '100%',
                            boxSizing: 'border-box',
                            overflow: 'hidden',
                            '&:hover': {
                                bgcolor: r.flag_severity === 'Critical'
                                    ? alpha(theme.palette.error.main, 0.08)
                                    : alpha(theme.palette.warning.main, 0.08),
                            }
                        }}
                    >
                        <Box 
                            display="flex" 
                            justifyContent="space-between" 
                            alignItems="flex-start" 
                            gap={2}
                            sx={{
                                width: '100%',
                                overflow: 'hidden',
                                minWidth: 0,
                            }}
                        >
                            <Box sx={{ flex: 1, minWidth: 0, overflow: 'hidden' }}>
                                <Typography 
                                    variant="body1" 
                                    sx={{ 
                                        fontWeight: 600,
                                        color: theme.palette.text.primary,
                                        wordBreak: 'break-word',
                                        overflowWrap: 'break-word',
                                        mb: 0.5
                                    }}
                                >
                                    {r.recommendation_type} - {r.resource_id_impacted}
                                </Typography>
                                <Box display="flex" alignItems="center" gap={1.5} flexWrap="wrap">
                                    <Chip
                                        icon={<ErrorIcon />}
                                        label={`Severity: ${r.flag_severity}`}
                                        size="small"
                                        color={r.flag_severity === 'Critical' ? 'error' : 'warning'}
                                        sx={{ 
                                            height: 24,
                                            fontSize: '0.75rem',
                                            fontWeight: 600
                                        }}
                                    />
                                    <Chip
                                        label={`Status: ${r.action_status}`}
                                        size="small"
                                        variant="outlined"
                                        sx={{ 
                                            height: 24,
                                            fontSize: '0.75rem',
                                            color: theme.palette.text.secondary
                                        }}
                                    />
                                </Box>
                            </Box>
                            <Box sx={{ flexShrink: 0 }}>
                                <ActionButton
                                    recommendation={r}
                                    onActionCompleted={onActionCompleted}
                                />
                            </Box>
                        </Box>
                    </Box>
                    {index < criticalActions.length - 1 && (
                        <Divider sx={{ my: 1, opacity: 0.3 }} />
                    )}
                </Box>
            ))}
        </Box>
    );
};

export default ActionQueueList;
