import apiClient from './api';
import { debugLog, errorLog } from '../config';

export interface Course {
  id: string;
  title: string;
  description: string;
  instructor_id: number;
  instructor_name?: string;
  estimated_duration?: number | null;
  is_published?: boolean;
  is_active?: boolean;
  is_public?: boolean;
  total_lessons?: number;
  created_at: string;
  updated_at: string | null;
}

export interface Lesson {
  id: string;
  course_id: string;
  title: string;
  content: string;
  order: number;
  video_url?: string;
  image_url?: string;
  duration?: number | null;
  instructor_id?: number;
  is_published?: boolean;
  is_active?: boolean;
  created_at: string;
  updated_at?: string | null;
}

export interface Deck {
  id: string;
  title: string;
  description?: string;
  instructor_id: number;
  instructor_name?: string;
  difficulty?: string;
  is_published?: boolean;
  is_public?: boolean;
  total_flashcards?: number;
  created_at: string;
  updated_at: string | null;
}

export interface Flashcard {
  id: string;
  deck_id: string;
  front: string;
  back: string;
  order: number;
  difficulty?: string;
  front_image_url?: string | null;
  back_image_url?: string | null;
  wordclass?: string | null;
  definition?: string | null;
  example?: string | null;
  created_at: string;
  updated_at: string | null;
}

