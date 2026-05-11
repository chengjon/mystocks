# Frontend View Governance A4 MarketDataDemo Paired Archive Execution

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: execution record for `A4-market-data-demo-paired-archive`.

## Approved Scope

Moved files:

- `web/frontend/src/views/MarketDataDemo.vue`
- `web/frontend/src/composables/useMarketData.js`

Retained out of scope:

- Canonical `/market/*` and `/data/*` routes
- `web/frontend/src/views/MarketData.vue`
- `web/frontend/src/views/market/MarketDataView.vue`
- Existing market/data route tests
- `web/frontend/src/views/DataVisualizationShowcase.vue`
- `web/frontend/src/views/SkeletonUsage.vue`
- `web/frontend/src/views/SmartDataSourceTest.vue`
- `web/frontend/src/views/StockAnalysisDemo.vue`

## Pre-Move Evidence

GitNexus impact:

| Target | Risk | Direct dependents | Affected processes |
| --- | --- | ---: | ---: |
| `MarketDataDemo.vue` | LOW | 0 | 0 |
| `useMarketData.js` | LOW | 1 (`MarketDataDemo.vue`) | 0 |

Static reference checks:

- No active import/read was found for `src/views/MarketDataDemo`, `@/views/MarketDataDemo`, or `MarketDataDemo.vue` under `web/frontend/src`, `web/frontend/tests`, `web/frontend/package.json`, or `.github` except the file itself.
- `@/composables/useMarketData` was imported only by `MarketDataDemo.vue`.
- The paired composable was not exported from the composables index and had no independent active route owner.

## Files Moved

| Original path | Archive path |
| --- | --- |
| `web/frontend/src/views/MarketDataDemo.vue` | `archive/web/frontend/src/views/root-sandbox/market-data-demo/MarketDataDemo.vue` |
| `web/frontend/src/composables/useMarketData.js` | `archive/web/frontend/src/views/root-sandbox/market-data-demo/useMarketData.js` |

## Files Added

| File | Purpose |
| --- | --- |
| `archive/web/frontend/src/views/root-sandbox/market-data-demo/README.md` | Governed archive manifest and restore rule |

## Cleanup Decision

This is an archive move, not deletion. The page is classified as `archive-candidate/demo-sandbox`, and its composable is classified as `demo-local-composable` because its only active consumer was the archived page. Canonical market/data route assets remain in place.

## Post-Move Checks

| Check | Command / Scope | Result |
| --- | --- | --- |
| Exact active-reference search for page | `rg -n "src/views/MarketDataDemo\|@/views/MarketDataDemo\|../MarketDataDemo\\.vue\|./MarketDataDemo\\.vue\|MarketDataDemo\\.vue" web/frontend/src web/frontend/tests web/frontend/package.json .github --glob '!**/.claude/**'` | Passed; exit `1`, no active references found. |
| Exact active-reference search for composable | `rg -n "@/composables/useMarketData\|src/composables/useMarketData\|composables/useMarketData\|useMarketData\\.js" web/frontend/src web/frontend/tests web/frontend/package.json .github --glob '!**/.claude/**'` | Passed; exit `1`, no active references found. |
| OpenSpec strict validation | `openspec validate update-frontend-view-governance --strict` | Passed. |
| Markdown governance gate | Archive README, this execution report, and `tasks.md` | Passed; `3` files, `0` errors. |
| Diff whitespace check | `git diff --check -- <changed paths>` | Passed. |

## Staged Commit Gate

Final staged scope:

| Check | Result |
| --- | --- |
| `git diff --cached --name-status` | Passed; staged scope contains only `MarketDataDemo.vue` rename, `useMarketData.js` rename, archive README, this execution record, and `tasks.md`. |
| `git diff --cached --check` | Passed. |
| `gitnexus_detect_changes(scope="staged")` | Passed; risk `low`, changed symbols `0`, affected processes `0`. |
