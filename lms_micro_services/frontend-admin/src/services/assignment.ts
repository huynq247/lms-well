import apiClient from './api';
import { debugLog, errorLog } from '../config';

export interface Assignment {
  id: string;
  title: string;
  description: string;
  course_id: string;
  instructor_id: number;
  due_date: string;
  max_score: number;
  is_published: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateAssignmentRequest {
  title: string;
  description: string;
  course_id: string;
  due_date: string;
  max_score: number;
}

export interface AssignmentListResponse {
  assignments: Assignment[];
  total: number;
  page: number;
  size: number;
}

export const assignmentService = {
  async getAssignments(params: { page?: number; size?: number }): Promise<AssignmentListResponse> {
    try {
      const response = await apiClient.get('/api/assignments', { params });
      debugLog('✅ Get assignments successful');
      return response.data;
    } catch (error) {
      errorLog('❌ Get assignments failed:', error);
      throw error;
    }
  },

  async getAssignment(id: string): Promise<Assignment> {
    try {
      const response = await apiClient.get(`/api/assignments/${id}`);
      debugLog('✅ Get assignment successful:', id);
      return response.data;
    } catch (error) {
      errorLog('❌ Get assignment failed:', error);
      throw error;
    }
  },

  async createAssignment(data: CreateAssignmentRequest): Promise<Assignment> {
    try {
      const response = await apiClient.post('/api/assignments', data);
      debugLog('✅ Create assignment successful');
      return response.data;
    } catch (error) {
      errorLog('❌ Create assignment failed:', error);
      throw error;
    }
  },

  async updateAssignment(id: string, data: Partial<CreateAssignmentRequest>): Promise<Assignment> {
    try {
      const response = await apiClient.put(`/api/assignments/${id}`, data);
      debugLog('✅ Update assignment successful:', id);
      return response.data;
    } catch (error) {
      errorLog('❌ Update assignment failed:', error);
      throw error;
    }
  },

  async deleteAssignment(id: string): Promise<void> {
    try {
      await apiClient.delete(`/api/assignments/${id}`);
      debugLog('✅ Delete assignment successful:', id);
    } catch (error) {
      errorLog('❌ Delete assignment failed:', error);
      throw error;
    }
  }
};

export default assignmentService;
