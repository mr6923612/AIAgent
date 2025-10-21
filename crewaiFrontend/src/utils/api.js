/**
 * API工具函数
 * 统一管理所有API调用
 */

const API_BASE_URL = 'http://127.0.0.1:8012';

/**
 * 通用API请求函数
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
    console.error(`API请求失败 ${endpoint}:`, error);
    throw error;
  }
}

/**
 * 会话相关API
 */
export const sessionAPI = {
  // 创建会话
  create: async (user_id, title) => {
    return apiRequest('/api/sessions', {
      method: 'POST',
      body: JSON.stringify({ user_id, title }),
    });
  },

  // 获取会话详情
  get: async (session_id) => {
    return apiRequest(`/api/sessions/${session_id}`);
  },

  // 删除会话
  delete: async (session_id) => {
    return apiRequest(`/api/sessions/${session_id}`, {
      method: 'DELETE',
    });
  },

  // 更新会话标题
  update: async (session_id, title) => {
    return apiRequest(`/api/sessions/${session_id}`, {
      method: 'PUT',
      body: JSON.stringify({ title }),
    });
  },

  // 获取用户所有会话
  getUserSessions: async (user_id) => {
    return apiRequest(`/api/users/${user_id}/sessions`);
  },

  // 添加消息到会话
  addMessage: async (session_id, role, content) => {
    return apiRequest(`/api/sessions/${session_id}/messages`, {
      method: 'POST',
      body: JSON.stringify({ role, content }),
    });
  },
};

/**
 * 客服机器人相关API
 */
export const crewAPI = {
  // 发送消息给客服机器人
  sendMessage: async (messageData) => {
    return apiRequest('/api/crew', {
      method: 'POST',
      body: JSON.stringify(messageData),
    });
  },

  // 发送文件消息给客服机器人
  sendFileMessage: async (formData) => {
    return apiRequest('/api/crew', {
      method: 'POST',
      body: formData,
      headers: {}, // 让浏览器自动设置Content-Type
    });
  },

  // 获取任务状态
  getStatus: async (job_id) => {
    return apiRequest(`/api/crew/${job_id}`);
  },
};

/**
 * 错误处理工具
 */
export const errorHandler = {
  // 处理API错误
  handleAPIError: (error, context = '') => {
    console.error(`API错误 ${context}:`, error);
    
    if (error.message.includes('Failed to fetch')) {
      return '网络连接失败，请检查网络连接';
    }
    
    if (error.message.includes('404')) {
      return '请求的资源不存在';
    }
    
    if (error.message.includes('500')) {
      return '服务器内部错误，请稍后重试';
    }
    
    return error.message || '未知错误';
  },

  // 显示错误消息
  showError: (message) => {
    alert(`错误: ${message}`);
  },
};

export default {
  sessionAPI,
  crewAPI,
  errorHandler,
};
