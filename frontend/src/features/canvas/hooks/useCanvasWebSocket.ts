import { useEffect, useCallback } from 'react';
import { useWebSocket } from '../../../hooks/useWebSocket';
import { useCanvasStore } from '../store/canvasStore';

interface CanvasWebSocketMessage {
    type: string;
    node_id?: string;
    status?: string;
    result?: string;
    error?: string;
    execution_time?: number;
    workflow_id?: string;
}

export const useCanvasWebSocket = () => {
    const { isConnected, lastMessage, sendMessage } = useWebSocket('ws://localhost:8000/ws/canvas');
    const updateNodeStatus = useCanvasStore(state => state.updateNodeStatus);

    // Handle incoming WebSocket messages
    useEffect(() => {
        if (!lastMessage) return;

        try {
            const message: CanvasWebSocketMessage = JSON.parse(lastMessage);

            switch (message.type) {
                case 'node_execution_started':
                    if (message.node_id) {
                        updateNodeStatus(message.node_id, 'running');
                    }
                    break;

                case 'node_execution_completed':
                    if (message.node_id) {
                        updateNodeStatus(
                            message.node_id,
                            'completed',
                            message.result,
                            undefined
                        );
                    }
                    break;

                case 'node_execution_failed':
                    if (message.node_id) {
                        updateNodeStatus(
                            message.node_id,
                            'failed',
                            undefined,
                            message.error
                        );
                    }
                    break;

                case 'node_execution_progress':
                    if (message.node_id) {
                        // Update node with intermediate progress
                        useCanvasStore.getState().updateNode(message.node_id, {
                            status: 'running',
                            result: message.result
                        });
                    }
                    break;

                default:
                    console.log('Unknown canvas WebSocket message type:', message.type);
            }
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    }, [lastMessage, updateNodeStatus]);

    // Subscribe to node execution
    const subscribeToNode = useCallback((nodeId: string) => {
        if (isConnected) {
            sendMessage(JSON.stringify({
                type: 'subscribe_node',
                node_id: nodeId
            }));
        }
    }, [isConnected, sendMessage]);

    // Unsubscribe from node execution
    const unsubscribeFromNode = useCallback((nodeId: string) => {
        if (isConnected) {
            sendMessage(JSON.stringify({
                type: 'unsubscribe_node',
                node_id: nodeId
            }));
        }
    }, [isConnected, sendMessage]);

    return {
        isConnected,
        subscribeToNode,
        unsubscribeFromNode
    };
};
