// Test factories for creating mock data
import { Task, TaskStep, UploadedDocument, Agent, LogEntry } from '../../types';

// Task Factory
export class TaskFactory {
    private static defaultTask: Partial<Task> = {
        title: 'Test Task',
        description: 'A test task for testing purposes',
        complexity: 'simple',
        mode: 'auto',
        status: 'pending',
        createdAt: new Date().toISOString(),
        documents: [],
        steps: [],
        logs: []
    };

    static create(overrides: Partial<Task> = {}): Task {
        return {
            id: `task-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            ...this.defaultTask,
            ...overrides,
        } as Task;
    }

    static createMultiple(count: number, overrides: Partial<Task> = {}): Task[] {
        return Array.from({ length: count }, (_, index) =>
            this.create({
                title: `Test Task ${index + 1}`,
                ...overrides
            })
        );
    }

    static createCompleted(overrides: Partial<Task> = {}): Task {
        return this.create({
            status: 'completed',
            completedAt: new Date().toISOString(),
            result: 'Task completed successfully',
            ...overrides
        });
    }

    static createInProgress(overrides: Partial<Task> = {}): Task {
        return this.create({
            status: 'running',
            ...overrides
        });
    }

    static createFailed(overrides: Partial<Task> = {}): Task {
        return this.create({
            status: 'error',
            result: 'Task failed with error',
            ...overrides
        });
    }
}

// TaskStep Factory
export class TaskStepFactory {
    private static defaultStep: Partial<TaskStep> = {
        title: 'Test Step',
        description: 'A test step for testing purposes',
        status: 'pending',
        agent: 'TestAgent'
    };

    static create(overrides: Partial<TaskStep> = {}): TaskStep {
        return {
            id: `step-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            ...this.defaultStep,
            ...overrides,
        } as TaskStep;
    }

    static createMultiple(count: number, overrides: Partial<TaskStep> = {}): TaskStep[] {
        return Array.from({ length: count }, (_, index) =>
            this.create({
                title: `Test Step ${index + 1}`,
                ...overrides
            })
        );
    }

    static createCompleted(overrides: Partial<TaskStep> = {}): TaskStep {
        return this.create({
            status: 'completed',
            startedAt: new Date(Date.now() - 60000).toISOString(),
            completedAt: new Date().toISOString(),
            result: 'Step completed successfully',
            ...overrides
        });
    }

    static createInProgress(overrides: Partial<TaskStep> = {}): TaskStep {
        return this.create({
            status: 'running',
            startedAt: new Date().toISOString(),
            ...overrides
        });
    }

    static createFailed(overrides: Partial<TaskStep> = {}): TaskStep {
        return this.create({
            status: 'error',
            startedAt: new Date(Date.now() - 30000).toISOString(),
            completedAt: new Date().toISOString(),
            result: 'Step failed with error',
            ...overrides
        });
    }
}

// UploadedDocument Factory
export class DocumentFactory {
    private static defaultDocument: Partial<UploadedDocument> = {
        name: 'test-document.txt',
        size: 1024,
        type: 'text/plain',
        status: 'uploaded'
    };

    static create(overrides: Partial<UploadedDocument> = {}): UploadedDocument {
        return {
            id: `doc-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            ...this.defaultDocument,
            ...overrides,
        } as UploadedDocument;
    }

    static createMultiple(count: number, overrides: Partial<UploadedDocument> = {}): UploadedDocument[] {
        return Array.from({ length: count }, (_, index) =>
            this.create({
                name: `test-document-${index + 1}.txt`,
                ...overrides
            })
        );
    }

    static createProcessed(overrides: Partial<UploadedDocument> = {}): UploadedDocument {
        return this.create({
            status: 'processed',
            extractedText: 'Extracted text content from the document',
            url: '/api/documents/download/test-doc',
            ...overrides
        });
    }

    static createWithError(overrides: Partial<UploadedDocument> = {}): UploadedDocument {
        return this.create({
            status: 'error',
            error: 'Failed to process document',
            ...overrides
        });
    }

    static createPDF(overrides: Partial<UploadedDocument> = {}): UploadedDocument {
        return this.create({
            name: 'test-document.pdf',
            type: 'application/pdf',
            size: 2048,
            ...overrides
        });
    }

    static createImage(overrides: Partial<UploadedDocument> = {}): UploadedDocument {
        return this.create({
            name: 'test-image.png',
            type: 'image/png',
            size: 4096,
            ...overrides
        });
    }
}

// Agent Factory
export class AgentFactory {
    private static defaultAgent: Partial<Agent> = {
        name: 'TestAgent',
        type: 'manus',
        status: 'idle',
        capabilities: ['test', 'automation']
    };

    static create(overrides: Partial<Agent> = {}): Agent {
        return {
            id: `agent-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            ...this.defaultAgent,
            ...overrides,
        } as Agent;
    }

