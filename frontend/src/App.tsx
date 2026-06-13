import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  Activity,
  Check,
  Database,
  Plus,
  RefreshCw,
  Search,
  Server,
  Trash2
} from "lucide-react";

import {
  createTask,
  deleteTask,
  finishTask,
  getHealth,
  getMetrics,
  getResourceTypes,
  getTasks,
  updateTask
} from "./api";
import type { CloudTask, Health, Metrics, TaskPayload, TaskPriority, TaskStatus } from "./types";

const statusOptions: Array<{ value: TaskStatus | "all"; label: string }> = [
  { value: "all", label: "全部状态" },
  { value: "planned", label: "待处理" },
  { value: "running", label: "进行中" },
  { value: "blocked", label: "受阻" },
  { value: "done", label: "已完成" }
];

const editableStatusOptions: Array<{ value: TaskStatus; label: string }> = statusOptions.filter(
  (item): item is { value: TaskStatus; label: string } => item.value !== "all"
);

const priorityOptions: Array<{ value: TaskPriority; label: string }> = [
  { value: "low", label: "低" },
  { value: "medium", label: "中" },
  { value: "high", label: "高" }
];

const emptyForm: TaskPayload = {
  title: "",
  resource_type: "ECS",
  owner: "",
  priority: "medium",
  status: "planned",
  due_date: "",
  description: ""
};

