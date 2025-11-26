/**
 * Ticket Service - API integration for ticket management
 */
import apiClient from './apiClient';

/**
 * Create a new ticket
 * 
 * @param {object} ticketData - Ticket data
 * @returns {Promise<object>} Created ticket
 */
export const createTicket = async (ticketData) => {
    try {
        const response = await apiClient.post('/api/tickets', ticketData);
        return {
            success: true,
            data: response.data,
        };
    } catch (error) {
        console.error('Create ticket error:', error);
        return {
            success: false,
            error: error.response?.data?.detail || error.message || 'Failed to create ticket',
        };
    }
};

/**
 * Get tickets with optional filtering
 * 
 * @param {object} filters - Query filters (status, priority, etc.)
 * @returns {Promise<array>} List of tickets
 */
export const getTickets = async (filters = {}) => {
    try {
        // Convert filters to query string params if needed
        // Currently backend supports basic listing, might need to add query params support
        const response = await apiClient.get('/api/tickets');

        // Client-side filtering if backend doesn't support it yet
        let tickets = response.data;

        if (filters.status) {
            tickets = tickets.filter(t => t.status === filters.status);
        }

        if (filters.priority) {
            tickets = tickets.filter(t => t.priority === filters.priority);
        }

        return {
            success: true,
            data: tickets,
        };
    } catch (error) {
        console.error('Get tickets error:', error);
        return {
            success: false,
            error: error.response?.data?.detail || error.message || 'Failed to fetch tickets',
        };
    }
};

/**
 * Get a single ticket by ID
 * 
 * @param {string} ticketId - Ticket ID
 * @returns {Promise<object>} Ticket details
 */
export const getTicketById = async (ticketId) => {
    try {
        const response = await apiClient.get(`/api/tickets/${ticketId}`);
        return {
            success: true,
            data: response.data,
        };
    } catch (error) {
        console.error('Get ticket error:', error);
        return {
            success: false,
            error: error.response?.data?.detail || error.message || 'Failed to fetch ticket',
        };
    }
};

/**
 * Update a ticket
 * 
 * @param {string} ticketId - Ticket ID
 * @param {object} updateData - Data to update
 * @returns {Promise<object>} Updated ticket
 */
export const updateTicket = async (ticketId, updateData) => {
    try {
        const response = await apiClient.patch(`/api/tickets/${ticketId}`, updateData);
        return {
            success: true,
            data: response.data,
        };
    } catch (error) {
        console.error('Update ticket error:', error);
        return {
            success: false,
            error: error.response?.data?.detail || error.message || 'Failed to update ticket',
        };
    }
};

export default {
    createTicket,
    getTickets,
    getTicketById,
    updateTicket,
};
