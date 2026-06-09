# Frontend View Governance A4 MarketDataDemo Paired Archive Prep

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: approval package for `A4-market-data-demo-paired-archive`.

This package does not move files, edit runtime code, or retire guards.

## Candidates

| File | Classification | Route/menu status | Guard status | Proposed lifecycle |
| --- | --- | --- | --- | --- |
| `web/frontend/src/views/MarketDataDemo.vue` | `candidate-review/demo-sandbox` | No active router/menu owner found | No direct package/test/workflow guard found in focused scan | `archive-candidate/demo-sandbox` |
| `web/frontend/src/composables/useMarketData.js` | `demo-local-composable` | Only imported by `MarketDataDemo.vue` | No separate active owner found | Archive together with owning demo page |

## Evidence

GitNexus impact:

| Target | Risk | Direct dependents | Affected processes |
| --- | --- | ---: | ---: |
| `MarketDataDemo.vue` | LOW | 0 | 0 |
| `useMarketData.js` | LOW | 1 (`MarketDataDemo.vue`) | 0 |

Static reference search:

- Focused search found no active import/read for `src/views/MarketDataDemo`, `@/views/MarketDataDemo`, or `MarketDataDemo.vue` under `web/frontend/src`, `web/frontend/tests`, `web/frontend/package.json`, or `.github` except the file itself.
- Focused search found `@/composables/useMarketData` is imported only by `MarketDataDemo.vue`.
- The paired composable is a demo unified-API client wrapper that fetches market overview, stocks basic, industries, and concepts; it is not exported from the composables index and has no independent active route owner.

Successor coverage:

- Market realtime and market technical truth remain in `web/frontend/src/views/market/Realtime.vue` and `web/frontend/src/views/market/Technical.vue`.
- Data-domain industry, concept, and fund-flow truth remain in `web/frontend/src/views/data/Industry.vue`, `web/frontend/src/views/data/Concepts.vue`, and `web/frontend/src/views/data/FundFlow.vue`.
- Existing market-data aggregate shells already degrade honestly when no one-to-one canonical owner exists: `web/frontend/src/views/MarketData.vue` and `web/frontend/src/views/market/MarketDataView.vue`.
- Market route behavior is covered by `web/frontend/tests/e2e/market-data.spec.ts` and domain unit tests for market/data pages.

## Proposed Mutation Scope

If approved:

- Move `web/frontend/src/views/MarketDataDemo.vue` to `archive/web/frontend/src/views/root-sandbox/market-data-demo/MarketDataDemo.vue`.
- Move `web/frontend/src/composables/useMarketData.js` to `archive/web/frontend/src/views/root-sandbox/market-data-demo/useMarketData.js`.
- Add an archive README for the paired demo page and local composable.
- Do not modify canonical `/market/*` or `/data/*` routes.
- Do not modify `MarketData.vue`, `market/MarketDataView.vue`, or existing market/data tests.
- Do not touch `DataVisualizationShowcase.vue`, `SkeletonUsage.vue`, `SmartDataSourceTest.vue`, or `StockAnalysisDemo.vue`.

## Required Execution Gates

- GitNexus impact for `MarketDataDemo.vue` and `useMarketData.js` before moving files.
- Exact active-reference search after the move for both the page and composable import path.
- OpenSpec strict validation.
- Markdown governance gate for archive README, execution report, and `tasks.md`.
- `git diff --cached --name-status`.
- `git diff --cached --check`.
- `gitnexus_detect_changes(scope="staged")`.

## Decision

This candidate is ready for an explicit execution decision as a paired archive batch. Moving the page without its local composable would leave an orphan demo-only composable; moving the composable without the page would break the archived page's restore context.
