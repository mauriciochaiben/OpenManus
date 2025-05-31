import React, { useCallback, useRef, useEffect } from 'react';
import {
    ReactFlow,
    ReactFlowProvider,
    Background,
    Controls,
    MiniMap,
    Panel,
    useReactFlow,
    ConnectionMode,
    SelectionMode
} from 'reactflow';
import { Card, Space, Button, Typography, Tooltip } from 'antd';
import {
    ZoomInOutlined,
    ZoomOutOutlined,
    AimOutlined,
    FullscreenOutlined,
    SaveOutlined,
    PlayCircleOutlined,
    StopOutlined,
    ClearOutlined
} from '@ant-design/icons';

import { useCanvasStore } from '../store/canvasStore';
import { CanvasNode, CanvasEdge } from '../types';
import { nodeTypes } from './nodes';
import { useCanvasWebSocket } from '../hooks/useCanvasWebSocket';

// Import ReactFlow CSS
import 'reactflow/dist/style.css';

const { Text } = Typography;

interface CanvasWorkspaceProps {
    className?: string;
    height?: string | number;
    readOnly?: boolean;
    onSave?: (nodes: CanvasNode[], edges: CanvasEdge[]) => void;
    onExecute?: (nodes: CanvasNode[], edges: CanvasEdge[]) => void;
}

