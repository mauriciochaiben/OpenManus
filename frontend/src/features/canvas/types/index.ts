/**
 * TypeScript interfaces for Canvas feature
 */

import { Node, Edge, Connection } from 'reactflow';

export interface CanvasNode extends Node {
    type: string;
    data: {
        label: string;
        description?: string;
        config?: Record<string, any>;
        status?: 'idle' | 'running' | 'completed' | 'failed';
        result?: any;
        error?: string;
    };
}

export interface CanvasEdge extends Edge {
    type?: string;
    animated?: boolean;
    style?: Record<string, any>;
}

export interface CanvasState {
    nodes: CanvasNode[];
    edges: CanvasEdge[];
    selectedNodes: string[];
    selectedEdges: string[];
    isConnecting: boolean;
    viewport: {
        x: number;
        y: number;
        zoom: number;
    };
}

export interface NodeTemplate {
    id: string;
    type: string;
    label: string;
    description: string;
    category: string;
    icon?: string;
    defaultData: Record<string, any>;
    inputs?: string[];
    outputs?: string[];
}

export interface WorkflowExecution {
    id: string;
    status: 'idle' | 'running' | 'completed' | 'failed';
    nodes: Record<string, any>;
    startTime?: Date;
    endTime?: Date;
    error?: string;
}
