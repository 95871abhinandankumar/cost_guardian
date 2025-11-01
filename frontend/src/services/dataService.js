// API service functions
import { apiService } from './api';

/**
 * Data Service:
 * Fetches real data from backend API endpoints
 */

// --- Functions to be used by components ---

export const getMetricsData = async (filters = {}) => {
    try {
        const params = new URLSearchParams();
        if (filters.resource_type) params.append('resource_type', filters.resource_type);
        if (filters.start_date) params.append('start_date', filters.start_date);
        if (filters.end_date) params.append('end_date', filters.end_date);
        if (filters.limit) params.append('limit', filters.limit);
        
        const queryString = params.toString();
        const endpoint = `/v1/metrics${queryString ? `?${queryString}` : ''}`;
        const data = await apiService.get(endpoint);
        return Array.isArray(data) ? data : [];
    } catch (error) {
        console.error('Error fetching metrics:', error);
        // Return empty array on error to prevent UI crashes
        return [];
    }
};

export const getRecommendationData = async (filters = {}) => {
    try {
        const params = new URLSearchParams();
        if (filters.status) params.append('status', filters.status);
        if (filters.resource_type) params.append('resource_type', filters.resource_type);
        if (filters.query) params.append('query', filters.query);
        if (filters.force_refresh) params.append('force_refresh', filters.force_refresh);
        
        const queryString = params.toString();
        const endpoint = `/v1/recommendations${queryString ? `?${queryString}` : ''}`;
        const data = await apiService.get(endpoint);
        return Array.isArray(data) ? data : [];
    } catch (error) {
        console.error('Error fetching recommendations:', error);
        // Return empty array on error to prevent UI crashes
        return [];
    }
};