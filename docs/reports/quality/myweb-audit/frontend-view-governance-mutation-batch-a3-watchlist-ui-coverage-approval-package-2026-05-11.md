# Frontend View Governance A3 Watchlist UI Coverage Approval Package

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: approval package for `A3-watchlist-ui-coverage-minimal` under `openspec/changes/update-frontend-view-governance`.

This package does not move files, edit runtime code, update tests, or change routes.

## Proposed Batch

```text
A3-watchlist-ui-coverage-minimal
```

This is a runtime UI coverage batch, not an archive batch.

## Why Archive Is Still Blocked

`monitoring/WatchlistManagement.vue` is the last active source file group under `web/frontend/src/views/monitoring/`, but it still contains useful UI-level workflows that are not fully exposed by the canonical `/watchlist/manage` route.

The previous A3 watchlist absorption already covered the action helper layer:

- `createMonitoringWatchlistActions().deleteWatchlist(watchlistId)`
- `createMonitoringWatchlistActions().addStock(watchlistId, richPayload)`
- `createMonitoringWatchlistActions().removeStock(watchlistId, symbol)`

However, the canonical route UI currently exposes:

- list watchlists
- select watchlist
- create watchlist through a prompt
- remove stock
- import/export JSON

It does not yet expose:

- delete current watchlist
- add stock from the canonical UI

Therefore archiving the legacy page now would risk discarding usable UI behavior before the canonical route has made an explicit product decision.

## Proposed Runtime Scope

Allowed files:

- `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`
- Existing direct tests for the canonical watchlist route if present, such as `web/frontend/src/views/watchlist/__tests__/Manage.spec.ts`
- `openspec/changes/update-frontend-view-governance/tasks.md`
- A short execution report under `docs/reports/quality/myweb-audit/`

Allowed behavior:

- Add a small delete-current-watchlist control near the watchlist tabs or action area.
- Wire it to the existing `watchlistActions.deleteWatchlist(displayActiveWatchlistId.value)`.
- After successful delete, refresh watchlist state and avoid leaking the deleted watchlist selection.
- Add a minimal add-stock control, or explicitly record that add-stock remains API-only for this batch.
- If a minimal add-stock control is added, only require `stock_code`; do not recreate the full legacy rich form unless explicitly approved.
- Preserve existing verified snapshot, pending, stale, and first-load failure semantics.

## Explicit Non-Scope

- Do not archive `web/frontend/src/views/monitoring/WatchlistManagement.vue`.
- Do not move `useWatchlistManagement.ts` or `WatchlistManagement.scss`.
- Do not edit `router/index.ts` or `MenuConfig.ts`.
- Do not absorb legacy total value, day P&L, win rate, or active-alert stats.
- Do not introduce `Math.random()`-derived runtime truth.
- Do not create a second watchlist store or independent snapshot layer.
- Do not change the API contract unless a separate contract proposal is approved.

## TDD Plan

Add or update canonical watchlist route tests first:

- Deleting the active watchlist calls `deleteWatchlist` with the active id and refreshes state.
- Delete control is disabled or absent when no active watchlist exists.
- Minimal add-stock, if implemented, calls `addStock` with the active id and a trimmed `stock_code`.
- Stale verified rows remain visible when a refresh after an action fails.
- Count KPI placeholders remain `--` before verified stock snapshots.

Then implement the smallest UI changes needed to make those tests pass.

## Required Impact Checks

Before runtime edits:

```json
{
  "repo": "mystocks_spec",
  "target": "web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue",
  "direction": "upstream",
  "maxDepth": 3,
  "includeTests": true
}
```

If `createMonitoringWatchlistActions` is changed, also run impact on that symbol. The preferred minimal batch should not need to change it.

## Required Validation

```bash
cd web/frontend && npx vitest run src/views/watchlist/__tests__/Manage.spec.ts tests/unit/stores/watchlist-api-stores.spec.ts
openspec validate update-frontend-view-governance --strict
python scripts/compliance/markdown_governance_gate.py --root-dir /opt/claude/mystocks_spec --format text --path openspec/changes/update-frontend-view-governance/tasks.md
git diff --check -- web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue web/frontend/src/views/watchlist/__tests__/Manage.spec.ts openspec/changes/update-frontend-view-governance/tasks.md
```

Before commit:

```json
{
  "repo": "mystocks_spec",
  "scope": "staged",
  "cwd": "/opt/claude/mystocks_spec"
}
```

## Completion Criteria

The batch is complete when:

- Canonical `/watchlist/manage` has an explicit decision for delete-watchlist UI and add-stock UI.
- Tests verify the chosen UI behavior.
- Legacy random/fallback-derived stats remain unabsorbed.
- `monitoring/WatchlistManagement.vue` remains in place until a later archive-prep batch.
- `tasks.md` advances to a post-runtime archive decision placeholder.

## Approval Needed

Recommended approval wording:

```text
批准执行 A3-watchlist-ui-coverage-minimal，只在 /watchlist/manage canonical UI 补齐删除清单，并对添加股票采用最小 stock_code 输入或明确 API-only 决策；不归档 monitoring/WatchlistManagement，不吸收旧页随机/兜底统计。
```

Without explicit approval, no runtime UI edit or archive move should occur.
