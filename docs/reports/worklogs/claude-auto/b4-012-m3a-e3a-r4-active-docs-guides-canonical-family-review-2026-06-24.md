# B4.012-M3a-E3a-R4 Active Docs Guides Canonical Family Review

Date: 2026-06-24
Program: artdeco-web-design-governance
Node: b4-012-m3a-e3a-r4-active-docs-guides-canonical-family-review
Parent: b4-012-m3a-e3a-repository-hygiene-unit-script-authorization
Mode: no-source decision audit
Source edits authorized: false
Current HEAD: 7b63e838f947

## Scope

This review isolates the active docs/guides portion of the remaining repository-hygiene failures after R2 and R3.

It does not modify:

- tests or test helpers
- docs or guides
- source/runtime/frontend/backend files
- OpenSpec files
- root agent-rule files
- external dirty files

## Fresh Verification

Commands executed at HEAD `7b63e838f947`:

| Command | Result |
| --- | --- |
| `python -m py_compile tests/unit/scripts/test_repository_hygiene_paths.py` | pass |
| `ruff check tests/unit/scripts/test_repository_hygiene_paths.py` | pass |
| `pytest -q --no-cov -o addopts= --tb=no -ra tests/unit/scripts/test_repository_hygiene_paths.py` | fail: 58 failed, 44 passed, 0 warnings, 1.82s |

From the 58 failures, 37 are active docs/guides canonical-family failures. Root/overview docs, reports/tasks/worklogs, API-docs, and cleanup-index families are excluded from this R4 review.

## Active Docs/Guides Family Split

| Family | Count | Tests |
| --- | ---: | --- |
| G1 quality/testing/ci-cd guides | 6 | `test_cicd_guides_are_converged_under_operations_ci_cd_family`; `test_testing_specialized_guides_are_converged_under_docs_testing_family`; `test_web_testing_methodology_doc_is_converged_under_docs_testing_family`; `test_additional_cicd_guides_are_converged_under_operations_ci_cd_family`; `test_cicd_optimization_system_is_converged_under_operations_ci_cd_family`; `test_python_quality_guides_are_converged_under_operations_ci_cd_family` |
| G2 agent/multicli/runtime-governance guides | 5 | `test_maestro_and_multicli_runtime_docs_are_converged_under_guides_multicli_tasks`; `test_mongo_multicli_guides_are_converged_under_guides_multicli_tasks`; `test_git_worktree_and_branch_strategy_guides_are_converged_under_guides_multicli_tasks`; `test_cli_registration_and_roles_guides_are_converged_under_guides_multicli_tasks`; `test_multicli_coordination_guides_are_converged_under_guides_multicli_tasks` |
| G3 market-data/domain integration guides | 5 | `test_data_source_guides_are_converged_under_guides_data_source_family`; `test_data_interface_guides_are_converged_under_guides_data_interface_family`; `test_quant_trading_guides_are_converged_under_guides_quant_trading_family`; `test_wencai_guides_are_converged_under_guides_wencai_family`; `test_windows_tdx_bridge_setup_is_converged_under_guides_tdx_integration_family` |
| G4 operations/monitoring/pm2 guides | 5 | `test_ai_quick_start_is_converged_under_guides_ai_tools_family`; `test_pm2_guides_are_converged_under_guides_pm2_family`; `test_operational_guides_are_converged_under_docs_operations_families`; `test_quick_start_guide_is_converged_under_docs_operations_family`; `test_monitoring_guides_are_converged_under_operations_monitoring_family` |
| G5 AI tooling guides | 2 | `test_ai_tooling_guides_are_converged_under_guides_ai_tools_family`; `test_ai_test_optimizer_guides_are_converged_under_guides_ai_tools_family` |
| G6 governance/documentation/security guides | 9 | `test_next_steps_governance_doc_is_converged_under_docs_architecture_family`; `test_governance_guides_are_converged_under_guides_governance_family`; `test_onboarding_guides_are_converged_under_guides_onboarding_family`; `test_documentation_process_guides_are_converged_under_guides_documentation_family`; `test_initialization_prompt_is_converged_under_guides_templates_family`; `test_technical_debt_governance_charter_is_converged_under_docs_standards_family`; `test_features_guides_are_converged_under_guides_features_family`; `test_security_guides_are_converged_under_standards_security_family`; `test_buger_client_guides_are_converged_under_guides_buger_family` |
| G7 architecture/OpenSpec/runtime-log guide references | 5 | `test_config_splitting_guide_is_converged_under_docs_architecture_family`; `test_page_config_usage_guide_is_converged_under_docs_architecture_family`; `test_active_guides_no_longer_point_runtime_logs_to_repo_root_logs_directory`; `test_openspec_command_template_is_converged_under_guides_openspec_cmd_family`; `test_mock_real_data_docs_are_converged_under_guides_mock_data_family` |

## Boundary Decision

Do not repair these failures as one monolithic docs/test batch.

The active docs/guides surface should be split by operational ownership and runtime risk:

1. G6 governance/documentation/security first because it defines canonical process language.
2. G1 quality/testing/ci-cd second because it affects verification documentation and test policy.
3. G2 agent/multicli/runtime-governance third because it touches execution workflow docs and root agent-rule references indirectly.
4. G3 market-data/domain integration fourth, with explicit OpenStock boundary protection.
5. G4 operations/monitoring/pm2 fifth, after guide canonical paths are stable.
6. G5 AI tooling and G7 architecture/OpenSpec/runtime-log references can be handled as small follow-up packages.

For G3, data-source documentation must describe only MyStocks consumer/adaptation behavior. Provider/runtime development belongs to `/opt/claude/openstock` and must not be reintroduced into `mystocks_spec`.

## Recommended Follow-Up Packages

Prepare separate no-source or implementation authorization packages:

1. `B4.012-M3a-E3a-R4-A governance documentation security guides truth`
2. `B4.012-M3a-E3a-R4-B quality testing ci-cd guides truth`
3. `B4.012-M3a-E3a-R4-C agent multicli runtime governance guides truth`
4. `B4.012-M3a-E3a-R4-D market-data domain integration guides truth`
5. `B4.012-M3a-E3a-R4-E operations monitoring pm2 guides truth`
6. `B4.012-M3a-E3a-R4-F ai tooling and architecture reference tail`

Each follow-up package must define exact allowed paths before any edits. `tests/unit/scripts/test_repository_hygiene_paths.py` should be edited only if the canonical docs-truth policy itself changes, not as the first move.

## Governance Outcome

R4 is ready to move to `decision-prepared`.

E3a remains blocked until the active docs/guides families and the other R2 families are resolved through separately authorized packages.
