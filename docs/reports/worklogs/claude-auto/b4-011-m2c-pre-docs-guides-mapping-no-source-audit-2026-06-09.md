# B4.011-M2c-pre Docs Guides Mapping No-Source Audit

Date: 2026-06-09

Mode: `no-source`

Branch: `wip/root-dirty-20260403`

Baseline HEAD: `527f86a88 B4.011-M1: audit docs archive reorg truth`

Source edits authorized: `false`

Deletion-retirement authorized: `false`

## Purpose

This follow-up audit maps the dirty `docs/guides/**` deletion family to either active replacement paths or ignored archive copies. It is evidence only. It does not accept deletions, force-add ignored archive files, move files, restore files, edit source, or stage implementation changes.

## Scope

In scope:

- Deleted tracked paths under `docs/guides/**`
- Untracked replacement candidates under `docs/guides/**`
- Ignored archive candidates under `archive/docs/guides-merged/**`
- Hash and filename matching for documentation-only disposition planning

Out of scope:

- `web/frontend/src/**`
- `web/frontend/tests/**`
- `src/**`
- `web/backend/**`
- `tests/**`
- `scripts/**`
- `reports/**` root artifacts
- `docs/reports/**`
- `docs/superpowers/**`
- Any deletion acceptance or archive staging

## Current Observations

| Observation | Count |
| --- | ---: |
| Deleted tracked `docs/guides/**` files | 58 |
| Modified tracked `docs/guides/**` files | 24 |
| Untracked `docs/guides/**` files | 31 |
| Current filesystem files under `docs/guides/**` | 252 |
| Current filesystem files under `archive/docs/guides-merged/**` | 31 |
| High-confidence exact hash mappings | 57 |
| Low-confidence / unmapped deletions | 1 |

Disposition split for the 58 deleted paths:

| Disposition | Count | Meaning |
| --- | ---: | --- |
| `active-reparent-exact` | 27 | Deleted path has an exact content hash match at a new active `docs/guides/**` path. |
| `archive-exact` | 30 | Deleted path has an exact content hash match under ignored `archive/docs/guides-merged/**`. |
| `unmapped` | 1 | Deleted path has no exact hash or basename match in active docs or archive. |

## Group Summary

| Source group | Count | Disposition |
| --- | ---: | --- |
| `docs/guides/akshare` | 4 | active reparent to `docs/guides/data-source/akshare` |
| `docs/guides/buger` | 1 | active reparent to `docs/guides/ai-tools/buger` |
| `docs/guides/chrome-devtools` | 6 | active reparent to `docs/guides/ai-tools/chrome-devtools` |
| `docs/guides/data-interface` | 4 | active reparent to `docs/guides/data-source/data-interface` |
| `docs/guides/tdx-integration` | 8 | active reparent to `docs/guides/data-source/tdx-integration` |
| `docs/guides/wencai` | 4 | active reparent to `docs/guides/data-source/wencai` |
| `docs/guides/features` | 6 | archive exact under `archive/docs/guides-merged/features` |
| `docs/guides/openspec-cmd` | 5 | archive exact under `archive/docs/guides-merged/openspec-cmd` |
| `docs/guides/quant-trading` | 12 | archive exact under `archive/docs/guides-merged/quant-trading` |
| `docs/guides/superpowers` | 3 | archive exact under `archive/docs/guides-merged/superpowers` |
| `docs/guides/templates` | 4 | archive exact under `archive/docs/guides-merged/templates` |
| `docs/guides/ai-tools` | 1 | unmapped |

## Active Reparent Exact Mapping

These deleted tracked paths have exact content matches at new active documentation paths. A future implementation package should treat these as reparent/rename candidates, not ordinary deletion-retirement.

