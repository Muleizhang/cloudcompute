from datetime import date

from pydantic import ValidationError

from app.models import TaskCreate


def test_task_create_accepts_valid_payload():
    task = TaskCreate(
        title="检查 CCE 节点状态",
        resource_type="CCE",
        owner="运维组",
        priority="high",
        status="running",
        due_date=date(2026, 6, 18),
        description="确认节点和容器组状态正常。",
    )

    assert task.resource_type == "CCE"
    assert task.priority == "high"


def test_task_create_rejects_unknown_resource_type():
    try:
        TaskCreate(title="非法资源", resource_type="Unknown", owner="运维组")
    except ValidationError as exc:
        assert "resource_type" in str(exc)
    else:
        raise AssertionError("ValidationError was not raised")

