from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_code_quality_workflow_runs_frontend_test_file_size_guard() -> None:
    content = (PROJECT_ROOT / ".github" / "workflows" / "code-quality.yml").read_text(encoding="utf-8")

    assert "Frontend/Test File Size Guard" in content
    assert "python scripts/compliance/file_size_guardrail.py --format json" in content
    assert "frontend-test-file-size-gate-report.json" in content


def test_code_quality_workflow_skips_generated_frontend_api_types_in_file_size_guard() -> None:
    content = (PROJECT_ROOT / ".github" / "workflows" / "code-quality.yml").read_text(encoding="utf-8")
    file_size_section = content.split("- name: Frontend/Test File Size Guard", 1)[1].split("- name: PM2 First-Class Gate", 1)[0]

    assert 'if [[ "$changed_file" =~ ^web/frontend/src/api/types/ ]]; then' in file_size_section
    assert 'echo "Skipping generated frontend API type file: $changed_file"' in file_size_section
    assert "continue" in file_size_section


def test_pre_commit_config_registers_frontend_test_file_size_guard() -> None:
    content = (PROJECT_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")

    assert "id: frontend-test-file-size-guard" in content
    assert "name: Frontend/Test File Size Guard" in content
    assert "python scripts/compliance/file_size_guardrail.py --format text" in content
    assert "web/frontend" in content
    assert "tests" in content


def test_githooks_pre_commit_runs_frontend_test_file_size_guard() -> None:
    content = (PROJECT_ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")

    assert "Running frontend/test file size guard" in content
    assert "frontend-test-file-size-guard" in content
    assert "file_size_guardrail.py" in content
