export type TaskStatus = "planned" | "running" | "blocked" | "done";
export type TaskPriority = "low" | "medium" | "high";

export interface CloudTask {
  id: number;
  title: string;
  resource_type: string;
  owner: string;
  priority: TaskPriority;
  status: TaskStatus;
  due_date: string | null;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface TaskPayload {
  title: string;
  resource_type: string;
  owner: string;
  priority: TaskPriority;
  status: TaskStatus;
  due_date: string | null;
  description: string;
}

export interface MetricBucket {
  key: string;
  count: number;
}

export interface Metrics {
  total: number;
  overdue: number;
  by_status: MetricBucket[];
  by_resource_type: MetricBucket[];
}

export interface SparkAnalytics {
  available: boolean;
  generated_at: string | null;
  total_tasks: number;
  done_tasks: number;
  running_tasks: number;
  overdue_tasks: number;
  high_priority_open_tasks: number;
  completion_rate: number;
}

export interface Health {
  service: string;
  database: string;
  detail: string;
}
