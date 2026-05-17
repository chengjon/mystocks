## Context

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Post-P3-B state: announcement, risk, trading, and backup domains are resolved. Strategy and market domains remain.

### Strategy Domain (P3-C1)

Three active routers share the strategy domain:

| Router | File | Prefix | Routes | Registered |
|--------|------|--------|--------|-----------|
| strategy.py | Flat, 6 routes | bare | `/api/v1/strategy` (via VERSION_MAPPING) | Yes |
| strategy_mgmt.py | Flat, 10 routes | `/api/strategy-mgmt` | `/api/strategy-mgmt/*` | Yes |
| strategy_management/ | Package, 18 routes (16+2) | `/api/v1/strategy` | `/api/v1/strategy/*` | Yes (16 from get_monitoring_db.py), orphan (2 from get_backtest_result.py) |

**Key fact**: `strategy.py` and `get_monitoring_db.py` both register routes under `/api/v1/strategy`. They are complementary (execution vs management), not competing, but the shared prefix creates a maintenance smell.

**Full-path duplicate**: `GET /api/v1/strategy/backtest/results/{backtest_id}` — served by both `get_monitoring_db.py` (registered) and `get_backtest_result.py` (orphan router).

### Market Domain (P3-C6)

`market.py` is a bare shim:
```python
"""market - 向后兼容入口"""
from market import *  # noqa: F401, F403
```

The `market/` package is the canonical implementation. The shim adds no value.

## Goals

- Single package per domain with clear prefix ownership
- Zero full-path route duplicates
- All frontend consumers on canonical paths
- Compat shims only where consumer migration is not immediate

## Non-Goals

- Health endpoint consolidation
- Core/Services DI migration
- Core exception merging
- Response model changes
- Database schema changes

## Decisions

### Decision: strategy_management/ is canonical for all strategy routes

The `strategy_management/` package becomes the single canonical router for all strategy operations (execution + management + CRUD).

| Sub-module | Responsibility | Routes |
|-----------|---------------|--------|
| `get_monitoring_db.py` | Strategy management CRUD, lifecycle, models, backtest | 16 |
| `_strategy_execution_router.py` (NEW) | Strategy execution (run, definitions, matched-stocks, stats) | 6 (from strategy.py) |
| `get_backtest_result.py` | DELETED (orphan, chart-data merged into get_monitoring_db.py) | 0 |

### Decision: Compat redirect for strategy-mgmt

`strategy_mgmt.py` is deleted. A FastAPI compatibility redirect router at `/api/strategy-mgmt/*` sends 307 → `/api/v1/strategy/*` until all frontend consumers are migrated.

### Decision: market.py shim deleted

No consumers depend on the shim. The `market/` package `__init__.py` already exports `router`. Update import in `router_registry.py`.

### Decision: Frontend consumer migration is part of this change

- `dashboardService.ts`: `/api/strategy-mgmt/strategies` → `/api/v1/strategy/strategies`
- `pageConfig.ts`: `/api/strategy/parameters`, `/api/strategy/signals`, `/api/strategy/gpu`, `/api/strategy/opt` — verify these have backend handlers

## Migration Plan

### Step 1: Delete get_backtest_result.py orphan

- Merge `get_backtest_chart_data` function into `get_monitoring_db.py`
- Remove `get_backtest_result.py`
- Update `__init__.py` exports
- Verify: full-path duplicate count → 0

### Step 2: Extract strategy.py execution routes into package

- Create `strategy_management/_strategy_execution_router.py` with the 6 execution routes from `strategy.py`
- Add sub-router to `strategy_management/__init__.py` aggregator
- Update `router_registry.py`: remove `strategy` from `router_modules` dict
- Delete `strategy.py` flat file
- Verify: all 6 execution routes still resolve at `/api/v1/strategy/*`

### Step 3: Add compat redirect for strategy-mgmt

- Create minimal compat router with 307 redirects: `/api/strategy-mgmt/{path}` → `/api/v1/strategy/{path}`
- Register in `router_registry.py`
- Delete `strategy_mgmt.py` flat file
- Update `dashboardService.ts` to use canonical path
- Verify: compat redirect responds 307, frontend uses canonical path

### Step 4: Delete market.py shim

- Update `router_registry.py` import: `from .api import market` → `from .api.market import router` (verify current resolution)
- Delete `market.py` flat file
- Verify: market routes unchanged

### Step 5: Baseline update

- Regenerate full-path route table
- Update route count metrics
- Verify: 0 full-path duplicates, reduced orphan count

## Rollback

Each step is independently reversible:

1. Restore deleted file from git
2. Restore router_registry.py import
3. Restore frontend URL if changed
4. Re-run route table script to verify

## Risks / Trade-offs

- **strategy_mgmt.py deletion**: Has real frontend consumer (`dashboardService.ts`) and test. Compat redirect + frontend update mitigates this.
- **strategy.py merge**: 6 execution routes moved into package. Functional code unchanged, only routing structure changes.
- **market.py deletion**: Pure shim with no added logic. Near-zero risk.
- **File size**: `get_monitoring_db.py` is already large. Adding chart-data function is minimal (2 functions). The new `_strategy_execution_router.py` stays under 800-line limit.
