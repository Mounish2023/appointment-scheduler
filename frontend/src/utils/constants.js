// API Configuration
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    SIGNUP: '/auth/signup',
    LOGOUT: '/auth/logout',
    ME: '/auth/me'
  },
  CHAT: {
    START_SESSION: '/chat/session/start',
    SEND_MESSAGE: (sessionId) => `/chat/session/${sessionId}/message`,
    GET_SESSION: (sessionId) => `/chat/session/${sessionId}`,
    GET_SESSIONS: '/chat/sessions'
  },
  APPOINTMENTS: {
    GET_ALL: '/appointments',
    BOOK: '/appointments/book',
    MODIFY: (id) => `/appointments/${id}/modify`,
    CANCEL: (id) => `/appointments/${id}/cancel`
  },
  WEBSOCKET: (sessionId) => `/ws/${sessionId}`
}

// WebSocket Message Types
export const WS_MESSAGE_TYPES = {
  USER_MESSAGE: 'user_message',
  AGENT_MESSAGE: 'agent_message',
  TYPING_INDICATOR: 'typing_indicator',
  REQUEST_APPROVAL: 'request_approval',
  APPROVAL_RESPONSE: 'approval_response',
  CONNECTION_STATUS: 'connection_status',
  ERROR: 'error'
}

// Appointment Status
export const APPOINTMENT_STATUS = {
  SCHEDULED: 'scheduled',
  MODIFIED: 'modified',
  CANCELED: 'canceled',
  COMPLETED: 'completed'
}

// Appointment Types
export const APPOINTMENT_TYPES = {
  CLEANING: 'cleaning',
  CONSULTATION: 'consultation',
  FILLING: 'filling',
  ORTHODONTIC: 'orthodontic',
  EMERGENCY: 'emergency',
  WHITENING: 'whitening',
  EXTRACTION: 'extraction',
  ROOT_CANAL: 'root_canal'
}

// Dental Specialties
export const DENTAL_SPECIALTIES = {
  GENERAL: 'General Dentistry',
  ORTHODONTICS: 'Orthodontics',
  PERIODONTICS: 'Periodontics',
  ORAL_SURGERY: 'Oral Surgery',
  ENDODONTICS: 'Endodontics',
  COSMETIC: 'Cosmetic Dentistry',
  PEDIATRIC: 'Pediatric Dentistry',
  PROSTHODONTICS: 'Prosthodontics'
}

// Insurance Providers
export const INSURANCE_PROVIDERS = [
  'Delta Dental',
  'Cigna',
  'Aetna',
  'MetLife',
  'Humana',
  'Guardian',
  'United Healthcare',
  'Blue Cross Blue Shield',
  'Other'
]

// Form Validation Rules
export const VALIDATION_RULES = {
  EMAIL: {
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    message: 'Please enter a valid email address'
  },
  PHONE: {
    pattern: /^[\+]?[1-9][\d]{0,15}$/,
    message: 'Please enter a valid phone number'
  },
  PASSWORD: {
    minLength: 6,
    message: 'Password must be at least 6 characters long'
  }
}

// Date/Time Formats
export const DATE_FORMATS = {
  DISPLAY: 'EEEE, MMMM do, yyyy',
  TIME: 'h:mm a',
  ISO: "yyyy-MM-dd'T'HH:mm:ss.SSSxxx",
  SHORT: 'MMM do, yyyy'
}

// Local Storage Keys
export const STORAGE_KEYS = {
  TOKEN: 'token',
  USER: 'user',
  CHAT_SESSION_ID: 'chatSessionId',
  THEME: 'theme',
  LANGUAGE: 'language'
}

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  SESSION_EXPIRED: 'Your session has expired. Please log in again.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  WEBSOCKET_ERROR: 'Connection lost. Please refresh the page.'
}

// Success Messages
export const SUCCESS_MESSAGES = {
  LOGIN: 'Successfully logged in!',
  SIGNUP: 'Account created successfully!',
  LOGOUT: 'Successfully logged out!',
  APPOINTMENT_BOOKED: 'Appointment booked successfully!',
  APPOINTMENT_MODIFIED: 'Appointment updated successfully!',
  APPOINTMENT_CANCELED: 'Appointment canceled successfully!'
}

// Loading States
export const LOADING_STATES = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error'
}

// Theme Configuration
export const THEME_CONFIG = {
  COLORS: {
    PRIMARY: '#1e40af', // aspen-blue
    PRIMARY_LIGHT: '#3b82f6', // aspen-light-blue
    SUCCESS: '#10b981', // aspen-green
    ERROR: '#ef4444',
    WARNING: '#f59e0b',
    INFO: '#3b82f6',
    GRAY: '#6b7280' // aspen-gray
  },
  BREAKPOINTS: {
    SM: '640px',
    MD: '768px',
    LG: '1024px',
    XL: '1280px',
    '2XL': '1536px'
  }
}

export default {
  API_ENDPOINTS,
  WS_MESSAGE_TYPES,
  APPOINTMENT_STATUS,
  APPOINTMENT_TYPES,
  DENTAL_SPECIALTIES,
  INSURANCE_PROVIDERS,
  VALIDATION_RULES,
  DATE_FORMATS,
  STORAGE_KEYS,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  LOADING_STATES,
  THEME_CONFIG
}