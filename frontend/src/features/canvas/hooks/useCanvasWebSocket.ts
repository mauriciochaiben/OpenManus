import { useCallback } from 'react';
import { useWebSocket } from '../../../hooks/useWebSocket';

export const useCanvasWebSocket = () => {
  const { isConnected, sendMessage } = useWebSocket({
    autoConnect: true,
  });

  // Subscribe to node execution updates
  const subscribeToNode = useCallback(
    (nodeId: string) => {
      if (isConnected) {
        sendMessage('subscribe_node', { node_id: nodeId });
      }
    },
    [isConnected, sendMessage]
  );

  // Unsubscribe from node execution
  const unsubscribeFromNode = useCallback(
    (nodeId: string) => {
      if (isConnected) {
        sendMessage('unsubscribe_node', { node_id: nodeId });
      }
    },
    [isConnected, sendMessage]
  );

  return {
    isConnected,
    subscribeToNode,
    unsubscribeFromNode,
  };
};
