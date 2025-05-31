/**
 * Canvas State Management with Zustand
 */

import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import {
    Node,
    Edge,
    addEdge,
    applyNodeChanges,
    applyEdgeChanges,
    Connection,
    NodeChange,
    EdgeChange,
    Viewport
} from 'reactflow';
import { CanvasNode, CanvasEdge, CanvasState, WorkflowExecution } from '../types';
import { createPromptNode, createResponseNode } from '../utils/nodeFactory';
import * as canvasApi from '../services/canvasApi';

interface CanvasStore extends CanvasState {
    // Node operations
    addNode: (node: CanvasNode) => void;
    updateNode: (nodeId: string, updates: Partial<CanvasNode['data']>) => void;
    deleteNode: (nodeId: string) => void;
    duplicateNode: (nodeId: string) => void;

    // Edge operations
    addEdge: (edge: CanvasEdge | Connection) => void;
    deleteEdge: (edgeId: string) => void;

    // Selection operations
    setSelectedNodes: (nodeIds: string[]) => void;
    setSelectedEdges: (edgeIds: string[]) => void;
    clearSelection: () => void;

    // Canvas operations
    onNodesChange: (changes: NodeChange[]) => void;
    onEdgesChange: (changes: EdgeChange[]) => void;
    onConnect: (connection: Connection) => void;
    setViewport: (viewport: Viewport) => void;

    // Workflow operations
    resetCanvas: () => void;
    loadWorkflow: (nodes: CanvasNode[], edges: CanvasEdge[]) => void;
    exportWorkflow: () => { nodes: CanvasNode[]; edges: CanvasEdge[] };

    // Execution state
    execution: WorkflowExecution | null;
    setExecution: (execution: WorkflowExecution | null) => void;
    updateNodeStatus: (nodeId: string, status: CanvasNode['data']['status'], result?: any, error?: string) => void;

    // API integration methods
    createNodeInBackend: (node: CanvasNode) => Promise<void>;
    executeConnectedNodes: (sourceNodeId: string, targetNodeId: string) => Promise<void>;

    // Helper methods for creating specific node types
    addPromptNode: (position: { x: number; y: number }, prompt?: string) => Promise<void>;
    addResponseNode: (position: { x: number; y: number }) => Promise<void>;
}

const initialState: CanvasState = {
    nodes: [],
    edges: [],
    selectedNodes: [],
    selectedEdges: [],
    isConnecting: false,
    viewport: { x: 0, y: 0, zoom: 1 }
};

