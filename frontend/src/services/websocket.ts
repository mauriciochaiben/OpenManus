import { EventBus } from "@/utils/eventBus";

export interface WebSocketOptions {
  url: string;
  maxReconnectAttempts?: number;
  reconnectInterval?: number;
  heartbeatInterval?: number;
  debug?: boolean;
}

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp?: number;
}

export type ConnectionState =
  | "connecting"
  | "connected"
  | "disconnected"
  | "reconnecting"
  | "failed";

export class RobustWebSocket {
  private ws: WebSocket | null = null;
  private url: string;
  private maxReconnectAttempts: number;
  private reconnectInterval: number;
  private heartbeatInterval: number;
  private debug: boolean;

  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private isManualClose = false;

  private eventBus = EventBus.getInstance();
  private connectionState: ConnectionState = "disconnected";

  private messageQueue: WebSocketMessage[] = [];
  private isOnline = navigator.onLine;

  constructor(options: WebSocketOptions) {
    this.url = options.url;
    this.maxReconnectAttempts = options.maxReconnectAttempts ?? 5;
    this.reconnectInterval = options.reconnectInterval ?? 3000;
    this.heartbeatInterval = options.heartbeatInterval ?? 30000;
    this.debug = options.debug ?? false;

    this.setupNetworkListeners();
  }

  private setupNetworkListeners(): void {
    window.addEventListener("online", () => {
      this.isOnline = true;
      this.log("Network back online, attempting reconnection...");
      if (this.connectionState === "disconnected") {
        this.connect();
      }
    });

    window.addEventListener("offline", () => {
      this.isOnline = false;
      this.log("Network offline detected");
      this.setConnectionState("disconnected");
    });
  }

  private log(message: string, ...args: any[]): void {
    if (this.debug) {
      console.log(`[RobustWebSocket] ${message}`, ...args);
    }
  }

  private setConnectionState(state: ConnectionState): void {
    if (this.connectionState !== state) {
      this.connectionState = state;
      this.eventBus.emit("websocket:connectionStateChanged", { state });
      this.log(`Connection state changed to: ${state}`);
    }
  }

  public getConnectionState(): ConnectionState {
    return this.connectionState;
  }

  public isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  public connect(): void {
    if (!this.isOnline) {
      this.log("Cannot connect: network is offline");
      return;
    }

    if (
      this.ws?.readyState === WebSocket.CONNECTING ||
      this.ws?.readyState === WebSocket.OPEN
    ) {
      this.log("WebSocket is already connecting or connected");
      return;
    }

    this.setConnectionState("connecting");
    this.isManualClose = false;

    try {
      this.ws = new WebSocket(this.url);
      this.setupWebSocketEventHandlers();
    } catch (error) {
      this.log("Failed to create WebSocket connection:", error);
      this.handleConnectionError();
    }
  }

