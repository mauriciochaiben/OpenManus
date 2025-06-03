export type EventHandler<T = any> = (data: T) => void;

export interface AppEvent {
  // WebSocket Events
  'websocket:connected': {};
  'websocket:disconnected': { code: number; reason: string };
  'websocket:error': { error: Event };
  'websocket:message': { type: string; data: any };
  'websocket:connectionStateChanged': { state: string };
  'websocket:maxReconnectAttemptsReached': { attempts: number };

  // Task Events
  'task:created': { id: string; title: string };
  'task:updated': { id: string; changes: any };
  'task:deleted': { id: string };
  'task:progressUpdated': { id: string; progress: number; status: string };
  'task:completed': { id: string; result: any };
  'task:failed': { id: string; error: string };
  'task:started': { id: string };
  'task:paused': { id: string };
  'task:resumed': { id: string };

  // Notification Events
  'notification:received': {
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    title: string;
    message: string;
    duration?: number;
  };
  'notification:dismissed': { id: string };
  'notification:cleared': {};

  // System Events
  'system:statusChanged': { status: string; details?: any };
  'system:error': { error: string; details?: any };
  'system:maintenance': { message: string; startTime?: Date; endTime?: Date };

  // User Events
  'user:authenticated': { user: any };
  'user:loggedOut': {};
  'user:profileUpdated': { user: any };

  // UI Events
  'ui:themeChanged': { theme: 'light' | 'dark' };
  'ui:sidebarToggled': { isOpen: boolean };
  'ui:modalOpened': { modalId: string };
  'ui:modalClosed': { modalId: string };

  // Dynamic WebSocket events (for any websocket:* event)
  [key: `websocket:${string}`]: any;
}

export class EventBus {
  private static instance: EventBus;
  private listeners: Map<string, Set<EventHandler>> = new Map();
  private debug = false;

  private constructor() {
    // Enable debug mode in development
    this.debug = process.env.NODE_ENV === 'development';
  }

  public static getInstance(): EventBus {
    if (!EventBus.instance) {
      EventBus.instance = new EventBus();
    }
    return EventBus.instance;
  }

  private log(message: string, ...args: any[]): void {
    if (this.debug) {
      console.log(`[EventBus] ${message}`, ...args);
    }
  }

  public on<K extends keyof AppEvent>(
    event: K,
    handler: EventHandler<AppEvent[K]>
  ): () => void;
  public on(event: string, handler: EventHandler<any>): () => void;
  public on(event: string, handler: EventHandler<any>): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }

    const handlers = this.listeners.get(event)!;
    handlers.add(handler);

    this.log(`Registered handler for event: ${event}`);

    // Return unsubscribe function
    return () => {
      handlers.delete(handler);
      if (handlers.size === 0) {
        this.listeners.delete(event);
      }
      this.log(`Unregistered handler for event: ${event}`);
    };
  }

  public once<K extends keyof AppEvent>(
    event: K,
    handler: EventHandler<AppEvent[K]>
  ): () => void;
  public once(event: string, handler: EventHandler<any>): () => void;
  public once(event: string, handler: EventHandler<any>): () => void {
    const unsubscribe = this.on(event, (data) => {
      handler(data);
      unsubscribe();
    });
    return unsubscribe;
  }

  public emit<K extends keyof AppEvent>(event: K, data: AppEvent[K]): void;
  public emit(event: string, data: any): void;
  public emit(event: string, data: any): void {
    const handlers = this.listeners.get(event);

    if (!handlers || handlers.size === 0) {
      this.log(`No handlers registered for event: ${event}`);
      return;
    }

    this.log(`Emitting event: ${event}`, data);

    // Create a copy of handlers to avoid issues if handlers are modified during emission
    const handlersCopy = Array.from(handlers);

    handlersCopy.forEach((handler) => {
      try {
        handler(data);
      } catch (error) {
        console.error(`Error in event handler for ${event}:`, error);
      }
    });
  }

  public off<K extends keyof AppEvent>(
    event: K,
    handler?: EventHandler<AppEvent[K]>
  ): void;
  public off(event: string, handler?: EventHandler<any>): void;
  public off(event: string, handler?: EventHandler<any>): void {
    if (!handler) {
      // Remove all handlers for the event
      this.listeners.delete(event);
      this.log(`Removed all handlers for event: ${event}`);
      return;
    }

    const handlers = this.listeners.get(event);
    if (handlers) {
      handlers.delete(handler);
      if (handlers.size === 0) {
        this.listeners.delete(event);
      }
      this.log(`Removed handler for event: ${event}`);
    }
  }

  public removeAllListeners(): void {
    this.listeners.clear();
    this.log('Removed all event listeners');
  }

  public getListenerCount(event: string): number {
    const handlers = this.listeners.get(event);
    return handlers ? handlers.size : 0;
  }

  public getEvents(): string[] {
    return Array.from(this.listeners.keys());
  }

  public hasListeners(event: string): boolean {
    return this.getListenerCount(event) > 0;
  }

  // Utility method to create a Promise that resolves when an event is emitted
  public waitFor<K extends keyof AppEvent>(
    event: K,
    timeout?: number
  ): Promise<AppEvent[K]>;
  public waitFor(event: string, timeout?: number): Promise<any>;
  public waitFor(event: string, timeout?: number): Promise<any> {
    return new Promise((resolve, reject) => {
      let timeoutId: NodeJS.Timeout | null = null;

      const unsubscribe = this.once(event, (data) => {
        if (timeoutId) {
          clearTimeout(timeoutId);
        }
        resolve(data);
      });

      if (timeout) {
        timeoutId = setTimeout(() => {
          unsubscribe();
          reject(new Error(`Timeout waiting for event: ${event}`));
        }, timeout);
      }
    });
  }

  // Enable/disable debug logging
  public setDebug(enabled: boolean): void {
    this.debug = enabled;
  }
}

// Export singleton instance
export const eventBus = EventBus.getInstance();

// Default export
export default EventBus;
