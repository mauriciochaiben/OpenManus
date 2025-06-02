/**
 * Canvas API Service
 *
 * Provides functions to interact with canvas and workflow endpoints
 */

import axios, { AxiosResponse, AxiosError } from 'axios';
import { CanvasNode, CanvasEdge } from '../types';

// API base configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const CANVAS_API_BASE = `${API_BASE_URL}/api/v1/canvas`;
const WORKFLOW_API_BASE = `${API_BASE_URL}/api/v1/workflows`;

// Configure axios instance
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Response interfaces
interface NodeExecutionResponse {
    id: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    result?: string;
    error?: string;
    execution_time?: number;
}

interface WorkflowExecutionResponse {
    workflow_id: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    nodes: Record<string, NodeExecutionResponse>;
}

/**
 * Create a node in the backend
 */
export const createNode = async (node: CanvasNode): Promise<CanvasNode> => {
    try {
        const response = await apiClient.post<CanvasNode>(`${CANVAS_API_BASE}/nodes`, {
            id: node.id,
            type: node.type,
            position: node.position,
            data: node.data
        });

        // Feedback de sucesso
        const { message } = await import('antd');
        message.success('Nó criado com sucesso!');

        return response.data;
    } catch (error) {
        console.error('Error creating node:', error);

        // Feedback de erro
        const { message } = await import('antd');
        message.error('Erro ao criar nó. Tente novamente.');

        throw error;
    }
};

/**
 * Update a node in the backend
 */
export const updateNode = async (nodeId: string, updates: Partial<CanvasNode>): Promise<CanvasNode> => {
    try {
        const response = await apiClient.put<CanvasNode>(`${CANVAS_API_BASE}/nodes/${nodeId}`, updates);

        // Feedback de sucesso
        const { message } = await import('antd');
        message.success('Nó atualizado com sucesso!');

        return response.data;
    } catch (error) {
        console.error('Error updating node:', error);

        // Feedback de erro
        const { message } = await import('antd');
        message.error('Erro ao atualizar nó. Tente novamente.');

        throw error;
    }
};

/**
 * Delete a node from the backend
 */
export const deleteNode = async (nodeId: string): Promise<void> => {
    try {
        await apiClient.delete(`${CANVAS_API_BASE}/nodes/${nodeId}`);

        // Feedback de sucesso
        const { message } = await import('antd');
        message.success('Nó excluído com sucesso!');
    } catch (error) {
        console.error('Error deleting node:', error);

        // Feedback de erro
        const { message } = await import('antd');
        message.error('Erro ao excluir nó. Tente novamente.');

        throw error;
    }
};

/**
 * Execute a prompt node
 */
export const executePromptNode = async (
    nodeId: string,
    prompt: string,
    sourceIds?: string[]
): Promise<NodeExecutionResponse> => {
    try {
        const response = await apiClient.post<NodeExecutionResponse>(
            `${CANVAS_API_BASE}/nodes/${nodeId}/execute`,
            {
                prompt,
                source_ids: sourceIds
            }
        );

        // Feedback de sucesso
        const { message } = await import('antd');
        message.success('Execução do nó iniciada com sucesso!');

        return response.data;
    } catch (error) {
        console.error('Error executing prompt node:', error);

        // Feedback de erro
        const { message } = await import('antd');
        message.error('Erro ao executar nó. Tente novamente.');

        throw error;
    }
};

/**
 * Execute a canvas workflow
 */
export const executeCanvasWorkflow = async (
    nodes: CanvasNode[],
    edges: CanvasEdge[]
): Promise<WorkflowExecutionResponse> => {
    try {
        const response = await apiClient.post<WorkflowExecutionResponse>(
            `${WORKFLOW_API_BASE}/canvas`,
            {
                title: 'Canvas Workflow',
                description: 'Workflow executed from canvas',
                nodes: nodes.map(node => ({
                    id: node.id,
                    type: node.type,
                    config: node.data
                })),
                edges: edges.map(edge => ({
                    source: edge.source,
                    target: edge.target,
                    type: edge.type
                }))
            }
        );

        // Feedback de sucesso
        const { message } = await import('antd');
        message.success('Execução do workflow iniciada com sucesso!');

        return response.data;
    } catch (error) {
        console.error('Error executing canvas workflow:', error);

        // Feedback de erro
        const { message } = await import('antd');
        message.error('Erro ao executar workflow. Tente novamente.');

        throw error;
    }
};

export * from '../types';
