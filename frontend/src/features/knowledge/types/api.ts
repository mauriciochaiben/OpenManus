/**
 * TypeScript interfaces for Knowledge API requests and responses
 */

export interface KnowledgeSource {
    id: string;
    filename: string;
    file_type: string;
    size: number;
    upload_date: string;
    status: ProcessingStatus;
    chunk_count?: number;
    metadata?: Record<string, any>;
}

export interface ProcessingStatus {
    status: 'pending' | 'processing' | 'completed' | 'failed';
    progress?: number;
    error_message?: string;
    processed_chunks?: number;
    total_chunks?: number;
    last_updated: string;
}

export interface UploadSourceRequest {
    file: File;
    metadata?: Record<string, any>;
}

export interface UploadSourceResponse {
    source_id: string;
    filename: string;
    file_type: string;
    size: number;
    status: ProcessingStatus;
    message: string;
}

export interface GetSourceStatusResponse {
    source_id: string;
    filename: string;
    status: ProcessingStatus;
}

export interface ListSourcesResponse {
    sources: KnowledgeSource[];
    total: number;
    page: number;
    page_size: number;
}

export interface ListSourcesParams {
    page?: number;
    page_size?: number;
    status?: string;
    file_type?: string;
}

export interface DeleteSourceResponse {
    message: string;
    deleted_source_id: string;
}

export interface SearchKnowledgeRequest {
    query: string;
    source_ids?: string[];
    k?: number;
    min_score?: number;
}

export interface SearchKnowledgeResponse {
    results: SearchResult[];
    query: string;
    total_results: number;
}

export interface SearchResult {
    text: string;
    score: number;
    metadata: {
        source_id: string;
        filename: string;
        chunk_id: string;
        page?: number;
        section?: string;
    };
}

export interface ApiError {
    message: string;
    details?: string;
    code?: string;
    status_code: number;
}
