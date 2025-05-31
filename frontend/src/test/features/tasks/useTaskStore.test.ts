// Tests for the Zustand task store
import { describe, test, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { TaskFactory, ApiResponseFactory } from '../../factories';
import { useTaskStore } from '../../../features/tasks/hooks/useTaskStore';
import { taskService } from '../../../features/tasks/services';

// Mock the task service
vi.mock('../../../features/tasks/services', () => ({
    taskService: {
        getTasks: vi.fn(),
        getTask: vi.fn(),
        createTask: vi.fn(),
        updateTask: vi.fn(),
        executeTask: vi.fn(),
        cancelTask: vi.fn(),
        deleteTask: vi.fn()
    }
}));

// Setup test environment
const setupTestEnvironment = () => {
    // Mock implementations and other setup
    return {
        cleanup: () => {
            // Cleanup mock implementations
        }
    };
};

describe('useTaskStore', () => {
    let testEnv: any;

    beforeEach(() => {
        testEnv = setupTestEnvironment();
        // Reset the store before each test
        useTaskStore.setState({
            tasks: [],
            currentTask: null,
            loading: false,
            error: null
        });
    });

    afterEach(() => {
        testEnv.cleanup();
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
            const mockTasks = TaskFactory.createMultiple(3);
            const mockResponse = { success: true, data: mockTasks };

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
            const mockError = ApiResponseFactory.createErrorResponse('Failed to fetch tasks');

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
            const promise = new Promise(resolve => {
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
                resolvePromise!(ApiResponseFactory.createTasksResponse([]));
                await promise;
            });

            expect(result.current.loading).toBe(false);
        });
    });

    describe('createTask', () => {
        it('should create task successfully', async () => {
            const taskData = { title: 'New Task', description: 'Test task' };
            const newTask = TaskFactory.create(taskData);
            const mockResponse = { success: true, data: newTask };

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
            const mockError = ApiResponseFactory.createErrorResponse('Failed to create task');

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
            const task = TaskFactory.create();
            const mockResponse = { success: true, data: task };

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
            const mockError = ApiResponseFactory.createErrorResponse('Task not found');

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
            const existingTask = TaskFactory.create();
            const updates = { title: 'Updated Task' };
            const updatedTask = { ...existingTask, ...updates };
            const mockResponse = { success: true, data: updatedTask };

            // Set initial state with existing task
            useTaskStore.setState({
                tasks: [existingTask],
                currentTask: existingTask,
                loading: false,
                error: null
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
            const task = TaskFactory.create();
            const runningTask = { ...task, status: 'running' as const };
            const mockResponse = { success: true, data: runningTask };

            useTaskStore.setState({
                tasks: [task],
                currentTask: null,
                loading: false,
                error: null
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
            const runningTask = TaskFactory.createInProgress();
            const cancelledTask = { ...runningTask, status: 'error' as const };
            const mockResponse = { success: true, data: cancelledTask };

            useTaskStore.setState({
                tasks: [runningTask],
                currentTask: runningTask,
                loading: false,
                error: null
            });

            (taskService.cancelTask as any).mockResolvedValue(mockResponse);

            const { result } = renderHook(() => useTaskStore());

            await act(async () => {
                await result.current.cancelTask(runningTask.id);
            });

            expect(result.current.loading).toBe(false);
            expect(result.current.error).toBeNull();
            expect(result.current.tasks[0].status).toBe('error');
            expect(result.current.currentTask?.status).toBe('error');
        });
    });

    describe('deleteTask', () => {
        it('should delete task successfully', async () => {
            const task = TaskFactory.create();
            const mockResponse = { success: true, message: 'Operation successful', data: null };

            useTaskStore.setState({
                tasks: [task],
                currentTask: task,
                loading: false,
                error: null
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
            const task = TaskFactory.create();
            const { result } = renderHook(() => useTaskStore());

            act(() => {
                result.current.setCurrentTask(task);
            });

            expect(result.current.currentTask).toEqual(task);
        });

        it('should clear current task', () => {
            const task = TaskFactory.create();
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
