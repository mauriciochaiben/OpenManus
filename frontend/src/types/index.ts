// Task execution types
export interface Task {
  id: string;
  title: string;
  description: string;
  complexity: 'simple' | 'complex';
  mode: 'auto' | 'single' | 'multi';
  status: 'pending' | 'running' | 'completed' | 'error';
  createdAt: string;
  completedAt?: string;
  result?: string;
  documents?: UploadedDocument[];
  steps?: TaskStep[];
  logs?: LogEntry[];
}

export interface TaskStep {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  startedAt?: string;
  completedAt?: string;
  result?: string;
  agent?: string;
}

export interface UploadedDocument {
  id: string;
  name: string;
  size: number;
  type: string;
  url?: string;
  status: 'uploading' | 'uploaded' | 'processing' | 'processed' | 'error';
  extractedText?: string;
  error?: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'success';
  message: string;
  source?: string;
}

// API request/response types
export interface CreateTaskRequest {
  title: string;
  description: string;
  mode?: 'auto' | 'single' | 'multi';
  documents?: string[]; // Document IDs
  config?: TaskConfig;
}

export interface TaskConfig {
  maxSteps?: number;
  enablePlanning?: boolean;
  enableCoordination?: boolean;
  mcpServers?: string[];
}

export interface TaskResponse {
  task: Task;
  message: string;
}

export interface ComplexityAnalysis {
  score: number;
  isComplex: boolean;
  indicators: {
    length: boolean;
    keywords: boolean;
    multipleDomains: boolean;
    timeConsuming: boolean;
  };
  recommendation: 'single' | 'multi';
}

// WebSocket message types
export interface WebSocketMessage {
  type: 'task_update' | 'step_update' | 'log_entry' | 'error';
  taskId: string;
  data: any;
}

// Settings and configuration
export interface AppSettings {
  apiBaseUrl: string;
  wsBaseUrl: string;
  maxFileSize: number;
  allowedFileTypes: string[];
  defaultTaskMode: 'auto' | 'single' | 'multi';
  enableRealTimeUpdates: boolean;
}

export interface MCPServer {
  id: string;
  name: string;
  type?: 'sse' | 'stdio';
  url?: string;
  command?: string;
  args?: string[];
  status: 'connected' | 'disconnected' | 'error';
  host?: string;
  port?: number;
  enabled?: boolean;
  description?: string;
  created_at?: string;
  last_seen?: string | null;
  tools?: any[];
}

// UI State types
export interface UIState {
  sidebarCollapsed: boolean;
  currentTask?: Task;
  tasks: Task[];
  settings: AppSettings;
  mcpServers: MCPServer[];
}

// Form types
export interface TaskFormData {
  title: string;
  description: string;
  mode: 'auto' | 'single' | 'multi';
  documents: File[];
  config: {
    maxSteps: number;
    enablePlanning: boolean;
    enableCoordination: boolean;
  };
}

// Agent types
export interface Agent {
  id: string;
  name: string;
  type: 'manus' | 'browser' | 'swe' | 'mcp' | 'data_analysis';
  status: 'idle' | 'running' | 'finished';
  capabilities: string[];
}

export interface MultiAgentFlow {
  id: string;
  agents: Agent[];
  coordinationEnabled: boolean;
  planningEnabled: boolean;
  executionMode: 'auto' | 'force_single' | 'force_multi';
}

// Additional types for API compatibility
export interface TaskCreateRequest {
  title: string;
  description: string;
  complexity: 'low' | 'medium' | 'high';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  document_ids?: string[];
  tags?: string[];
}

export interface DocumentUploadResponse {
  id: string;
  filename: string;
  file_size: number;
  file_type: string;
  upload_url?: string;
  status: 'uploaded' | 'processing' | 'processed' | 'error';
}

export interface MCPServerConfig {
  name: string;
  host: string;
  port: number;
  enabled: boolean;
  description?: string;
}

export interface TaskExecution {
  id: string;
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  started_at: string;
  completed_at?: string;
  progress: number;
}

export interface ExecutionStep {
  id: string;
  step_number: number;
  title: string;
  description?: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  started_at?: string;
  completed_at?: string;
  agent_name?: string;
  output?: string;
  error_message?: string;
}

// Chat types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  task_id?: string;
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

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  mode?: 'auto' | 'single' | 'multi';
  documents?: string[];
  config?: TaskConfig;
}

// Additional UI and system types
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

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

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