export const useCanvasStore = create<CanvasStore>()(
    devtools(
        subscribeWithSelector((set, get) => ({
            ...initialState,
            execution: null,

            // Node operations
            addNode: (node: CanvasNode) => {
                set((state) => ({
                    nodes: [...state.nodes, node]
                }), false, 'addNode');
            },

            updateNode: (nodeId: string, updates: Partial<CanvasNode['data']>) => {
                set((state) => ({
                    nodes: state.nodes.map(node =>
                        node.id === nodeId
                            ? { ...node, data: { ...node.data, ...updates } }
                            : node
                    )
                }), false, 'updateNode');
            },

            deleteNode: (nodeId: string) => {
                set((state) => ({
                    nodes: state.nodes.filter(node => node.id !== nodeId),
                    edges: state.edges.filter(edge =>
                        edge.source !== nodeId && edge.target !== nodeId
                    ),
                    selectedNodes: state.selectedNodes.filter(id => id !== nodeId)
                }), false, 'deleteNode');
            },

            duplicateNode: (nodeId: string) => {
                const node = get().nodes.find(n => n.id === nodeId);
                if (node) {
                    const newNode: CanvasNode = {
                        ...node,
                        id: `${node.id}-copy-${Date.now()}`,
                        position: {
                            x: node.position.x + 50,
                            y: node.position.y + 50
                        },
                        data: {
                            ...node.data,
                            label: `${node.data.label} (Copy)`
                        }
                    };
                    get().addNode(newNode);
                }
            },

            // Edge operations
            addEdge: (edge: CanvasEdge | Connection) => {
                set((state) => ({
                    edges: addEdge(edge, state.edges)
                }), false, 'addEdge');
            },

            deleteEdge: (edgeId: string) => {
                set((state) => ({
                    edges: state.edges.filter(edge => edge.id !== edgeId),
                    selectedEdges: state.selectedEdges.filter(id => id !== edgeId)
                }), false, 'deleteEdge');
            },

            // Selection operations
            setSelectedNodes: (nodeIds: string[]) => {
                set({ selectedNodes: nodeIds }, false, 'setSelectedNodes');
            },

            setSelectedEdges: (edgeIds: string[]) => {
                set({ selectedEdges: edgeIds }, false, 'setSelectedEdges');
            },

            clearSelection: () => {
                set({
                    selectedNodes: [],
                    selectedEdges: []
                }, false, 'clearSelection');
            },

            // Canvas operations
            onNodesChange: (changes: NodeChange[]) => {
                set((state) => ({
                    nodes: applyNodeChanges(changes, state.nodes)
                }), false, 'onNodesChange');
            },

            onEdgesChange: (changes: EdgeChange[]) => {
                set((state) => ({
                    edges: applyEdgeChanges(changes, state.edges)
                }), false, 'onEdgesChange');
            },

            onConnect: (connection: Connection) => {
                get().addEdge(connection);
            },

            setViewport: (viewport: Viewport) => {
                set({ viewport }, false, 'setViewport');
            },

            // Workflow operations
            resetCanvas: () => {
                set(initialState, false, 'resetCanvas');
            },

            loadWorkflow: (nodes: CanvasNode[], edges: CanvasEdge[]) => {
                set({
                    nodes,
                    edges,
                    selectedNodes: [],
                    selectedEdges: []
                }, false, 'loadWorkflow');
            },

            exportWorkflow: () => {
                const { nodes, edges } = get();
                return { nodes, edges };
            },

            // Execution state
            setExecution: (execution: WorkflowExecution | null) => {
                set({ execution }, false, 'setExecution');
            },

            updateNodeStatus: (nodeId: string, status: CanvasNode['data']['status'], result?: any, error?: string) => {
                set((state) => ({
                    nodes: state.nodes.map(node =>
                        node.id === nodeId
                            ? {
                                ...node,
                                data: {
                                    ...node.data,
                                    status,
                                    result,
                                    error
                                }
                            }
                            : node
                    )
                }), false, 'updateNodeStatus');
            },

            // API integration methods
            createNodeInBackend: async (node: CanvasNode) => {
                try {
                    await canvasApi.createNode(node);
                } catch (error) {
                    console.error('Failed to create node in backend:', error);
                    // Remove node from frontend if backend creation fails
                    set((state) => ({
                        nodes: state.nodes.filter(n => n.id !== node.id)
                    }));
                    throw error;
                }
            },

            executeConnectedNodes: async (sourceNodeId: string, targetNodeId: string) => {
                try {
                    const state = get();
                    const sourceNode = state.nodes.find(n => n.id === sourceNodeId);
                    const targetNode = state.nodes.find(n => n.id === targetNodeId);

                    if (!sourceNode || !targetNode) {
                        throw new Error('Source or target node not found');
                    }

                    // Check if source is a prompt node and target is a response node
                    if (sourceNode.type === 'promptNode' && targetNode.type === 'responseNode') {
                        // Update target node to running state
                        get().updateNodeStatus(targetNodeId, 'running');

                        // Execute the prompt
                        const result = await canvasApi.executePromptNode(
                            sourceNodeId,
                            sourceNode.data.prompt || '',
                            sourceNode.data.source_ids
                        );

                        // Update target node with result
                        get().updateNodeStatus(
                            targetNodeId,
                            result.status === 'completed' ? 'completed' : 'failed',
                            result.result,
                            result.error
                        );
                    }
                } catch (error) {
                    console.error('Failed to execute connected nodes:', error);
                    // Update target node with error
                    get().updateNodeStatus(targetNodeId, 'failed', undefined, String(error));
                }
            },

            // Enhanced addEdge to trigger execution
            addEdge: (edge: CanvasEdge | Connection) => {
                set((state) => {
                    const newEdges = addEdge(edge, state.edges);

                    // Trigger execution when nodes are connected
                    setTimeout(async () => {
                        try {
                            await get().executeConnectedNodes(edge.source!, edge.target!);
                        } catch (error) {
                            console.error('Auto-execution failed:', error);
                        }
                    }, 100);

                    return { edges: newEdges };
                }, false, 'addEdge');
            },

            // Helper methods for creating specific node types
            addPromptNode: async (position: { x: number; y: number }, prompt?: string) => {
                const node = createPromptNode(position, { prompt: prompt || '' });

                // Add to frontend first
                get().addNode(node);

                // Then create in backend
                try {
                    await get().createNodeInBackend(node);
                } catch (error) {
                    console.error('Failed to create prompt node in backend:', error);
                }
            },

            addResponseNode: async (position: { x: number; y: number }) => {
                const node = createResponseNode(position);

                // Add to frontend first
                get().addNode(node);

                // Then create in backend
                try {
                    await get().createNodeInBackend(node);
                } catch (error) {
                    console.error('Failed to create response node in backend:', error);
                }
            },
        })),
        {
            name: 'canvas-store',
            partialize: (state) => ({
                nodes: state.nodes,
                edges: state.edges,
                viewport: state.viewport
            })
        }
    )
);
