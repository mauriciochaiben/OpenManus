// WebSocket service with automatic reconnection and event bus

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp?: string;
  id?: string;
}

export type WebSocketConnectionState =
  | "connecting"
  | "connected"
  | "disconnected"
  | "reconnecting"
  | "failed";

// Simple Event Emitter for browser compatibility
class SimpleEventEmitter {
  private events: { [key: string]: ((...args: any[]) => void)[] } = {};

  on(event: string, listener: (...args: any[]) => void): void {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(listener);
  }

  emit(event: string, ...args: any[]): void {
    if (this.events[event]) {
      this.events[event].forEach((listener) => listener(...args));
    }
  }

  off(event: string, listener: (...args: any[]) => void): void {
    if (this.events[event]) {
      this.events[event] = this.events[event].filter((l) => l !== listener);
    }
  }
}

export class RobustWebSocket extends SimpleEventEmitter {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectInterval = 5000;
  private heartbeatInterval = 30000;
  private heartbeatTimer?: number;
  private reconnectTimer?: number;
  private connectionState: WebSocketConnectionState = "disconnected";
  private isManuallyDisconnected = false;

  constructor(url: string) {
    super();
    this.url = url;
  }

  connect(): void {
    if (
      this.ws?.readyState === WebSocket.CONNECTING ||
      this.ws?.readyState === WebSocket.OPEN
    ) {
      return;
    }

    this.isManuallyDisconnected = false;
    this.setConnectionState("connecting");

    try {
      this.ws = new WebSocket(this.url);
      this.setupEventListeners();
    } catch (error) {
      console.error("Failed to create WebSocket connection:", error);
      this.handleConnectionError();
    }
  }

  disconnect(): void {
    this.isManuallyDisconnected = true;
    this.cleanup();
    if (this.ws) {
      this.ws.close(1000, "Manual disconnect");
    }
    this.setConnectionState("disconnected");
  }

  send(message: WebSocketMessage): boolean {
    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        const messageWithTimestamp = {
          ...message,
          timestamp: new Date().toISOString(),
          id: this.generateMessageId(),
        };
        this.ws.send(JSON.stringify(messageWithTimestamp));
        this.emit("messageSent", messageWithTimestamp);
        return true;
      } catch (error) {
        console.error("Failed to send message:", error);
        this.emit("sendError", error);
        return false;
      }
    }
    return false;
  }

  getConnectionState(): WebSocketConnectionState {
    return this.connectionState;
  }

  isConnected(): boolean {
    return this.connectionState === "connected";
  }

  private setupEventListeners(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log("WebSocket connected");
      this.reconnectAttempts = 0;
      this.setConnectionState("connected");
      this.startHeartbeat();
      this.emit("connected");
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.emit("message", message);

        // Handle heartbeat response
        if (message.type === "pong") {
          this.emit("heartbeat");
        }
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
        this.emit("parseError", error);
      }
    };

    this.ws.onclose = (event) => {
      console.log("WebSocket closed:", event.code, event.reason);
      this.cleanup();
      this.setConnectionState("disconnected");
      this.emit("disconnected", { code: event.code, reason: event.reason });

      if (!this.isManuallyDisconnected && event.code !== 1000) {
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      this.emit("error", error);
      this.handleConnectionError();
    };
  }

  private setConnectionState(state: WebSocketConnectionState): void {
    if (this.connectionState !== state) {
      const previousState = this.connectionState;
      this.connectionState = state;
      this.emit("stateChange", { from: previousState, to: state });
    }
  }

  private startHeartbeat(): void {
    this.heartbeatTimer = window.setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({ type: "ping", data: {} });
      }
    }, this.heartbeatInterval);
  }

  private cleanup(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = undefined;
    }
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = undefined;
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error("Max reconnection attempts reached");
      this.setConnectionState("failed");
      this.emit("maxReconnectAttemptsReached");
      return;
    }

    this.reconnectAttempts++;
    this.setConnectionState("reconnecting");

    const delay =
      this.reconnectInterval * Math.pow(1.5, this.reconnectAttempts - 1);
    console.log(
      `Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`,
    );

    this.reconnectTimer = window.setTimeout(() => {
      this.emit("reconnecting", this.reconnectAttempts);
      this.connect();
    }, delay);
  }

  private handleConnectionError(): void {
    if (!this.isManuallyDisconnected) {
      this.scheduleReconnect();
    }
  }

  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Event Bus for application-wide communication
