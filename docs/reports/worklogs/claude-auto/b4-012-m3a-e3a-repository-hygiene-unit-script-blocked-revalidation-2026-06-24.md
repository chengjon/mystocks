# B4.012-M3a-E3a Repository Hygiene Unit Script Blocked Revalidation

Date: 2026-06-24
Node: `b4-012-m3a-e3a-repository-hygiene-unit-script-authorization`
Program: `.governance/programs/artdeco-web-design-governance`
Mode: no-source blocked audit

## Scope

This is a no-source revalidation of the E3a blocked parent node after the downstream E3a-R1 lint-only recovery and E3b docs truth decision lane were closed.

No implementation authorization is granted by this worklog.

## Current Node State

- `b4-012-m3a-e3a-repository-hygiene-unit-script-authorization`
  - Status: `blocked`
  - Unblock target: `authorization-prepared`
  - Previous blocker: focused repository-hygiene pytest remained broadly red at `87 failed / 15 passed`.
- `b4-012-m3a-e3a-r1-repository-hygiene-lint-only-recovery-authorization`
  - Status: `closed`
- `b4-012-m3a-e3b-repository-hygiene-docs-truth-drift-decision`
  - Status: `closed`

## Fresh Verification

Commands executed against `tests/unit/scripts/test_repository_hygiene_paths.py`:

- `python -m py_compile tests/unit/scripts/test_repository_hygiene_paths.py`
  - Result: passed.
- `ruff check tests/unit/scripts/test_repository_hygiene_paths.py`
  - Result: passed, `All checks passed!`.
- `pytest -q --no-cov -o addopts='' --tb=short tests/unit/scripts/test_repository_hygiene_paths.py`
  - Result: failed, `58 failed, 44 passed in 6.42s`.

Failure family summary from the focused pytest run:

- `docs-guides`: 36
- `reports`: 12
- `api-docs`: 4
- `root-overview`: 3
- `other`: 2
- `cleanup-index`: 1

Representative first failures:

- `test_docs_root_entrypoints_are_frozen_to_index_and_function_tree`
- `test_next_steps_governance_doc_is_converged_under_docs_architecture_family`
- `test_config_splitting_guide_is_converged_under_docs_architecture_family`
- `test_page_config_usage_guide_is_converged_under_docs_architecture_family`
- `test_docs_claude_doc_is_converged_under_overview_family`
- `test_docs_iflow_doc_is_converged_under_overview_family`
- `test_active_guides_no_longer_point_runtime_logs_to_repo_root_logs_directory`
- `test_openspec_command_template_is_converged_under_guides_openspec_cmd_family`

## Decision

The old E3a blocker is partially stale but still substantively valid:

- Stale part: the lint/import portion has been recovered by E3a-R1.
- Still valid: the focused repository-hygiene pytest remains red across broad docs truth and policy families.

Therefore E3a must remain `blocked`. It is not safe to restore the parent node to `authorization-prepared` yet, because the parent acceptance surface still cannot close without either additional docs truth repair or a formal test-policy decision.

## Governance State Note

The latest blocker evidence is this worklog and its FUNCTION_TREE observation note. The node was re-blocked in place through the helper so the active gate and `blocker_reason` now reflect the fresh `58 failed / 44 passed` evidence.

## Required Next Decision

Do not directly unblock E3a.

Recommended next package:

- `B4.012-M3a-E3a-R2 repository hygiene remaining failure disposition`
- Mode: no-source decision first.
- Scope:
  - classify the current `58 failed / 44 passed` failure surface;
  - identify which failures are docs truth repair candidates and which are obsolete-policy candidates;
  - decide whether to continue docs repair, split the test file by family, or retire/update obsolete assertions;
  - keep all source/test edits prohibited until a separate implementation authorization is granted.

## Boundary Confirmation

- No source, runtime, test, OpenSpec, or root agent-rule files were modified.
- No E3a unblock was performed.
- No assertion update, skip/xfail addition, docs truth repair, or test-policy implementation was performed.
- External untracked worklogs under `docs/reports/worklogs/claude-auto/` remain isolated and are not part of this package.

## Closeout Position

This package refreshes the blocker evidence only. E3a remains active and blocked; E3 parent cannot close while this blocker remains active.