const CanvasContent: React.FC<CanvasWorkspaceProps> = ({
    className,
    height = '100vh',
    readOnly = false,
    onSave,
    onExecute
}) => {
    const reactFlowWrapper = useRef<HTMLDivElement>(null);
    const reactFlowInstance = useReactFlow();

    const {
        nodes,
        edges,
        selectedNodes,
        selectedEdges,
        execution,
        onNodesChange,
        onEdgesChange,
        onConnect,
        setViewport,
        clearSelection,
        resetCanvas,
        exportWorkflow
    } = useCanvasStore();

    // WebSocket integration
    const { isConnected, subscribeToNode, unsubscribeFromNode } = useCanvasWebSocket();

    // Subscribe to all nodes for real-time updates
    useEffect(() => {
        if (isConnected) {
            nodes.forEach(node => {
                subscribeToNode(node.id);
            });
        }

        return () => {
            if (isConnected) {
                nodes.forEach(node => {
                    unsubscribeFromNode(node.id);
                });
            }
        };
    }, [isConnected, nodes, subscribeToNode, unsubscribeFromNode]);

    // Handle viewport changes
    const onMove = useCallback((viewport: any) => {
        setViewport(viewport);
    }, [setViewport]);

    // Handle node selection
    const onSelectionChange = useCallback((params: any) => {
        const { nodes: selectedNodes, edges: selectedEdges } = params;
        useCanvasStore.getState().setSelectedNodes(selectedNodes.map((n: any) => n.id));
        useCanvasStore.getState().setSelectedEdges(selectedEdges.map((e: any) => e.id));
    }, []);

    // Canvas controls
    const handleZoomIn = useCallback(() => {
        reactFlowInstance.zoomIn();
    }, [reactFlowInstance]);

    const handleZoomOut = useCallback(() => {
        reactFlowInstance.zoomOut();
    }, [reactFlowInstance]);

    const handleFitView = useCallback(() => {
        reactFlowInstance.fitView();
    }, [reactFlowInstance]);

    const handleZoomToFit = useCallback(() => {
        reactFlowInstance.fitView({ padding: 0.2 });
    }, [reactFlowInstance]);

    const handleSave = useCallback(() => {
        const workflow = exportWorkflow();
        onSave?.(workflow.nodes, workflow.edges);
    }, [exportWorkflow, onSave]);

    const handleExecute = useCallback(() => {
        const workflow = exportWorkflow();
        onExecute?.(workflow.nodes, workflow.edges);
    }, [exportWorkflow, onExecute]);

    const handleClear = useCallback(() => {
        resetCanvas();
    }, [resetCanvas]);

    // Keyboard shortcuts
    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if (readOnly) return;

            // Delete selected elements
            if (event.key === 'Delete' || event.key === 'Backspace') {
                selectedNodes.forEach(nodeId => {
                    useCanvasStore.getState().deleteNode(nodeId);
                });
                selectedEdges.forEach(edgeId => {
                    useCanvasStore.getState().deleteEdge(edgeId);
                });
            }

            // Clear selection
            if (event.key === 'Escape') {
                clearSelection();
            }

            // Save (Ctrl+S)
            if (event.ctrlKey && event.key === 's') {
                event.preventDefault();
                handleSave();
            }

            // Execute (Ctrl+Enter)
            if (event.ctrlKey && event.key === 'Enter') {
                event.preventDefault();
                handleExecute();
            }
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [selectedNodes, selectedEdges, readOnly, clearSelection, handleSave, handleExecute]);

    const isExecuting = execution?.status === 'running';

    return (
        <div
            className={className}
            style={{
                width: '100%',
                height: typeof height === 'number' ? `${height}px` : height,
                position: 'relative'
            }}
            ref={reactFlowWrapper}
        >
            <ReactFlow
                nodes={nodes}
                edges={edges}
                nodeTypes={nodeTypes}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                onMove={onMove}
                onSelectionChange={onSelectionChange}
                connectionMode={ConnectionMode.Loose}
                selectionMode={SelectionMode.Partial}
                fitView
                attributionPosition="bottom-left"
                proOptions={{ hideAttribution: true }}
                deleteKeyCode={null} // Handle delete with custom logic
                multiSelectionKeyCode="Shift"
                selectionKeyCode="Shift"
                panOnDrag={!readOnly}
                nodesConnectable={!readOnly}
                nodesDraggable={!readOnly}
                elementsSelectable={!readOnly}
            >
                {/* Background */}
                <Background
                    variant="dots"
                    gap={20}
                    size={1}
                    color="#f0f0f0"
                />

                {/* Controls */}
                <Controls
                    position="bottom-left"
                    showZoom={true}
                    showFitView={true}
                    showInteractive={true}
                />

                {/* Mini Map */}
                <MiniMap
                    position="bottom-right"
                    nodeColor={(node) => {
                        switch (node.data?.status) {
                            case 'running': return '#1890ff';
                            case 'completed': return '#52c41a';
                            case 'failed': return '#ff4d4f';
                            default: return '#d9d9d9';
                        }
                    }}
                    maskColor="rgba(0, 0, 0, 0.1)"
                    pannable
                    zoomable
                />

                {/* Top Control Panel */}
                <Panel position="top-left">
                    <Card size="small" style={{ minWidth: '300px' }}>
                        <Space>
                            <Space.Compact>
                                <Tooltip title="Zoom In">
                                    <Button
                                        icon={<ZoomInOutlined />}
                                        size="small"
                                        onClick={handleZoomIn}
                                    />
                                </Tooltip>
                                <Tooltip title="Zoom Out">
                                    <Button
                                        icon={<ZoomOutOutlined />}
                                        size="small"
                                        onClick={handleZoomOut}
                                    />
                                </Tooltip>
                                <Tooltip title="Fit View">
                                    <Button
                                        icon={<FullscreenOutlined />}
                                        size="small"
                                        onClick={handleFitView}
                                    />
                                </Tooltip>
                                <Tooltip title="Center">
                                    <Button
                                        icon={<AimOutlined />}
                                        size="small"
                                        onClick={handleZoomToFit}
                                    />
                                </Tooltip>
                            </Space.Compact>

                            {!readOnly && (
                                <>
                                    <Tooltip title="Save Workflow (Ctrl+S)">
                                        <Button
                                            icon={<SaveOutlined />}
                                            size="small"
                                            type="primary"
                                            onClick={handleSave}
                                        >
                                            Save
                                        </Button>
                                    </Tooltip>

                                    <Tooltip title="Execute Workflow (Ctrl+Enter)">
                                        <Button
                                            icon={isExecuting ? <StopOutlined /> : <PlayCircleOutlined />}
                                            size="small"
                                            type={isExecuting ? "default" : "primary"}
                                            loading={isExecuting}
                                            onClick={handleExecute}
                                            disabled={nodes.length === 0}
                                        >
                                            {isExecuting ? 'Stop' : 'Execute'}
                                        </Button>
                                    </Tooltip>

                                    <Tooltip title="Clear Canvas">
                                        <Button
                                            icon={<ClearOutlined />}
                                            size="small"
                                            danger
                                            onClick={handleClear}
                                            disabled={nodes.length === 0}
                                        >
                                            Clear
                                        </Button>
                                    </Tooltip>
                                </>
                            )}
                        </Space>
                    </Card>
                </Panel>

                {/* Status Panel */}
                <Panel position="top-right">
                    <Card size="small">
                        <Space direction="vertical" size="small">
                            <Text type="secondary" style={{ fontSize: '12px' }}>
                                Nodes: {nodes.length} | Edges: {edges.length}
                            </Text>

                            {selectedNodes.length > 0 && (
                                <Text type="secondary" style={{ fontSize: '12px' }}>
                                    Selected: {selectedNodes.length} node{selectedNodes.length !== 1 ? 's' : ''}
                                </Text>
                            )}

                            {execution && (
                                <Text
                                    type={execution.status === 'failed' ? 'danger' : 'success'}
                                    style={{ fontSize: '12px' }}
                                >
                                    Status: {execution.status}
                                </Text>
                            )}
                        </Space>
                    </Card>
                </Panel>

                {/* Connection Status Panel */}
                <Panel position="top-center">
                    {!isConnected && (
                        <Card size="small" style={{ backgroundColor: '#fff2f0', border: '1px solid #ffccc7' }}>
                            <Space>
                                <Text type="danger" style={{ fontSize: '12px' }}>
                                    WebSocket disconnected - Real-time updates unavailable
                                </Text>
                            </Space>
                        </Card>
                    )}
                </Panel>
            </ReactFlow>
        </div>
    );
};

const CanvasWorkspace: React.FC<CanvasWorkspaceProps> = (props) => {
    return (
        <ReactFlowProvider>
            <CanvasContent {...props} />
        </ReactFlowProvider>
    );
};

export default CanvasWorkspace;
