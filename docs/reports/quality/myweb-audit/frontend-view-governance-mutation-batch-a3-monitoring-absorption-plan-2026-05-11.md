# Frontend View Governance Mutation Batch A3 Monitoring Absorption Plan

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: proposed A3 mutation batch for `openspec/changes/update-frontend-view-governance`.

This plan does not move files, edit routes, edit tests, or change runtime code.

## Why A3 Chooses Monitoring Before Root Styles

The remaining recommended choices after A1/A2 are monitoring functional absorption and root style residual cleanup. Root styles are still coupled to many root/demo page lifecycle decisions and the broad `src/views/styles` ArtDeco directory gate. Monitoring is a better next batch because it has a clear functional split across current canonical domains: risk, watchlist, and system.

## Candidate Set

| File | Current route/menu owner | Guard status | Initial lifecycle |
| --- | --- | --- | --- |
| `web/frontend/src/views/monitoring/MonitoringDashboard.vue` | none found | direct local spec, style/cleanup guards | `candidate-review/legacy-static-shell` |
| `web/frontend/src/views/monitoring/AlertRulesManagement.vue` | none found | style normalization guard | `candidate-review/legacy-functional-page` |
| `web/frontend/src/views/monitoring/RiskDashboard.vue` | none found | style bridge + style normalization guard | `candidate-review/legacy-functional-page` |
| `web/frontend/src/views/monitoring/WatchlistManagement.vue` | none found | style bridge + style normalization guard | `candidate-review/legacy-functional-page` |
| `web/frontend/src/views/monitoring/composables/*.ts` | page-local helpers | tied to legacy pages | `candidate-support-asset` |
| `web/frontend/src/views/monitoring/styles/*.scss` | page-local styles | direct style guards | `candidate-support-asset` |

## Current Canonical Successor Map

| Legacy asset | Candidate successor | Absorption decision |
| --- | --- | --- |
| `MonitoringDashboard.vue` | `/market/realtime`, `/risk/overview`, `/market/lhb` guidance already embedded in shell | Prefer archive after guard retirement; no additional reusable runtime asset found. |
| `AlertRulesManagement.vue` + `useAlertRulesManagement.ts` | `/risk/overview`, `/risk/alerts` | Do not archive yet. Extract only if canonical risk pages lack rule CRUD; otherwise retire as legacy duplicate. |
| `RiskDashboard.vue` + `useRiskDashboard.ts` | `/risk/overview`, `/risk/stop-loss`, `/risk/center` | Do not absorb as truth. It contains `Math.random()` trend generation, `|| 0` fallbacks, and old `/api/monitoring/analysis/portfolio/*` fetch paths. Prefer downgrade/archive after confirming canonical risk coverage. |
| `WatchlistManagement.vue` + `useWatchlistManagement.ts` | `/watchlist/manage` via `views/artdeco-pages/stock-management-tabs/WatchlistManager.vue` and `stores/apiStores.ts` | Likely archive candidate after confirming canonical watchlist create/delete/stock management covers the useful workflow. |
| `MonitoringDashboard.scss` | none | Orphan-style candidate once direct style guard is retired. |
| `AlertRulesManagement.scss`, `RiskDashboard.scss`, `WatchlistManagement.scss` | page-local only | Move with owning legacy page after guard retirement or absorption decision. |

## Hard Blockers Before Mutation

- `web/frontend/tests/unit/config/monitoring-style-sources.spec.ts` reads monitoring style files.
- `web/frontend/tests/unit/config/monitoring-fintech-bridge-style-sources.spec.ts` reads risk/watchlist monitoring styles.
- `web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts` reads all four monitoring Vue files.
- `web/frontend/tests/unit/config/console-log-cleanup-batch-1.spec.ts` includes `MonitoringDashboard.vue`.
- `web/frontend/src/views/monitoring/__tests__/MonitoringDashboard.spec.ts` directly imports `MonitoringDashboard.vue`.
- Historical E2E specs still mention `/monitoring/watchlists` and `/monitoring/risk`, but current `router/index.ts` does not expose those as active route truth.