  private setupWebSocketEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      this.log("WebSocket connected successfully");
      this.setConnectionState("connected");
      this.reconnectAttempts = 0;
      this.startHeartbeat();
      this.processMessageQueue();
      this.eventBus.emit("websocket:connected", {});
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        this.log("Failed to parse WebSocket message:", error);
      }
    };

    this.ws.onclose = (event) => {
      this.log("WebSocket connection closed:", event.code, event.reason);
      this.stopHeartbeat();

      if (!this.isManualClose && this.isOnline) {
        this.setConnectionState("reconnecting");
        this.scheduleReconnect();
      } else {
        this.setConnectionState("disconnected");
      }

      this.eventBus.emit("websocket:disconnected", {
        code: event.code,
        reason: event.reason,
      });
    };

    this.ws.onerror = (error) => {
      this.log("WebSocket error:", error);
      this.eventBus.emit("websocket:error", { error });
    };
  }

  private handleMessage(message: WebSocketMessage): void {
    this.log("Received message:", message);

    // Handle heartbeat responses
    if (message.type === "pong") {
      return;
    }

    // Emit message-specific events
    this.eventBus.emit(`websocket:${message.type}`, message.data);

    // Emit general message event
    this.eventBus.emit("websocket:message", message);
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected()) {
        this.send({ type: "ping", data: {} });
      }
    }, this.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private handleConnectionError(): void {
    this.setConnectionState("reconnecting");
    this.scheduleReconnect();
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.log("Max reconnection attempts reached");
      this.setConnectionState("failed");
      this.eventBus.emit("websocket:maxReconnectAttemptsReached", {
        attempts: this.reconnectAttempts,
      });
      return;
    }

    const delay = Math.min(
      this.reconnectInterval * Math.pow(2, this.reconnectAttempts),
      30000, // Max delay of 30 seconds
    );

    this.reconnectAttempts++;
    this.log(
      `Scheduling reconnection attempt ${this.reconnectAttempts} in ${delay}ms`,
    );

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, delay);
  }

  private processMessageQueue(): void {
    while (this.messageQueue.length > 0 && this.isConnected()) {
      const message = this.messageQueue.shift();
      if (message) {
        this.sendImmediate(message);
      }
    }
  }

  public send(message: Omit<WebSocketMessage, "timestamp">): void {
    const fullMessage: WebSocketMessage = {
      ...message,
      timestamp: Date.now(),
    };

    if (this.isConnected()) {
      this.sendImmediate(fullMessage);
    } else {
      this.log("WebSocket not connected, queueing message:", fullMessage);
      this.messageQueue.push(fullMessage);
    }
  }

  private sendImmediate(message: WebSocketMessage): void {
    if (this.ws && this.isConnected()) {
      try {
        this.ws.send(JSON.stringify(message));
        this.log("Sent message:", message);
      } catch (error) {
        this.log("Failed to send message:", error);
        this.messageQueue.unshift(message); // Re-queue the message
      }
    }
  }

  public disconnect(): void {
    this.log("Manually disconnecting WebSocket");
    this.isManualClose = true;

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    this.stopHeartbeat();

    if (this.ws) {
      this.ws.close(1000, "Manual disconnect");
      this.ws = null;
    }

    this.setConnectionState("disconnected");
    this.reconnectAttempts = 0;
  }

  public reconnect(): void {
    this.log("Manual reconnection requested");
    this.disconnect();
    setTimeout(() => this.connect(), 100);
  }

  public getReconnectAttempts(): number {
    return this.reconnectAttempts;
  }

  public getQueuedMessageCount(): number {
    return this.messageQueue.length;
  }

  public clearMessageQueue(): void {
    this.messageQueue = [];
    this.log("Message queue cleared");
  }
}

// WebSocket Manager for centralized WebSocket handling
export class WebSocketManager {
  private static instance: WebSocketManager;
  private robustWS: RobustWebSocket | null = null;
  private eventBus = EventBus.getInstance();

  private constructor() {}

  public static getInstance(): WebSocketManager {
    if (!WebSocketManager.instance) {
      WebSocketManager.instance = new WebSocketManager();
    }
    return WebSocketManager.instance;
  }

  public initialize(url: string, options?: Partial<WebSocketOptions>): void {
    if (this.robustWS) {
      this.robustWS.disconnect();
    }

    this.robustWS = new RobustWebSocket({
      url,
      maxReconnectAttempts: 10,
      reconnectInterval: 2000,
      heartbeatInterval: 30000,
      debug: process.env.NODE_ENV === "development",
      ...options,
    });

    this.setupEventForwarding();
  }

  private setupEventForwarding(): void {
    if (!this.robustWS) return;

    // Forward WebSocket events to application events
    this.eventBus.on("websocket:message", (message: WebSocketMessage) => {
      switch (message.type) {
        case "task_progress":
          this.eventBus.emit("task:progressUpdated", message.data);
          break;
        case "task_completed":
          this.eventBus.emit("task:completed", message.data);
          break;
        case "task_failed":
          this.eventBus.emit("task:failed", message.data);
          break;
        case "notification":
          this.eventBus.emit("notification:received", message.data);
          break;
        case "system_status":
          this.eventBus.emit("system:statusChanged", message.data);
          break;
        default:
          // Forward unknown message types as-is
          this.eventBus.emit(`websocket:${message.type}`, message.data);
      }
    });
  }

  public connect(): void {
    this.robustWS?.connect();
  }

  public disconnect(): void {
    this.robustWS?.disconnect();
  }

  public send(type: string, data: any): void {
    this.robustWS?.send({ type, data });
  }

  public getConnectionState(): ConnectionState {
    return this.robustWS?.getConnectionState() ?? "disconnected";
  }

  public isConnected(): boolean {
    return this.robustWS?.isConnected() ?? false;
  }

  public getReconnectAttempts(): number {
    return this.robustWS?.getReconnectAttempts() ?? 0;
  }
}

// Export singleton instance
export const webSocketManager = WebSocketManager.getInstance();

// Default export for the class
export default RobustWebSocket;
