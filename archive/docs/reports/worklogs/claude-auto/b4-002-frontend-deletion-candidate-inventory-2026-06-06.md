# B4.002 frontend deletion candidate inventory

Date: 2026-06-06
Mode: `no-source`
Scope: `web/frontend/**` deleted entries only

## Governance boundary

This node inventories frontend deletion candidates only. It does not accept, restore, delete, stage, or commit any frontend source, resource, style, or test file.

Primary references:

- `architecture/STANDARDS.md`
- `docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE.md`
- `docs/reports/worklogs/claude-auto/b4-001-frontend-route-ui-dirty-atlas-2026-06-06.md`
- `docs/guides/frontend-structure.md`
- `web/frontend/src/router/index.ts`

Inherited B4.001 boundary:

- The operator-stated `312` frontend set is the non-deletion frontend dirty set.
- The additional `28` frontend deleted entries are deletion-retirement candidates.
- These `28` entries must not be mixed into ordinary frontend source-authorized route/UI cleanup.
- Route-header migration residue remains isolated and should continue in B4.003, not in this deletion inventory.

## OPENDOG observation

OPENDOG was rechecked for this no-source inventory.

- `verification --id mystocks --json`: parsed successfully and still contains stale signal.
- `agent-guidance --project mystocks --top 5 --json`: parsed successfully and still contains stale signal.
- `stats --id mystocks --path-classification source`: CLI text summary available; command does not accept `--json` in the current binary.
- `unused --id mystocks --path-classification source`: CLI text summary available; command does not accept `--json` in the current binary.

Disposition:

- Stale OPENDOG evidence does not block this no-source inventory.
- Any later source edit, risky cleanup, or deletion-retirement acceptance must either refresh OPENDOG verification evidence or explicitly record stale-evidence acceptance in that package report.

## Snapshot

Branch:

- `wip/root-dirty-20260403`

Frontend deleted entries:

- Count: `28`
- Source runtime exact references in current `web/frontend/src`: `0`
- Active router direct references in current `web/frontend/src/router/index.ts`: `0`
- Deletion candidates requiring immediate restore due to direct runtime dependency: `0`

Decision buckets:

| Bucket | Count | Meaning |
| --- | ---: | --- |
| 可安全退役候选 | 13 | No current router reference, no current runtime source exact reference, no exact test/config evidence reference detected. Still requires explicit deletion-retirement authorization before staging. |
| 需归档后删除 | 15 | No runtime blocker, but exact test/config evidence remains or the deleted file itself is test evidence. Requires archive/test-baseline disposition before accepting deletion. |
| 依赖牵连需保留 | 0 | No deleted file is currently directly imported by router or runtime source under the exact-reference scan. |

## Domain split

| Domain | Count | Deleted entries | Disposition |
| --- | ---: | --- | --- |
| Root legacy view/support | 12 | `SkeletonUsage.vue`, 5 root-level view composables, 6 root-level view styles | Mostly safe-retirement candidates; owner pages are modified dirty items and must stay in later source-authorized root-legacy package if touched. |
| Market TDX support | 2 | `market/composables/useTdx.ts`, `market/styles/Tdx.scss` | Runtime-isolated; owner `market/Tdx.vue` is modified and should be handled only in a later market package. |
| Stock-analysis retired tabs | 6 | `StockBacktestTab.vue`, `StockDataTab.vue`, `StockOverviewTab.vue`, `StockRealtimeTab.vue`, `StockStatusTab.vue`, `StockStrategyTab.vue` | Needs archive/test-baseline pairing because `stock-analysis-style-normalization.spec.ts` still records these paths. |
| Strategy legacy workbench styles | 4 | `BatchScan.scss`, `ResultsQuery.scss`, `SingleRun.scss`, `StatsAnalysis.scss` | Needs archive/test-baseline pairing because legacy workbench decommission specs still record these paths. |
| Deleted unit config specs | 4 | `batch-scan-style-source.spec.ts`, `results-query-style-source.spec.ts`, `single-run-style-source.spec.ts`, `stats-analysis-style-source.spec.ts` | Test evidence deletion; requires test-baseline disposition before acceptance. |

