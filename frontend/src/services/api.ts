import axios from 'axios';
import type {
    Task,
    CreateTaskRequest,
    TaskResponse,
    ComplexityAnalysis,
    UploadedDocument,
    MCPServer,
    MCPServerConfig,
    ChatMessage,
    ChatRequest,
    ChatResponse
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
    baseURL: `${API_BASE_URL}/api/v2`,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for logging
api.interceptors.request.use(
    (config) => {
        console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
    },
    (error) => {
        console.error('❌ API Request Error:', error);
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`);
        return response;
    },
    (error) => {
        console.error('❌ API Response Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);

// Task Management API
export const taskApi = {
    // Analyze task complexity
    analyzeComplexity: async (description: string): Promise<ComplexityAnalysis> => {
        const response = await api.post('/analyze-complexity', { description });
        return response.data;
    },

    // Create new task
    createTask: async (taskData: CreateTaskRequest): Promise<TaskResponse> => {
        const response = await api.post('/tasks', taskData);
        return response.data;
    },

    // Get all tasks
    getTasks: async (): Promise<Task[]> => {
        const response = await api.get('/tasks');
        return response.data;
    },

    // Get task by ID
    getTask: async (taskId: string): Promise<Task> => {
        const response = await api.get(`/tasks/${taskId}`);
        return response.data;
    },

    // Cancel task
    cancelTask: async (taskId: string): Promise<void> => {
        await api.post(`/tasks/${taskId}/cancel`);
    },

    // Delete task
    deleteTask: async (taskId: string): Promise<void> => {
        await api.delete(`/tasks/${taskId}`);
    },

    // Get task logs
    getTaskLogs: async (taskId: string): Promise<any[]> => {
        const response = await api.get(`/tasks/${taskId}/logs`);
        return response.data;
    },

    // Retry failed task
    retryTask: async (taskId: string): Promise<TaskResponse> => {
        const response = await api.post(`/tasks/${taskId}/retry`);
        return response.data;
    },
};

// Document Management API
export const documentApi = {
    // Upload document
    uploadDocument: async (file: File, onProgress?: (progress: number) => void): Promise<UploadedDocument> => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await api.post('/documents/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            onUploadProgress: (progressEvent) => {
                if (onProgress && progressEvent.total) {
                    const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    onProgress(progress);
                }
            },
        });

        return response.data;
    },

    // Get document info
    getDocument: async (documentId: string): Promise<UploadedDocument> => {
        const response = await api.get(`/documents/${documentId}`);
        return response.data;
    },

    // Delete document
    deleteDocument: async (documentId: string): Promise<void> => {
        await api.delete(`/documents/${documentId}`);
    },

    // Process document (extract text, analyze)
    processDocument: async (documentId: string): Promise<UploadedDocument> => {
        const response = await api.post(`/documents/${documentId}/process`);
        return response.data;
    },

    // Download document
    downloadDocument: async (documentId: string): Promise<Blob> => {
        const response = await api.get(`/documents/${documentId}/download`, {
            responseType: 'blob',
        });
        return response.data;
    },
};

// MCP Server Management API
export const mcpApi = {
    // Get available MCP servers
    getServers: async (): Promise<MCPServer[]> => {
        const response = await api.get('/mcp/servers');
        return response.data;
    },

    // Create new MCP server
    createServer: async (serverConfig: MCPServerConfig): Promise<MCPServer> => {
        const response = await api.post('/mcp/servers', serverConfig);
        return response.data;
    },

    // Update MCP server
    updateServer: async (serverId: string, serverConfig: Partial<MCPServerConfig>): Promise<MCPServer> => {
        const response = await api.put(`/mcp/servers/${serverId}`, serverConfig);
        return response.data;
    },

    // Delete MCP server
    deleteServer: async (serverId: string): Promise<void> => {
        await api.delete(`/mcp/servers/${serverId}`);
    },

    // Connect to MCP server
    connectServer: async (serverId: string): Promise<MCPServer> => {
        const response = await api.post(`/mcp/servers/${serverId}/connect`);
        return response.data;
    },

    // Disconnect from MCP server
    disconnectServer: async (serverId: string): Promise<void> => {
        await api.post(`/mcp/servers/${serverId}/disconnect`);
    },

    // Get server tools
    getServerTools: async (serverId: string): Promise<any[]> => {
        const response = await api.get(`/mcp/servers/${serverId}/tools`);
        return response.data;
    },
};

// System API
export const systemApi = {
    // Get system health
    getHealth: async (): Promise<{ status: string; version: string }> => {
        const response = await api.get('/health');
        return response.data;
    },

    // Get system info
    getInfo: async (): Promise<any> => {
        const response = await api.get('/info');
        return response.data;
    },

    // Get dashboard statistics
    getDashboardStats: async (): Promise<any> => {
        const response = await api.get('/dashboard/stats');
        return response.data;
    },

    // Get available agents
    getAgents: async (): Promise<any[]> => {
        const response = await api.get('/agents');
        return response.data;
    },
};

// Chat API
export const chatApi = {
    // Send chat message
    sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
        const response = await api.post('/chat', request);
        return response.data;
    },

    // Get chat history
    getHistory: async (sessionId: string = 'default'): Promise<ChatMessage[]> => {
        const response = await api.get(`/chat/history?session_id=${sessionId}`);
        return response.data;
    },

    // Clear chat history
    clearHistory: async (sessionId: string = 'default'): Promise<void> => {
        await api.delete(`/chat/history?session_id=${sessionId}`);
    },
};

export default api;

// Individual function exports for cleaner imports
export const createTask = taskApi.createTask;
export const getTasks = taskApi.getTasks;
export const getTask = taskApi.getTask;
export const uploadDocument = documentApi.uploadDocument;
export const getMCPServers = mcpApi.getServers;
export const createMCPServer = mcpApi.createServer;
export const updateMCPServer = mcpApi.updateServer;
export const deleteMCPServer = mcpApi.deleteServer;