| Deleted path | Exact active target |
| --- | --- |
| `docs/guides/akshare/AKSHARE_MARKET_EXTENSION_GUIDE.md` | `docs/guides/data-source/akshare/AKSHARE_MARKET_EXTENSION_GUIDE.md` |
| `docs/guides/akshare/AKSHARE_MARKET_MAINTENANCE.md` | `docs/guides/data-source/akshare/AKSHARE_MARKET_MAINTENANCE.md` |
| `docs/guides/akshare/AKSHARE_MARKET_TROUBLESHOOTING.md` | `docs/guides/data-source/akshare/AKSHARE_MARKET_TROUBLESHOOTING.md` |
| `docs/guides/akshare/INDEX.md` | `docs/guides/data-source/akshare/INDEX.md` |
| `docs/guides/buger/INDEX.md` | `docs/guides/ai-tools/buger/INDEX.md` |
| `docs/guides/chrome-devtools/CHROME_DEVTOOLS_MCP_FIX_GUIDE.md` | `docs/guides/ai-tools/chrome-devtools/CHROME_DEVTOOLS_MCP_FIX_GUIDE.md` |
| `docs/guides/chrome-devtools/CHROME_DEVTOOLS_MCP_GUIDE.md` | `docs/guides/ai-tools/chrome-devtools/CHROME_DEVTOOLS_MCP_GUIDE.md` |
| `docs/guides/chrome-devtools/CHROME_DEVTOOLS_MCP_SOLUTION.md` | `docs/guides/ai-tools/chrome-devtools/CHROME_DEVTOOLS_MCP_SOLUTION.md` |
| `docs/guides/chrome-devtools/INDEX.md` | `docs/guides/ai-tools/chrome-devtools/INDEX.md` |
| `docs/guides/chrome-devtools/chrome-devtools-wsl2-guide.md` | `docs/guides/ai-tools/chrome-devtools/chrome-devtools-wsl2-guide.md` |
| `docs/guides/chrome-devtools/mystocks-chromedevtools-testing-guide.md` | `docs/guides/ai-tools/chrome-devtools/mystocks-chromedevtools-testing-guide.md` |
| `docs/guides/data-interface/DATA_INTERFACE_SCANNER_GUIDE.md` | `docs/guides/data-source/data-interface/DATA_INTERFACE_SCANNER_GUIDE.md` |
| `docs/guides/data-interface/INDEX.md` | `docs/guides/data-source/data-interface/INDEX.md` |
| `docs/guides/data-interface/UNIFIED_INTERFACE_GUIDE.md` | `docs/guides/data-source/data-interface/UNIFIED_INTERFACE_GUIDE.md` |
| `docs/guides/data-interface/analyze_api_data_usage_README.md` | `docs/guides/data-source/data-interface/analyze_api_data_usage_README.md` |
| `docs/guides/tdx-integration/INDEX.md` | `docs/guides/data-source/tdx-integration/INDEX.md` |
| `docs/guides/tdx-integration/INTEGRATION_ANALYSIS.md` | `docs/guides/data-source/tdx-integration/INTEGRATION_ANALYSIS.md` |
| `docs/guides/tdx-integration/README.md` | `docs/guides/data-source/tdx-integration/README.md` |
| `docs/guides/tdx-integration/WINDOWS_TDX_BRIDGE_SETUP.md` | `docs/guides/data-source/tdx-integration/WINDOWS_TDX_BRIDGE_SETUP.md` |
| `docs/guides/tdx-integration/complete_example.md` | `docs/guides/data-source/tdx-integration/complete_example.md` |
| `docs/guides/tdx-integration/data_analysis.md` | `docs/guides/data-source/tdx-integration/data_analysis.md` |
| `docs/guides/tdx-integration/data_capture.md` | `docs/guides/data-source/tdx-integration/data_capture.md` |
| `docs/guides/tdx-integration/data_visualization.md` | `docs/guides/data-source/tdx-integration/data_visualization.md` |
| `docs/guides/wencai/INDEX.md` | `docs/guides/data-source/wencai/INDEX.md` |
| `docs/guides/wencai/WENCAI_INTEGRATION_INDEX.md` | `docs/guides/data-source/wencai/WENCAI_INTEGRATION_INDEX.md` |
| `docs/guides/wencai/WENCAI_INTEGRATION_PLAN.md` | `docs/guides/data-source/wencai/WENCAI_INTEGRATION_PLAN.md` |
| `docs/guides/wencai/WENCAI_INTEGRATION_QUICKREF.md` | `docs/guides/data-source/wencai/WENCAI_INTEGRATION_QUICKREF.md` |

