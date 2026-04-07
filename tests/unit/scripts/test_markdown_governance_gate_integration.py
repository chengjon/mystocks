from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_pre_commit_config_registers_markdown_governance_gate_hook() -> None:
    content = (PROJECT_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")

    assert "id: markdown-governance-gate" in content
    assert "name: Markdown Governance Gate" in content
    assert "python scripts/compliance/markdown_governance_gate.py" in content
    assert "files: \\.md$" in content


def test_githooks_pre_commit_runs_markdown_governance_gate() -> None:
    content = (PROJECT_ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")

    assert "run_markdown_governance_gate" in content
    assert "markdown_governance_gate.py" in content
    assert "SKIP=markdown-governance-gate" in content or "markdown-governance-gate" in content


def test_directory_compliance_workflow_runs_markdown_governance_gate() -> None:
    content = (PROJECT_ROOT / ".github" / "workflows" / "directory-compliance.yml").read_text(encoding="utf-8")

    assert "Check markdown governance boundaries" in content
    assert "python scripts/compliance/markdown_governance_gate.py --root-dir . --format json" in content
    assert "'*.md'" in content
    assert "'**/*.md'" in content
