/**
 * Notes API Service
 *
 * Provides functions to interact with the notes management endpoints
 */

import axios, { AxiosResponse, AxiosError } from 'axios';
import {
  Note,
  NoteCreate,
  NoteUpdate,
  NoteSearchQuery,
  NoteSearchResponse,
  ApiError,
} from '../types';

// API base configuration
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const NOTES_API_BASE = `${API_BASE_URL}/api/v1/notes`;

// Configure axios instance
const apiClient = axios.create({
  baseURL: NOTES_API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    const apiError: ApiError = {
      message: error.message || 'An error occurred',
      status_code: error.response?.status || 500,
    };

    if (error.response?.data) {
      const errorData = error.response.data as any;
      apiError.message =
        errorData.message || errorData.detail || apiError.message;
      apiError.details = errorData.details;
      apiError.code = errorData.code;
    }

    throw apiError;
  }
);

/**
 * Create a new note
 */
export const createNote = async (noteData: NoteCreate): Promise<Note> => {
  try {
    const response = await apiClient.post<Note>('/', noteData);

    // Feedback de sucesso
    const { message } = await import('antd');
    message.success('Nota criada com sucesso!');

    return response.data;
  } catch (error) {
    console.error('Error creating note:', error);

    // Feedback de erro
    const { message } = await import('antd');
    message.error('Erro ao criar nota. Tente novamente.');

    throw error;
  }
};

/**
 * Get a note by ID
 */
export const getNote = async (noteId: string): Promise<Note> => {
  try {
    const response = await apiClient.get<Note>(`/${noteId}`);
    return response.data;
  } catch (error) {
    console.error(`Error getting note ${noteId}:`, error);
    throw error;
  }
};

/**
 * Update a note
 */
export const updateNote = async (
  noteId: string,
  noteData: NoteUpdate
): Promise<Note> => {
  try {
    const response = await apiClient.put<Note>(`/${noteId}`, noteData);

    // Feedback de sucesso
    const { message } = await import('antd');
    message.success('Nota atualizada com sucesso!');

    return response.data;
  } catch (error) {
    console.error(`Error updating note ${noteId}:`, error);

    // Feedback de erro
    const { message } = await import('antd');
    message.error('Erro ao atualizar nota. Tente novamente.');

    throw error;
  }
};

/**
 * Delete a note
 */
export const deleteNote = async (noteId: string): Promise<void> => {
  try {
    await apiClient.delete(`/${noteId}`);

    // Feedback de sucesso
    const { message } = await import('antd');
    message.success('Nota excluída com sucesso!');
  } catch (error) {
    console.error(`Error deleting note ${noteId}:`, error);

    // Feedback de erro
    const { message } = await import('antd');
    message.error('Erro ao excluir nota. Tente novamente.');

    throw error;
  }
};

/**
 * List notes with pagination
 */
export const listNotes = async (params?: {
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: string;
}): Promise<{ notes: Note[]; total: number }> => {
  try {
    const queryParams = new URLSearchParams();

    if (params?.limit !== undefined) {
      queryParams.append('limit', params.limit.toString());
    }

    if (params?.offset !== undefined) {
      queryParams.append('offset', params.offset.toString());
    }

    if (params?.sort_by) {
      queryParams.append('sort_by', params.sort_by);
    }

    if (params?.sort_order) {
      queryParams.append('sort_order', params.sort_order);
    }

    const response = await apiClient.get<{ notes: Note[]; total: number }>(
      `/?${queryParams.toString()}`
    );
    return response.data;
  } catch (error) {
    console.error('Error listing notes:', error);
    throw error;
  }
};

/**
 * Search notes with advanced filtering
 */
export const searchNotes = async (
  searchQuery: NoteSearchQuery
): Promise<NoteSearchResponse> => {
  try {
    const response = await apiClient.post<NoteSearchResponse>(
      '/search',
      searchQuery
    );
    return response.data;
  } catch (error) {
    console.error('Error searching notes:', error);
    throw error;
  }
};

/**
 * Get notes that reference a specific knowledge source
 */
export const getNotesBySource = async (
  sourceId: string,
  params?: { limit?: number; offset?: number }
): Promise<{ notes: Note[]; total: number }> => {
  try {
    const queryParams = new URLSearchParams();

    if (params?.limit !== undefined) {
      queryParams.append('limit', params.limit.toString());
    }

    if (params?.offset !== undefined) {
      queryParams.append('offset', params.offset.toString());
    }

    const response = await apiClient.get<{ notes: Note[]; total: number }>(
      `/by-source/${sourceId}?${queryParams.toString()}`
    );
    return response.data;
  } catch (error) {
    console.error(`Error getting notes by source ${sourceId}:`, error);
    throw error;
  }
};

export * from '../types';
