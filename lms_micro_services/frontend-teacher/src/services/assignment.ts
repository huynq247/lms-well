import apiClient from './api';
import { debugLog, errorLog } from '../config';

export interface Assignment {
  id: number;
  instructor_id: number;
  instructor_name?: string;
  student_id: number;
  student_name?: string;
  content_type: 'course' | 'deck';
  content_id: string;
  content_title: string;
  title: string;
  description?: string;
  instructions?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'overdue';
  assigned_at: string;
  due_date?: string;
  completed_at?: string;
  is_active: boolean;
  course_progress_percentage?: number;
  total_lessons?: number;
  completed_lessons?: number;
  supporting_decks?: string[];
  supporting_deck_titles?: string[];
  created_at: string;
  updated_at?: string;
}

export interface CreateAssignmentRequest {
  instructor_id: number;
  student_id: number;
  content_type: 'course' | 'deck';
  content_id: string;
  content_title: string;
  title: string;
  description?: string;
  instructions?: string;
  due_date?: string;
  supporting_decks?: string[];
  supporting_deck_titles?: string[];
}

export interface AssignmentListResponse {
  assignments: Assignment[];
  total: number;
  page: number;
  size: number;
  total_pages: number;
}

export const assignmentService = {
  async getAssignments(params?: { 
    student_id?: number;
    instructor_id?: number;
    page?: number; 
    size?: number;
  }): Promise<AssignmentListResponse> {
    try {
      const { student_id, instructor_id, page = 1, size = 50 } = params || {};
      const queryParams = new URLSearchParams({
        page: page.toString(),
        size: size.toString(),
        ...(student_id && { student_id: student_id.toString() }),
        ...(instructor_id && { instructor_id: instructor_id.toString() })
      });
      
      debugLog('📋 Fetching assignments with params:', params);
      const response = await apiClient.get(`/api/assignments/?${queryParams.toString()}`);
      debugLog('✅ Assignments fetched:', response.data);
      return response.data;
    } catch (error) {
      errorLog('❌ Get assignments failed:', error);
      throw error;
    }
  },

  async getAssignment(assignmentId: number): Promise<Assignment> {
    try {
      debugLog('📋 Fetching assignment:', assignmentId);
      const response = await apiClient.get(`/api/assignments/${assignmentId}`);
      debugLog('✅ Assignment fetched:', response.data);
      return response.data;
    } catch (error) {
      errorLog('❌ Get assignment failed:', error);
      throw error;
    }
  },

  async createAssignment(data: CreateAssignmentRequest): Promise<Assignment> {
    try {
      debugLog('📋 Creating assignment:', data);
      const response = await apiClient.post('/api/assignments/', data);
      debugLog('✅ Assignment created:', response.data);
      return response.data;
    } catch (error) {
      errorLog('❌ Create assignment failed:', error);
      throw error;
    }
  },

  async updateAssignment(assignmentId: number, data: Partial<CreateAssignmentRequest>): Promise<Assignment> {
    try {
      debugLog('📋 Updating assignment:', assignmentId, data);
      const response = await apiClient.put(`/api/assignments/${assignmentId}`, data);
      debugLog('✅ Assignment updated:', response.data);
      return response.data;
    } catch (error) {
      errorLog('❌ Update assignment failed:', error);
      throw error;
    }
  },

  async updateAssignmentStatus(assignmentId: number, status: Assignment['status']): Promise<Assignment> {
    try {
      debugLog('📋 Updating assignment status:', assignmentId, status);
      const response = await apiClient.put(`/api/assignments/${assignmentId}`, { status });
      debugLog('✅ Assignment status updated:', response.data);
      return response.data;
    } catch (error) {
      errorLog('❌ Update assignment status failed:', error);
      throw error;
    }
  },

  async deleteAssignment(assignmentId: number): Promise<void> {
    try {
      debugLog('📋 Deleting assignment:', assignmentId);
      await apiClient.delete(`/api/assignments/${assignmentId}`);
      debugLog('✅ Assignment deleted');
    } catch (error) {
      errorLog('❌ Delete assignment failed:', error);
      throw error;
    }
  }
};

export default assignmentService;
