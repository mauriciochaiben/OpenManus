import { io, Socket } from 'socket.io-client';
import type { WebSocketMessage, Task, TaskStep, LogEntry } from '../types';

class WebSocketService {
    private socket: Socket | null = null;
    private callbacks: Map<string, (data: any) => void> = new Map();
    private isConnected = false;

    constructor() {
        this.connect();
    }

    private connect() {
        const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'http://localhost:8000';

        console.log('🔌 Connecting to WebSocket:', WS_BASE_URL);

        this.socket = io(WS_BASE_URL, {
            transports: ['websocket', 'polling'],
            autoConnect: true,
            reconnection: true,
            reconnectionAttempts: 5,
            reconnectionDelay: 1000,
        });

        this.socket.on('connect', () => {
            console.log('✅ WebSocket connected');
            this.isConnected = true;
        });

        this.socket.on('disconnect', (reason) => {
            console.log('❌ WebSocket disconnected:', reason);
            this.isConnected = false;
        });

        this.socket.on('reconnect', (attemptNumber) => {
            console.log('🔄 WebSocket reconnected after', attemptNumber, 'attempts');
            this.isConnected = true;
        });

        this.socket.on('reconnect_error', (error) => {
            console.error('🚨 WebSocket reconnection error:', error);
        });

        // Handle different message types
        this.socket.on('task_update', (data: { taskId: string; task: Task }) => {
            console.log('📋 Task update received:', data);
            this.triggerCallback('task_update', data);
        });

        this.socket.on('step_update', (data: { taskId: string; step: TaskStep }) => {
            console.log('👣 Step update received:', data);
            this.triggerCallback('step_update', data);
        });

        this.socket.on('log_entry', (data: { taskId: string; log: LogEntry }) => {
            console.log('📝 Log entry received:', data);
            this.triggerCallback('log_entry', data);
        });

        this.socket.on('error', (data: { taskId: string; error: string }) => {
            console.error('❌ Error received:', data);
            this.triggerCallback('error', data);
        });

        this.socket.on('agent_status', (data: { agentId: string; status: string }) => {
            console.log('🤖 Agent status update:', data);
            this.triggerCallback('agent_status', data);
        });

        this.socket.on('progress_update', (data: { taskId: string; progress: number }) => {
            console.log('📊 Progress update:', data);
            this.triggerCallback('progress_update', data);
        });
    }

    private triggerCallback(event: string, data: any) {
        const callback = this.callbacks.get(event);
        if (callback) {
            callback(data);
        }
    }

    // Subscribe to task updates
    subscribeToTask(taskId: string) {
        if (this.socket && this.isConnected) {
            console.log('📡 Subscribing to task:', taskId);
            this.socket.emit('subscribe_task', { taskId });
        }
    }

    // Unsubscribe from task updates
    unsubscribeFromTask(taskId: string) {
        if (this.socket && this.isConnected) {
            console.log('📡 Unsubscribing from task:', taskId);
            this.socket.emit('unsubscribe_task', { taskId });
        }
    }

    // Subscribe to system events
    subscribeToSystem() {
        if (this.socket && this.isConnected) {
            console.log('📡 Subscribing to system events');
            this.socket.emit('subscribe_system');
        }
    }

    // Register event callbacks
    on(event: string, callback: (data: any) => void) {
        this.callbacks.set(event, callback);
    }

    // Unregister event callbacks
    off(event: string) {
        this.callbacks.delete(event);
    }

    // Send message to server
    emit(event: string, data: any) {
        if (this.socket && this.isConnected) {
            this.socket.emit(event, data);
        } else {
            console.warn('⚠️ Cannot emit - WebSocket not connected');
        }
    }

    // Check connection status
    isSocketConnected(): boolean {
        return this.isConnected && this.socket?.connected === true;
    }

    // Manual reconnection
    reconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket.connect();
        }
    }

    // Disconnect
    disconnect() {
        if (this.socket) {
            console.log('🔌 Disconnecting WebSocket');
            this.socket.disconnect();
            this.isConnected = false;
        }
    }

    // Cleanup
    destroy() {
        this.callbacks.clear();
        this.disconnect();
        this.socket = null;
    }
}

// Export the class for direct usage
export { WebSocketService };

// Create singleton instance
const wsService = new WebSocketService();

export default wsService;
