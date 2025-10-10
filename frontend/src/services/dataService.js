// Import the data from the mock files
import { METRICS_MOCK_DATA } from './metricsMock';
import { RECOMMENDATIONS_MOCK_DATA } from './recommendationsMock';

/**
 * MOCK DATA SERVICE:
 * This file serves as a temporary substitute for the React Query fetching hooks.
 * It provides a single point of truth for mock data and mimics API filtering logic.
 */

// --- Functions to be used by components (mimicking API endpoints) ---

export const getMetricsData = () => {
    // In the real app, this function will contain the useQuery fetch call.
    return METRICS_MOCK_DATA;
};

export const getRecommendationData = (filters = {}) => {
    // Mimics backend filtering and sorting logic for the Action List
    let data = RECOMMENDATIONS_MOCK_DATA;

    if (filters.status) {
        data = data.filter(r => r.action_status === filters.status);
    }

    // In the real app, this function will contain the useQuery fetch call.
    return data;
};