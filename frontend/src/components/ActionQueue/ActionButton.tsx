// frontend/src/components/ActionQueue/ActionButton.tsx

import React, { useState } from 'react';
import { Button, CircularProgress, Tooltip } from '@mui/material';
import { CheckCircleOutline, PlayArrow, RestoreOutlined } from '@mui/icons-material';

export enum RecommendationType {
    Resize = 'resize',
    Terminate = 'terminate',
    Reconfigure = 'reconfigure',
    Review = 'review'
}

const mockApiMutation = (actionId: string): Promise<any> => {
    return new Promise((resolve) => {
        setTimeout(() => {
            console.log(`[MOCK API] Action ${actionId} successfully ACCEPTED.`);
            resolve({ success: true, newStatus: 'applied' });
        }, 1000);
    });
};

interface Recommendation {
    recommendation_id: string;
    recommendation_type: RecommendationType;
    action_status: string;
}

interface ActionButtonProps {
    recommendation: Recommendation;
    onActionCompleted?: () => void;
}

const ActionButton: React.FC<ActionButtonProps> = ({ recommendation, onActionCompleted }) => {
    const [status, setStatus] = useState(recommendation.action_status);
    const [isLoading, setIsLoading] = useState(false);

    const isPrimaryAction = recommendation.recommendation_type === RecommendationType.Resize ||
                            recommendation.recommendation_type === RecommendationType.Terminate;

    const handleAccept = async () => {
        setIsLoading(true);
        try {
            await mockApiMutation(recommendation.recommendation_id);
            setStatus('applied');
            if (onActionCompleted) {
                onActionCompleted();
            }
        } catch (error) {
            console.error("Mutation failed:", error);
        } finally {
            setIsLoading(false);
        }
    };

    if (status === 'applied' || status === 'accepted') {
        return (
            <Tooltip title="Action applied, waiting for cost data confirmation">
                <Button variant="outlined" color="success" startIcon={<CheckCircleOutline />} disabled size="small">
                    Applied
                </Button>
            </Tooltip>
        );
    }

    if (isLoading) {
        return (
            <Button variant="contained" color="success" disabled size="small">
                <CircularProgress size={20} sx={{ mr: 1 }} />
                Applying...
            </Button>
        );
    }

    if (isPrimaryAction) {
        return (
            <Button
                variant="contained"
                color="success" // Uses the Neon Green for 'Apply Fix'
                startIcon={<PlayArrow />}
                onClick={handleAccept}
                size="small"
            >
                Apply Fix
            </Button>
        );
    }

    return (
        <Button variant="text" color="primary" startIcon={<RestoreOutlined />} onClick={handleAccept} size="small">
            Review Policy
        </Button>
    );
};

export default ActionButton;