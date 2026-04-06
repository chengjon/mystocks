from __future__ import annotations

from pathlib import Path

from scripts.dev.quality_gate.governance_report_fields_guard import (
    detect_structural_debt_markdown_violations,
    is_structural_debt_governance_file,
)


def test_is_structural_debt_governance_file_detects_cleanup_tasks() -> None:
    assert is_structural_debt_governance_file(
        Path("reports/governance/2026-04-06-active-tree-legacy-backup-cleanup.TASK.md"),
        "# TASK\n- Issue Title: `Classify and clean active-tree legacy backup files`\n",
    )


def test_is_structural_debt_governance_file_ignores_regular_phase_tasks() -> None:
    assert not is_structural_debt_governance_file(
        Path("reports/governance/2026-04-03-frontend-mainline-phase-1.TASK.md"),
        "# TASK\n- Issue Title: `Frontend Mainline Phase 1`\n- Objective: `Track routine frontend batch progress.`\n",
    )


def test_is_structural_debt_governance_file_ignores_historical_legacy_block_exports() -> None:
    assert not is_structural_debt_governance_file(
        Path("reports/governance/2026-03-05-mock-manager-fix.TASK.md"),
        "# TASK\n"
        "- Issue Title: `Mock Manager Repair And End-To-End Verification`\n"
        "- Objective: `Preserve the workstream as dedicated Mongo history instead of leaving it only in archived root markdown.`\n"
        "- Decision Basis: `Imported from archived root TASK-REPORT legacy blocks on 2026-04-03.`\n",
    )


def test_is_structural_debt_governance_file_ignores_runtime_audit_compatibility_wording() -> None:
    assert not is_structural_debt_governance_file(
        Path("reports/governance/2026-03-12-data-db-runtime-audit.TASK.md"),
        "# TASK\n"
        "- Issue Title: `Data And DB Runtime Audit Convergence`\n"
        "- Objective: `Preserve the multi-round runtime audit, compatibility isolation, and final verification sweep as a single Mongo-backed historical workstream.`\n",
    )


def test_detect_structural_debt_markdown_violations_reports_missing_sections(tmp_path: Path) -> None:
    path = tmp_path / "reports/governance/2026-04-06-cleanup.TASK.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# TASK\n\n"
        "- Issue Title: `Legacy cleanup`\n"
        "- Objective: `Remove backup files from active tree.`\n",
        encoding="utf-8",
    )

    violations = detect_structural_debt_markdown_violations([path], project_root=tmp_path)

    messages = [item.message for item in violations]
    assert any("Structural Debt Disclosure" in message for message in messages)
    assert any("canonical_source" in message for message in messages)
    assert any("Metrics Lens" in message for message in messages)


def test_detect_structural_debt_markdown_violations_allows_complete_task_with_na_values(tmp_path: Path) -> None:
    path = tmp_path / "reports/governance/2026-04-06-cleanup.TASK.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# TASK\n\n"
        "- Issue Title: `Legacy cleanup`\n"
        "- Objective: `Remove backup files from active tree.`\n\n"
        "## Structural Debt Disclosure\n\n"
        "- canonical_source: `current active module`\n"
        "- compatibility_surface: `N/A`\n"
        "- callers_or_consumers: `N/A`\n"
        "- verification_command: `rg -n legacy reports/governance`\n"
        "- exit_condition: `N/A`\n\n"
        "## Cleanup / Removal Decision\n\n"
        "- code_path_verdict: `safe-to-remove`\n"
        "- function_tree_verdict: `重复冗余`\n"
        "- removal_basis: `proven redundant`\n"
        "- keep_reason: `N/A`\n\n"
        "## Temporary / Compatibility Asset Ledger\n\n"
        "| path | type | owner | introduced_by | reason | exit_condition | planned_removal_milestone | target_removal_date | current_status |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
        "| `N/A` | `other` | `main` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` |\n\n"
        "## Metrics Lens\n\n"
        "| metric | measured | baseline | inferred | target | source_or_command |\n"
        "|---|---|---|---|---|---|\n"
        "| `cleanup_count` | `1` | `N/A` | `N/A` | `1` | `manual` |\n",
        encoding="utf-8",
    )

    violations = detect_structural_debt_markdown_violations([path], project_root=tmp_path)

    assert violations == []


def test_detect_structural_debt_markdown_violations_accepts_report_delta_section(tmp_path: Path) -> None:
    path = tmp_path / "reports/governance/2026-04-06-cleanup.TASK-REPORT.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# TASK-REPORT\n\n"
        "- Issue Title: `Legacy cleanup`\n"
        "- Latest Progress: `Removed backup files.`\n\n"
        "#### Structural Debt Disclosure\n\n"
        "- canonical_source: `current active module`\n"
        "- compatibility_surface: `N/A`\n"
        "- callers_or_consumers: `N/A`\n"
        "- verification_command: `rg -n legacy reports/governance`\n"
        "- exit_condition: `N/A`\n\n"
        "#### Cleanup / Removal Decision\n\n"
        "- code_path_verdict: `safe-to-remove`\n"
        "- function_tree_verdict: `重复冗余`\n"
        "- removal_basis: `proven redundant`\n"
        "- keep_reason: `N/A`\n\n"
        "#### Temporary / Compatibility Asset Ledger Delta\n\n"
        "| path | type | owner | introduced_by | reason | exit_condition | planned_removal_milestone | target_removal_date | current_status |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
        "| `N/A` | `other` | `main` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` |\n\n"
        "#### Metrics Lens\n\n"
        "| metric | measured | baseline | inferred | target | source_or_command |\n"
        "|---|---|---|---|---|---|\n"
        "| `cleanup_count` | `1` | `N/A` | `N/A` | `1` | `manual` |\n",
        encoding="utf-8",
    )

    violations = detect_structural_debt_markdown_violations([path], project_root=tmp_path)

    assert violations == []


def test_detect_structural_debt_markdown_violations_requires_structured_introduced_by(tmp_path: Path) -> None:
    path = tmp_path / "reports/governance/2026-04-06-cleanup.TASK.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# TASK\n\n"
        "- Issue Title: `Legacy cleanup`\n"
        "- Objective: `Remove backup files from active tree.`\n\n"
        "## Structural Debt Disclosure\n\n"
        "- canonical_source: `current active module`\n"
        "- compatibility_surface: `N/A`\n"
        "- callers_or_consumers: `N/A`\n"
        "- verification_command: `rg -n legacy reports/governance`\n"
        "- exit_condition: `N/A`\n\n"
        "## Cleanup / Removal Decision\n\n"
        "- code_path_verdict: `safe-to-remove`\n"
        "- function_tree_verdict: `重复冗余`\n"
        "- removal_basis: `proven redundant`\n"
        "- keep_reason: `N/A`\n\n"
        "## Temporary / Compatibility Asset Ledger\n\n"
        "| path | type | owner | introduced_by | reason | exit_condition | planned_removal_milestone | target_removal_date | current_status |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
        "| `foo.backup` | `backup` | `main` | `historical snapshot` | `legacy file` | `remove after proof` | `phase-x` | `2026-04-06` | `planned-removal` |\n\n"
        "## Metrics Lens\n\n"
        "| metric | measured | baseline | inferred | target | source_or_command |\n"
        "|---|---|---|---|---|---|\n"
        "| `cleanup_count` | `1` | `N/A` | `N/A` | `1` | `manual` |\n",
        encoding="utf-8",
    )

    violations = detect_structural_debt_markdown_violations([path], project_root=tmp_path)

    assert any("introduced_by must include issue_or_task=...; created_at=..." in item.message for item in violations)