export const contentService = {
  // Courses
  async getCourses(): Promise<Course[]> {
    try {
      const response = await apiClient.get('/api/courses');
      debugLog('✅ Get courses successful');
      return response.data.items || response.data;
    } catch (error) {
      errorLog('❌ Get courses failed:', error);
      throw error;
    }
  },

  async getCourse(id: string): Promise<Course> {
    try {
      const response = await apiClient.get(`/api/courses/${id}`);
      debugLog('✅ Get course successful:', id);
      return response.data;
    } catch (error) {
      errorLog('❌ Get course failed:', error);
      throw error;
    }
  },

  async createCourse(data: Partial<Course>): Promise<Course> {
    try {
      const response = await apiClient.post('/api/courses', data);
      debugLog('✅ Create course successful');
      return response.data;
    } catch (error) {
      errorLog('❌ Create course failed:', error);
      throw error;
    }
  },

  async updateCourse(id: string, data: Partial<Course>): Promise<Course> {
    try {
      const response = await apiClient.put(`/api/courses/${id}`, data);
      debugLog('✅ Update course successful:', id);
      return response.data;
    } catch (error) {
      errorLog('❌ Update course failed:', error);
      throw error;
    }
  },

  async deleteCourse(id: string): Promise<void> {
    try {
      await apiClient.delete(`/api/courses/${id}`);
      debugLog('✅ Delete course successful:', id);
    } catch (error) {
      errorLog('❌ Delete course failed:', error);
      throw error;
    }
  },

  // Lessons
  async getLessons(courseId: string): Promise<Lesson[]> {
    try {
      const response = await apiClient.get(`/api/courses/${courseId}/lessons`);
      debugLog('✅ Get lessons successful');
      return response.data;
    } catch (error) {
      errorLog('❌ Get lessons failed:', error);
      throw error;
    }
  },

  async getAllLessons(params?: {
    search?: string;
    page?: number;
    size?: number;
    course_id?: string;
    instructor_id?: number;
    is_published?: boolean;
    is_active?: boolean;
  }): Promise<{
    items: Lesson[];
    total: number;
    page: number;
    size: number;
    pages: number;
  }> {
    try {
      const response = await apiClient.get('/api/lessons/', { params });
      debugLog('✅ Get all lessons successful');
      return response.data;
    } catch (error) {
      errorLog('❌ Get all lessons failed:', error);
      throw error;
    }
  },

  async getLesson(courseId: string, lessonId: string): Promise<Lesson> {
    try {
      const response = await apiClient.get(`/api/courses/${courseId}/lessons/${lessonId}`);
      debugLog('✅ Get lesson successful:', lessonId);
      return response.data;
    } catch (error) {
      errorLog('❌ Get lesson failed:', error);
      throw error;
    }
  },

  async getLessonById(lessonId: string): Promise<Lesson> {
    try {
      const response = await apiClient.get(`/api/courses/lessons/${lessonId}`);
      debugLog('✅ Get lesson by ID successful:', lessonId);
      return response.data;
    } catch (error) {
      errorLog('❌ Get lesson by ID failed:', error);
      throw error;
    }
  },

  async createLesson(courseId: string, data: Partial<Lesson>): Promise<Lesson> {
    try {
      const response = await apiClient.post(`/api/courses/${courseId}/lessons`, data);
      debugLog('✅ Create lesson successful');
      return response.data;
    } catch (error) {
      errorLog('❌ Create lesson failed:', error);
      throw error;
    }
  },

  async updateLesson(courseId: string, lessonId: string, data: Partial<Lesson>): Promise<Lesson> {
    try {
      const response = await apiClient.put(`/api/courses/${courseId}/lessons/${lessonId}`, data);
      debugLog('✅ Update lesson successful:', lessonId);
      return response.data;
    } catch (error) {
      errorLog('❌ Update lesson failed:', error);
      throw error;
    }
  },

  async deleteLesson(courseId: string, lessonId: string): Promise<void> {
    try {
      await apiClient.delete(`/api/courses/${courseId}/lessons/${lessonId}`);
      debugLog('✅ Delete lesson successful:', lessonId);
    } catch (error) {
      errorLog('❌ Delete lesson failed:', error);
      throw error;
    }
  },

  // Decks
  async getDecks(): Promise<Deck[]> {
    try {
      const response = await apiClient.get('/api/decks');
      debugLog('✅ Get decks successful');
      return response.data.items || response.data;
    } catch (error) {
      errorLog('❌ Get decks failed:', error);
      throw error;
    }
  },

  async getDeck(id: string): Promise<Deck> {
    try {
      const response = await apiClient.get(`/api/decks/${id}`);
      debugLog('✅ Get deck successful:', id);
      return response.data;
    } catch (error) {
      errorLog('❌ Get deck failed:', error);
      throw error;
    }
  },

  async createDeck(data: Partial<Deck>): Promise<Deck> {
    try {
      const response = await apiClient.post('/api/decks/', data);
      debugLog('✅ Create deck successful');
      return response.data;
    } catch (error) {
      errorLog('❌ Create deck failed:', error);
      throw error;
    }
  },

  async updateDeck(id: string, data: Partial<Deck>): Promise<Deck> {
    try {
      const response = await apiClient.put(`/api/decks/${id}`, data);
      debugLog('✅ Update deck successful:', id);
      return response.data;
    } catch (error) {
      errorLog('❌ Update deck failed:', error);
      throw error;
    }
  },

  async deleteDeck(id: string): Promise<void> {
    try {
      await apiClient.delete(`/api/decks/${id}`);
      debugLog('✅ Delete deck successful:', id);
    } catch (error) {
      errorLog('❌ Delete deck failed:', error);
      throw error;
    }
  },

  // Flashcards
  async getFlashcards(deckId: string): Promise<Flashcard[]> {
    try {
      const response = await apiClient.get(`/api/decks/${deckId}/flashcards`);
      debugLog('✅ Get flashcards successful');
      return response.data || [];
    } catch (error) {
      errorLog('❌ Get flashcards failed:', error);
      throw error;
    }
  },

  async createFlashcard(deckId: string, data: Partial<Flashcard>): Promise<Flashcard> {
    try {
      const response = await apiClient.post(`/api/decks/${deckId}/flashcards`, data);
      debugLog('✅ Create flashcard successful');
      return response.data;
    } catch (error) {
      errorLog('❌ Create flashcard failed:', error);
      throw error;
    }
  },

  async updateFlashcard(flashcardId: string, data: Partial<Flashcard>): Promise<Flashcard> {
    try {
      const response = await apiClient.put(`/api/decks/flashcards/${flashcardId}`, data);
      debugLog('✅ Update flashcard successful:', flashcardId);
      return response.data;
    } catch (error) {
      errorLog('❌ Update flashcard failed:', error);
      throw error;
    }
  },

  async deleteFlashcard(flashcardId: string): Promise<void> {
    try {
      await apiClient.delete(`/api/decks/flashcards/${flashcardId}`);
      debugLog('✅ Delete flashcard successful:', flashcardId);
    } catch (error) {
      errorLog('❌ Delete flashcard failed:', error);
      throw error;
    }
  }
};

export default contentService;
