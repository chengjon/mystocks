from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_pre_commit_config_registers_directory_governance_hook() -> None:
    content = (PROJECT_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")

    assert "id: directory-governance" in content
    assert "name: Directory Governance Check" in content
    assert "bash scripts/maintenance/check-structure.sh --staged" in content


def test_githooks_pre_commit_delegates_to_staged_directory_governance() -> None:
    content = (PROJECT_ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")

    assert "scripts/maintenance/check-structure.sh" in content
    assert "--staged" in content
    assert "directory governance" in content.lower()


def test_pre_commit_config_registers_production_python_guardrail_hook() -> None:
    content = (PROJECT_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")

    assert "id: production-python-guardrails" in content
    assert "name: Production Python Guardrails" in content
    assert "python scripts/compliance/production_python_guardrails.py" in content
    assert "^((src/)|(web/backend/app/)).*\\.py$" in content


def test_githooks_pre_commit_runs_production_python_guardrails() -> None:
    content = (PROJECT_ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")

    assert "production_python_guardrails.py" in content
    assert "Running production Python guardrails" in content
    assert "SKIP=production-python-guardrails" in content or "production-python-guardrails" in content


def test_code_quality_workflow_runs_delta_directory_governance_check() -> None:
    content = (PROJECT_ROOT / ".github" / "workflows" / "code-quality.yml").read_text(encoding="utf-8")

    assert "Directory Governance Check" in content
    assert "python scripts/maintenance/check_structure.py --format json" in content
    assert "--path" in content
