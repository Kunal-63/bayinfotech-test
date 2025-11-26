/**
 * Metrics Service - API integration for analytics dashboard
 */
import apiClient from './apiClient';

/**
 * Get summary metrics
 * 
 * @returns {Promise<object>} Summary metrics
 */
export const getSummary = async () => {
    try {
        const response = await apiClient.get('/api/metrics/summary');
        return {
            success: true,
            data: response.data,
        };
    } catch (error) {
        console.error('Get summary metrics error:', error);
        return {
            success: false,
            error: error.response?.data?.detail || error.message || 'Failed to fetch summary metrics',
        };
    }
};

/**
 * Get trend metrics
 * 
 * @param {string} period - Time period (e.g., '7d', '30d')
 * @returns {Promise<object>} Trend data
 */
export const getTrends = async (period = '7d') => {
    try {
        const response = await apiClient.get('/api/metrics/trends', { params: { period } });
        return {
            success: true,
            data: response.data,
        };
    } catch (error) {
        console.error('Get trends error:', error);
        return {
            success: false,
            error: error.response?.data?.detail || error.message || 'Failed to fetch trends',
        };
    }
};

/**
 * Get deflection metrics
 * 
 * @returns {Promise<object>} Deflection data
 */
export const getDeflection = async () => {
    try {
        const response = await apiClient.get('/api/metrics/deflection');
        return {
            success: true,
            data: response.data,
        };
    } catch (error) {
        console.error('Get deflection metrics error:', error);
        return {
            success: false,
            error: error.response?.data?.detail || error.message || 'Failed to fetch deflection metrics',
        };
    }
};

/**
 * Get guardrail metrics
 * 
 * @returns {Promise<object>} Guardrail data
 */
export const getGuardrails = async () => {
    try {
        const response = await apiClient.get('/api/metrics/guardrails');
        return {
            success: true,
            data: response.data,
        };
    } catch (error) {
        console.error('Get guardrail metrics error:', error);
        return {
            success: false,
            error: error.response?.data?.detail || error.message || 'Failed to fetch guardrail metrics',
        };
    }
};

export default {
    getSummary,
    getTrends,
    getDeflection,
    getGuardrails,
};
