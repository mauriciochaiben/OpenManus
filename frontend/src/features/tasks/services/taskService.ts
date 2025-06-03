// Task service for API communication
import {
  Task,
  CreateTaskRequest,
  UpdateTaskRequest,
  ApiResponse,
} from "../../../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_V2_BASE = `${API_BASE}/api/v2`;

class TaskService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${API_V2_BASE}${endpoint}`, {
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        ...options,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.detail || data.message || "Request failed",
        };
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error("API request failed:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Network error",
      };
    }
  }

  async getTasks(): Promise<ApiResponse<Task[]>> {
    return this.request<Task[]>("/tasks");
  }

  async getTask(taskId: string): Promise<ApiResponse<Task>> {
    return this.request<Task>(`/tasks/${taskId}`);
  }

  async createTask(taskData: CreateTaskRequest): Promise<ApiResponse<Task>> {
    const result = await this.request<Task>("/tasks", {
      method: "POST",
      body: JSON.stringify(taskData),
    });

    if (result.success) {
      // Feedback de sucesso
      const { message } = await import("antd");
      message.success("Tarefa criada com sucesso!");
    } else {
      // Feedback de erro
      const { message } = await import("antd");
      message.error("Erro ao criar tarefa. Tente novamente.");
    }

    return result;
  }

  async updateTask(
    taskId: string,
    updates: UpdateTaskRequest,
  ): Promise<ApiResponse<Task>> {
    const result = await this.request<Task>(`/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(updates),
    });

    if (result.success) {
      // Feedback de sucesso
      const { message } = await import("antd");
      message.success("Tarefa atualizada com sucesso!");
    } else {
      // Feedback de erro
      const { message } = await import("antd");
      message.error("Erro ao atualizar tarefa. Tente novamente.");
    }

    return result;
  }

  async deleteTask(taskId: string): Promise<ApiResponse<void>> {
    const result = await this.request<void>(`/tasks/${taskId}`, {
      method: "DELETE",
    });

    if (result.success) {
      // Feedback de sucesso
      const { message } = await import("antd");
      message.success("Tarefa excluída com sucesso!");
    } else {
      // Feedback de erro
      const { message } = await import("antd");
      message.error("Erro ao excluir tarefa. Tente novamente.");
    }

    return result;
  }

  async executeTask(taskId: string): Promise<ApiResponse<Task>> {
    const result = await this.request<Task>(`/tasks/${taskId}/execute`, {
      method: "POST",
    });

    if (result.success) {
      // Feedback de sucesso
      const { message } = await import("antd");
      message.success("Execução da tarefa iniciada com sucesso!");
    } else {
      // Feedback de erro
      const { message } = await import("antd");
      message.error("Erro ao executar tarefa. Tente novamente.");
    }

    return result;
  }

  async cancelTask(taskId: string): Promise<ApiResponse<Task>> {
    const result = await this.request<Task>(`/tasks/${taskId}/cancel`, {
      method: "POST",
    });

    if (result.success) {
      // Feedback de sucesso
      const { message } = await import("antd");
      message.success("Tarefa cancelada com sucesso!");
    } else {
      // Feedback de erro
      const { message } = await import("antd");
      message.error("Erro ao cancelar tarefa. Tente novamente.");
    }

    return result;
  }

  async pauseTask(taskId: string): Promise<ApiResponse<Task>> {
    return this.request<Task>(`/tasks/${taskId}/pause`, {
      method: "POST",
    });
  }

  async resumeTask(taskId: string): Promise<ApiResponse<Task>> {
    return this.request<Task>(`/tasks/${taskId}/resume`, {
      method: "POST",
    });
  }

  async getTasksByStatus(status: string): Promise<ApiResponse<Task[]>> {
    return this.request<Task[]>(`/tasks?status=${encodeURIComponent(status)}`);
  }

  async searchTasks(query: string): Promise<ApiResponse<Task[]>> {
    return this.request<Task[]>(`/tasks/search?q=${encodeURIComponent(query)}`);
  }

  // WebSocket connection for real-time updates
  createWebSocketConnection(
    onMessage: (data: any) => void,
    onError: (error: Event) => void = console.error,
    onClose: () => void = () => console.log("WebSocket disconnected"),
  ): WebSocket | null {
    try {
      const wsUrl = `ws://localhost:8000/ws`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log("WebSocket connected");
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error);
        }
      };

      ws.onerror = onError;
      ws.onclose = onClose;

      return ws;
    } catch (error) {
      console.error("Failed to create WebSocket connection:", error);
      return null;
    }
  }
}

export const taskService = new TaskService();
export default taskService;
