// Core types for the application

export interface Task {
    id: string;
    title: string;
    description: string;
    complexity: 'simple' | 'medium' | 'complex';
    mode: 'auto' | 'single' | 'multi';
    status: 'pending' | 'running' | 'completed' | 'error' | 'cancelled';
    progress: number;
    createdAt: string;
    updatedAt: string;
    completedAt?: string;
    priority: 'low' | 'medium' | 'high' | 'urgent';
    tags: string[];
    documentIds: string[];
    steps?: TaskStep[];
    config?: Record<string, any>;
}

export interface TaskStep {
    id: string;
    stepNumber: number;
    title: string;
    description?: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    startedAt?: string;
    completedAt?: string;
    agentName?: string;
    output?: string;
    errorMessage?: string;
}

export interface CreateTaskRequest {
    title: string;
    description: string;
    mode?: 'auto' | 'single' | 'multi';
    priority?: 'low' | 'medium' | 'high' | 'urgent';
    tags?: string[];
    documentIds?: string[];
    config?: Record<string, any>;
}

export interface UpdateTaskRequest {
    title?: string;
    description?: string;
    priority?: 'low' | 'medium' | 'high' | 'urgent';
    tags?: string[];
    config?: Record<string, any>;
}

export interface Document {
    id: string;
    filename: string;
    storedFilename: string;
    fileSize: number;
    fileType: string;
    status: 'uploading' | 'uploaded' | 'processing' | 'processed' | 'error';
    uploadedAt: string;
    filePath: string;
    extractedText?: string;
    errorMessage?: string;
}

export interface Agent {
    id: string;
    name: string;
    type: 'manus' | 'browser' | 'swe' | 'mcp' | 'data_analysis';
    status: 'idle' | 'running' | 'finished';
    capabilities: string[];
    description?: string;
}

// Chat types
export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
    taskId?: string;
}

export interface ChatRequest {
    message: string;
    context?: Record<string, any>;
}

export interface ChatResponse {
    id: string;
    message: string;
    timestamp: string;
    suggestions?: string[];
}

// API Response types
export interface ApiResponse<T = any> {
    data?: T;
    message?: string;
    error?: string;
    success: boolean;
}

export interface TaskResponse {
    task: Task;
    message: string;
}

export interface DashboardStats {
    totalTasks: number;
    completedTasks: number;
    runningTasks: number;
    pendingTasks: number;
    errorTasks: number;
    completionPercentage: number;
    recentActivity: RecentActivity[];
}

export interface RecentActivity {
    taskId: string;
    taskTitle: string;
    status: string;
    createdAt: string;
    updatedAt: string;
    completedAt?: string;
}

// UI State types
export interface UIState {
    sidebarCollapsed: boolean;
    theme: 'light' | 'dark';
    notifications: Notification[];
}

export interface Notification {
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    title: string;
    message: string;
    timestamp: string;
    read: boolean;
}

// WebSocket types
export interface WebSocketMessage {
    type: 'task_update' | 'step_update' | 'progress_update' | 'task_created' | 'task_completed' | 'error';
    taskId?: string;
    data: any;
}

// System types
export interface HealthStatus {
    status: 'healthy' | 'unhealthy';
    version: string;
    message?: string;
    services?: Record<string, 'connected' | 'disconnected' | 'error'>;
}

export interface SystemInfo {
    name: string;
    version: string;
    description: string;
    architecture?: string;
}
