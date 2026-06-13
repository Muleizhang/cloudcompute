from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import RESOURCE_TYPES, get_connection, initialize_database
from .models import HealthOut, MetricsOut, TaskCreate, TaskOut, TaskUpdate


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _fetch_task(task_id: int) -> dict[str, Any]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cloud_tasks WHERE id = %s;", (task_id,))
            row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return row


@app.get("/api/health", response_model=HealthOut)
def health() -> HealthOut:
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version() AS version;")
                detail = cur.fetchone()["version"]
        return HealthOut(service="ok", database="ok", detail=detail)
    except Exception as exc:
        return HealthOut(service="ok", database="unavailable", detail=str(exc))


@app.get("/api/resource-types", response_model=list[str])
def resource_types() -> list[str]:
    return RESOURCE_TYPES


@app.get("/api/tasks", response_model=list[TaskOut])
def list_tasks(
    keyword: str | None = Query(default=None, max_length=80),
    status_filter: str | None = Query(default=None, alias="status"),
    resource_type: str | None = Query(default=None),
) -> list[dict[str, Any]]:
    where: list[str] = []
    params: list[Any] = []

    if keyword:
        like_value = f"%{keyword.lower()}%"
        where.append(
            "(LOWER(title) LIKE %s OR LOWER(owner) LIKE %s OR LOWER(description) LIKE %s)"
        )
        params.extend([like_value, like_value, like_value])

    if status_filter and status_filter != "all":
        where.append("status = %s")
        params.append(status_filter)

    if resource_type and resource_type != "all":
        where.append("resource_type = %s")
        params.append(resource_type)

    query = "SELECT * FROM cloud_tasks"
    if where:
        query += " WHERE " + " AND ".join(where)
    query += """
        ORDER BY
            CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
            COALESCE(due_date, DATE '2999-12-31'),
            id DESC;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return list(cur.fetchall())


@app.post("/api/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> dict[str, Any]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO cloud_tasks (
                    title, resource_type, owner, priority, status, due_date, description
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING *;
                """,
                (
                    payload.title,
                    payload.resource_type,
                    payload.owner,
                    payload.priority,
                    payload.status,
                    payload.due_date,
                    payload.description,
                ),
            )
            row = cur.fetchone()
        conn.commit()
    return row


@app.patch("/api/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate) -> dict[str, Any]:
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return _fetch_task(task_id)

    assignments = [f"{column} = %s" for column in updates]
    values = list(updates.values())
    values.append(task_id)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE cloud_tasks
                SET {", ".join(assignments)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING *;
                """,
                values,
            )
            row = cur.fetchone()
        conn.commit()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return row


@app.post("/api/tasks/{task_id}/finish", response_model=TaskOut)
def finish_task(task_id: int) -> dict[str, Any]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE cloud_tasks
                SET status = 'done', updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING *;
                """,
                (task_id,),
            )
            row = cur.fetchone()
        conn.commit()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return row


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> Response:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM cloud_tasks WHERE id = %s;", (task_id,))
            deleted = cur.rowcount
        conn.commit()

    if deleted == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/metrics", response_model=MetricsOut)
def metrics() -> dict[str, Any]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM cloud_tasks;")
            total = cur.fetchone()["total"]

            cur.execute(
                """
                SELECT COUNT(*) AS overdue
                FROM cloud_tasks
                WHERE due_date < CURRENT_DATE AND status <> 'done';
                """
            )
            overdue = cur.fetchone()["overdue"]

            cur.execute(
                """
                SELECT status AS key, COUNT(*) AS count
                FROM cloud_tasks
                GROUP BY status
                ORDER BY status;
                """
            )
            by_status = list(cur.fetchall())

            cur.execute(
                """
                SELECT resource_type AS key, COUNT(*) AS count
                FROM cloud_tasks
                GROUP BY resource_type
                ORDER BY resource_type;
                """
            )
            by_resource_type = list(cur.fetchall())

    return {
        "total": total,
        "overdue": overdue,
        "by_status": by_status,
        "by_resource_type": by_resource_type,
    }

