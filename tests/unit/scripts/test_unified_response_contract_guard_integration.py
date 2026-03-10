from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_code_quality_workflow_runs_unified_response_contract_guard() -> None:
    content = (PROJECT_ROOT / ".github" / "workflows" / "code-quality.yml").read_text(encoding="utf-8")

    assert "UnifiedResponse Contract Guard" in content
    assert "python scripts/compliance/unified_response_contract_guard.py --format json" in content
    assert "unified-response-contract-guard-report.json" in content


def test_pre_commit_config_registers_unified_response_contract_guard() -> None:
    content = (PROJECT_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")

    assert "id: unified-response-contract-guard" in content
    assert "name: UnifiedResponse Contract Guard" in content
    assert "python scripts/compliance/unified_response_contract_guard.py --format text" in content
    assert "^web/backend/app/api/.*\\.py$" in content


def test_githooks_pre_commit_runs_unified_response_contract_guard() -> None:
    content = (PROJECT_ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")

    assert "unified_response_contract_guard.py" in content
    assert "Running UnifiedResponse contract guard" in content
    assert "unified-response-contract-guard" in content
