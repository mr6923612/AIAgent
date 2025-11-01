/**
 * API Utility Functions
 * Unified management of all API calls
 */

const API_BASE_URL = 'http://127.0.0.1:8012';

/**
 * Generic API request function
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const config = { ...defaultOptions, ...options };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API request failed ${endpoint}:`, error);
    throw error;
  }
}

/**
 * Session related APIs
 */
export const sessionAPI = {
  // Create session
  create: async (user_id, title) => {
    return apiRequest('/api/sessions', {
      method: 'POST',
      body: JSON.stringify({ user_id, title }),
    });
  },

  // Get session details
  get: async (session_id) => {
    return apiRequest(`/api/sessions/${session_id}`);
  },

  // Delete session
  delete: async (session_id) => {
    return apiRequest(`/api/sessions/${session_id}`, {
      method: 'DELETE',
    });
  },

  // Update session title
  update: async (session_id, title) => {
    return apiRequest(`/api/sessions/${session_id}`, {
      method: 'PUT',
      body: JSON.stringify({ title }),
    });
  },

  // Get all user sessions
  getUserSessions: async (user_id) => {
    return apiRequest(`/api/users/${user_id}/sessions`);
  },

  // Add message to session
  addMessage: async (session_id, role, content) => {
    return apiRequest(`/api/sessions/${session_id}/messages`, {
      method: 'POST',
      body: JSON.stringify({ role, content }),
    });
  },
};

/**
 * Customer service bot related APIs
 */
export const crewAPI = {
  // Send message to customer service bot
  sendMessage: async (messageData) => {
    return apiRequest('/api/crew', {
      method: 'POST',
      body: JSON.stringify(messageData),
    });
  },

  // Send file message to customer service bot
  sendFileMessage: async (formData) => {
    return apiRequest('/api/crew', {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser automatically set Content-Type
    });
  },

  // Get task status
  getStatus: async (job_id) => {
    return apiRequest(`/api/crew/${job_id}`);
  },
};

/**
 * Error handling utilities
 */
export const errorHandler = {
  // Handle API errors
  handleAPIError: (error, context = '') => {
    console.error(`API error ${context}:`, error);
    
    if (error.message.includes('Failed to fetch')) {
      return 'Network connection failed, please check your network connection';
    }
    
    if (error.message.includes('404')) {
      return 'Requested resource not found';
    }
    
    if (error.message.includes('500')) {
      return 'Internal server error, please try again later';
    }
    
    return error.message || 'Unknown error';
  },

  // Show error message
  showError: (message) => {
    alert(`Error: ${message}`);
  },
};

export default {
  sessionAPI,
  crewAPI,
  errorHandler,
};
