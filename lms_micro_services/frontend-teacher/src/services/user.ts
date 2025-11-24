import apiClient from './api';
import { debugLog, errorLog } from '../config';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface CreateUserRequest {
  username: string;
  email: string;
  password: string;
  full_name: string;
  role: 'STUDENT' | 'TEACHER' | 'ADMIN';
}

export interface UpdateUserRequest {
  username?: string;
  email?: string;
  full_name?: string;
  password?: string;
  is_active?: boolean;
  role?: string;
}

export const userService = {
  async getUsers(): Promise<{ users: User[] }> {
    try {
      const response = await apiClient.get('/api/v1/users');
      debugLog('✅ Get users successful');
      return response.data;
    } catch (error) {
      errorLog('❌ Get users failed:', error);
      throw error;
    }
  },

  async getMyStudents(): Promise<{ users: User[] }> {
    try {
      const response = await apiClient.get('/api/v1/users/my-students');
      debugLog('✅ Get my students successful');
      return response.data;
    } catch (error) {
      errorLog('❌ Get my students failed:', error);
      throw error;
    }
  },

  async getUser(id: number): Promise<User> {
    try {
      const response = await apiClient.get(`/api/v1/users/${id}`);
      debugLog('✅ Get user successful:', id);
      return response.data;
    } catch (error) {
      errorLog('❌ Get user failed:', error);
      throw error;
    }
  },

  async createUser(data: CreateUserRequest): Promise<User> {
    try {
      const response = await apiClient.post('/api/v1/users', data);
      debugLog('✅ Create user successful');
      return response.data;
    } catch (error) {
      errorLog('❌ Create user failed:', error);
      throw error;
    }
  },

  async updateUser(id: number, data: UpdateUserRequest): Promise<User> {
    try {
      const response = await apiClient.put(`/api/v1/users/${id}`, data);
      debugLog('✅ Update user successful:', id);
      return response.data;
    } catch (error) {
      errorLog('❌ Update user failed:', error);
      throw error;
    }
  },

  async deleteUser(id: number): Promise<void> {
    try {
      await apiClient.delete(`/api/v1/users/${id}`);
      debugLog('✅ Delete user successful:', id);
    } catch (error) {
      errorLog('❌ Delete user failed:', error);
      throw error;
    }
  }
};

export default userService;