function App() {
  const [tasks, setTasks] = useState<CloudTask[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [resourceTypes, setResourceTypes] = useState<string[]>(["ECS"]);
  const [keyword, setKeyword] = useState("");
  const [statusFilter, setStatusFilter] = useState<TaskStatus | "all">("all");
  const [resourceFilter, setResourceFilter] = useState("all");
  const [form, setForm] = useState<TaskPayload>(emptyForm);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("正在连接后端服务");

  const statusMap = useMemo(
    () => Object.fromEntries(statusOptions.map((item) => [item.value, item.label])),
    []
  );

  async function loadData() {
    setBusy(true);
    try {
      const [taskResult, metricResult, healthResult, typeResult] = await Promise.all([
        getTasks({ keyword, status: statusFilter, resourceType: resourceFilter }),
        getMetrics(),
        getHealth(),
        getResourceTypes()
      ]);
      setTasks(taskResult);
      setMetrics(metricResult);
      setHealth(healthResult);
      setResourceTypes(typeResult);
      setMessage(`已同步 ${taskResult.length} 条任务`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "请求失败");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function submitTask(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    try {
      await createTask({ ...form, due_date: form.due_date || null });
      setForm({ ...emptyForm, resource_type: resourceTypes[0] ?? "ECS" });
      await loadData();
      setMessage("任务已写入 openGauss");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "新增失败");
    } finally {
      setBusy(false);
    }
  }

  async function changeStatus(task: CloudTask, status: TaskStatus) {
    setBusy(true);
    try {
      await updateTask(task.id, { status });
      await loadData();
      setMessage(`任务 #${task.id} 状态已更新`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "状态更新失败");
    } finally {
      setBusy(false);
    }
  }

  async function markDone(task: CloudTask) {
    setBusy(true);
    try {
      await finishTask(task.id);
      await loadData();
      setMessage(`任务 #${task.id} 已完成`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "完成操作失败");
    } finally {
      setBusy(false);
    }
  }

  async function removeTask(task: CloudTask) {
    setBusy(true);
    try {
      await deleteTask(task.id);
      await loadData();
      setMessage(`任务 #${task.id} 已删除`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "删除失败");
    } finally {
      setBusy(false);
    }
  }

  const doneCount = metrics?.by_status.find((item) => item.key === "done")?.count ?? 0;
  const runningCount = metrics?.by_status.find((item) => item.key === "running")?.count ?? 0;

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">openGauss / GaussDB</p>
          <h1>GaussOps 资源巡检任务台</h1>
        </div>
        <div className={`db-pill ${health?.database === "ok" ? "ok" : "warn"}`}>
          <Database size={18} aria-hidden="true" />
          <span>{health?.database === "ok" ? "数据库在线" : "数据库未就绪"}</span>
        </div>
      </header>

      <section className="toolbar" aria-label="任务筛选">
        <label className="search-box">
          <Search size={18} aria-hidden="true" />
          <input
            value={keyword}
            onChange={(event) => setKeyword(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") void loadData();
            }}
            placeholder="搜索标题、负责人、描述"
          />
        </label>
        <select
          value={statusFilter}
          onChange={(event) => setStatusFilter(event.target.value as TaskStatus | "all")}
          aria-label="按状态筛选"
        >
          {statusOptions.map((option) => (
            <option value={option.value} key={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <select
          value={resourceFilter}
          onChange={(event) => setResourceFilter(event.target.value)}
          aria-label="按资源类型筛选"
        >
          <option value="all">全部资源</option>
          {resourceTypes.map((type) => (
            <option value={type} key={type}>
              {type}
            </option>
          ))}
        </select>
        <button type="button" className="icon-button primary" onClick={() => void loadData()} disabled={busy} title="查询">
          <Search size={18} aria-hidden="true" />
          <span>查询</span>
        </button>
        <button type="button" className="icon-button" onClick={() => void loadData()} disabled={busy} title="刷新">
          <RefreshCw size={18} aria-hidden="true" />
          <span>刷新</span>
        </button>
      </section>

      <section className="metric-grid" aria-label="运行概览">
        <article className="metric-card">
          <span>任务总数</span>
          <strong>{metrics?.total ?? "--"}</strong>
        </article>
        <article className="metric-card accent-green">
          <span>已完成</span>
          <strong>{doneCount}</strong>
        </article>
        <article className="metric-card accent-blue">
          <span>进行中</span>
          <strong>{runningCount}</strong>
        </article>
        <article className="metric-card accent-red">
          <span>逾期未完成</span>
          <strong>{metrics?.overdue ?? "--"}</strong>
        </article>
      </section>

      <div className="content-grid">
        <form className="task-form" onSubmit={(event) => void submitTask(event)}>
          <div className="section-title">
            <Plus size={18} aria-hidden="true" />
            <h2>新增巡检任务</h2>
          </div>
          <label>
            <span>任务标题</span>
            <input
              required
              minLength={2}
              maxLength={120}
              value={form.title}
              onChange={(event) => setForm({ ...form, title: event.target.value })}
            />
          </label>
          <div className="form-row">
            <label>
              <span>资源类型</span>
              <select
                value={form.resource_type}
                onChange={(event) => setForm({ ...form, resource_type: event.target.value })}
              >
                {resourceTypes.map((type) => (
                  <option value={type} key={type}>
                    {type}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>优先级</span>
              <select
                value={form.priority}
                onChange={(event) => setForm({ ...form, priority: event.target.value as TaskPriority })}
              >
                {priorityOptions.map((option) => (
                  <option value={option.value} key={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="form-row">
            <label>
              <span>负责人</span>
              <input
                required
                minLength={2}
                maxLength={60}
                value={form.owner}
                onChange={(event) => setForm({ ...form, owner: event.target.value })}
              />
            </label>
            <label>
              <span>截止日期</span>
              <input
                type="date"
                value={form.due_date ?? ""}
                onChange={(event) => setForm({ ...form, due_date: event.target.value })}
              />
            </label>
          </div>
          <label>
            <span>初始状态</span>
            <select
              value={form.status}
              onChange={(event) => setForm({ ...form, status: event.target.value as TaskStatus })}
            >
              {editableStatusOptions.map((option) => (
                <option value={option.value} key={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>任务描述</span>
            <textarea
              maxLength={500}
              rows={4}
              value={form.description}
              onChange={(event) => setForm({ ...form, description: event.target.value })}
            />
          </label>
          <button type="submit" className="icon-button primary wide" disabled={busy} title="写入数据库">
            <Plus size={18} aria-hidden="true" />
            <span>写入数据库</span>
          </button>
        </form>

        <section className="table-panel">
          <div className="section-title table-title">
            <Server size={18} aria-hidden="true" />
            <h2>任务列表</h2>
            <span className="status-text">{message}</span>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>任务</th>
                  <th>资源</th>
                  <th>负责人</th>
                  <th>优先级</th>
                  <th>状态</th>
                  <th>截止</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {tasks.map((task) => (
                  <tr key={task.id}>
                    <td>
                      <div className="task-title">{task.title}</div>
                      <div className="task-desc">{task.description || "无描述"}</div>
                    </td>
                    <td>
                      <span className="resource-chip">{task.resource_type}</span>
                    </td>
                    <td>{task.owner}</td>
                    <td>
                      <span className={`priority ${task.priority}`}>
                        {priorityOptions.find((item) => item.value === task.priority)?.label}
                      </span>
                    </td>
                    <td>
                      <select
                        value={task.status}
                        onChange={(event) => void changeStatus(task, event.target.value as TaskStatus)}
                        aria-label={`更新任务 ${task.id} 状态`}
                      >
                        {editableStatusOptions.map((option) => (
                          <option value={option.value} key={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td>{task.due_date ?? "-"}</td>
                    <td>
                      <div className="row-actions">
                        <button
                          type="button"
                          className="square-button"
                          onClick={() => void markDone(task)}
                          disabled={busy || task.status === "done"}
                          title="标记完成"
                        >
                          <Check size={17} aria-hidden="true" />
                        </button>
                        <button
                          type="button"
                          className="square-button danger"
                          onClick={() => void removeTask(task)}
                          disabled={busy}
                          title="删除任务"
                        >
                          <Trash2 size={17} aria-hidden="true" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {tasks.length === 0 && (
              <div className="empty-state">
                <Activity size={22} aria-hidden="true" />
                <span>暂无匹配任务</span>
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}

export default App;

