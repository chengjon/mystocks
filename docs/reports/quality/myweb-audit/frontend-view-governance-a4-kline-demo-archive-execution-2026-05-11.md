# Frontend View Governance A4 KLineDemo Archive Execution

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: execution record for `A4-kline-demo-archive`.

## Approved Scope

Moved file:

- `web/frontend/src/views/KLineDemo.vue`

Retained out of scope:

- `web/frontend/src/views/market/Technical.vue`
- `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue`
- `web/frontend/src/components/charts/ProKLineChart.vue`
- `web/frontend/src/components/market/ProKLineChart.vue`
- K-line unit and E2E tests
- `web/frontend/src/views/MarketDataDemo.vue`
- `web/frontend/src/views/DataVisualizationShowcase.vue`
- `web/frontend/src/views/SkeletonUsage.vue`
- `web/frontend/src/views/SmartDataSourceTest.vue`
- `web/frontend/src/views/StockAnalysisDemo.vue`

## Pre-Move Evidence

GitNexus impact:

| Target | Risk | Direct dependents | Affected processes |
| --- | --- | ---: | ---: |
| `KLineDemo.vue` | LOW | 0 | 0 |

Static reference checks:

- No active import/read was found for `src/views/KLineDemo`, `@/views/KLineDemo`, or `KLineDemo.vue` under `web/frontend/src`, `web/frontend/tests`, `web/frontend/package.json`, or `.github`.
- `/market/kline` remains represented by `web/frontend/src/views/market/Technical.vue`.
- Detail K-line analysis remains represented by `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue`.
- K-line component behavior remains covered by existing component/unit/E2E references.

## Files Moved

| Original path | Archive path |
| --- | --- |
| `web/frontend/src/views/KLineDemo.vue` | `archive/web/frontend/src/views/root-sandbox/kline-demo/KLineDemo.vue` |

## Files Added

| File | Purpose |
| --- | --- |
| `archive/web/frontend/src/views/root-sandbox/kline-demo/README.md` | Governed archive manifest and restore rule |

## Cleanup Decision

This is an archive move, not deletion. The page is classified as `archive-candidate/demo-sandbox` because it was a root-level visual demo shell with no active route, menu, package, or direct test ownership. Canonical K-line route/component/test assets remain in place.

## Post-Move Checks

| Check | Command / Scope | Result |
| --- | --- | --- |
| Exact active-reference search | `rg -n "src/views/KLineDemo\|@/views/KLineDemo\|../KLineDemo\\.vue\|./KLineDemo\\.vue\|KLineDemo\\.vue" web/frontend/src web/frontend/tests web/frontend/package.json .github --glob '!**/.claude/**'` | Passed; exit `1`, no active references found. |
| OpenSpec strict validation | `openspec validate update-frontend-view-governance --strict` | Passed. |
| Markdown governance gate | Archive README, this execution report, and `tasks.md` | Passed; `3` files, `0` errors. |
| Diff whitespace check | `git diff --check -- <changed paths>` | Passed. |

## Staged Commit Gate

Final staged scope:

| Check | Result |
| --- | --- |
| `git diff --cached --name-status` | Passed; staged scope contains only `KLineDemo.vue` rename, archive README, this execution record, and `tasks.md`. |
| `git diff --cached --check` | Passed. |
| `gitnexus_detect_changes(scope="staged")` | Passed; risk `low`, changed symbols `0`, affected processes `0`. |