## Candidate table

| # | Deleted path | Runtime refs | Evidence refs | Owner / related dirty path | Decision |
| ---: | --- | ---: | ---: | --- | --- |
| 1 | `web/frontend/src/views/SkeletonUsage.vue` | 0 | 0 | none detected | 可安全退役候选 |
| 2 | `web/frontend/src/views/composables/useAdvancedAnalysis.ts` | 0 | 0 | `web/frontend/src/views/AdvancedAnalysis.vue` is modified | 可安全退役候选 |
| 3 | `web/frontend/src/views/composables/useBacktestWizard.ts` | 0 | 0 | `web/frontend/src/views/BacktestWizard.vue` is modified | 可安全退役候选 |
| 4 | `web/frontend/src/views/composables/useIndustryConceptAnalysis.ts` | 0 | 0 | `web/frontend/src/views/IndustryConceptAnalysis.vue` is modified | 可安全退役候选 |
| 5 | `web/frontend/src/views/composables/usePortfolioManagement.ts` | 0 | 0 | `web/frontend/src/views/PortfolioManagement.vue` is modified | 可安全退役候选 |
| 6 | `web/frontend/src/views/composables/usemonitor.ts` | 0 | 0 | `web/frontend/src/views/monitor.vue` is modified | 可安全退役候选 |
| 7 | `web/frontend/src/views/market/composables/useTdx.ts` | 0 | 0 | `web/frontend/src/views/market/Tdx.vue` is modified | 可安全退役候选 |
| 8 | `web/frontend/src/views/market/styles/Tdx.scss` | 0 | 0 | `web/frontend/src/views/market/Tdx.vue` is modified | 可安全退役候选 |
| 9 | `web/frontend/src/views/stock-analysis/StockBacktestTab.vue` | 0 | 1 | `web/frontend/tests/unit/config/stock-analysis-style-normalization.spec.ts` | 需归档后删除 |
| 10 | `web/frontend/src/views/stock-analysis/StockDataTab.vue` | 0 | 1 | `web/frontend/tests/unit/config/stock-analysis-style-normalization.spec.ts` | 需归档后删除 |
| 11 | `web/frontend/src/views/stock-analysis/StockOverviewTab.vue` | 0 | 1 | `web/frontend/tests/unit/config/stock-analysis-style-normalization.spec.ts` | 需归档后删除 |
| 12 | `web/frontend/src/views/stock-analysis/StockRealtimeTab.vue` | 0 | 1 | `web/frontend/tests/unit/config/stock-analysis-style-normalization.spec.ts` | 需归档后删除 |
| 13 | `web/frontend/src/views/stock-analysis/StockStatusTab.vue` | 0 | 1 | `web/frontend/tests/unit/config/stock-analysis-style-normalization.spec.ts` | 需归档后删除 |
| 14 | `web/frontend/src/views/stock-analysis/StockStrategyTab.vue` | 0 | 1 | `web/frontend/tests/unit/config/stock-analysis-style-normalization.spec.ts` | 需归档后删除 |
| 15 | `web/frontend/src/views/strategy/styles/BatchScan.scss` | 0 | 1 | `web/frontend/src/views/strategy/BatchScan.vue` is modified; `legacy-strategy-workbench-decommission.spec.ts` records the style path | 需归档后删除 |
| 16 | `web/frontend/src/views/strategy/styles/ResultsQuery.scss` | 0 | 2 | `web/frontend/src/views/strategy/ResultsQuery.vue` is modified; `legacy-strategy-workbench-decommission.spec.ts` records the style path | 需归档后删除 |
| 17 | `web/frontend/src/views/strategy/styles/SingleRun.scss` | 0 | 1 | `web/frontend/src/views/strategy/SingleRun.vue` is modified; `legacy-strategy-workbench-decommission.spec.ts` records the style path | 需归档后删除 |
| 18 | `web/frontend/src/views/strategy/styles/StatsAnalysis.scss` | 0 | 1 | `web/frontend/src/views/strategy/StatsAnalysis.vue` is modified; `legacy-strategy-workbench-decommission.spec.ts` records the style path | 需归档后删除 |
| 19 | `web/frontend/src/views/styles/BacktestWizard.scss` | 0 | 0 | `web/frontend/src/views/BacktestWizard.vue` is modified | 可安全退役候选 |
| 20 | `web/frontend/src/views/styles/IndustryConceptAnalysis.scss` | 0 | 0 | `web/frontend/src/views/IndustryConceptAnalysis.vue` is modified | 可安全退役候选 |
| 21 | `web/frontend/src/views/styles/PortfolioManagement.scss` | 0 | 0 | `web/frontend/src/views/PortfolioManagement.vue` is modified | 可安全退役候选 |
| 22 | `web/frontend/src/views/styles/RealTimeMonitor.scss` | 0 | 0 | `web/frontend/src/views/RealTimeMonitor.vue` is modified | 可安全退役候选 |
| 23 | `web/frontend/src/views/styles/StockAnalysisDemo.scss` | 0 | 2 | `web/frontend/src/views/StockAnalysisDemo.vue` is modified; stock-analysis style normalization specs record this path | 需归档后删除 |
| 24 | `web/frontend/src/views/styles/monitor.scss` | 0 | 0 | `web/frontend/src/views/monitor.vue` is modified | 可安全退役候选 |
| 25 | `web/frontend/tests/unit/config/batch-scan-style-source.spec.ts` | 0 | 0 | deleted unit config spec | 需归档后删除 |
| 26 | `web/frontend/tests/unit/config/results-query-style-source.spec.ts` | 0 | 0 | deleted unit config spec | 需归档后删除 |
| 27 | `web/frontend/tests/unit/config/single-run-style-source.spec.ts` | 0 | 0 | deleted unit config spec | 需归档后删除 |
| 28 | `web/frontend/tests/unit/config/stats-analysis-style-source.spec.ts` | 0 | 0 | deleted unit config spec | 需归档后删除 |

