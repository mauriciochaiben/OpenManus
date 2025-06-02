/**
 * LLM Configuration API Services
 */

import {
    LLMConfiguration,
    LLMProvider,
    LLMTestResult,
    LLMUsageStats,
    CreateLLMConfigRequest,
    UpdateLLMConfigRequest,
    TestLLMConfigRequest,
    LLMConfigListResponse,
    LLMProvidersResponse
} from '../types';

const API_BASE = '/api/v2/llm-config';

class LLMConfigService {
    // Get all available providers
    async getProviders(): Promise<LLMProvider[]> {
        const response = await fetch(`${API_BASE}/providers`);
        if (!response.ok) {
            throw new Error('Failed to fetch LLM providers');
        }
        const data: LLMProvidersResponse = await response.json();
        return data.providers;
    }

    // Get all configurations
    async getConfigurations(page = 1, pageSize = 50): Promise<LLMConfigListResponse> {
        const params = new URLSearchParams({
            page: page.toString(),
            page_size: pageSize.toString()
        });

        const response = await fetch(`${API_BASE}/configurations?${params}`);
        if (!response.ok) {
            throw new Error('Failed to fetch LLM configurations');
        }
        return response.json();
    }

    // Get configuration by ID
    async getConfiguration(id: string): Promise<LLMConfiguration> {
        const response = await fetch(`${API_BASE}/configurations/${id}`);
        if (!response.ok) {
            throw new Error('Failed to fetch LLM configuration');
        }
        return response.json();
    }

    // Create new configuration
    async createConfiguration(config: CreateLLMConfigRequest): Promise<LLMConfiguration> {
        const response = await fetch(`${API_BASE}/configurations`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(config),
        });

        if (!response.ok) {
            const error = await response.json();

            // Feedback de erro
            const { message } = await import('antd');
            message.error('Erro ao criar configuração LLM. Tente novamente.');

            throw new Error(error.detail || 'Failed to create LLM configuration');
        }

        // Feedback de sucesso
        const { message } = await import('antd');
        message.success('Configuração LLM criada com sucesso!');

        return response.json();
    }

    // Update configuration
    async updateConfiguration(id: string, updates: UpdateLLMConfigRequest): Promise<LLMConfiguration> {
        const response = await fetch(`${API_BASE}/configurations/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updates),
        });

        if (!response.ok) {
            const error = await response.json();

            // Feedback de erro
            const { message } = await import('antd');
            message.error('Erro ao atualizar configuração LLM. Tente novamente.');

            throw new Error(error.detail || 'Failed to update LLM configuration');
        }

        // Feedback de sucesso
        const { message } = await import('antd');
        message.success('Configuração LLM atualizada com sucesso!');

        return response.json();
    }

    // Delete configuration
    async deleteConfiguration(id: string): Promise<void> {
        const response = await fetch(`${API_BASE}/configurations/${id}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            const error = await response.json();

            // Feedback de erro
            const { message } = await import('antd');
            message.error('Erro ao excluir configuração LLM. Tente novamente.');

            throw new Error(error.detail || 'Failed to delete LLM configuration');
        }

        // Feedback de sucesso
        const { message } = await import('antd');
        message.success('Configuração LLM excluída com sucesso!');
    }

    // Set default configuration
    async setDefaultConfiguration(id: string): Promise<LLMConfiguration> {
        const response = await fetch(`${API_BASE}/configurations/${id}/set-default`, {
            method: 'POST',
        });

        if (!response.ok) {
            const error = await response.json();

            // Feedback de erro
            const { message } = await import('antd');
            message.error('Erro ao definir configuração padrão. Tente novamente.');

            throw new Error(error.detail || 'Failed to set default configuration');
        }

        // Feedback de sucesso
        const { message } = await import('antd');
        message.success('Configuração padrão definida com sucesso!');

        return response.json();
    }

    // Test configuration
    async testConfiguration(id: string, testRequest?: TestLLMConfigRequest): Promise<LLMTestResult> {
        const body = testRequest || { prompt: 'Hello, this is a test message.' };

        const response = await fetch(`${API_BASE}/configurations/${id}/test`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to test LLM configuration');
        }
        return response.json();
    }

    // Get configuration usage stats
    async getUsageStats(id: string): Promise<LLMUsageStats> {
        const response = await fetch(`${API_BASE}/configurations/${id}/stats`);
        if (!response.ok) {
            throw new Error('Failed to fetch usage statistics');
        }
        return response.json();
    }

    // Activate/deactivate configuration
    async toggleConfiguration(id: string, isActive: boolean): Promise<LLMConfiguration> {
        return this.updateConfiguration(id, { isActive });
    }

    // Get models for a specific provider
    async getProviderModels(providerId: string): Promise<any[]> {
        const response = await fetch(`${API_BASE}/providers/${providerId}/models`);
        if (!response.ok) {
            throw new Error('Failed to fetch provider models');
        }
        const data = await response.json();
        return data.models || [];
    }

    // Validate API key for a provider
    async validateApiKey(providerId: string, apiKey: string, baseUrl?: string): Promise<boolean> {
        const response = await fetch(`${API_BASE}/providers/${providerId}/validate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ api_key: apiKey, base_url: baseUrl }),
        });

        if (!response.ok) {
            return false;
        }
        const data = await response.json();
        return data.valid === true;
    }
}

export const llmConfigService = new LLMConfigService();

// Individual functions for easier imports
export const {
    getProviders,
    getConfigurations,
    getConfiguration,
    createConfiguration,
    updateConfiguration,
    deleteConfiguration,
    setDefaultConfiguration,
    testConfiguration,
    getUsageStats,
    toggleConfiguration,
    getProviderModels,
    validateApiKey
} = llmConfigService;
