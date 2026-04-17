from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from app.api import tasks as module
from app.models.task import TaskConfig, TaskResponse


def test_tasks_route_source_contains_no_direct_use_mock_env_reads():
    source = Path(module.__file__).read_text(encoding="utf-8")

    assert 'os.getenv("USE_MOCK_DATA"' not in source


@pytest.mark.asyncio
async def test_register_task_uses_runtime_manager_even_when_mock_enabled(monkeypatch):
    monkeypatch.setattr(module.settings, "use_mock_apis", True, raising=False)

    captured: dict[str, str] = {}

    def _register_task(task_config: TaskConfig) -> TaskResponse:
        captured["task_id"] = task_config.task_id
        return TaskResponse(
            success=True,
            message="Task registered successfully",
            task_id=task_config.task_id,
            data={"task_id": task_config.task_id},
        )

    monkeypatch.setattr(module.task_manager, "register_task", _register_task)
    monkeypatch.setattr(module, "check_task_rate_limit", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(module, "log_task_operation", lambda **_kwargs: None)

    response = await module.register_task(
        task_config=TaskConfig(
            task_id="daily_sync_job",
            task_name="日终同步任务",
            task_type="manual",
            task_module="app.jobs.daily_sync",
            task_function="run_daily_sync",
        ),
        current_user=SimpleNamespace(id=1, username="tester"),
    )

    assert captured["task_id"] == "daily_sync_job"
    assert response.data["created_by"] == "tester"


@pytest.mark.asyncio
async def test_tasks_health_uses_runtime_state_even_when_mock_enabled(monkeypatch):
    monkeypatch.setattr(module.settings, "use_mock_apis", True, raising=False)
    monkeypatch.setattr(module.task_manager, "list_tasks", lambda: ["task-a", "task-b"])
    monkeypatch.setattr(module.task_manager, "running_tasks", {"task-a": object()}, raising=False)
    monkeypatch.setattr(module.task_manager, "executions", {"exec-1": object(), "exec-2": object()}, raising=False)

    result = await module.tasks_health()

    assert result["status"] == "healthy"
    assert result["total_tasks"] == 2
    assert result["running_tasks"] == 1
    assert result["total_executions"] == 2
    assert result["mock_mode"] is True
