import { useState, useEffect, useCallback } from 'react';
import type { Task, LogEntry, TaskStep } from '../types';
import { taskApi } from '../services/api';
import wsService from '../services/websocket';

export const useTask = (taskId?: string) => {
    const [task, setTask] = useState<Task | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchTask = useCallback(async (id: string) => {
        if (!id) return;

        setLoading(true);
        setError(null);

        try {
            const taskData = await taskApi.getTask(id);
            setTask(taskData);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch task');
        } finally {
            setLoading(false);
        }
    }, []);

    const refreshTask = useCallback(() => {
        if (taskId) {
            fetchTask(taskId);
        }
    }, [taskId, fetchTask]);

    useEffect(() => {
        if (taskId) {
            fetchTask(taskId);

            // Subscribe to real-time updates
            wsService.subscribeToTask(taskId);

            // Set up event listeners
            const handleTaskUpdate = (data: { taskId: string; task: Task }) => {
                if (data.taskId === taskId) {
                    setTask(data.task);
                }
            };

            const handleStepUpdate = (data: { taskId: string; step: TaskStep }) => {
                if (data.taskId === taskId) {
                    setTask(prevTask => {
                        if (!prevTask) return null;

                        const updatedSteps = prevTask.steps ? [...prevTask.steps] : [];
                        const stepIndex = updatedSteps.findIndex(s => s.id === data.step.id);

                        if (stepIndex >= 0) {
                            updatedSteps[stepIndex] = data.step;
                        } else {
                            updatedSteps.push(data.step);
                        }

                        return { ...prevTask, steps: updatedSteps };
                    });
                }
            };

            const handleLogEntry = (data: { taskId: string; log: LogEntry }) => {
                if (data.taskId === taskId) {
                    setTask(prevTask => {
                        if (!prevTask) return null;

                        const logs = prevTask.logs ? [...prevTask.logs, data.log] : [data.log];
                        return { ...prevTask, logs };
                    });
                }
            };

            wsService.on('task_update', handleTaskUpdate);
            wsService.on('step_update', handleStepUpdate);
            wsService.on('log_entry', handleLogEntry);

            return () => {
                wsService.unsubscribeFromTask(taskId);
                wsService.off('task_update');
                wsService.off('step_update');
                wsService.off('log_entry');
            };
        }
    }, [taskId, fetchTask]);

    return {
        task,
        loading,
        error,
        refreshTask,
    };
};

export const useTasks = () => {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchTasks = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const tasksData = await taskApi.getTasks();
            setTasks(tasksData);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch tasks');
        } finally {
            setLoading(false);
        }
    }, []);

    const createTask = useCallback(async (taskData: any) => {
        try {
            const response = await taskApi.createTask(taskData);
            setTasks(prevTasks => [response.task, ...prevTasks]);
            return response.task;
        } catch (err) {
            throw new Error(err instanceof Error ? err.message : 'Failed to create task');
        }
    }, []);

    const deleteTask = useCallback(async (taskId: string) => {
        try {
            await taskApi.deleteTask(taskId);
            setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
        } catch (err) {
            throw new Error(err instanceof Error ? err.message : 'Failed to delete task');
        }
    }, []);

    const cancelTask = useCallback(async (taskId: string) => {
        try {
            await taskApi.cancelTask(taskId);
            // Task status will be updated via WebSocket
        } catch (err) {
            throw new Error(err instanceof Error ? err.message : 'Failed to cancel task');
        }
    }, []);

    useEffect(() => {
        fetchTasks();

        // Subscribe to system-wide task updates
        wsService.subscribeToSystem();

        const handleTaskUpdate = (data: { taskId: string; task: Task }) => {
            setTasks(prevTasks => {
                const taskIndex = prevTasks.findIndex(t => t.id === data.taskId);
                if (taskIndex >= 0) {
                    const updatedTasks = [...prevTasks];
                    updatedTasks[taskIndex] = data.task;
                    return updatedTasks;
                } else {
                    return [data.task, ...prevTasks];
                }
            });
        };

        wsService.on('task_update', handleTaskUpdate);

        return () => {
            wsService.off('task_update');
        };
    }, [fetchTasks]);

    return {
        tasks,
        loading,
        error,
        fetchTasks,
        createTask,
        deleteTask,
        cancelTask,
    };
};
