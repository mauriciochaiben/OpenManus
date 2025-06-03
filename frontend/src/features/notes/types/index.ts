/**
 * TypeScript interfaces for Notes feature
 */

export interface Note {
  id: string;
  title: string;
  content: string;
  source_ids?: string[];
  tags?: string[];
  author_id?: string;
  is_public: boolean;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
  word_count?: number;
  reading_time?: string;
  source_count?: number;
}

export interface NoteCreate {
  title: string;
  content: string;
  source_ids?: string[];
  tags?: string[];
  is_public?: boolean;
  metadata?: Record<string, any>;
}

export interface NoteUpdate {
  title?: string;
  content?: string;
  source_ids?: string[];
  tags?: string[];
  is_public?: boolean;
  metadata?: Record<string, any>;
}

export interface NoteSearchQuery {
  query?: string;
  tags?: string[];
  source_ids?: string[];
  author_id?: string;
  is_public?: boolean;
  created_after?: string;
  created_before?: string;
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface NoteSearchResponse {
  notes: Note[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface ApiError {
  message: string;
  details?: string;
  code?: string;
  status_code: number;
}
