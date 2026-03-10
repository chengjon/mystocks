from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_code_quality_workflow_runs_production_python_guardrails() -> None:
    content = (PROJECT_ROOT / ".github" / "workflows" / "code-quality.yml").read_text(encoding="utf-8")

    assert "Production Python Guardrails" in content
    assert "python scripts/compliance/production_python_guardrails.py --format json" in content
    assert "production-python-guardrails-report.json" in content


def test_pull_request_template_includes_large_file_self_check() -> None:
    content = (PROJECT_ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8")

    assert "## Large File Governance (Required)" in content
    assert "largest_touched_python_file:" in content
    assert "independent_responsibility_added:" in content
    assert "large_file_guardrails:" in content
    assert "backlog_updated:" in content