## Recommended A3 Profiles

| Profile | Scope | Work | Risk |
| --- | --- | --- | --- |
| `A3-static-shell-archive` | `MonitoringDashboard.vue`, its local test, and `MonitoringDashboard.scss` guard references | Retire/migrate direct static-shell guards, archive the static shell and orphan style | Low-medium |
| `A3-watchlist-archive-prep` | `WatchlistManagement.vue`, `useWatchlistManagement.ts`, `WatchlistManagement.scss` | Compare against `/watchlist/manage`; if fully covered, retire guards and archive | Medium |
| `A3-risk-downgrade` | `RiskDashboard.vue`, `useRiskDashboard.ts`, `RiskDashboard.scss` | Downgrade to honest static shell or archive after confirming `/risk/*` coverage | Medium-high |
| `A3-alert-rules-review` | `AlertRulesManagement.vue`, `useAlertRulesManagement.ts`, `AlertRulesManagement.scss` | Compare rule CRUD against `/risk/overview` and `/risk/alerts`; absorb missing CRUD only if current canonical pages lack it | Medium-high |

Recommended next profile: `A3-static-shell-archive`.

Reason: `MonitoringDashboard.vue` is already an honest static shell with no active route/menu owner. It is the smallest monitoring mutation and avoids prematurely absorbing old API logic or stale pseudo-live calculations.

## Required Pre-Mutation Checks

```bash
rg -n "MonitoringDashboard|monitoring/MonitoringDashboard|src/views/monitoring/MonitoringDashboard|MonitoringDashboard.scss" web/frontend/src web/frontend/tests web/frontend/package.json docs openspec --glob '!**/.claude/**'
rg -n "@/views/monitoring|../monitoring|./monitoring" web/frontend/src web/frontend/tests --glob '!**/.claude/**'
rg -n "/monitoring/dashboard|/monitoring/risk|/monitoring/watchlists" web/frontend/src/router/index.ts web/frontend/src/layouts/MenuConfig.ts web/frontend/tests docs --glob '!**/.claude/**'
```

Before touching functional pages, also compare against canonical successors:

```bash
rg -n "alert-rules|watchlists|risk overview|stop-loss|createWatchlist|deleteWatchlist" web/frontend/src/views/risk web/frontend/src/views/watchlist web/frontend/src/stores web/frontend/tests/e2e --glob '!**/.claude/**'
```

## Required Validation

For `A3-static-shell-archive`:

```bash
cd web/frontend && npx vitest run src/views/monitoring/__tests__/MonitoringDashboard.spec.ts tests/unit/config/monitoring-style-sources.spec.ts tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts tests/unit/config/console-log-cleanup-batch-1.spec.ts
openspec validate update-frontend-view-governance --strict
```

If package or style guards are edited:

```bash
cd web/frontend && npm run lint:artdeco:changed
```

If route/menu entries are edited, run route/layout smoke. The preferred A3 profile should not edit router or menu.

## Non-Scope

- Do not restore `/monitoring/*` routes.
- Do not add monitoring pages to `MenuConfig.ts`.
- Do not absorb `RiskDashboard.vue` random trend or fallback-derived values into canonical risk pages.
- Do not treat old E2E `/monitoring/*` references as current route truth without checking `router/index.ts`.
- Do not archive `AlertRulesManagement.vue`, `RiskDashboard.vue`, or `WatchlistManagement.vue` until successor coverage is explicitly recorded.

## Approval Needed

A3 is not yet approved for mutation. The next decision should choose exactly one profile:

- `A3-static-shell-archive`
- `A3-watchlist-archive-prep`
- `A3-risk-downgrade`
- `A3-alert-rules-review`
- `A3-defer`
