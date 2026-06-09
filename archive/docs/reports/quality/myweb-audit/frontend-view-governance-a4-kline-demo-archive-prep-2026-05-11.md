# Frontend View Governance A4 KLineDemo Archive Prep

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: approval package for `A4-kline-demo-archive`.

This package does not move files, edit runtime code, or retire guards.

## Candidate

| File | Classification | Route/menu status | Guard status | Proposed lifecycle |
| --- | --- | --- | --- | --- |
| `web/frontend/src/views/KLineDemo.vue` | `candidate-review/demo-sandbox` | No active router/menu owner found | No direct package/test/workflow guard found in focused scan | `archive-candidate/demo-sandbox` |

## Evidence

GitNexus impact:

| Target | Risk | Direct dependents | Affected processes |
| --- | --- | ---: | ---: |
| `KLineDemo.vue` | LOW | 0 | 0 |

Static reference search:

- Focused search found no active import/read for `src/views/KLineDemo`, `@/views/KLineDemo`, or `KLineDemo.vue` under `web/frontend/src`, `web/frontend/tests`, `web/frontend/package.json`, or `.github`.
- The page is a root-level visual demo shell around a shared K-line chart component with fixed initial symbol/interval.
- The shared K-line component and canonical K-line route are not owned by this page.

Successor coverage:

- `/market/kline` remains represented by `web/frontend/src/views/market/Technical.vue` and router metadata for `/api/v1/market/kline`.
- Detail K-line analysis remains represented by `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue`.
- K-line behavior is covered by existing component/unit/E2E references including `ProKLineChart` tests and `market-data.spec.ts` checks for `.market-kline-tab`.

## Proposed Mutation Scope

If approved:

- Move `web/frontend/src/views/KLineDemo.vue` to `archive/web/frontend/src/views/root-sandbox/kline-demo/KLineDemo.vue`.
- Add an archive README for the K-line demo shell.
- Do not modify `ProKLineChart`, `/market/kline`, K-line analysis detail pages, router/menu config, or K-line tests.
- Do not touch `MarketDataDemo.vue`, `DataVisualizationShowcase.vue`, `SkeletonUsage.vue`, `SmartDataSourceTest.vue`, or `StockAnalysisDemo.vue`.

## Required Execution Gates

- GitNexus impact for `KLineDemo.vue` before moving the file.
- Exact active-reference search after the move.
- OpenSpec strict validation.
- Markdown governance gate for archive README, execution report, and `tasks.md`.
- `git diff --cached --name-status`.
- `git diff --cached --check`.
- `gitnexus_detect_changes(scope="staged")`.

## Decision

This candidate is ready for an explicit execution decision. It is smaller than `MarketDataDemo.vue` because it has no discovered direct local composable dependency, whereas `MarketDataDemo.vue` solely owns `src/composables/useMarketData.js` and needs a paired dependency decision.
