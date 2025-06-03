/**
 * Knowledge API Service
 *
 * Provides functions to interact with the knowledge management endpoints
 * in the backend API.
 */

import axios, { AxiosResponse, AxiosError } from "axios";
import {
  KnowledgeSource,
  UploadSourceRequest,
  UploadSourceResponse,
  GetSourceStatusResponse,
  ListSourcesResponse,
  ListSourcesParams,
  DeleteSourceResponse,
  SearchKnowledgeRequest,
  SearchKnowledgeResponse,
  ApiError,
} from "../types/api";

// API base configuration
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const KNOWLEDGE_API_BASE = `${API_BASE_URL}/api/v1/knowledge`;

// Configure axios instance
const apiClient = axios.create({
  baseURL: KNOWLEDGE_API_BASE,
  timeout: 30000, // 30 seconds timeout for file uploads
  headers: {
    "Content-Type": "application/json",
  },
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    const apiError: ApiError = {
      message: error.message || "An error occurred",
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
  },
);

/**
 * Upload a file to the knowledge base
 */
export const uploadSource = async (
  request: UploadSourceRequest,
): Promise<UploadSourceResponse> => {
  const formData = new FormData();
  formData.append("file", request.file);

  if (request.metadata) {
    formData.append("metadata", JSON.stringify(request.metadata));
  }

  try {
    const response = await apiClient.post<UploadSourceResponse>(
      "/sources/upload",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      },
    );

    // Feedback de sucesso
    const { message } = await import("antd");
    message.success("Fonte de conhecimento enviada com sucesso!");

    return response.data;
  } catch (error) {
    console.error("Error uploading source:", error);

    // Feedback de erro
    const { message } = await import("antd");
    message.error("Erro ao enviar fonte de conhecimento. Tente novamente.");

    throw error;
  }
};

/**
 * Get the processing status of a specific source
 */
export const getSourceStatus = async (
  sourceId: string,
): Promise<GetSourceStatusResponse> => {
  try {
    const response = await apiClient.get<GetSourceStatusResponse>(
      `/sources/${sourceId}/status`,
    );

    return response.data;
  } catch (error) {
    console.error(`Error getting status for source ${sourceId}:`, error);
    throw error;
  }
};

/**
 * List all knowledge sources with optional filtering and pagination
 */
export const listSources = async (
  params?: ListSourcesParams,
): Promise<ListSourcesResponse> => {
  try {
    const queryParams = new URLSearchParams();

    if (params?.page !== undefined) {
      queryParams.append("page", params.page.toString());
    }

    if (params?.page_size !== undefined) {
      queryParams.append("page_size", params.page_size.toString());
    }

    if (params?.status) {
      queryParams.append("status", params.status);
    }

    if (params?.file_type) {
      queryParams.append("file_type", params.file_type);
    }

    const response = await apiClient.get<ListSourcesResponse>(
      `/sources?${queryParams.toString()}`,
    );

    return response.data;
  } catch (error) {
    console.error("Error listing sources:", error);
    throw error;
  }
};

/**
 * Get details of a specific knowledge source
 */
export const getSource = async (sourceId: string): Promise<KnowledgeSource> => {
  try {
    const response = await apiClient.get<KnowledgeSource>(
      `/sources/${sourceId}`,
    );
    return response.data;
  } catch (error) {
    console.error(`Error getting source ${sourceId}:`, error);
    throw error;
  }
};

/**
 * Delete a knowledge source and all its associated data
 */
export const deleteSource = async (
  sourceId: string,
): Promise<DeleteSourceResponse> => {
  try {
    const response = await apiClient.delete<DeleteSourceResponse>(
      `/sources/${sourceId}`,
    );

    // Feedback de sucesso
    const { message } = await import("antd");
    message.success("Fonte de conhecimento excluída com sucesso!");

    return response.data;
  } catch (error) {
    console.error(`Error deleting source ${sourceId}:`, error);

    // Feedback de erro
    const { message } = await import("antd");
    message.error("Erro ao excluir fonte de conhecimento. Tente novamente.");

    throw error;
  }
};

/**
 * Search for relevant content in the knowledge base
 */
export const searchKnowledge = async (
  request: SearchKnowledgeRequest,
): Promise<SearchKnowledgeResponse> => {
  try {
    const response = await apiClient.post<SearchKnowledgeResponse>(
      "/search",
      request,
    );

    return response.data;
  } catch (error) {
    console.error("Error searching knowledge:", error);
    throw error;
  }
};

/**
 * Reprocess a knowledge source (useful if processing failed)
 */
export const reprocessSource = async (
  sourceId: string,
): Promise<{ message: string; source_id: string }> => {
  try {
    const response = await apiClient.post<{
      message: string;
      source_id: string;
    }>(`/sources/${sourceId}/reprocess`);

    // Feedback de sucesso
    const { message } = await import("antd");
    message.success("Reprocessamento da fonte iniciado com sucesso!");

    return response.data;
  } catch (error) {
    console.error(`Error reprocessing source ${sourceId}:`, error);

    // Feedback de erro
    const { message } = await import("antd");
    message.error(
      "Erro ao reprocessar fonte de conhecimento. Tente novamente.",
    );

    throw error;
  }
};

/**
 * Get processing statistics for the knowledge base
 */
export const getKnowledgeStats = async (): Promise<{
  total_sources: number;
  processing_sources: number;
  failed_sources: number;
  total_chunks: number;
  total_size_bytes: number;
}> => {
  try {
    const response = await apiClient.get("/stats");
    return response.data;
  } catch (error) {
    console.error("Error getting knowledge stats:", error);
    throw error;
  }
};

/**
 * Health check for the knowledge service
 */
export const checkKnowledgeHealth = async (): Promise<{
  status: string;
  timestamp: string;
  services: Record<string, string>;
}> => {
  try {
    const response = await apiClient.get("/health");
    return response.data;
  } catch (error) {
    console.error("Error checking knowledge health:", error);
    throw error;
  }
};

// Export the configured axios instance for custom requests
export { apiClient as knowledgeApiClient };

// Export all types for convenience
export * from "../types/api";
