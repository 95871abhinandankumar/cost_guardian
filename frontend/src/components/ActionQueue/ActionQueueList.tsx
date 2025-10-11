// frontend/src/components/ActionQueue/ActionQueueList.tsx
import React from 'react';
import { List, ListItem, ListItemText } from '@mui/material';
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
    onActionCompleted?: () => void; // Matches ActionButton expected type
}

const ActionQueueList: React.FC<ActionQueueListProps> = ({ data, onActionCompleted }) => {
    // Filter critical/high actions
    const criticalActions = data.filter(r => r.flag_severity === 'Critical' || r.flag_severity === 'High');

    return (
        <List disablePadding>
            {criticalActions.map((r) => (
                <ListItem key={r.recommendation_id} alignItems="flex-start"
                    secondaryAction={
                        <ActionButton
                            recommendation={r}
                            onActionCompleted={onActionCompleted} // Correct signature
                        />
                    }
                >
                    <ListItemText
                        primary={`${r.recommendation_type} - ${r.resource_id_impacted}`}
                        secondary={`Severity: ${r.flag_severity} | Status: ${r.action_status}`}
                    />
                </ListItem>
            ))}
        </List>
    );
};

export default ActionQueueList;
