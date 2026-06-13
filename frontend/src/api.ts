import type { CloudTask, Health, Metrics, TaskPayload, TaskStatus } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {})
    },
    ...options
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `HTTP ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function getHealth(): Promise<Health> {
  return request<Health>("/api/health");
}

export function getResourceTypes(): Promise<string[]> {
  return request<string[]>("/api/resource-types");
}

export function getMetrics(): Promise<Metrics> {
  return request<Metrics>("/api/metrics");
}

export function getTasks(params: {
  keyword?: string;
  status?: TaskStatus | "all";
  resourceType?: string;
}): Promise<CloudTask[]> {
  const search = new URLSearchParams();
  if (params.keyword) search.set("keyword", params.keyword);
  if (params.status && params.status !== "all") search.set("status", params.status);
  if (params.resourceType && params.resourceType !== "all") {
    search.set("resource_type", params.resourceType);
  }
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return request<CloudTask[]>(`/api/tasks${suffix}`);
}

export function createTask(payload: TaskPayload): Promise<CloudTask> {
  return request<CloudTask>("/api/tasks", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function updateTask(id: number, payload: Partial<TaskPayload>): Promise<CloudTask> {
  return request<CloudTask>(`/api/tasks/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

export function finishTask(id: number): Promise<CloudTask> {
  return request<CloudTask>(`/api/tasks/${id}/finish`, { method: "POST" });
}

export function deleteTask(id: number): Promise<void> {
  return request<void>(`/api/tasks/${id}`, { method: "DELETE" });
}

