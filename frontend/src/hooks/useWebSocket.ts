// Hook for WebSocket integration with React and Zustand
import { useEffect, useCallback, useState, useRef } from "react";
import { webSocketManager, ConnectionState } from "../services/websocket";
import { eventBus } from "../utils/eventBus";
import { useTaskStore } from "../features/tasks/hooks/useTaskStore";

export interface UseWebSocketOptions {
  autoConnect?: boolean;
  onConnect?: () => void;
  onDisconnect?: (reason?: string) => void;
  onError?: (error: any) => void;
  onMessage?: (message: any) => void;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    autoConnect = true,
    onConnect,
    onDisconnect,
    onError,
    onMessage,
  } = options;
  const [connectionState, setConnectionState] =
    useState<ConnectionState>("disconnected");
  const [isConnected, setIsConnected] = useState(false);
  const taskStore = useTaskStore();

  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  // Connection management
  const connect = useCallback((): void => {
    try {
      if (ws.current?.readyState === WebSocket.OPEN) {
        return;
      }

      ws.current = new WebSocket("ws://localhost:8080"); // Replace with your WebSocket URL

      ws.current.onopen = () => {
        setIsConnected(true);
        setConnectionState("connected");
        reconnectAttempts.current = 0;
        onConnect?.();
        console.log("WebSocket connected");
      };

      ws.current.onmessage = (event) => {
        const message = JSON.parse(event.data);
        console.log("Message received:", message);
        onMessage?.(message);
      };

      ws.current.onclose = (event) => {
        setIsConnected(false);
        setConnectionState("disconnected");
        onDisconnect?.(event.reason);
        console.log("WebSocket disconnected:", event.code, event.reason);

        // Attempt to reconnect if not a normal closure
        if (
          event.code !== 1000 &&
          reconnectAttempts.current < maxReconnectAttempts
        ) {
          const delay = Math.pow(2, reconnectAttempts.current) * 1000; // Exponential backoff
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttempts.current++;
            connect();
          }, delay);
        }
      };

      ws.current.onerror = (error) => {
        console.error("WebSocket error:", error);
        setConnectionState("disconnected");
        setIsConnected(false);
        onError?.(error);
      };
    } catch (error) {
      console.error("Failed to create WebSocket connection:", error);
      setConnectionState("disconnected");
      setIsConnected(false);
      onError?.(error);
    }
  }, [onConnect, onDisconnect, onError, onMessage]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (ws.current) {
      ws.current.close(1000, "Normal closure");
      ws.current = null;
    }

    setIsConnected(false);
    setConnectionState("disconnected");
  }, []);

  const sendMessage = useCallback((type: string, data: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      const message = JSON.stringify({ type, data });
      ws.current.send(message);
    } else {
      console.warn("WebSocket is not connected. Message not sent:", {
        type,
        data,
      });
    }
  }, []);

  // Setup event listeners
  useEffect(() => {
    // Task-related events
    const handleTaskCreated = (task: any) => {
      console.log("Task created via WebSocket:", task);
      taskStore.fetchTasks(); // Refresh tasks list
    };

    const handleTaskUpdated = (task: any) => {
      console.log("Task updated via WebSocket:", task);
      taskStore.fetchTasks(); // Refresh tasks to get latest state
    };

    const handleTaskCompleted = (task: any) => {
      console.log("Task completed via WebSocket:", task);
      taskStore.fetchTasks();

      // Show notification
      eventBus.emit("notification:received", {
        id: `task-completed-${task.id}`,
        type: "success" as const,
        title: "Task Completed",
        message: `Task "${task.title}" has been completed successfully`,
        duration: 5000,
      });
    };

    const handleTaskFailed = (data: { id: string; error: string }) => {
      console.log("Task failed via WebSocket:", data);
      taskStore.fetchTasks();

      // Show error notification
      eventBus.emit("notification:received", {
        id: `task-failed-${data.id}`,
        type: "error" as const,
        title: "Task Failed",
        message: `Task failed: ${data.error}`,
        duration: 10000,
      });
    };

    const handleTaskProgress = (data: {
      id: string;
      progress: number;
      status: string;
    }) => {
      console.log("Task progress via WebSocket:", data);
      // Update task progress in store
      const currentTask = taskStore.currentTask;
      if (currentTask && currentTask.id === data.id) {
        // Update current task progress if it matches
        const validStatus = [
          "pending",
          "running",
          "completed",
          "error",
        ].includes(data.status)
          ? (data.status as "pending" | "running" | "completed" | "error")
          : currentTask.status;

        const updatedTask = {
          ...currentTask,
          status: validStatus,
        };
        taskStore.setCurrentTask(updatedTask);
      }
    };

    // Register event listeners
    const unsubscribeFunctions = [
      eventBus.on("task:created", handleTaskCreated),
      eventBus.on("task:updated", handleTaskUpdated),
      eventBus.on("task:completed", handleTaskCompleted),
      eventBus.on("task:failed", handleTaskFailed),
      eventBus.on("task:progressUpdated", handleTaskProgress),
    ];

    // Auto-connect if enabled
    if (autoConnect) {
      connect();
    }

    // Cleanup function
    return () => {
      unsubscribeFunctions.forEach((unsubscribe) => unsubscribe());
      disconnect();
    };
  }, [autoConnect, connect, disconnect, taskStore]);

  return {
    connectionState,
    isConnected,
    connect,
    disconnect,
    sendMessage,
    webSocketManager,
  };
}

// Hook for notifications
export function useNotifications() {
  const [notifications, setNotifications] = useState<any[]>([]);

  useEffect(() => {
    const handleNotificationReceived = (notification: any) => {
      setNotifications((prev) => [notification, ...prev]);

      // Auto-dismiss notifications with duration
      if (notification.duration) {
        setTimeout(() => {
          setNotifications((prev) =>
            prev.filter((n) => n.id !== notification.id),
          );
        }, notification.duration);
      }
    };

    const handleNotificationDismissed = (data: { id: string }) => {
      setNotifications((prev) => prev.filter((n) => n.id !== data.id));
    };

    const handleNotificationCleared = () => {
      setNotifications([]);
    };

    const unsubscribeFunctions = [
      eventBus.on("notification:received", handleNotificationReceived),
      eventBus.on("notification:dismissed", handleNotificationDismissed),
      eventBus.on("notification:cleared", handleNotificationCleared),
    ];

    return () => {
      unsubscribeFunctions.forEach((unsubscribe) => unsubscribe());
    };
  }, []);

  const dismissNotification = useCallback((notificationId: string) => {
    eventBus.emit("notification:dismissed", { id: notificationId });
  }, []);

  const clearAllNotifications = useCallback(() => {
    eventBus.emit("notification:cleared", {});
  }, []);

  return {
    notifications,
    dismissNotification,
    clearAllNotifications,
  };
}
