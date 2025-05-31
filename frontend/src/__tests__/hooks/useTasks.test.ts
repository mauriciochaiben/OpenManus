import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useTasks, useTask } from '../../hooks/useTasks';
import { taskApi } from '../../services/api';
import { eventBus } from '../../utils/eventBus';

// Mock the API
vi.mock('../../services/api', () => ({
    taskApi: {
        getTasks: vi.fn(),
        getTask: vi.fn(),
        createTask: vi.fn(),
        deleteTask: vi.fn(),
        cancelTask: vi.fn(),
    },
}));

// Mock event bus
vi.mock('../../utils/eventBus', () => ({
    eventBus: {
        on: vi.fn(() => vi.fn()), // Return a mock unsubscribe function
        off: vi.fn(),
        emit: vi.fn(),
    },
}));

const mockTasks = [
    {
        id: 'task-1',
        title: 'Test Task 1',
        description: 'Test description 1',
        complexity: 'simple' as const,
        mode: 'auto' as const,
        status: 'pending' as const,
        progress: 0,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
        priority: 'medium' as const,
        tags: ['test'],
        documentIds: [],
    },
    {
        id: 'task-2',
        title: 'Test Task 2',
        description: 'Test description 2',
        complexity: 'medium' as const,
        mode: 'single' as const,
        status: 'running' as const,
        progress: 50,
        createdAt: '2024-01-02T00:00:00Z',
        updatedAt: '2024-01-02T00:00:00Z',
        priority: 'high' as const,
        tags: ['test', 'automation'],
        documentIds: [],
    },
];