export class EventBus extends SimpleEventEmitter {
  private static instance: EventBus;

  static getInstance(): EventBus {
    if (!EventBus.instance) {
      EventBus.instance = new EventBus();
    }
    return EventBus.instance;
  }

  // Task-related events
  emitTaskCreated(task: any): void {
    this.emit("task:created", task);
  }

  emitTaskUpdated(task: any): void {
    this.emit("task:updated", task);
  }

  emitTaskCompleted(task: any): void {
    this.emit("task:completed", task);
  }

  emitTaskFailed(task: any, error: any): void {
    this.emit("task:failed", { task, error });
  }

  emitTaskProgress(taskId: string, progress: number): void {
    this.emit("task:progress", { taskId, progress });
  }

  // WebSocket-related events
  emitWebSocketConnected(): void {
    this.emit("websocket:connected");
  }

  emitWebSocketDisconnected(reason?: string): void {
    this.emit("websocket:disconnected", reason);
  }

  emitWebSocketError(error: any): void {
    this.emit("websocket:error", error);
  }

  // Notification events
  emitNotification(notification: any): void {
    this.emit("notification:show", notification);
  }

  emitNotificationClear(notificationId: string): void {
    this.emit("notification:clear", notificationId);
  }
}

// WebSocket manager that integrates with event bus
export class WebSocketManager {
  private ws: RobustWebSocket;
  private eventBus: EventBus;

  constructor(url: string) {
    this.eventBus = EventBus.getInstance();
    this.ws = new RobustWebSocket(url);
    this.setupEventHandlers();
  }

  connect(): void {
    this.ws.connect();
  }

  disconnect(): void {
    this.ws.disconnect();
  }

  send(message: WebSocketMessage): boolean {
    return this.ws.send(message);
  }

  isConnected(): boolean {
    return this.ws.isConnected();
  }

  getConnectionState(): WebSocketConnectionState {
    return this.ws.getConnectionState();
  }

  private setupEventHandlers(): void {
    // WebSocket events
    this.ws.on("connected", () => {
      console.log("WebSocket manager: Connected");
      this.eventBus.emitWebSocketConnected();
    });

    this.ws.on("disconnected", (event: any) => {
      console.log("WebSocket manager: Disconnected");
      this.eventBus.emitWebSocketDisconnected(event.reason);
    });

    this.ws.on("error", (error: any) => {
      console.error("WebSocket manager: Error", error);
      this.eventBus.emitWebSocketError(error);
    });

    this.ws.on("message", (message: WebSocketMessage) => {
      this.handleIncomingMessage(message);
    });

    this.ws.on("stateChange", (change: any) => {
      console.log(`WebSocket state changed: ${change.from} -> ${change.to}`);
      this.eventBus.emit("websocket:stateChange", change);
    });
  }

  private handleIncomingMessage(message: WebSocketMessage): void {
    console.log("Received WebSocket message:", message);

    switch (message.type) {
      case "task_created":
        this.eventBus.emitTaskCreated(message.data);
        break;
      case "task_updated":
        this.eventBus.emitTaskUpdated(message.data);
        break;
      case "task_completed":
        this.eventBus.emitTaskCompleted(message.data);
        break;
      case "task_failed":
        this.eventBus.emitTaskFailed(message.data.task, message.data.error);
        break;
      case "task_progress":
        this.eventBus.emitTaskProgress(
          message.data.taskId,
          message.data.progress,
        );
        break;
      case "notification":
        this.eventBus.emitNotification(message.data);
        break;
      default:
        // Emit generic message event
        this.eventBus.emit(`websocket:${message.type}`, message.data);
    }
  }
}

// Singleton instance for the application
// Generate a unique client ID for this session
const clientId = `frontend-alt-${Date.now()}-${Math.random()
  .toString(36)
  .substr(2, 9)}`;
export const webSocketManager = new WebSocketManager(
  `ws://localhost:8000/api/v2/chat/ws/${clientId}`,
);
export const eventBus = EventBus.getInstance();
