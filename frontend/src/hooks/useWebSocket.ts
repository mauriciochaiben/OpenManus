// Hook for WebSocket integration with React and Zustand
import { useEffect, useCallback, useState } from 'react';
import { webSocketManager, ConnectionState } from '../services/websocket';
import { eventBus } from '../utils/eventBus';
import { useTaskStore } from '../features/tasks/hooks/useTaskStore';

export interface UseWebSocketOptions {
    autoConnect?: boolean;
    onConnect?: () => void;
    onDisconnect?: (reason?: string) => void;
    onError?: (error: any) => void;
    onMessage?: (message: any) => void;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
    const { autoConnect = true, onConnect, onDisconnect, onError, onMessage } = options;
    const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
    const [isConnected, setIsConnected] = useState(false);
    const taskStore = useTaskStore();

    // Connection management
    const connect = useCallback(() => {
        webSocketManager.connect();
    }, []);

    const disconnect = useCallback(() => {
        webSocketManager.disconnect();
    }, []);

    const sendMessage = useCallback((type: string, data: any) => {
        webSocketManager.send(type, data);
    }, []);

    // Setup event listeners
    useEffect(() => {
        // WebSocket connection events
        const handleConnected = () => {
            setIsConnected(true);
            setConnectionState('connected');
            onConnect?.();
        };

        const handleDisconnected = (data: { code: number; reason: string }) => {
            setIsConnected(false);
            setConnectionState('disconnected');
            onDisconnect?.(data.reason);
        };

        const handleError = (data: { error: any }) => {
            onError?.(data.error);
        };

        const handleStateChange = (data: { state: ConnectionState }) => {
            setConnectionState(data.state);
            setIsConnected(data.state === 'connected');
        };

        // Task-related events
        const handleTaskCreated = (task: any) => {
            console.log('Task created via WebSocket:', task);
            taskStore.fetchTasks(); // Refresh tasks list
        };

        const handleTaskUpdated = (task: any) => {
            console.log('Task updated via WebSocket:', task);
            taskStore.fetchTasks(); // Refresh tasks to get latest state
        };

        const handleTaskCompleted = (task: any) => {
            console.log('Task completed via WebSocket:', task);
            taskStore.fetchTasks();

            // Show notification
            eventBus.emit('notification:received', {
                id: `task-completed-${task.id}`,
                type: 'success' as const,
                title: 'Task Completed',
                message: `Task "${task.title}" has been completed successfully`,
                duration: 5000
            });
        };

        const handleTaskFailed = (data: { id: string; error: string }) => {
            console.log('Task failed via WebSocket:', data);
            taskStore.fetchTasks();

            // Show error notification
            eventBus.emit('notification:received', {
                id: `task-failed-${data.id}`,
                type: 'error' as const,
                title: 'Task Failed',
                message: `Task failed: ${data.error}`,
                duration: 10000
            });
        };

        const handleTaskProgress = (data: { id: string; progress: number; status: string }) => {
            console.log('Task progress via WebSocket:', data);
            // Update task progress in store
            const currentTask = taskStore.currentTask;
            if (currentTask && currentTask.id === data.id) {
                // Update current task progress if it matches
                const validStatus = ['pending', 'running', 'completed', 'error'].includes(data.status)
                    ? data.status as 'pending' | 'running' | 'completed' | 'error'
                    : currentTask.status;

                const updatedTask = {
                    ...currentTask,
                    status: validStatus,
                };
                taskStore.setCurrentTask(updatedTask);
            }
        };

        const handleGenericMessage = (message: any) => {
            console.log('Generic WebSocket message:', message);
            onMessage?.(message);
        };

        // Register event listeners
        const unsubscribeFunctions = [
            eventBus.on('websocket:connected', handleConnected),
            eventBus.on('websocket:disconnected', handleDisconnected),
            eventBus.on('websocket:error', handleError),
            eventBus.on('websocket:connectionStateChanged', handleStateChange),

            eventBus.on('task:created', handleTaskCreated),
            eventBus.on('task:updated', handleTaskUpdated),
            eventBus.on('task:completed', handleTaskCompleted),
            eventBus.on('task:failed', handleTaskFailed),
            eventBus.on('task:progressUpdated', handleTaskProgress),

            // Generic message handler
            eventBus.on('websocket:message', handleGenericMessage)
        ];

        // Auto-connect if enabled
        if (autoConnect) {
            connect();
        }

        // Cleanup function
        return () => {
            unsubscribeFunctions.forEach(unsubscribe => unsubscribe());
        };
    }, [autoConnect, connect, onConnect, onDisconnect, onError, onMessage, taskStore]);

    return {
        connectionState,
        isConnected,
        connect,
        disconnect,
        sendMessage,
        webSocketManager
    };
}

// Hook for notifications
export function useNotifications() {
    const [notifications, setNotifications] = useState<any[]>([]);

    useEffect(() => {
        const handleNotificationReceived = (notification: any) => {
            setNotifications(prev => [notification, ...prev]);

            // Auto-dismiss notifications with duration
            if (notification.duration) {
                setTimeout(() => {
                    setNotifications(prev => prev.filter(n => n.id !== notification.id));
                }, notification.duration);
            }
        };

        const handleNotificationDismissed = (data: { id: string }) => {
            setNotifications(prev => prev.filter(n => n.id !== data.id));
        };

        const handleNotificationCleared = () => {
            setNotifications([]);
        };

        const unsubscribeFunctions = [
            eventBus.on('notification:received', handleNotificationReceived),
            eventBus.on('notification:dismissed', handleNotificationDismissed),
            eventBus.on('notification:cleared', handleNotificationCleared)
        ];

        return () => {
            unsubscribeFunctions.forEach(unsubscribe => unsubscribe());
        };
    }, []);

    const dismissNotification = useCallback((notificationId: string) => {
        eventBus.emit('notification:dismissed', { id: notificationId });
    }, []);

    const clearAllNotifications = useCallback(() => {
        eventBus.emit('notification:cleared', {});
    }, []);

    return {
        notifications,
        dismissNotification,
        clearAllNotifications
    };
}
