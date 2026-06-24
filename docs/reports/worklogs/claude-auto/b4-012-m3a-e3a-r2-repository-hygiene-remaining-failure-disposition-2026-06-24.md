# B4.012-M3a-E3a-R2 Repository Hygiene Remaining Failure Disposition

Date: 2026-06-24
Program: artdeco-web-design-governance
Node: b4-012-m3a-e3a-r2-repository-hygiene-remaining-failure-disposition
Parent: b4-012-m3a-e3a-repository-hygiene-unit-script-authorization
Mode: no-source decision audit
Source edits authorized: false
Current HEAD: 27a10e566763

## Scope

This package revalidates and classifies the remaining failures in `tests/unit/scripts/test_repository_hygiene_paths.py` after the E3b docs-truth packages were closed.

It does not modify:

- source/runtime code
- tests or test helpers
- OpenSpec assets
- root agent-rule documents
- frontend/backend runtime files
- external dirty files

The goal is to decide the next batching strategy for the remaining repository-hygiene failure surface, not to repair the failures in this package.

## Fresh Verification

Commands executed at HEAD `27a10e566763`:

| Command | Result |
| --- | --- |
| `python -m py_compile tests/unit/scripts/test_repository_hygiene_paths.py` | pass |
| `ruff check tests/unit/scripts/test_repository_hygiene_paths.py` | pass |
| `pytest -q --no-cov -o addopts= --tb=no -ra tests/unit/scripts/test_repository_hygiene_paths.py` | fail: 58 failed, 44 passed, 0 warnings, 1.72s |

The failure count remains outside the completed E3a-R1 lint/import recovery scope. The parent E3a node must remain blocked.

## Failure Family Split

The 58 failing assertions are not a single implementation issue. They represent several repository-hygiene policy surfaces and should be handled by family-level packages.

| Family | Count | Examples | Disposition |
| --- | ---: | --- | --- |
| F1 root docs entrypoints / overview family | 3 | `test_docs_root_entrypoints_are_frozen_to_index_and_function_tree`, `test_docs_claude_doc_is_converged_under_overview_family`, `test_docs_iflow_doc_is_converged_under_overview_family` | Requires a root/overview docs truth decision before editing assertions or documents. |
| F2 active docs/guides truth family | 20 | `test_next_steps_governance_doc_is_converged_under_docs_architecture_family`, `test_config_splitting_guide_is_converged_under_docs_architecture_family`, `test_ai_tooling_guides_are_converged_under_guides_ai_tools_family`, `test_pm2_guides_are_converged_under_guides_pm2_family` | Batch by current canonical guide families. Do not weaken assertions before validating canonical paths. |
| F3 reports / tasks / worklogs family | 12 | `test_phase6_e2e_reports_are_converged_under_reports_completion_reports`, `test_next_work_tasks_doc_is_converged_under_reports_tasks`, `test_recurring_claude_auto_worklog_is_converged_under_reports_worklogs_trunk` | Treat as evidence-placement and historical-report retention policy, not runtime behavior. |
| F4 api-docs / docs-api family | 4 | `test_api_endpoints_statistics_report_is_converged_under_docs_api_family`, `test_api_alignment_and_contract_plan_guides_are_converged_under_docs_api_guides_integration` | Separate from runtime API contracts. This is documentation placement and contract-report truth only. |
| F5 cleanup-index / policy index family | 1 | `test_refactoring_and_index_analysis_docs_are_converged_under_reports_analysis` | Small tail package after the larger families are decided. |
| F6 specialized guide families requiring manual review | 18 | `test_data_source_guides_are_converged_under_guides_data_source_family`, `test_quant_trading_guides_are_converged_under_guides_quant_trading_family`, `test_root_agents_and_claude_document_gitnexus_staged_microbatch_rule` | Split by domain before authorization. Data-source references must preserve the OpenStock boundary: MyStocks consumes/adapts OpenStock data and must not resume provider/runtime development here. |

## Decision

Do not continue by editing `tests/unit/scripts/test_repository_hygiene_paths.py` directly.

The remaining failure surface should be split into family packages with no-source review first, then separate docs/test authorization only when the canonical truth is clear. The packages should be ordered by mainline policy risk rather than by file order.

Recommended sequence:

1. `B4.012-M3a-E3a-R3-A root overview and agent-rule docs truth review`
2. `B4.012-M3a-E3a-R3-B active docs/guides canonical-family review`
3. `B4.012-M3a-E3a-R3-C reports tasks worklogs evidence-placement review`
4. `B4.012-M3a-E3a-R3-D api-docs contract-report placement review`
5. `B4.012-M3a-E3a-R3-E cleanup-index residual review`

Each package must preserve:

- no source/runtime edits unless separately authorized
- no OpenSpec edits unless separately authorized
- no root AGENTS/CLAUDE edits unless separately authorized
- no external dirty staging
- no OpenStock provider/runtime development inside `mystocks_spec`

## Governance Outcome

R2 is ready to move to `decision-prepared`.

E3a remains blocked because the focused repository-hygiene pytest surface is still red at 58 failed / 44 passed and exceeds the closed E3a-R1 recovery scope.