## Route truth scan

Current route truth sources checked:

- `web/frontend/src/router/index.ts`
- `docs/guides/frontend-structure.md`

Findings:

- None of the 28 deleted entries are directly referenced by current router dynamic imports.
- The known route truth exceptions remain unchanged for this inventory:
  - `/dashboard` is backed by `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`.
  - `/trade/terminal` is backed by `web/frontend/src/views/TradingDashboard.vue`.
- The 28 deleted entries do not include either exception file.

## Retirement gates

The deletion candidates can be queued as follows:

1. Safe-retirement authorization candidate
   - Includes 13 runtime-isolated and evidence-isolated paths.
   - Required gate: explicit deletion-retirement authorization.
   - Suggested later package: root legacy support plus market TDX deletion acceptance, only if the modified owner pages are not mixed into the deletion package.

2. Archive/test-baseline candidate
   - Includes 15 paths with exact evidence coupling or deleted test specs.
   - Required gate: test-baseline/archive disposition before accepting the deletion.
   - Suggested later package: stock-analysis style-normalization evidence, strategy legacy workbench decommission evidence, and deleted style-source spec disposition.

3. Dependency-coupled restore candidate
   - Count: 0.
   - No immediate restore package is justified by current router/runtime exact-reference evidence.

## B4.003 handoff

B4.003 should remain route-header residue preflight / no-source.

Do not mix the B4.002 deletion-retirement candidate queue with route-header continuation. If route-header work resumes later, use the existing handoff boundary and route-specific package discipline.

## Verification performed

Read-only checks only:

- Parsed `git status --porcelain=v1 -z -- web/frontend`.
- Scanned current `web/frontend/src/router/index.ts` for direct route references.
- Scanned current `web/frontend/src` for exact runtime references to each deleted source path.
- Scanned frontend tests/config specs for exact evidence references.
- Rechecked OPENDOG verification/guidance/stats/unused in read-only mode.

Not run:

- Frontend build
- Frontend type check
- Vitest
- Playwright/E2E
- PM2 service checks

Reason: B4.002 is a no-source inventory node and does not modify or accept source/test deletions.
