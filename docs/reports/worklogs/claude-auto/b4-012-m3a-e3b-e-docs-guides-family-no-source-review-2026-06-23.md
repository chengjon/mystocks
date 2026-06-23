# B4.012-M3a-E3b-E Docs/Guides Family No-Source Review

Date: 2026-06-23
Program: artdeco-web-design-governance
Node: b4-012-m3a-e3b-e-docs-guides-family-split
Mode: no-source review

## Scope

This review classifies the remaining repository hygiene failures after E3b-C and E3b-D closeout.

No source, runtime, test implementation, OpenSpec, or external dirty file is modified.

## Fresh Verification Snapshot

- Command: `pytest -q --no-cov -o addopts='' --tb=no tests/unit/scripts/test_repository_hygiene_paths.py`
- Result: `81 failed, 21 passed`

The dominant remaining family is `docs-guides` with 45 failures.

## docs-guides Failure Matrix

### E1 entrypoints/navigation

Count: 5

Representative failures:

- `test_active_documentation_entry_guides_no_longer_point_to_removed_quickstart_and_start_here_files`
- `test_guides_readme_navigation_links_use_current_canonical_paths`
- `test_guides_root_remains_supporting_surface_not_docs_trunk`
- `test_active_guides_no_longer_point_runtime_logs_to_repo_root_logs_directory`
- `test_active_workflow_docs_no_longer_point_to_removed_docs_top_level_families`

Candidate allowed paths:

- `docs/README.md`
- `docs/guides/README.md`
- `docs/guides/INDEX.md`
- `docs/operations/`
- `docs/overview/`
- `docs/reports/cleanup/index-artifacts/`

### E2 web/frontend guides

Count: 14

Representative failures:

- `test_web_dev_tracking_runtime_artifacts_are_converged_under_var_log`
- `test_selected_web_guides_are_converged_under_guides_web_family`
- `test_html5_migration_experience_doc_is_converged_under_guides_web_family`
- `test_theme_guides_are_converged_under_guides_web_family`
- `test_additional_web_runtime_and_planning_guides_are_converged_under_guides_web_family`
- `test_realtime_integration_guide_is_converged_under_guides_web_family`

Candidate allowed paths:

- `docs/guides/web/`
- `docs/guides/frontend/`
- `docs/guides/chrome-devtools/`
- `docs/guides/typescript/`
- `docs/reports/cleanup/`

### E3 ai/multicli guides

Count: 4

Representative failures:

- `test_ai_tooling_guides_are_converged_under_guides_ai_tools_family`
- `test_ai_quick_start_is_converged_under_guides_ai_tools_family`
- `test_ai_test_optimizer_guides_are_converged_under_guides_ai_tools_family`
- `test_wencai_guides_are_converged_under_guides_wencai_family`

Candidate allowed paths:

- `docs/guides/ai-tools/`
- `docs/guides/multicli-tasks/`
- `docs/guides/git-worktree/`
- `docs/reports/cleanup/`

### E4 governance/dev guides

Count: 8

Representative failures:

- `test_hook_guides_are_converged_under_guides_hooks_family`
- `test_superpowers_docs_are_converged_under_guides_family`
- `test_openspec_command_template_is_converged_under_guides_openspec_cmd_family`
- `test_governance_guides_are_converged_under_guides_governance_family`
- `test_cicd_guides_are_converged_under_operations_ci_cd_family`
- `test_testing_specialized_guides_are_converged_under_docs_testing_family`

Candidate allowed paths:

- `docs/guides/governance/`
- `docs/guides/testing/`
- `docs/guides/workflows/`
- `docs/guides/openspec-cmd/`
- `docs/guides/hooks/`
- `docs/guides/superpowers/`
- `docs/operations/ci-cd/`

### E5 integration guides

Count: 2

Representative failures:

- `test_windows_tdx_bridge_setup_is_converged_under_guides_tdx_integration_family`
- `test_buger_client_guides_are_converged_under_guides_buger_family`

Candidate allowed paths:

- `docs/guides/tdx-integration/`
- `docs/guides/buger/`

### E6 remaining guides-other

Count: 12

Representative failures:

- `test_onboarding_guides_are_converged_under_guides_onboarding_family`
- `test_mock_real_data_docs_are_converged_under_guides_mock_data_family`
- `test_pm2_guides_are_converged_under_guides_pm2_family`
- `test_operational_guides_are_converged_under_docs_operations_families`
- `test_monitoring_guides_are_converged_under_operations_monitoring_family`
- `test_data_source_guides_are_converged_under_guides_data_source_family`

Candidate allowed paths:

- `docs/guides/`

## Risk Assessment

- Impact: medium documentation navigation surface, high repository hygiene visibility.
- Runtime risk: low.
- Boundary risk: medium, because this family spans root docs entrypoints, web/frontend guides, governance/dev guides, and remaining integration/other guides.

## Recommendation

Start with `E1 entrypoints/navigation` first.

Reason:

- It has the smallest surface.
- It controls the canonical root-facing documentation routes and anchors for the remaining guide families.
- It is the best place to restore structural truth before any broader guide-family cleanup.

## Non-Goals

- Do not modify source/runtime/test/OpenSpec content in this review.
- Do not touch the current external `TASK-REPORT.md` append hunk.
- Do not conflate docs-guides with docs-reports, docs-api, docs-root-overview, or root-agent-rule cleanup.
