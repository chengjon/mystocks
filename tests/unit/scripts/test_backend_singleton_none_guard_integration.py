from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_code_quality_workflow_runs_backend_singleton_none_guard() -> None:
    content = (PROJECT_ROOT / ".github" / "workflows" / "code-quality.yml").read_text(encoding="utf-8")

    assert "Backend Singleton None Guard" in content
    assert "python scripts/compliance/backend_singleton_none_guard.py --format json" in content
    assert "backend-singleton-none-guard-report.json" in content


def test_pre_commit_config_registers_backend_singleton_none_guard() -> None:
    content = (PROJECT_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")

    assert "id: backend-singleton-none-guard" in content
    assert "name: Backend Singleton None Guard" in content
    assert "python scripts/compliance/backend_singleton_none_guard.py --format text" in content
    assert "^((src/)|(web/backend/app/)).*\\.py$" in content


def test_githooks_pre_commit_runs_backend_singleton_none_guard() -> None:
    content = (PROJECT_ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")

    assert "backend_singleton_none_guard.py" in content
    assert "Running backend singleton None guard" in content
    assert "backend-singleton-none-guard" in content
