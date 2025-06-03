/**
 * Types for LLM Configuration System
 */

export interface LLMProvider {
  id: string;
  name: string;
  displayName: string;
  type: "openai" | "anthropic" | "google" | "ollama" | "custom";
  description: string;
  icon?: string;
  requiresApiKey: boolean;
  baseUrl?: string;
  supportedFeatures: LLMFeature[];
  models: LLMModel[];
}

export interface LLMModel {
  id: string;
  name: string;
  displayName: string;
  providerId: string;
  description?: string;
  contextWindow: number;
  pricing?: {
    input: number;
    output: number;
    currency: string;
  };
  capabilities: ModelCapability[];
  parameters: ModelParameter[];
}

export interface LLMConfiguration {
  id: string;
  name: string;
  providerId: string;
  modelId: string;
  apiKey?: string;
  baseUrl?: string;
  customHeaders?: Record<string, string>;
  parameters: Record<string, any>;
  isDefault: boolean;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ModelParameter {
  name: string;
  displayName: string;
  type: "string" | "number" | "boolean" | "select" | "range";
  description: string;
  defaultValue: any;
  required: boolean;
  options?: Array<{ label: string; value: any }>;
  min?: number;
  max?: number;
  step?: number;
}

export type LLMFeature =
  | "chat"
  | "completion"
  | "embedding"
  | "image_analysis"
  | "function_calling"
  | "streaming"
  | "vision"
  | "code_generation";

export type ModelCapability =
  | "text_generation"
  | "conversation"
  | "function_calling"
  | "tool_use"
  | "vision"
  | "multimodal"
  | "code_completion"
  | "reasoning";

export interface LLMTestResult {
  success: boolean;
  latency: number;
  error?: string;
  response?: string;
  model?: string;
  timestamp: string;
}

export interface LLMUsageStats {
  configId: string;
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageLatency: number;
  totalTokens: number;
  estimatedCost: number;
  lastUsed: string;
}

// API Request/Response types
export interface CreateLLMConfigRequest {
  name: string;
  providerId: string;
  modelId: string;
  apiKey?: string;
  baseUrl?: string;
  customHeaders?: Record<string, string>;
  parameters: Record<string, any>;
  isDefault?: boolean;
}

export interface UpdateLLMConfigRequest
  extends Partial<CreateLLMConfigRequest> {
  isActive?: boolean;
}

export interface TestLLMConfigRequest {
  prompt?: string;
  useStreaming?: boolean;
}

export interface LLMConfigListResponse {
  configurations: LLMConfiguration[];
  total: number;
  page: number;
  pageSize: number;
}

export interface LLMProvidersResponse {
  providers: LLMProvider[];
}