describe('useTasks Hook', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('useTasks', () => {
        it('should fetch tasks on mount', async () => {
            const mockTaskApi = taskApi as any;
            mockTaskApi.getTasks.mockResolvedValue(mockTasks);

            const { result } = renderHook(() => useTasks());

            // Should start with loading state
            expect(result.current.loading).toBe(true);
            expect(result.current.tasks).toEqual([]);
            expect(result.current.error).toBeNull();

            // Wait for async operation to complete
            await waitFor(() => {
                expect(result.current.loading).toBe(false);
            });

            expect(result.current.tasks).toEqual(mockTasks);
            expect(result.current.error).toBeNull();
            expect(mockTaskApi.getTasks).toHaveBeenCalledTimes(1);
        });

        it('should handle fetch error', async () => {
            const mockTaskApi = taskApi as any;
            const errorMessage = 'Failed to fetch tasks';
            mockTaskApi.getTasks.mockRejectedValue(new Error(errorMessage));

            const { result } = renderHook(() => useTasks());

            await waitFor(() => {
                expect(result.current.loading).toBe(false);
            });

            expect(result.current.tasks).toEqual([]);
            expect(result.current.error).toBe(errorMessage);
        });

        it('should create task successfully', async () => {
            const mockTaskApi = taskApi as any;
            mockTaskApi.getTasks.mockResolvedValue([]);

            const newTask = {
                id: 'task-3',
                title: 'New Task',
                description: 'New task description',
                complexity: 'simple' as const,
                mode: 'auto' as const,
                status: 'pending' as const,
                progress: 0,
                createdAt: '2024-01-03T00:00:00Z',
                updatedAt: '2024-01-03T00:00:00Z',
                priority: 'medium' as const,
                tags: [],
                documentIds: [],
            };

            const mockResponse = { task: newTask };
            mockTaskApi.createTask.mockResolvedValue(mockResponse);

            const { result } = renderHook(() => useTasks());

            await waitFor(() => {
                expect(result.current.loading).toBe(false);
            });

            let createdTask;
            await act(async () => {
                createdTask = await result.current.createTask({
                    title: 'New Task',
                    description: 'New task description',
                    complexity: 'simple',
                    priority: 'medium',
                    document_ids: [],
                    tags: [],
                });
            });

            expect(createdTask).toEqual(newTask);
            expect(result.current.tasks).toContain(newTask);
            expect(mockTaskApi.createTask).toHaveBeenCalledWith({
                title: 'New Task',
                description: 'New task description',
                complexity: 'simple',
                priority: 'medium',
                document_ids: [],
                tags: [],
            });
        });

        it('should delete task successfully', async () => {
            const mockTaskApi = taskApi as any;
            mockTaskApi.getTasks.mockResolvedValue(mockTasks);
            mockTaskApi.deleteTask.mockResolvedValue({});

            const { result } = renderHook(() => useTasks());

            await waitFor(() => {
                expect(result.current.tasks).toEqual(mockTasks);
            });

            await act(async () => {
                await result.current.deleteTask('task-1');
            });

            expect(result.current.tasks).not.toContain(
                expect.objectContaining({ id: 'task-1' })
            );
            expect(mockTaskApi.deleteTask).toHaveBeenCalledWith('task-1');
        });

        it('should cancel task successfully', async () => {
            const mockTaskApi = taskApi as any;
            mockTaskApi.getTasks.mockResolvedValue(mockTasks);
            mockTaskApi.cancelTask.mockResolvedValue({});

            const { result } = renderHook(() => useTasks());

            await waitFor(() => {
                expect(result.current.tasks).toEqual(mockTasks);
            });

            await act(async () => {
                await result.current.cancelTask('task-2');
            });

            expect(mockTaskApi.cancelTask).toHaveBeenCalledWith('task-2');
        });

        it('should handle task updates via event bus', async () => {
            const mockTaskApi = taskApi as any;
            const mockEventBus = eventBus as any;
            mockTaskApi.getTasks.mockResolvedValue([mockTasks[0]]);

            let eventHandler: any;
            mockEventBus.on.mockImplementation((event: string, handler: any) => {
                if (event === 'task:updated') {
                    eventHandler = handler;
                }
                return vi.fn(); // Return unsubscribe function
            });

            const { result } = renderHook(() => useTasks());

            await waitFor(() => {
                expect(result.current.tasks).toEqual([mockTasks[0]]);
            });

            // Simulate task update via event bus
            const updatedTask = { ...mockTasks[0], status: 'completed' as const };
            act(() => {
                eventHandler({ taskId: 'task-1', task: updatedTask });
            });

            expect(result.current.tasks[0]).toEqual(updatedTask);
        });
    });

    describe('useTask', () => {
        it('should fetch single task on mount', async () => {
            const mockTaskApi = taskApi as any;
            const task = mockTasks[0];
            mockTaskApi.getTask.mockResolvedValue(task);

            const { result } = renderHook(() => useTask('task-1'));

            expect(result.current.loading).toBe(true);
            expect(result.current.task).toBeNull();

            await waitFor(() => {
                expect(result.current.loading).toBe(false);
            });

            expect(result.current.task).toEqual(task);
            expect(result.current.error).toBeNull();
            expect(mockTaskApi.getTask).toHaveBeenCalledWith('task-1');
        });

        it('should handle single task fetch error', async () => {
            const mockTaskApi = taskApi as any;
            const errorMessage = 'Task not found';
            mockTaskApi.getTask.mockRejectedValue(new Error(errorMessage));

            const { result } = renderHook(() => useTask('invalid-id'));

            await waitFor(() => {
                expect(result.current.loading).toBe(false);
            });

            expect(result.current.task).toBeNull();
            expect(result.current.error).toBe(errorMessage);
        });

        it('should refresh task when refreshTask is called', async () => {
            const mockTaskApi = taskApi as any;
            const task = mockTasks[0];
            mockTaskApi.getTask.mockResolvedValue(task);

            const { result } = renderHook(() => useTask('task-1'));

            await waitFor(() => {
                expect(result.current.task).toEqual(task);
            });

            const updatedTask = { ...task, status: 'completed' as const };
            mockTaskApi.getTask.mockResolvedValue(updatedTask);

            await act(async () => {
                result.current.refreshTask();
            });

            await waitFor(() => {
                expect(result.current.task).toEqual(updatedTask);
            });

            expect(mockTaskApi.getTask).toHaveBeenCalledTimes(2);
        });

        it('should handle task updates via event bus', async () => {
            const mockTaskApi = taskApi as any;
            const mockEventBus = eventBus as any;
            const task = mockTasks[0];
            mockTaskApi.getTask.mockResolvedValue(task);

            let taskUpdateHandler: any;
            let stepUpdateHandler: any;
            let logEntryHandler: any;

            mockEventBus.on.mockImplementation((event: string, handler: any) => {
                if (event === 'task:updated') taskUpdateHandler = handler;
                if (event === 'task:stepUpdated') stepUpdateHandler = handler;
                if (event === 'task:logEntry') logEntryHandler = handler;
                return vi.fn(); // Return unsubscribe function
            });

            const { result } = renderHook(() => useTask('task-1'));

            await waitFor(() => {
                expect(result.current.task).toEqual(task);
            });

            // Test task update
            const updatedTask = { ...task, status: 'completed' as const };
            act(() => {
                taskUpdateHandler({ taskId: 'task-1', task: updatedTask });
            });

            expect(result.current.task).toEqual(updatedTask);

            // Test step update
            const newStep = {
                id: 'step-1',
                stepNumber: 1,
                title: 'Test Step',
                status: 'completed' as const,
            };

            act(() => {
                stepUpdateHandler({ taskId: 'task-1', step: newStep });
            });

            expect(result.current.task?.steps).toContain(newStep);

            // Test log entry
            const logEntry = {
                id: 'log-1',
                timestamp: '2024-01-01T00:00:00Z',
                level: 'info' as const,
                message: 'Test log message',
            };

            act(() => {
                logEntryHandler({ taskId: 'task-1', log: logEntry });
            });

            expect(result.current.task?.logs).toContain(logEntry);
        });

        it('should not fetch if taskId is undefined', () => {
            const mockTaskApi = taskApi as any;

            renderHook(() => useTask(undefined));

            expect(mockTaskApi.getTask).not.toHaveBeenCalled();
        });
    });
});
