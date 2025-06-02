/**
 * TypeScript interfaces for Canvas feature
 */

// Base interfaces (simplified without external dependencies)
export interface Position {
    x: number;
    y: number;
}

export interface BaseNode {
    id: string;
    type: string;
    position: Position;
    data: any;
}

export interface BaseEdge {
    id: string;
    source: string;
    target: string;
    type?: string;
}

export interface CanvasNode extends BaseNode {
    type: string;
    data: {
        label: string;
        description?: string;
        config?: Record<string, any>;
        status?: 'idle' | 'running' | 'completed' | 'failed';
        result?: any;
        error?: string;
        prompt?: string;
        response?: string;
        source_ids?: string[];
    };
}

export interface CanvasEdge extends BaseEdge {
    type?: string;
    data?: {
        label?: string;
        config?: Record<string, any>;
    };
}

export interface CanvasState {
    nodes: CanvasNode[];
    edges: CanvasEdge[];
    selectedNodes: string[];
    selectedEdges: string[];
    isConnecting: boolean;
    viewport: { x: number; y: number; zoom: number };
}

export interface CanvasActions {
    addNode: (node: Omit<CanvasNode, 'id'>) => void;
    updateNode: (id: string, updates: Partial<CanvasNode>) => void;
    deleteNode: (id: string) => void;
    addEdge: (edge: Omit<CanvasEdge, 'id'>) => void;
    deleteEdge: (id: string) => void;
    selectNode: (id: string | null) => void;
    executeNode: (id: string) => Promise<void>;
    executeWorkflow: () => Promise<void>;
    setExecutionResult: (nodeId: string, result: any) => void;
    setExecutionError: (nodeId: string, error: string) => void;
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