## Archive Exact Mapping

These deleted tracked paths have exact content matches under ignored `archive/docs/guides-merged/**`. A future implementation package must decide whether the archive should remain local-only or be force-added under an explicitly authorized path list.

| Deleted path | Exact archive target |
| --- | --- |
| `docs/guides/features/INDEX.md` | `archive/docs/guides-merged/features/INDEX.md` |
| `docs/guides/features/STOCK_HEATMAP_IMPLEMENTATION.md` | `archive/docs/guides-merged/features/STOCK_HEATMAP_IMPLEMENTATION.md` |
| `docs/guides/features/TRADINGVIEW_FIX_SUMMARY.md` | `archive/docs/guides-merged/features/TRADINGVIEW_FIX_SUMMARY.md` |
| `docs/guides/features/TRADINGVIEW_TROUBLESHOOTING.md` | `archive/docs/guides-merged/features/TRADINGVIEW_TROUBLESHOOTING.md` |
| `docs/guides/features/WATCHLIST_GROUP_IMPLEMENTATION.md` | `archive/docs/guides-merged/features/WATCHLIST_GROUP_IMPLEMENTATION.md` |
| `docs/guides/features/WENCAI_MENU_FIX.md` | `archive/docs/guides-merged/features/WENCAI_MENU_FIX.md` |
| `docs/guides/openspec-cmd/INDEX.md` | `archive/docs/guides-merged/openspec-cmd/INDEX.md` |
| `docs/guides/openspec-cmd/README.md` | `archive/docs/guides-merged/openspec-cmd/README.md` |
| `docs/guides/openspec-cmd/check-report-example.md` | `archive/docs/guides-merged/openspec-cmd/check-report-example.md` |
| `docs/guides/openspec-cmd/check.md` | `archive/docs/guides-merged/openspec-cmd/check.md` |
| `docs/guides/openspec-cmd/command-template.md` | `archive/docs/guides-merged/openspec-cmd/command-template.md` |
| `docs/guides/quant-trading/INDEX.md` | `archive/docs/guides-merged/quant-trading/INDEX.md` |
| `docs/guides/quant-trading/advanced_algorithms_usage_guide.md` | `archive/docs/guides-merged/quant-trading/advanced_algorithms_usage_guide.md` |
| `docs/guides/quant-trading/algorithm_system_usage_guide.md` | `archive/docs/guides-merged/quant-trading/algorithm_system_usage_guide.md` |
| `docs/guides/quant-trading/broker-execution-truth-registry.md` | `archive/docs/guides-merged/quant-trading/broker-execution-truth-registry.md` |
| `docs/guides/quant-trading/miniqmt-project-alignment-questionnaire.md` | `archive/docs/guides-merged/quant-trading/miniqmt-project-alignment-questionnaire.md` |
| `docs/guides/quant-trading/miniqmt-project-feedback-response.md` | `archive/docs/guides-merged/quant-trading/miniqmt-project-feedback-response.md` |
| `docs/guides/quant-trading/neural_algorithms_usage_guide.md` | `archive/docs/guides-merged/quant-trading/neural_algorithms_usage_guide.md` |
| `docs/guides/quant-trading/quantitative_trading_implementation.md` | `archive/docs/guides-merged/quant-trading/quantitative_trading_implementation.md` |
| `docs/guides/quant-trading/risk_management_system_plan.md` | `archive/docs/guides-merged/quant-trading/risk_management_system_plan.md` |
| `docs/guides/quant-trading/windows-qmt-agent-contract-acceptance-guide.md` | `archive/docs/guides-merged/quant-trading/windows-qmt-agent-contract-acceptance-guide.md` |
| `docs/guides/quant-trading/windows-qmt-agent-live-contract-requirements-review.md` | `archive/docs/guides-merged/quant-trading/windows-qmt-agent-live-contract-requirements-review.md` |
| `docs/guides/quant-trading/windows-qmt-service-ready-checklist.md` | `archive/docs/guides-merged/quant-trading/windows-qmt-service-ready-checklist.md` |
| `docs/guides/superpowers/INDEX.md` | `archive/docs/guides-merged/superpowers/INDEX.md` |
| `docs/guides/superpowers/plans/2026-03-23-frontend-test-gates.md` | `archive/docs/guides-merged/superpowers/plans/2026-03-23-frontend-test-gates.md` |
| `docs/guides/superpowers/plans/2026-03-25-guides-onboarding-migration.md` | `archive/docs/guides-merged/superpowers/plans/2026-03-25-guides-onboarding-migration.md` |
| `docs/guides/templates/INDEX.md` | `archive/docs/guides-merged/templates/INDEX.md` |
| `docs/guides/templates/INITIALIZATION_PROMPT.md` | `archive/docs/guides-merged/templates/INITIALIZATION_PROMPT.md` |
| `docs/guides/templates/task-card-standard-template.md` | `archive/docs/guides-merged/templates/task-card-standard-template.md` |
| `docs/guides/templates/tech-debt-exception-template.md` | `archive/docs/guides-merged/templates/tech-debt-exception-template.md` |

