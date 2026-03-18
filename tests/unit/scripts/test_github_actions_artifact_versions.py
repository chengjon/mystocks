from __future__ import annotations

from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_ROOT = PROJECT_ROOT / ".github" / "workflows"


def test_target_workflows_are_valid_yaml() -> None:
    for filename in ("mainline-governance.yml", "directory-compliance.yml"):
        workflow = WORKFLOW_ROOT / filename
        yaml.safe_load(workflow.read_text(encoding="utf-8", errors="ignore"))


def test_mainline_governance_summary_avoids_heredoc_python_block() -> None:
    workflow = WORKFLOW_ROOT / "mainline-governance.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "python - <<'PY'" not in content
    assert "python -c '" in content


def test_directory_compliance_uses_budgeted_root_file_threshold_variable() -> None:
    workflow = WORKFLOW_ROOT / "directory-compliance.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert 'MAX_ROOT_FILES=40' in content
    assert 'echo "Root files: $ROOT_FILES (max: $MAX_ROOT_FILES)"' in content
    assert 'if [ "$ROOT_FILES" -gt "$MAX_ROOT_FILES" ]' in content
    assert 'if [ "$ROOT_FILES" -gt 20 ]' not in content
