import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Authentication APIs
export const authAPI = {
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password })
    return response.data
  },

  signup: async (userData) => {
    const response = await api.post('/auth/signup', userData)
    return response.data
  },

  logout: async () => {
    const response = await api.post('/auth/logout')
    return response.data
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me')
    return response.data
  }
}

// Chat APIs
export const chatAPI = {
  startSession: async () => {
    const response = await api.post('/chat/session/start', {})
    return response.data
  },

  sendMessage: async (sessionId, content) => {
    const response = await api.post(`/chat/session/${sessionId}/message`, { content })
    return response.data
  },

  getSession: async (sessionId) => {
    const response = await api.get(`/chat/session/${sessionId}`)
    return response.data
  },

  getUserSessions: async () => {
    const response = await api.get('/chat/sessions')
    return response.data
  }
}

// Appointment APIs
export const appointmentAPI = {
  getAppointments: async () => {
    const response = await api.get('/appointments')
    return response.data
  },

  bookAppointment: async (appointmentData) => {
    const response = await api.post('/appointments/book', appointmentData)
    return response.data
  },

  modifyAppointment: async (appointmentId, appointmentData) => {
    const response = await api.put(`/appointments/${appointmentId}/modify`, appointmentData)
    return response.data
  },

  cancelAppointment: async (appointmentId) => {
    const response = await api.delete(`/appointments/${appointmentId}/cancel`)
    return response.data
  }
}

export default api