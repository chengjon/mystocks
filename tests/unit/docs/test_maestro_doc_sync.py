from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_mongo_coordination_guide_uses_current_checklist_path_and_cli_surface() -> None:
    guide = (PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "MONGO_MULTICLI_COORDINATION_GUIDE.md").read_text(
        encoding="utf-8"
    )

    assert "docs/guides/multi-cli-tasks/MONGO_MULTICLI_OPERATION_CHECKLIST.md" in guide
    assert "docs/guides/MONGO_MULTICLI_OPERATION_CHECKLIST.md" not in guide
    assert "python scripts/runtime/coordctl.py plan add" not in guide
    assert "python scripts/runtime/coordctl.py plan mark" not in guide
    assert "python scripts/runtime/coordctl.py work mark" in guide
    assert "python scripts/runtime/coordctl.py update add" in guide
    assert "python scripts/runtime/coordctl.py work transition" in guide
    assert "mystocks-mongodb" in guide
    assert "coordctl.py` / `maestro_collab.py`" in guide
    assert "export_collab_snapshots.py" in guide
    assert "`error_code`" in guide
    assert "`message`" in guide
    assert "python scripts/runtime/coordctl.py work list --output json" in guide
    assert "python scripts/runtime/smoke_mongo_multicli.py" in guide
    assert "python scripts/runtime/smoke_graphiti_preflight.py --actor-cli cli-preflight" in guide
    assert "/tmp/mongo-collab-snapshots-codex" in guide
    assert "bash scripts/runtime/run_local_maestro_acceptance.sh" in guide
    assert "python scripts/runtime/run_local_maestro_acceptance.sh" not in guide


def test_mongo_operation_checklist_matches_current_control_plane_commands() -> None:
    checklist = (
        PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "MONGO_MULTICLI_OPERATION_CHECKLIST.md"
    ).read_text(encoding="utf-8")

    assert "`work claim`" not in checklist
    assert "`plan add`" not in checklist
    assert "`plan mark`" not in checklist
    assert "`work submit`" not in checklist
    assert "`work mark`" in checklist
    assert "`update add`" in checklist
    assert "`work transition`" in checklist
    assert "`error_code`" in checklist
    assert "`message`" in checklist
    assert "bash scripts/runtime/run_local_maestro_acceptance.sh" in checklist
    assert "python scripts/runtime/run_local_maestro_acceptance.sh" not in checklist


def test_graphiti_workflow_guide_mentions_structured_json_error_output() -> None:
    guide = (PROJECT_ROOT / "docs" / "guides" / "ai-tools" / "GRAPHITI_MCP_WORKFLOW.md").read_text(encoding="utf-8")

    assert "`error_code`" in guide
    assert "`message`" in guide
    assert "python scripts/runtime/smoke_graphiti_cli.py" in guide
    assert "python scripts/runtime/smoke_graphiti_preflight.py --actor-cli cli-preflight" in guide
    assert "bash scripts/runtime/run_local_maestro_acceptance.sh" in guide
    assert "python scripts/runtime/run_local_maestro_acceptance.sh" not in guide


def test_maestro_quick_start_surfaces_repo_local_acceptance_entrypoint() -> None:
    guide = (PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "MAESTRO_QUICK_START.md").read_text(
        encoding="utf-8"
    )

    assert "bash scripts/runtime/run_local_maestro_acceptance.sh" in guide
    assert "python scripts/runtime/run_local_maestro_acceptance.sh" not in guide
    assert "docs/reports/tasks/2026-04-03-maestro-local-acceptance-report.md" in guide


def test_maestro_summary_and_task_index_keep_local_acceptance_entry_discoverable() -> None:
    summary = (PROJECT_ROOT / "docs" / "guides" / "multi-cli-tasks" / "MAESTRO_SUMMARY.md").read_text(
        encoding="utf-8"
    )
    task_index = (PROJECT_ROOT / "docs" / "reports" / "tasks" / "INDEX.md").read_text(encoding="utf-8")

    assert "### Repo-Local Acceptance" in summary
    assert "bash scripts/runtime/run_local_maestro_acceptance.sh" in summary
    assert "docs/reports/tasks/2026-04-03-maestro-local-acceptance-report.md" in summary
    assert "2026-04-03-maestro-local-acceptance-report" in task_index
