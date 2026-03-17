from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_ROOT = PROJECT_ROOT / ".github" / "workflows"


def test_github_actions_workflows_do_not_use_deprecated_artifact_v3() -> None:
    deprecated_hits: list[str] = []

    for workflow in sorted(WORKFLOW_ROOT.glob("*.yml")):
        content = workflow.read_text(encoding="utf-8", errors="ignore")
        if "actions/upload-artifact@v3" in content or "actions/download-artifact@v3" in content:
            deprecated_hits.append(workflow.relative_to(PROJECT_ROOT).as_posix())

    assert deprecated_hits == []