## Unmapped Deletion

| Deleted path | Hash | Finding | Required disposition |
| --- | --- | --- | --- |
| `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md` | `7e7ac60e363f83c2` | No exact hash or basename match under active `docs/guides/**` or ignored `archive/docs/guides-merged/**`. | Do not accept deletion in a batch. Preserve or investigate separately. |

## Modified And Untracked Side Effects

The mapping pass also observed modified and untracked files under active `docs/guides/**`. These should be reviewed separately from deletion-retirement:

- Modified active docs include root guide indexes, AI tooling guides, frontend HTML5 docs, governance docs, mock-data docs, and web/docs sidecars.
- Untracked active docs include replacement paths under `docs/guides/ai-tools/**` and `docs/guides/data-source/**`, plus new frontend and page-audit docs.

These are likely part of the same human docs reorganization, but they are not safe to mix with archive acceptance until a docs-authorized implementation batch is explicitly scoped.

## Recommended Next Batches

1. `B4.011-M2b` docs/superpowers exact archive-retirement remains the smallest low-risk deletion-retirement candidate outside `docs/guides`.
2. `B4.011-M2c-A` active guide reparent package: authorize only the 27 `active-reparent-exact` pairs and their directly related index updates, if any.
3. `B4.011-M2c-B` guides archive package: authorize only the 30 `archive-exact` pairs and decide whether ignored archive targets should be force-added.
4. `B4.011-M2c-HOLD` `OMC_WORKFLOW_GUIDE.md`: keep out of deletion packages until a replacement or archive copy is found.

## Gate Recommendation

No implementation should proceed from this report without a separate authorization that states:

- Whether active reparent pairs may be staged as renames/additions.
- Whether ignored archive files under `archive/docs/guides-merged/**` may be force-added.
- Whether the unmapped `OMC_WORKFLOW_GUIDE.md` is explicitly preserved, restored, or investigated.
- Exact path list for staging.

## Verification Commands Used

- `git diff --name-status`
- `git ls-files --others --exclude-standard`
- `git show HEAD:<path>` for deleted tracked blobs
- Filesystem scan of `docs/guides/**` and `archive/docs/guides-merged/**`
- SHA-256 content hashing for exact-match mapping

## Decision

`docs/guides` is no longer a single undifferentiated dirty family. It should be split into:

- active reparent exact batch,
- archive exact batch,
- unmapped hold item,
- separate modified/untracked active docs review.

No deletion, archive acceptance, source edit, test edit, or staging action was performed by this audit.
