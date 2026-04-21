from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_frontend_testing_workflow_runs_artdeco_token_lint() -> None:
    content = (PROJECT_ROOT / ".github" / "workflows" / "frontend-testing.yml").read_text(encoding="utf-8")

    assert "Run ArtDeco token changed-file gate" in content
    assert "npm run lint:artdeco:changed" in content
