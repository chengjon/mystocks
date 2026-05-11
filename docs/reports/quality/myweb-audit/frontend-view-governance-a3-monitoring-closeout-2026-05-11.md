# Frontend View Governance A3 Monitoring Closeout

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: closeout for A3 monitoring lifecycle cleanup under `openspec/changes/update-frontend-view-governance`.

## Result

A3 monitoring cleanup is complete.

Current active source state:

- `web/frontend/src/views/monitoring/` contains no remaining source files.
- No current `router/index.ts` or `MenuConfig.ts` entry points to `views/monitoring/*`.
- The remaining `src/views/monitoring` mention in `web/frontend/package.json` is an ArtDeco changed-file lint target for the empty directory, not page ownership.
- The remaining `monitoring-style-sources.spec.ts` assertion checks that archived `AlertRulesManagement.scss` is absent from the active monitoring style directory.

## Archived Monitoring Assets

Governed archive paths:

- `archive/web/frontend/src/views/monitoring/static-shell/MonitoringDashboard.vue`
- `archive/web/frontend/src/views/monitoring/static-shell/MonitoringDashboard.scss`
- `archive/web/frontend/src/views/monitoring/static-shell/MonitoringDashboard.spec.ts`
- `archive/web/frontend/src/views/monitoring/alert-rules/AlertRulesManagement.vue`
- `archive/web/frontend/src/views/monitoring/alert-rules/useAlertRulesManagement.ts`
- `archive/web/frontend/src/views/monitoring/alert-rules/AlertRulesManagement.scss`
- `archive/web/frontend/src/views/monitoring/risk-dashboard/RiskDashboard.vue`
- `archive/web/frontend/src/views/monitoring/risk-dashboard/useRiskDashboard.ts`
- `archive/web/frontend/src/views/monitoring/risk-dashboard/RiskDashboard.scss`
- `archive/web/frontend/src/views/monitoring/watchlist-management/WatchlistManagement.vue`
- `archive/web/frontend/src/views/monitoring/watchlist-management/useWatchlistManagement.ts`
- `archive/web/frontend/src/views/monitoring/watchlist-management/WatchlistManagement.scss`

## Canonical Successors

Successor coverage used during A3:

- Monitoring dashboard static shell: no runtime successor needed; archived after direct guard retirement.
- Alert rules: `/risk/alerts` absorbed minimal CRUD and retains verified snapshot/provenance behavior.
- Risk dashboard: `/risk/overview`, `/risk/alerts`, `/risk/stop-loss`, `/risk/management`, and `/risk/pnl` cover current risk-domain route truth; random/fallback-derived old metrics were not absorbed.
- Watchlist management: `/watchlist/manage` covers list/select/create/delete/add/remove/import/export and verified snapshot/stale-state behavior; random/fallback-derived old stats were not absorbed.

## Validation Evidence

Executed during A3 batches:

- Targeted config Vitest for monitoring guard retirement.
- Risk route tests for alert/risk successor coverage.
- Watchlist route and store tests for canonical action/UI coverage.
- OpenSpec strict validation after each batch.
- Markdown governance gate after each docs/tasks update.
- GitNexus impact before archive moves and staged change detection before commits.

Most recent A3 archive validation:

```text
Vitest: 4 files passed, 13 tests passed
OpenSpec: update-frontend-view-governance valid
GitNexus staged detection: low risk, affected processes 0
```

## Remaining Non-Blocking Mentions

These are not active monitoring page ownership:

- `web/frontend/src/views/demo/openstock/components/WatchlistManagement.vue` and OpenStock demo references.
- Historical E2E labels such as `WatchlistManagement Page` and `RiskDashboard Page`.
- Archived docs and inventory JSON records.
- Empty-directory lint target `src/views/monitoring` in `web/frontend/package.json`.

## Next Governance Domain

Recommended next domain:

```text
A4-demo-openstock-and-root-demo-sidecars
```

Reason:

- A3 left OpenStock demo Watchlist references untouched by design.
- Demo/root sidecar pages still contain page-like assets that should be classified separately from canonical route truth.
- This keeps the governance sequence narrow and avoids mixing demo lifecycle decisions with active business route cleanup.
