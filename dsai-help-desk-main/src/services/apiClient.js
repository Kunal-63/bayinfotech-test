/**
 * API Client - Centralized HTTP client for backend communication
 */
import axios from 'axios';

// Get API base URL from environment variable
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://bayinfotech-test.onrender.com';
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '30000');

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: API_TIMEOUT,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for logging and auth
apiClient.interceptors.request.use(
    (config) => {
        console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data);
        return config;
    },
    (error) => {
        console.error('[API Request Error]', error);
        return Promise.reject(error);
    }
);

// Response interceptor for logging and error handling
apiClient.interceptors.response.use(
    (response) => {
        console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
        return response;
    },
    (error) => {
        console.error('[API Response Error]', {
            url: error.config?.url,
            status: error.response?.status,
            data: error.response?.data,
            message: error.message,
        });

        // Handle specific error cases
        if (error.response) {
            // Server responded with error status
            const { status, data } = error.response;

            if (status === 500) {
                console.error('Server error:', data);
            } else if (status === 404) {
                console.error('Resource not found:', error.config?.url);
            } else if (status === 400) {
                console.error('Bad request:', data);
            }
        } else if (error.request) {
            // Request made but no response received
            console.error('No response from server. Is the backend running?');
        } else {
            // Error in request setup
            console.error('Request setup error:', error.message);
        }

        return Promise.reject(error);
    }
);

export default apiClient;
export { API_BASE_URL };
