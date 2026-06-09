# Frontend View Governance A4 Demo OpenStock And Root Sidecars Startup

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: startup package for the next frontend-view governance domain after A3 monitoring closeout.

This package does not move files, edit runtime code, update tests, or change routes.

## Selected Domain

```text
A4-demo-openstock-and-root-demo-sidecars
```

## Why This Domain

A3 monitoring cleanup intentionally left demo/OpenStock references untouched. After archiving the legacy monitoring Watchlist page, the remaining `WatchlistManagement` references in active source/test scope point to a distinct demo component family:

- `web/frontend/src/views/demo/openstock/components/WatchlistManagement.vue`
- `web/frontend/src/views/demo/OpenStockDemo.vue`
- `web/frontend/src/views/OpenStockDemo.vue`

These are not monitoring route owners. They should be governed with demo/root sidecar lifecycle rules, not mixed into the A3 archive chain.

## Initial Scope

Read-only inventory scope:

- `web/frontend/src/views/demo/OpenStockDemo.vue`
- `web/frontend/src/views/OpenStockDemo.vue`
- `web/frontend/src/views/demo/openstock/components/*`
- `web/frontend/src/views/demo/openstock/config.ts`
- `web/frontend/src/views/examples/*`
- `web/frontend/src/views/freqtrade-demo/*`
- `web/frontend/src/views/tdxpy-demo/*`
- root demo/test/sandbox pages listed by `frontend-view-checklist-root-demo-sidecars-2026-05-11.md`

Explicit exclusions:

- `web/frontend/src/views/TradingDashboard.vue`, because it remains active `/trade/terminal` route truth.
- `web/frontend/src/views/Login.vue` and `web/frontend/src/views/NotFound.vue`, already covered by blank-layout governance.
- archived A1/A2/A3 files under `archive/`.

## Current Evidence

Existing read-only evidence to reuse:

- `docs/reports/quality/myweb-audit/frontend-view-checklist-demo-examples-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-demo-directory-2026-05-10.md`
- `docs/reports/quality/myweb-audit/frontend-view-checklist-root-demo-sidecars-2026-05-11.md`
- `docs/reports/quality/myweb-audit/frontend-view-guard-map-2026-05-10.json`

Current active router/menu truth:

- No active router/menu owner was found for `views/demo/openstock`, `views/examples`, `views/freqtrade-demo`, or `views/tdxpy-demo`.
- Root `FreqtradeDemo.vue` and `TdxpyDemo.vue` still own their child tab directories.
- Root/demo OpenStock pages own the OpenStock demo component family.

## Required Next Step

Prepare a read-only A4 inventory delta:

```text
A4-demo-openstock-root-sidecars-inventory
```

Required output:

- exact file list
- route/menu owner status
- direct importer status
- direct guard/test status
- lifecycle classification: `retain-as-demo`, `absorb-assets`, `archive-candidate`, `sidecar-exclude`, or `active-route-exclude`
- successor or `no-successor-needed` hint for every archive-candidate

## Non-Scope

- Do not archive demo files in the startup package.
- Do not remove package `lint:artdeco:changed` targets.
- Do not modify OpenStock UI or root demo wrappers.
- Do not merge demo components into canonical business routes without a separate absorption plan.
- Do not mix `TradingDashboard.vue` into demo cleanup.

## Recommended Batch Order

1. `A4-demo-openstock-root-sidecars-inventory`: read-only exact inventory and guard map reconciliation.
2. `A4-openstock-demo-decision`: decide whether OpenStock demo is retained as demo documentation, absorbed, or archive-prepared.
3. `A4-root-demo-parent-shells-decision`: decide parent/child lifecycle for Freqtrade, Tdxpy, Pyprofiling, and similar demo shells.
4. `A4-demo-archive-prep`: only after successor/no-successor proof and guard retirement plans exist.
