from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
import time

import psycopg
from psycopg.rows import dict_row

from .config import get_settings


RESOURCE_TYPES = ["ECS", "CCE", "RDS", "OBS", "GaussDB", "ELB"]

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS cloud_tasks (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(120) NOT NULL,
    resource_type VARCHAR(30) NOT NULL,
    owner VARCHAR(60) NOT NULL,
    priority VARCHAR(12) NOT NULL CHECK (priority IN ('low', 'medium', 'high')),
    status VARCHAR(12) NOT NULL CHECK (status IN ('planned', 'running', 'blocked', 'done')),
    due_date DATE,
    description TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cloud_tasks_status ON cloud_tasks(status);
CREATE INDEX IF NOT EXISTS idx_cloud_tasks_resource_type ON cloud_tasks(resource_type);
CREATE INDEX IF NOT EXISTS idx_cloud_tasks_due_date ON cloud_tasks(due_date);
"""

SEED_ROWS = [
    (
        "部署 openGauss 容器",
        "GaussDB",
        "数据库组",
        "high",
        "done",
        date(2026, 6, 14),
        "在华为云开发者空间中完成 openGauss 容器启动和连通性验证。",
    ),
    (
        "检查 ECS 安全组",
        "ECS",
        "运维组",
        "medium",
        "running",
        date(2026, 6, 16),
        "确认前端、后端和数据库端口只开放必要访问范围。",
    ),
    (
        "整理实验报告截图",
        "OBS",
        "文档组",
        "low",
        "planned",
        date(2026, 6, 18),
        "保存部署、接口测试和页面演示截图。",
    ),
]


def _conninfo() -> str:
    settings = get_settings()
    return (
        f"host={settings.database_host} "
        f"port={settings.database_port} "
        f"dbname={settings.database_name} "
        f"user={settings.database_user} "
        f"password={settings.database_password} "
        f"sslmode={settings.database_sslmode} "
        "connect_timeout=5"
    )


@contextmanager
def get_connection() -> Iterator[psycopg.Connection]:
    with psycopg.connect(_conninfo(), row_factory=dict_row) as conn:
        yield conn


def initialize_database(max_attempts: int = 30) -> None:
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(SCHEMA_SQL)
                    cur.execute("SELECT COUNT(*) AS count FROM cloud_tasks;")
                    count = cur.fetchone()["count"]
                    if count == 0:
                        cur.executemany(
                            """
                            INSERT INTO cloud_tasks (
                                title, resource_type, owner, priority, status, due_date, description
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s);
                            """,
                            SEED_ROWS,
                        )
                conn.commit()
            return
        except Exception as exc:
            last_error = exc
            time.sleep(min(2.0, 0.25 * attempt))
    raise RuntimeError(f"Database initialization failed: {last_error}") from last_error

