import { Todo, TodoCreate, TodoUpdate } from "@/types/todo";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Auth token management
let _authToken: string | null = null;

export function setAuthToken(token: string | null) {
  _authToken = token;
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_URL}${endpoint}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  // Add auth token if available
  if (_authToken) {
    headers["Authorization"] = `Bearer ${_authToken}`;
  }

  const config: RequestInit = {
    ...options,
    headers,
  };

  const response = await fetch(url, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error.detail || "Request failed");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

export async function fetchTodos(): Promise<Todo[]> {
  return request<Todo[]>("/api/todos");
}

export async function createTodo(data: TodoCreate): Promise<Todo> {
  return request<Todo>("/api/todos", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateTodo(id: string, data: TodoUpdate): Promise<Todo> {
  return request<Todo>(`/api/todos/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteTodo(id: string): Promise<void> {
  return request<void>(`/api/todos/${id}`, {
    method: "DELETE",
  });
}

export async function toggleTodo(id: string): Promise<Todo> {
  return request<Todo>(`/api/todos/${id}/toggle`, {
    method: "PATCH",
  });
}

export { ApiError };