    static createMultiple(count: number, overrides: Partial<Agent> = {}): Agent[] {
        return Array.from({ length: count }, (_, index) =>
            this.create({
                name: `TestAgent${index + 1}`,
                ...overrides
            })
        );
    }

    static createBrowserAgent(overrides: Partial<Agent> = {}): Agent {
        return this.create({
            name: 'BrowserAgent',
            type: 'browser',
            capabilities: ['web_scraping', 'browser_automation'],
            ...overrides
        });
    }

    static createMCPAgent(overrides: Partial<Agent> = {}): Agent {
        return this.create({
            name: 'MCPAgent',
            type: 'mcp',
            capabilities: ['mcp_server', 'protocol_communication'],
            ...overrides
        });
    }
}

// LogEntry Factory
export class LogEntryFactory {
    private static defaultLog: Partial<LogEntry> = {
        level: 'info',
        message: 'Test log message',
        timestamp: new Date().toISOString(),
        source: 'test'
    };

    static create(overrides: Partial<LogEntry> = {}): LogEntry {
        return {
            id: `log-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            ...this.defaultLog,
            ...overrides,
        } as LogEntry;
    }

    static createMultiple(count: number, overrides: Partial<LogEntry> = {}): LogEntry[] {
        return Array.from({ length: count }, (_, index) =>
            this.create({
                message: `Test log message ${index + 1}`,
                ...overrides
            })
        );
    }

    static createError(overrides: Partial<LogEntry> = {}): LogEntry {
        return this.create({
            level: 'error',
            message: 'Test error message',
            ...overrides
        });
    }

    static createWarning(overrides: Partial<LogEntry> = {}): LogEntry {
        return this.create({
            level: 'warning',
            message: 'Test warning message',
            ...overrides
        });
    }

    static createSuccess(overrides: Partial<LogEntry> = {}): LogEntry {
        return this.create({
            level: 'success',
            message: 'Test success message',
            ...overrides
        });
    }
}

// API Response Factory
export class ApiResponseFactory {
    static createTaskResponse(task: Task = TaskFactory.create()) {
        return {
            task,
            success: true,
            message: 'Task retrieved successfully'
        };
    }

    static createTasksResponse(tasks: Task[] = TaskFactory.createMultiple(3)) {
        return {
            tasks,
            total: tasks.length,
            success: true,
            message: 'Tasks retrieved successfully'
        };
    }

    static createErrorResponse(message: string = 'An error occurred') {
        return {
            success: false,
            error: message,
            message
        };
    }
}

// WebSocket Message Factory
export class WebSocketMessageFactory {
    static createTaskUpdate(taskId: string, task: Partial<Task> = {}) {
        return {
            type: 'task:updated',
            data: {
                taskId,
                task: TaskFactory.create({ id: taskId, ...task })
            },
            timestamp: Date.now()
        };
    }

    static createStepUpdate(taskId: string, step: Partial<TaskStep> = {}) {
        return {
            type: 'task:stepUpdated',
            data: {
                taskId,
                step: TaskStepFactory.create(step)
            },
            timestamp: Date.now()
        };
    }

    static createLogEntry(taskId: string, log: Partial<LogEntry> = {}) {
        return {
            type: 'task:logEntry',
            data: {
                taskId,
                log: LogEntryFactory.create(log)
            },
            timestamp: Date.now()
        };
    }

    static createConnectionEvent(event: 'connected' | 'disconnected' | 'reconnecting') {
        return {
            type: `websocket:${event}`,
            data: {},
            timestamp: Date.now()
        };
    }

    static createNotification(notification: {
        type?: 'info' | 'success' | 'warning' | 'error';
        title?: string;
        message: string;
        taskId?: string;
    }) {
        return {
            type: 'system:notification',
            data: {
                type: notification.type || 'info',
                title: notification.title || 'System Notification',
                message: notification.message,
                taskId: notification.taskId
            },
            timestamp: Date.now()
        };
    }
}
