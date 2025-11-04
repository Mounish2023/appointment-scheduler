// Configuration file for API settings
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000/chat', // Change this to your backend URL
  USER_ID: "148234b1-8960-4397-a318-4522557d79b8", // Replace with actual user ID
};

export const API_ENDPOINTS = {
  START_SESSION: (userId) => `${API_CONFIG.BASE_URL}/session/start?userid=${userId}`,
  SEND_MESSAGE: (userId, sessionId) => `${API_CONFIG.BASE_URL}/session/${sessionId}/message?userid=${userId}`,
  GET_ALL_SESSIONS: (userId) => `${API_CONFIG.BASE_URL}/sessions?userid=${userId}`,
  GET_SESSION_MESSAGES: (userId, sessionId) => `${API_CONFIG.BASE_URL}/sessions/${sessionId}/messages?userid=${userId}`,
};