from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TaskStatus = Literal["planned", "running", "blocked", "done"]
TaskPriority = Literal["low", "medium", "high"]
ResourceType = Literal["ECS", "CCE", "RDS", "OBS", "GaussDB", "ELB"]


class TaskBase(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    resource_type: ResourceType
    owner: str = Field(min_length=2, max_length=60)
    priority: TaskPriority = "medium"
    status: TaskStatus = "planned"
    due_date: date | None = None
    description: str = Field(default="", max_length=500)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=120)
    resource_type: ResourceType | None = None
    owner: str | None = Field(default=None, min_length=2, max_length=60)
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    due_date: date | None = None
    description: str | None = Field(default=None, max_length=500)


class TaskOut(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class MetricBucket(BaseModel):
    key: str
    count: int


class MetricsOut(BaseModel):
    total: int
    overdue: int
    by_status: list[MetricBucket]
    by_resource_type: list[MetricBucket]


class HealthOut(BaseModel):
    service: str
    database: str
    detail: str


class SparkAnalyticsOut(BaseModel):
    available: bool
    generated_at: datetime | None = None
    total_tasks: int
    done_tasks: int
    running_tasks: int
    overdue_tasks: int
    high_priority_open_tasks: int
    completion_rate: float
