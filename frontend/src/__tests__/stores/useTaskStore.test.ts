import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useTaskStore } from '../../features/tasks/hooks/useTaskStore';
import { taskService } from '../../features/tasks/services/taskService';

// Mock the task service
vi.mock('../../features/tasks/services/taskService', () => ({
    taskService: {
        getTasks: vi.fn(),
        getTask: vi.fn(),
        createTask: vi.fn(),
        updateTask: vi.fn(),
        executeTask: vi.fn(),
        cancelTask: vi.fn(),
        deleteTask: vi.fn(),
    },
}));

// Factory for creating test tasks
const createTestTask = (overrides = {}) => ({
    id: 'task-1',
    title: 'Test Task',
    description: 'Test description',
    complexity: 'simple' as const,
    mode: 'auto' as const,
    status: 'pending' as const,
    progress: 0,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
    priority: 'medium' as const,
    tags: [],
    documentIds: [],
    ...overrides,
});

// Factory for creating API responses
const createApiResponse = (data: any, success = true) => ({
    success,
    data: success ? data : undefined,
    error: success ? undefined : data,
});

describe('useTaskStore', () => {
    beforeEach(() => {
        // Reset the store before each test
        useTaskStore.setState({
            tasks: [],
            currentTask: null,
            loading: false,
            error: null,
        });
        vi.clearAllMocks();
    });

    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('Initial State', () => {
        it('should have correct initial state', () => {
            const { result } = renderHook(() => useTaskStore());

            expect(result.current.tasks).toEqual([]);
            expect(result.current.currentTask).toBeNull();
            expect(result.current.loading).toBe(false);
            expect(result.current.error).toBeNull();
        });
    });

    describe('fetchTasks', () => {
        it('should fetch tasks successfully', async () => {
            const mockTasks = [
                createTestTask({ id: 'task-1' }),
                createTestTask({ id: 'task-2', title: 'Task 2' }),
            ];
            const mockResponse = createApiResponse(mockTasks);

            (taskService.getTasks as any).mockResolvedValue(mockResponse);

            const { result } = renderHook(() => useTaskStore());

            await act(async () => {
                await result.current.fetchTasks();
            });

            expect(result.current.loading).toBe(false);
            expect(result.current.error).toBeNull();
            expect(result.current.tasks).toEqual(mockTasks);
            expect(taskService.getTasks).toHaveBeenCalledTimes(1);
        });

        it('should handle fetch tasks error', async () => {
            const mockError = createApiResponse('Failed to fetch tasks', false);

            (taskService.getTasks as any).mockResolvedValue(mockError);

            const { result } = renderHook(() => useTaskStore());

            await act(async () => {
                await result.current.fetchTasks();
            });

            expect(result.current.loading).toBe(false);
            expect(result.current.error).toBe('Failed to fetch tasks');
            expect(result.current.tasks).toEqual([]);
        });

        it('should handle network error', async () => {
            (taskService.getTasks as any).mockRejectedValue(new Error('Network error'));

            const { result } = renderHook(() => useTaskStore());

            await act(async () => {
                await result.current.fetchTasks();
            });

            expect(result.current.loading).toBe(false);
            expect(result.current.error).toBe('Network error');
            expect(result.current.tasks).toEqual([]);
        });

        it('should set loading state during fetch', async () => {
            let resolvePromise: (value: any) => void;
            const promise = new Promise((resolve) => {
                resolvePromise = resolve;
            });

            (taskService.getTasks as any).mockReturnValue(promise);

            const { result } = renderHook(() => useTaskStore());

            act(() => {
                result.current.fetchTasks();
            });

            expect(result.current.loading).toBe(true);
            expect(result.current.error).toBeNull();

            await act(async () => {
                resolvePromise!(createApiResponse([]));
                await promise;
            });

            expect(result.current.loading).toBe(false);
        });
    });

    describe('createTask', () => {
        it('should create task successfully', async () => {
            const taskData = { title: 'New Task', description: 'Test task' };
            const newTask = createTestTask(taskData);
            const mockResponse = createApiResponse(newTask);

            (taskService.createTask as any).mockResolvedValue(mockResponse);

            const { result } = renderHook(() => useTaskStore());

            let createdTask: any;
            await act(async () => {
                createdTask = await result.current.createTask(taskData);
            });

            expect(result.current.loading).toBe(false);
            expect(result.current.error).toBeNull();
            expect(result.current.tasks).toContain(newTask);
            expect(createdTask).toEqual(newTask);
            expect(taskService.createTask).toHaveBeenCalledWith(taskData);
        });

        it('should handle create task error', async () => {
            const taskData = { title: 'New Task', description: 'Test task' };
            const mockError = createApiResponse('Failed to create task', false);

            (taskService.createTask as any).mockResolvedValue(mockError);

            const { result } = renderHook(() => useTaskStore());

            await act(async () => {
                try {
                    await result.current.createTask(taskData);
                } catch (error) {
                    expect(error).toBeInstanceOf(Error);
                }
            });

            expect(result.current.loading).toBe(false);
            expect(result.current.error).toBe('Failed to create task');
            expect(result.current.tasks).toEqual([]);
        });
    });

    describe('getTask', () => {
        it('should get task successfully', async () => {
            const task = createTestTask();
            const mockResponse = createApiResponse(task);

            (taskService.getTask as any).mockResolvedValue(mockResponse);

            const { result } = renderHook(() => useTaskStore());

            let retrievedTask: any;
            await act(async () => {
                retrievedTask = await result.current.getTask(task.id);
            });

            expect(result.current.loading).toBe(false);
            expect(result.current.error).toBeNull();
            expect(result.current.currentTask).toEqual(task);
            expect(retrievedTask).toEqual(task);
            expect(taskService.getTask).toHaveBeenCalledWith(task.id);
        });

        it('should handle get task error', async () => {
            const taskId = 'test-task-id';
            const mockError = createApiResponse('Task not found', false);

            (taskService.getTask as any).mockResolvedValue(mockError);

            const { result } = renderHook(() => useTaskStore());

            let retrievedTask: any;
            await act(async () => {
                retrievedTask = await result.current.getTask(taskId);
            });

            expect(result.current.loading).toBe(false);
            expect(result.current.error).toBe('Task not found');
            expect(result.current.currentTask).toBeNull();
            expect(retrievedTask).toBeNull();
        });
    });

    describe('updateTask', () => {
        it('should update task successfully', async () => {
            const existingTask = createTestTask();
            const updates = { title: 'Updated Task' };
            const updatedTask = { ...existingTask, ...updates };
            const mockResponse = createApiResponse(updatedTask);

            // Set initial state with existing task
            useTaskStore.setState({
                tasks: [existingTask],
                currentTask: existingTask,
                loading: false,
                error: null,
            });

            (taskService.updateTask as any).mockResolvedValue(mockResponse);

            const { result } = renderHook(() => useTaskStore());

            await act(async () => {
                await result.current.updateTask(existingTask.id, updates);
            });

            expect(result.current.loading).toBe(false);
            expect(result.current.error).toBeNull();
            expect(result.current.tasks[0]).toEqual(updatedTask);
            expect(result.current.currentTask).toEqual(updatedTask);
            expect(taskService.updateTask).toHaveBeenCalledWith(existingTask.id, updates);
        });
    });

    describe('executeTask', () => {
        it('should execute task successfully', async () => {
            const task = createTestTask();
            const runningTask = { ...task, status: 'running' as const };
            const mockResponse = createApiResponse(runningTask);

            useTaskStore.setState({
                tasks: [task],
                currentTask: null,
                loading: false,
                error: null,
            });

            (taskService.executeTask as any).mockResolvedValue(mockResponse);

            const { result } = renderHook(() => useTaskStore());

            await act(async () => {
                await result.current.executeTask(task.id);
            });

            expect(result.current.loading).toBe(false);
            expect(result.current.error).toBeNull();
            expect(result.current.tasks[0].status).toBe('running');
            expect(taskService.executeTask).toHaveBeenCalledWith(task.id);
        });
    });

    describe('cancelTask', () => {
        it('should cancel task successfully', async () => {
            const runningTask = createTestTask({ status: 'running' });
            const cancelledTask = { ...runningTask, status: 'cancelled' as const };
            const mockResponse = createApiResponse(cancelledTask);

            useTaskStore.setState({
                tasks: [runningTask],
                currentTask: runningTask,
                loading: false,
                error: null,
            });

            (taskService.cancelTask as any).mockResolvedValue(mockResponse);

            const { result } = renderHook(() => useTaskStore());

            await act(async () => {
                await result.current.cancelTask(runningTask.id);
            });

            expect(result.current.loading).toBe(false);
            expect(result.current.error).toBeNull();
            expect(result.current.tasks[0].status).toBe('cancelled');
            expect(result.current.currentTask?.status).toBe('cancelled');
        });
    });

    describe('deleteTask', () => {
        it('should delete task successfully', async () => {
            const task = createTestTask();
            const mockResponse = createApiResponse(null);

            useTaskStore.setState({
                tasks: [task],
                currentTask: task,
                loading: false,
                error: null,
            });

            (taskService.deleteTask as any).mockResolvedValue(mockResponse);

            const { result } = renderHook(() => useTaskStore());

            await act(async () => {
                await result.current.deleteTask(task.id);
            });

            expect(result.current.loading).toBe(false);
            expect(result.current.error).toBeNull();
            expect(result.current.tasks).toEqual([]);
            expect(result.current.currentTask).toBeNull();
            expect(taskService.deleteTask).toHaveBeenCalledWith(task.id);
        });
    });

    describe('setCurrentTask', () => {
        it('should set current task', () => {
            const task = createTestTask();
            const { result } = renderHook(() => useTaskStore());

            act(() => {
                result.current.setCurrentTask(task);
            });

            expect(result.current.currentTask).toEqual(task);
        });

        it('should clear current task', () => {
            const task = createTestTask();
            useTaskStore.setState({ currentTask: task });

            const { result } = renderHook(() => useTaskStore());

            act(() => {
                result.current.setCurrentTask(null);
            });

            expect(result.current.currentTask).toBeNull();
        });
    });

    describe('clearError', () => {
        it('should clear error', () => {
            useTaskStore.setState({ error: 'Test error' });

            const { result } = renderHook(() => useTaskStore());

            act(() => {
                result.current.clearError();
            });

            expect(result.current.error).toBeNull();
        });
    });
});
