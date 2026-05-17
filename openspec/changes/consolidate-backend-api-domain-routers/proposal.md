# Change: Consolidate backend API domain routers

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why

The backend quality audit found that several API domains still mix flat modules, package routers, compatibility shims, and historical route registrations. P3-B Safe Closure resolved announcement (dual registration fix + orphan deletion), risk (6 orphan files deleted), backup (new aggregator router registered), and trading (orphan deleted). The remaining structural work requires OpenSpec-approved proposals.

### Current State (post-P3-B)

| Domain | Router Files | Registration | Issues |
|--------|-------------|-------------|--------|
| **Strategy** | `strategy.py` (6 routes) + `strategy_mgmt.py` (10 routes) + `strategy_management/` package (18 routes) | `/api/v1/strategy` (strategy.py + get_monitoring_db.py), `/api/strategy-mgmt` (strategy_mgmt.py) | Two routers share `/api/v1/strategy` prefix; 1 full-path duplicate; strategy_mgmt.py is parallel implementation |
| **Market** | `market.py` (shim) + `market/` package + `market_v2.py` | `/api/v1/market` (market.py shim → market/), `/api/v2/market` (market_v2.py) | market.py is bare shim with `from market import *` |
| **Risk** | `risk/` package only | `/api/v1/risk` | RESOLVED in P3-B — single canonical package |
| **Announcement** | `announcement/` package only | `/api/announcement` | RESOLVED in P3-B — single canonical package |

### Key Evidence

1. **Full-path duplicate**: `GET /api/v1/strategy/backtest/results/{backtest_id}` served by both `get_monitoring_db.py` (registered) and `get_backtest_result.py` (orphan router not registered, but same resolved path)
2. **Prefix collision**: `strategy.py` (registered via VERSION_MAPPING at `/api/v1/strategy`) and `get_monitoring_db.py` (own prefix `/api/v1/strategy`) both register routes under the same base URL — FastAPI resolves by registration order, last-wins for same path
3. **Parallel implementation**: `strategy_mgmt.py` provides its own CRUD/backtest using SQLAlchemy repos, while `get_monitoring_db.py` uses MyStocksUnifiedManager — different data access patterns for overlapping functionality
4. **Frontend consumers**: `strategyService.ts` → `/api/v1/strategy/*`, `dashboardService.ts` → `/api/strategy-mgmt/*`, `pageConfig.ts` → mixed paths

## What Changes

### Phase 1: Strategy domain convergence (P3-C1)

1. Delete orphan `get_backtest_result.py` — its router is not registered; merge `get_backtest_chart_data` function into `get_monitoring_db.py`
2. Establish `strategy_management/` package as canonical management router at `/api/v1/strategy`
3. Merge `strategy.py` execution routes (6) into `strategy_management/` as a separate module (e.g., `_strategy_execution_router.py`)
4. Add compatibility redirect from `/api/strategy-mgmt/*` → `/api/v1/strategy/*` until `dashboardService.ts` is updated
5. Update `dashboardService.ts` to use canonical path
6. Delete `strategy_mgmt.py` after migration
7. Keep `strategy_list_mock.py` as-is (conditional dev-only)

### Phase 2: Market domain flat→package (P3-C6)

1. Delete `market.py` bare shim (`from market import *`)
2. Update `router_registry.py` import to use `market/` package directly
3. No URL change — `market/` package's `__init__.py` already exports `router`

## Impact

- Affected specs:
  - `api-integration`
  - `api-documentation`
  - `architecture-governance`
- Affected code:
  - `web/backend/app/api/strategy_management/` — structural changes, new module
  - `web/backend/app/api/strategy.py` — merge into package, then delete
  - `web/backend/app/api/strategy_mgmt.py` — migrate, then delete
  - `web/backend/app/api/strategy_management/get_backtest_result.py` — delete orphan
  - `web/backend/app/router_registry.py` — updated registrations
  - `web/backend/app/api/market.py` — delete shim
  - `web/frontend/src/services/dashboardService.ts` — URL update
  - Tests consuming `/api/strategy-mgmt/*`

## Scope

### In

- Strategy domain 3-router → 1-package convergence
- Market domain shim deletion
- Frontend URL updates for affected paths
- Route table baseline update after each change

### Out

- Health endpoint consolidation (P3-C7, separate proposal)
- Core/Services singleton→Depends migration (P3-C3/C3-C4, separate proposal)
- Core exception consolidation (P3-C5, separate proposal)
- Core subdirectory split (P3-C8, separate proposal)
- Schema directory merge (P3-C10, separate proposal)
- Response model or data access pattern changes
- Database schema changes

## Source Evidence

- `docs/reports/quality/backend-audit-phase3-decision-records.md` — P3-A2 strategy decision
- `docs/reports/quality/generated/backend-fullpath-route-table.md` — current baseline (589 routes, 1 duplicate)
- `docs/reports/quality/backend-route-table-openapi-baseline-2026-05-18.md`
- P3-B commit history (orphan deletions, registration fixes)

## Approval Boundary

This change is a proposal and design package only. It does not approve code implementation. Implementation must not begin until this OpenSpec change is reviewed and approved.
