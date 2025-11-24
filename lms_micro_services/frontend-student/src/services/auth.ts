import apiClient from './api';
import { debugLog, errorLog } from '../config';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  role?: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      // First, login to get tokens
      const loginResponse = await apiClient.post<LoginResponse>('/api/v1/auth/login', credentials);
      const { access_token, refresh_token, token_type } = loginResponse.data;
      
      // Store token in localStorage
      localStorage.setItem('student_authToken', access_token);
      localStorage.setItem('refreshToken', refresh_token);
      
      // Then fetch user info
      const userResponse = await apiClient.get<User>('/api/v1/auth/me');
      const user = userResponse.data;
      
      localStorage.setItem('user', JSON.stringify(user));
      
      debugLog('✅ Login successful:', user);
      return {
        access_token,
        refresh_token,
        token_type,
        user
      };
    } catch (error) {
      errorLog('❌ Login failed:', error);
      throw error;
    }
  },

  async register(data: RegisterData): Promise<AuthResponse> {
    try {
      const response = await apiClient.post('/api/v1/auth/register', data);
      debugLog('✅ Registration successful');
      return response.data;
    } catch (error) {
      errorLog('❌ Registration failed:', error);
      throw error;
    }
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post('/api/v1/auth/logout');
      localStorage.removeItem('student_authToken');
      localStorage.removeItem('user');
      debugLog('✅ Logout successful');
    } catch (error) {
      errorLog('❌ Logout failed:', error);
      // Clear local storage even if API call fails
      localStorage.removeItem('student_authToken');
      localStorage.removeItem('user');
    }
  },

  async getCurrentUser(): Promise<User> {
    try {
      const response = await apiClient.get('/api/v1/auth/me');
      debugLog('✅ Get current user successful');
      return response.data;
    } catch (error) {
      errorLog('❌ Get current user failed:', error);
      throw error;
    }
  },

  getStoredUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch (error) {
        errorLog('❌ Failed to parse stored user:', error);
        return null;
      }
    }
    return null;
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('student_authToken');
  }
};

export default authService;
