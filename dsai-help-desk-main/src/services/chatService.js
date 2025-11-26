/**
 * Chat Service - API integration for chat functionality
 */
import apiClient from './apiClient';

/**
 * Generate a simple random session ID
 */
const generateSessionId = () => {
    return 'session-' + Date.now() + '-' + Math.random().toString(36).substring(2, 15);
};

/**
 * Generate or retrieve session ID
 * Stores in localStorage for persistence across page reloads
 */
export const getSessionId = () => {
    let sessionId = localStorage.getItem('chat_session_id');

    if (!sessionId) {
        sessionId = generateSessionId();
        localStorage.setItem('chat_session_id', sessionId);
    }

    return sessionId;
};

/**
 * Clear session ID (useful for starting fresh conversation)
 */
export const clearSessionId = () => {
    localStorage.removeItem('chat_session_id');
};

/**
 * Send a chat message to the backend
 * 
 * @param {string} message - User's message
 * @param {string} userRole - User role (trainee, instructor, admin, etc.)
 * @param {object} context - Additional context (module, channel, etc.)
 * @returns {Promise<object>} Chat response with answer, KB references, tier, severity, etc.
 */
export const sendMessage = async (message, userRole = 'trainee', context = {}) => {
    try {
        const sessionId = getSessionId();

        const requestData = {
            session_id: sessionId,
            message: message,
            user_role: userRole,
            context: context,
        };

        const response = await apiClient.post('/api/chat', requestData);

        return {
            success: true,
            data: response.data,
        };
    } catch (error) {
        console.error('Chat service error:', error);

        return {
            success: false,
            error: error.response?.data?.detail || error.message || 'Failed to send message',
            status: error.response?.status,
        };
    }
};

/**
 * Parse KB references from backend response
 * 
 * @param {array} kbReferences - Array of KB reference objects
 * @returns {array} Formatted KB references
 */
export const parseKBReferences = (kbReferences) => {
    if (!kbReferences || !Array.isArray(kbReferences)) {
        return [];
    }

    return kbReferences.map(ref => ({
        id: ref.id,
        title: ref.title,
        excerpt: ref.excerpt,
    }));
};

/**
 * Format chat response for UI consumption
 * 
 * @param {object} backendResponse - Raw response from backend
 * @returns {object} Formatted response for UI
 */
export const formatChatResponse = (backendResponse) => {
    return {
        message: backendResponse.answer,
        kbReferences: parseKBReferences(backendResponse.kb_references),
        confidence: backendResponse.confidence,
        tier: backendResponse.tier,
        severity: backendResponse.severity,
        needsEscalation: backendResponse.needs_escalation,
        guardrail: backendResponse.guardrail,
        ticketId: backendResponse.ticket_id,
    };
};

export default {
    sendMessage,
    getSessionId,
    clearSessionId,
    parseKBReferences,
    formatChatResponse,
};
