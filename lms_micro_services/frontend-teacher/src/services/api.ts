// API Base Configuration
import axios from 'axios';
import { config, debugLog, errorLog } from '../config';

export const apiClient = axios.create({
  baseURL: config.API_BASE_URL,
  timeout: config.TIMEOUT_MS,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('teacher_authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    debugLog('🌐 API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    errorLog('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    debugLog('✅ API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    errorLog('❌ Response Error:', error.response?.status, error.config?.url, error.message);
    
    if (error.response?.status === 401) {
      // Handle unauthorized access
      errorLog('🔒 Unauthorized access detected');
      
      // Only auto-redirect if it's a GET request to prevent interrupting user actions
      if (error.config?.method?.toLowerCase() === 'get') {
        errorLog('🔒 GET request unauthorized, redirecting to login');
        localStorage.removeItem('teacher_authToken');
        window.location.href = '/login';
      } else {
        errorLog('🔒 Non-GET request unauthorized, letting component handle');
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
