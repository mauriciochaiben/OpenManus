import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { Task, CreateTaskRequest } from "../../../types";
import { taskService } from "../services";

interface TaskStore {
  // State
  tasks: Task[];
  currentTask: Task | null;
  loading: boolean;
  error: string | null;

  // Actions
  fetchTasks: () => Promise<void>;
  createTask: (taskData: CreateTaskRequest) => Promise<Task>;
  getTask: (id: string) => Promise<Task | null>;
  updateTask: (id: string, updates: any) => Promise<Task>;
  executeTask: (id: string) => Promise<Task>;
  cancelTask: (id: string) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
  setCurrentTask: (task: Task | null) => void;
  clearError: () => void;
}

export const useTaskStore = create<TaskStore>()(
  devtools(
    (set) => ({
      // Initial state
      tasks: [],
      currentTask: null,
      loading: false,
      error: null,

      // Actions
      fetchTasks: async () => {
        set({ loading: true, error: null });
        try {
          const response = await taskService.getTasks();
          if (response.success && response.data) {
            set({ tasks: response.data, loading: false });
          } else {
            set({
              error: response.error || "Failed to fetch tasks",
              loading: false,
            });
          }
        } catch (error) {
          set({
            error:
              error instanceof Error ? error.message : "Failed to fetch tasks",
            loading: false,
          });
        }
      },

      createTask: async (taskData: CreateTaskRequest) => {
        set({ loading: true, error: null });
        try {
          const response = await taskService.createTask(taskData);
          if (response.success && response.data) {
            set((state) => ({
              tasks: [response.data!, ...state.tasks],
              loading: false,
            }));
            return response.data;
          } else {
            const errorMessage = response.error || "Failed to create task";
            set({ error: errorMessage, loading: false });
            throw new Error(errorMessage);
          }
        } catch (error) {
          const errorMessage =
            error instanceof Error ? error.message : "Failed to create task";
          set({ error: errorMessage, loading: false });
          throw error;
        }
      },

      getTask: async (id: string) => {
        set({ loading: true, error: null });
        try {
          const response = await taskService.getTask(id);
          if (response.success && response.data) {
            set({ currentTask: response.data, loading: false });
            return response.data;
          } else {
            const errorMessage = response.error || "Failed to get task";
            set({ error: errorMessage, loading: false });
            return null;
          }
        } catch (error) {
          set({
            error:
              error instanceof Error ? error.message : "Failed to get task",
            loading: false,
          });
          return null;
        }
      },

      updateTask: async (id: string, updates: any) => {
        set({ loading: true, error: null });
        try {
          const response = await taskService.updateTask(id, updates);
          if (response.success && response.data) {
            set((state) => ({
              tasks: state.tasks.map((task) =>
                task.id === id ? response.data! : task,
              ),
              currentTask:
                state.currentTask?.id === id
                  ? response.data
                  : state.currentTask,
              loading: false,
            }));
            return response.data;
          } else {
            const errorMessage = response.error || "Failed to update task";
            set({ error: errorMessage, loading: false });
            throw new Error(errorMessage);
          }
        } catch (error) {
          set({
            error:
              error instanceof Error ? error.message : "Failed to update task",
            loading: false,
          });
          throw error;
        }
      },

      executeTask: async (id: string) => {
        set({ loading: true, error: null });
        try {
          const response = await taskService.executeTask(id);
          if (response.success && response.data) {
            set((state) => ({
              tasks: state.tasks.map((task) =>
                task.id === id ? response.data! : task,
              ),
              currentTask:
                state.currentTask?.id === id
                  ? response.data
                  : state.currentTask,
              loading: false,
            }));
            return response.data;
          } else {
            const errorMessage = response.error || "Failed to execute task";
            set({ error: errorMessage, loading: false });
            throw new Error(errorMessage);
          }
        } catch (error) {
          set({
            error:
              error instanceof Error ? error.message : "Failed to execute task",
            loading: false,
          });
          throw error;
        }
      },

      cancelTask: async (id: string) => {
        set({ loading: true, error: null });
        try {
          const response = await taskService.cancelTask(id);
          if (response.success && response.data) {
            set((state) => ({
              tasks: state.tasks.map((task) =>
                task.id === id ? response.data! : task,
              ),
              currentTask:
                state.currentTask?.id === id
                  ? response.data
                  : state.currentTask,
              loading: false,
            }));
          } else {
            const errorMessage = response.error || "Failed to cancel task";
            set({ error: errorMessage, loading: false });
          }
        } catch (error) {
          set({
            error:
              error instanceof Error ? error.message : "Failed to cancel task",
            loading: false,
          });
        }
      },

      deleteTask: async (id: string) => {
        set({ loading: true, error: null });
        try {
          const response = await taskService.deleteTask(id);
          if (response.success) {
            set((state) => ({
              tasks: state.tasks.filter((task) => task.id !== id),
              currentTask:
                state.currentTask?.id === id ? null : state.currentTask,
              loading: false,
            }));
          } else {
            const errorMessage = response.error || "Failed to delete task";
            set({ error: errorMessage, loading: false });
          }
        } catch (error) {
          set({
            error:
              error instanceof Error ? error.message : "Failed to delete task",
            loading: false,
          });
        }
      },

      setCurrentTask: (task: Task | null) => {
        set({ currentTask: task });
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: "task-store",
    },
  ),
);
