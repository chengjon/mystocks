# Decision Records: Phase 3-A Route Canonicalization

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

---

# P3-A1: Announcement Canonical Route

> **Date**: 2026-05-18
> **Status**: Proposed
> **Deciders**: Pending review

## Context

The announcement domain has three route sources producing potential URL conflicts:

1. **Flat file** `app/api/announcement.py` — defines 11 routes with `APIRouter()` (no prefix)
2. **Package** `app/api/announcement/routes.py` — defines 14 routes with `APIRouter(prefix="/announcement")`
3. **Dual registration** in `router_registry.py`:
   - Line 83: `router_modules["announcement"]` registered via VERSION_MAPPING at prefix `/api/v1/announcement`
   - Line 96: `announcement.router` registered at prefix `/api` with tags `["announcement"]`

Since `from .api import announcement` resolves to the **package** (not the flat file), both registrations target `announcement/routes.py`'s router. The flat file is unreachable via normal import.

## Current Facts

| Fact | Value | Source |
|------|-------|--------|
| Flat file routes | 11 decorators | AST scan `announcement.py` |
| Package routes | 14 decorators | AST scan `announcement/routes.py` |
| Full-path from registry line 96 | `/api/announcement/{local_path}` | `/api` + `/announcement` + local |
| Full-path from VERSION_MAPPING (line 83) | `/api/v1/announcement/announcement/{local_path}` | `/api/v1/announcement` + `/announcement` + local (DOUBLE PREFIX BUG) |
| Flat file registration | None (orphan) | Not in `router_registry.py` |
| Frontend consumers | All use `/api/announcement/*` | `useAnnouncementMonitor.ts` |
| Test consumers | All use `/api/announcement/*` | `test_announcement_api.py`, e2e tests |
| `/api/v1/announcement` consumers | None found | `versionNegotiationPolicy.ts` declares version but no direct calls |
| Local decorator duplicates | 11 (flat vs package same local paths) | Baseline §2.1 |
| Full-path conflicts | **0** (flat file is orphan; package registered at different prefixes) | P3-0.5 output |

## Options Considered

### Option A: Keep package as canonical, delete flat file, remove VERSION_MAPPING entry

- **Result**: Single router at `/api/announcement/*`. Remove VERSION_MAPPING `"announcement"` key to eliminate the double-prefix bug at `/api/v1/announcement/announcement/*`.
- **Pros**: Cleanest outcome. One source of truth. No compat burden.
- **Cons**: None — `/api/v1/announcement` has zero consumers.

### Option B: Keep both, add compat alias

- **Result**: Package at `/api/announcement/*`, flat file at `/api/announcement-legacy/*`, VERSION_MAPPING alias at `/api/v1/announcement/*`.
- **Pros**: Maximum backward compatibility.
- **Cons**: Unnecessary complexity. No evidence of `/api/v1/announcement` usage. Adds three registrations for one domain.

### Option C: Migrate flat file routes into package, keep VERSION_MAPPING

- **Result**: All 11 flat routes merged into package. VERSION_MAPPING kept for v1 alias.
- **Cons**: Same double-prefix bug remains. More work for no additional benefit.

## Decision

**Option A**: Package `announcement/routes.py` is the canonical router. Flat file `announcement.py` is dead code and should be deleted. VERSION_MAPPING `"announcement"` entry should be removed to eliminate the double-prefix registration bug.

### Compatibility Policy

- **Canonical URL**: `/api/announcement/*` (current working path)
- **Deprecated alias**: `/api/v1/announcement/*` — never had consumers; remove immediately
- **Flat file**: `announcement.py` — orphan (not registered); remove after verification

### Rollback

If `/api/v1/announcement` consumers are discovered after removal, add a one-line `include_router` with prefix `/api/v1/announcement` pointing to the same package router (without the `/announcement` sub-prefix).

## OpenSpec

- **required**: no — this is a dead-code cleanup with zero consumer impact
- **reason**: No API contract change. The canonical URL `/api/announcement/*` is unchanged. Only unreachable routes are removed.

## Follow-up Issues Unlocked

- [ ] P3-B1: Delete `app/api/announcement.py` (flat file)
- [ ] Remove `"announcement"` key from `VERSION_MAPPING`
- [ ] Update `router_registry.py` to remove announcement from `router_modules` dict
- [ ] Verify no `/api/v1/announcement` references in test suites
- [ ] Update route table baseline numbers

## Verification

```bash
# 1. Verify flat file has no import references
grep -r "from.*api.*import.*announcement\b" web/backend/ --include="*.py" | grep -v "__pycache__" | grep -v "announcement/"
grep -r "announcement\.py" web/backend/ --include="*.py" | grep -v "__pycache__"

# 2. Verify no /api/v1/announcement consumers
grep -r "v1/announcement" web/frontend/src/ web/backend/tests/ tests/ --include="*.ts" --include="*.py" | grep -v "versionNegotiationPolicy"

# 3. After fix, regenerate baseline
cd web/backend && python3 ../../scripts/dev/backend_audit_baseline.py /opt/claude/mystocks_spec/docs/reports/quality/generated
cd web/backend && python3 ../../scripts/dev/backend_audit_fullpath_routes.py /opt/claude/mystocks_spec/docs/reports/quality/generated
```

---

# Decision Record: P3-A2 Strategy Domain Canonical Routes

> **Date**: 2026-05-18
> **Status**: Proposed
> **Deciders**: Pending review

## Context

The strategy domain has **five route sources** producing overlapping URL patterns:

1. **Flat file** `app/api/strategy.py` — 6 routes with `APIRouter()` (no prefix), registered via VERSION_MAPPING at `/api/v1/strategy`
2. **Flat file** `app/api/strategy_mgmt.py` — 10 routes with `APIRouter(prefix="/api/strategy-mgmt")`, registered directly (no extra prefix)
3. **Package** `app/api/strategy_management/get_monitoring_db.py` — 16 routes with `APIRouter(prefix="/api/v1/strategy")`, registered as `strategy_management.router` (no extra prefix)
4. **Orphan** `app/api/strategy_management/get_backtest_result.py` — 2 routes with `APIRouter(prefix="/api/v1/strategy")`, router NOT registered anywhere
5. **Mock** `app/api/strategy_list_mock.py` — 1 route with `APIRouter(prefix="/api/mock/strategy")`, conditional (only when `use_mock_apis=True`)

## Current Facts

| Fact | Value | Source |
|------|-------|--------|
| strategy.py routes | 6 decorators (`/definitions`, `/run/single`, `/run/batch`, `/results`, `/matched-stocks`, `/stats/summary`) | AST scan |
| strategy_mgmt.py routes | 10 decorators (CRUD + backtest + health) | AST scan |
| get_monitoring_db.py routes | 16 decorators (CRUD + lifecycle + models + backtest) | AST scan |
| get_backtest_result.py routes | 2 decorators (`/backtest/results/{id}`, `/backtest/results/{id}/chart-data`) | AST scan |
| Full-path overlap: strategy.py vs get_monitoring_db.py | Both serve `/api/v1/strategy/*` | P3-0.5 output |
| Full-path duplicate group | GET `/api/v1/strategy/backtest/results/{backtest_id}` served by both get_monitoring_db.py and get_backtest_result.py | P3-0.5 output #3 |
| Frontend consumers `/api/strategy/*` | `api.js` (6 endpoints), `strategy.ts` (baseUrl) | Frontend code |
| Frontend consumers `/api/v1/strategy/*` | `pageConfig.ts` (4 pages), `router/index.ts` (3 routes), `strategyService.ts` | Frontend code |
| Frontend consumers `/api/strategy-mgmt/*` | `dashboardService.ts` (1 call) | Frontend code |
| Test consumers `/api/v1/strategy/*` | `test_week1_strategy_api.py`, `test_strategy_runtime_fallback.py`, `test_backtest_runtime_fallback.py` | Test code |
| Test consumers `/api/strategy/*` | `_test_e2e_user_workflows_*.py` (multiple) | Test code |
| Test consumers `/api/strategy-mgmt/*` | `test_health_route_conflicts.py` | Test code |

### Functional Overlap Analysis

| Capability | strategy.py | strategy_mgmt.py | get_monitoring_db.py |
|-----------|-------------|-----------------|---------------------|
| Strategy definitions/run | 6 endpoints | — | — |
| Strategy CRUD | — | 5 endpoints | 5 endpoints (duplicate) |
| Strategy lifecycle (start/pause/resume/stop) | — | — | 4 endpoints |
| Model training | — | — | 3 endpoints |
| Backtest run/results/status | — | 4 endpoints | 3 endpoints |
| Backtest chart-data | — | — | (in orphan file) |
| Health | — | 1 endpoint | — |

**Key insight**: `strategy.py` and `get_monitoring_db.py` are **complementary**, not competing. strategy.py handles strategy *execution* (run strategies against stocks), while get_monitoring_db.py handles strategy *management* (CRUD, lifecycle, models, backtests). The overlap is only at `/api/v1/strategy/backtest/results/{backtest_id}` where get_backtest_result.py (orphan) duplicates get_monitoring_db.py.

`strategy_mgmt.py` is a **parallel implementation** of strategy CRUD and backtest, using different infrastructure (SQLAlchemy repos vs MyStocksUnifiedManager).

## Options Considered

### Option A: Keep all three, clarify URL ownership

- **Result**: strategy.py at `/api/strategy/*` (canonical for execution), get_monitoring_db.py at `/api/v1/strategy/*` (canonical for management), strategy_mgmt.py at `/api/strategy-mgmt/*` (canonical for DB-backed CRUD).
- **Pros**: No breaking changes. Clear functional separation.
- **Cons**: Three URLs for one domain is confusing. `/api/v1/strategy` mix of execution + management endpoints is semantically muddy.

### Option B: Merge strategy.py into get_monitoring_db.py package, keep strategy_mgmt.py

- **Result**: Single package at `/api/v1/strategy/*` for all strategy operations. strategy_mgmt.py stays as DB-backed CRUD layer.
- **Pros**: One file removed. Execution + management routes co-located.
- **Cons**: get_monitoring_db.py is already large (16 routes, ~1600 lines). Adding 6 more exceeds the 800-line guideline. Requires structural split first.

### Option C: Declare get_monitoring_db.py as canonical management router, strategy.py as canonical execution router, delete strategy_mgmt.py after migration

- **Result**: Two canonical routers: `/api/v1/strategy/*` (management from package), `/api/strategy/*` (execution from flat file). strategy_mgmt.py functionality migrates to package. Orphan get_backtest_result.py merged.
- **Pros**: Cleanest separation. strategy_mgmt.py is a parallel implementation using different data access patterns — consolidating eliminates the duality.
- **Cons**: Requires OpenSpec for the migration (P3-C1). strategy_mgmt.py has real tests and frontend consumers.

## Decision

**Option A (interim) + Option C (target)**: 

**Interim (P3-B)**: Accept current three-router state with clarified ownership:
- `strategy.py` → canonical for strategy **execution** at `/api/strategy/*` (registered via VERSION_MAPPING → `/api/v1/strategy/*`)
- `get_monitoring_db.py` (package) → canonical for strategy **management** at `/api/v1/strategy/*` (registered directly)
- `strategy_mgmt.py` → **active but non-canonical** at `/api/strategy-mgmt/*` (parallel DB-backed CRUD)
- `get_backtest_result.py` → **orphan**, delete after merging chart-data route into get_monitoring_db.py

**Target (P3-C1)**: Merge strategy_mgmt.py functionality into the strategy_management package, achieving single-package ownership of management routes.

### Compatibility Policy

- **Canonical execution URL**: `/api/v1/strategy/definitions`, `/api/v1/strategy/run/*`, `/api/v1/strategy/results`, `/api/v1/strategy/matched-stocks`, `/api/v1/strategy/stats/summary` (from strategy.py via VERSION_MAPPING)
- **Canonical management URL**: `/api/v1/strategy/strategies/*`, `/api/v1/strategy/{id}/start|pause|resume|stop`, `/api/v1/strategy/models/*`, `/api/v1/strategy/backtest/*` (from get_monitoring_db.py)
- **Active non-canonical**: `/api/strategy-mgmt/*` (from strategy_mgmt.py) — has dashboardService consumer; migrate in P3-C1
- **To delete**: `get_backtest_result.py` (orphan, chart-data route to merge into get_monitoring_db.py)

### Rollback

If strategy_mgmt.py consumers are found beyond dashboardService.ts, add a deprecation header (Sunset) and keep the route active until consumer migration completes.

## OpenSpec

- **required**: yes for P3-C1 (migration of strategy_mgmt.py into package)
- **reason**: Merging two active routers with different data access patterns is a structural change. The P3-A2 decision itself is classification-only and does not change runtime behavior.

## Follow-up Issues Unlocked

- [ ] P3-B: Delete `app/api/strategy_management/get_backtest_result.py` (orphan)
- [ ] P3-B: Merge `get_backtest_chart_data` route into `get_monitoring_db.py`
- [ ] P3-C1: Migrate strategy_mgmt.py routes into strategy_management package
- [ ] Update `dashboardService.ts` from `/api/strategy-mgmt/strategies` to `/api/v1/strategy/strategies`
- [ ] Update route table baseline numbers

## Verification

```bash
# 1. Verify get_backtest_result.py router is not registered
grep -r "get_backtest_result" web/backend/app/router_registry.py
grep -r "backtest_result" web/backend/app/api/strategy_management/__init__.py | grep router

# 2. Verify strategy_mgmt.py consumers
grep -r "strategy-mgmt" web/frontend/src/ --include="*.ts" --include="*.vue" --include="*.js"

# 3. Verify no /api/v1/strategy/backtest/results/{id} collision after orphan removal
cd web/backend && python3 ../../scripts/dev/backend_audit_fullpath_routes.py /opt/claude/mystocks_spec/docs/reports/quality/generated
```

---

# P3-A3: Risk Domain Canonical Routes

> **Date**: 2026-05-18
> **Status**: Proposed
> **Deciders**: Pending review

## Context

The risk domain has multiple route sources with unclear ownership:

1. **Package** `app/api/risk/` — aggregator `__init__.py` includes 4 sub-routers (metrics, alerts, stop_loss, v31)
2. **Facade** `app/api/risk_management_v31.py` — includes `risk_v31/` sub-routers
3. **Package** `app/api/risk_v31/` — stop_loss, alerts, system (3 files, 13 routes)
4. **Compat shim** `app/api/risk_management.py` — re-exports `risk.router`, explicitly deprecated
5. **Business logic** `app/api/risk_management_core.py` — `RiskCalculator` class, no routes

## Current Facts

| Fact | Value | Source |
|------|-------|--------|
| `risk/metrics.py` routes | 6 (VaR, CVaR, Beta, Dashboard, metrics history, calculation) | AST scan |
| `risk/alerts.py` routes | 12 (alert CRUD, rules, notifications, statistics) | AST scan |
| `risk/stop_loss.py` routes | 10 (position management, triggers, history) | AST scan |
| `risk/v31.py` routes | 5 (stock risk, portfolio risk, risk history, stop-loss, health) | AST scan |
| `risk_v31/stop_loss.py` routes | 6 (stop-loss CRUD, overview, calculate) | AST scan |
| `risk_v31/alerts.py` routes | 3 (create alert, statistics, acknowledge) | AST scan |
| `risk_v31/system.py` routes | 4 (stock risk, health, WebSocket connections) | AST scan |
| `risk/` package registration | `app.include_router(risk.router)` at no prefix (L127) | router_registry.py |
| `risk_management_v31.py` registration | **NONE** — orphan | Not in router_registry.py |
| `risk_management.py` registration | **NONE** — compat shim only | Not in router_registry.py |
| `risk_management_core.py` routes | **0** — business logic only | No APIRouter |
| Full-path prefix (risk/ package) | `/api/v1/risk/*` (from sub-router prefix declarations) | Sub-routers declare `prefix="/api/v1/risk"` |
| Frontend consumers `/api/v1/risk/*` | `pageConfig.ts` (5 pages), `unified-api.ts` (6 endpoints), `dashboardService.ts` | Frontend code |
| Frontend consumers `/api/risk-management/v31/*` | `useStopLossMonitoringTab.ts` (4 calls), `RiskOverviewTab.vue` (3 calls) | Frontend code |
| Test consumers `/api/v1/risk/*` | `test_week1_risk_api.py` (16 calls) | Test code |
| Full-path conflicts | GET `/health` from `risk_v31/system.py` (orphan) overlaps with P3-A5 health taxonomy | P3-0.5 output |

### Critical Finding

Frontend calls `/api/risk-management/v31/*` (7 calls in composables/views) but **no registered router serves this prefix**. The `risk_management_v31.py` facade and `risk_v31/` sub-routers are orphans. These frontend calls return 404 at runtime.

### Architecture

```
risk/ (registered via router_registry L127)
├── __init__.py          → APIRouter(), includes sub-routers
├── metrics.py           → APIRouter(prefix="/api/v1/risk"), 6 routes
├── alerts.py            → APIRouter(prefix="/api/v1/risk"), 12 routes
├── stop_loss.py         → APIRouter(prefix="/api/v1/risk"), 10 routes
└── v31.py               → APIRouter(prefix="/api/v1/risk"), 5 routes

risk_v31/ (ORPHAN — not registered)
├── stop_loss.py         → APIRouter(), 6 routes
├── alerts.py            → APIRouter(), 3 routes
└── system.py            → APIRouter(), 4 routes

risk_management.py       → compat shim, re-exports risk.router (deprecated)
risk_management_v31.py   → facade, includes risk_v11/ with prefix /v31 (ORPHAN)
risk_management_core.py  → business logic, no routes
```

## Options Considered

### Option A: Keep risk/ package as canonical, delete orphans, fix frontend

- **Result**: Single package at `/api/v1/risk/*`. Delete `risk_v31/`, `risk_management_v31.py`, `risk_management.py`, `risk_management_core.py`. Update frontend composables to use `/api/v1/risk/*`.
- **Pros**: Cleanest outcome. Eliminates all dead code. Frontend 404s become evidence of the bug this fixes.
- **Cons**: Need to verify that `risk/v31.py` covers all routes that `risk_v31/` would have served.

### Option B: Register risk_management_v31.py at `/api/risk-management`, keep both

- **Result**: risk/ at `/api/v1/risk/*`, risk_management_v31 at `/api/risk-management/v31/*`. Fix frontend by activating the orphan.
- **Cons**: Two parallel routers for one domain. Duplicates `risk_v31/` logic already in `risk/v31.py`.

### Option C: Merge risk_v31/ into risk/ package, delete facade files

- **Result**: All risk routes in one package. Frontend migrates to `/api/v1/risk/*`. No orphans.
- **Cons**: More work than Option A. `risk/v31.py` may already cover needed routes.

## Decision

**Option A**: Package `risk/` is the canonical router. All other risk files are dead code or compat shims.

- `risk_v31/` directory — orphan (not registered). Delete after verifying `risk/v31.py` covers equivalent routes.
- `risk_management_v31.py` — orphan facade. Delete with `risk_v31/`.
- `risk_management.py` — compat shim, explicitly deprecated. Delete.
- `risk_management_core.py` — business logic already extracted to `risk/_shared.py`. Delete after verifying no remaining imports.
- **Frontend fix**: Update `useStopLossMonitoringTab.ts` and `RiskOverviewTab.vue` from `/api/risk-management/v31/*` to `/api/v1/risk/*`.

### Compatibility Policy

- **Canonical URL**: `/api/v1/risk/*` (current working path from risk/ package)
- **Broken URL**: `/api/risk-management/v31/*` — never served by any registered router; frontend calls are 404s
- **No migration needed**: There are no active consumers of the broken URL to migrate

### Rollback

If `risk_v31/` routes provide functionality not covered by `risk/v31.py`, register `risk_management_v31.py` at `/api/risk-management` prefix.

## OpenSpec

- **required**: no — this is dead-code cleanup + frontend bug fix (404 → working URL)
- **reason**: No API contract change. The canonical URL `/api/v1/risk/*` is unchanged. Only unreachable code and broken frontend references are removed/fixed.

## Follow-up Issues Unlocked

- [ ] Verify `risk/v31.py` covers all routes that `risk_v31/` provides
- [ ] Delete `app/api/risk_v31/` directory
- [ ] Delete `app/api/risk_management_v31.py`
- [ ] Delete `app/api/risk_management.py` (compat shim)
- [ ] Verify no imports of `risk_management_core.py` remain
- [ ] Update `useStopLossMonitoringTab.ts` URLs
- [ ] Update `RiskOverviewTab.vue` URLs
- [ ] Regenerate baseline numbers

## Verification

```bash
# 1. Verify risk_v31/ is orphan (no registration)
grep -r "risk_management_v31\|risk_v31" web/backend/app/router_registry.py

# 2. Verify no imports of orphan files
grep -r "risk_management_v31\|from.*risk_v31" web/backend/app/ --include="*.py" | grep -v "__pycache__" | grep -v "risk_v31/"

# 3. Verify frontend broken URLs
grep -r "risk-management/v31" web/frontend/src/ --include="*.ts" --include="*.vue"

# 4. After fix, regenerate baseline
cd web/backend && python3 ../../scripts/dev/backend_audit_fullpath_routes.py /opt/claude/mystocks_spec/docs/reports/quality/generated
```

---

# P3-A4: Singleton Lifecycle Inventory

> **Date**: 2026-05-18
> **Status**: Proposed
> **Deciders**: Pending review

## Context

The backend uses a module-level lazy singleton pattern extensively: `_instance = None` + `get_X()` function that creates on first call. This is incompatible with FastAPI's per-request dependency injection (`Depends()`) and prevents proper testing with dependency overrides.

## Current Facts

| Metric | Value | Source |
|--------|-------|--------|
| Lazy singleton instances (`_x = None` pattern) | 32 | grep for `^_[a-z_]+\s*=\s*None\s*$` in app/ |
| Files with singleton pattern | 30 | across adapters/, core/, services/ |
| Module-level instantiations (no lazy) | ~10 | `adapter_factory.py`, `risk_utils.py`, etc. |
| Already using Depends() | ~15 | `database.py:get_db()`, `strategy_mgmt.py` repos |

### Singleton Classification

| Category | Count | Examples | Migration Risk |
|----------|-------|----------|---------------|
| **Adapters** (data sources) | 6 | eastmoney, akshare, tqlex, cninfo, realtime_mtm, eastmoney_enhanced | Low — stateless, no side effects |
| **Services** (business logic) | 12 | data_service, strategy_service, watchlist_service, indicator_*, backtest_engine | Low-Medium — may hold state |
| **Core infrastructure** | 8 | encryption, password_policy, secure_config, database_factory, service_factory | Medium — initialization side effects |
| **Core managers** | 4 | cache_manager, sync_db_manager, tdengine_manager, room_manager | Medium-High — hold connections/sessions |
| **WebSocket/SSE** | 3 | sse_manager, socketio_manager, stability_manager | High — maintain live connections |
| **Other** | 3 | strategy_registry, email_service, unified_data_service | Low |

## Decision

Classify singletons into three migration tiers:

1. **Tier 1 — Keep as singleton** (7): WebSocket/SSE managers, encryption, socketio, stability, reconnection. These manage process-level resources that must be unique.
2. **Tier 2 — Migrate to Depends() in P3-C3/C4** (20): Adapters, services, data managers. Replace `get_X()` with `Depends(get_X)` where `get_X()` yields from `app.state` or creates per-request.
3. **Tier 3 — Evaluate per-case** (5): Database engine/session factory, cache infrastructure. These need connection pooling considerations.

## OpenSpec

- **required**: yes for P3-C3/C4 (actual migration)
- **reason**: This inventory is classification-only. Migration requires OpenSpec because it changes initialization lifecycle.

## Follow-up Issues Unlocked

- [ ] P3-C3: Core tier singletons → Depends() migration
- [ ] P3-C4: Services tier singletons → Depends() migration
- [ ] Add `app.state` lifecycle hooks for Tier 1 singletons (if not already present)

---

# P3-A5: Health/Status Route Taxonomy Decision

> **Date**: 2026-05-18
> **Status**: Proposed
> **Deciders**: Pending review

## Context

The route table shows 5 full-path conflicts in health/status endpoints (P3-0.5 output items #1, #12, #13) plus scattered `/health` and `/status` endpoints across 37+ modules. These endpoints serve different purposes but share the same URL patterns.

## Current Facts

From P3-0.5 full-path duplicate table:

| # | Full Path | Handlers |
|---|-----------|----------|
| 1 | GET `/health` | `get_risk_management_health` (risk_v31/system.py), `health_check` (stock_ratings_api.py), `health_check` (technical/routes.py) |
| 12 | GET `/status` | `get_cache_status` (_cache_basic_routes.py), `get_status` (technical/routes.py) |
| 13 | GET `/monitoring/health` | `get_cache_health_status` (_cache_prewarming_routes.py), `health_check` (monitoring_old/routes.py) |

Plus ~30 domain-level health endpoints at `/api/{domain}/health`.

### Proposed Taxonomy

| Category | URL Pattern | Purpose | Examples |
|----------|-------------|---------|----------|
| **Platform liveness** | `/health`, `/status` | "Is the app running?" — load balancer checks | `app/main.py` root health, `/status` |
| **Dependency health** | `/health/dependencies`, `/health/ready` | "Are DB/cache/external APIs reachable?" | TDengine check, PostgreSQL check, Redis check |
| **Domain operational status** | `/api/{domain}/health` | "Is {domain} operational?" — domain-specific diagnostics | strategy-mgmt health, backup-recovery health, trading status |

## Decision

1. **Platform liveness**: Designate ONE handler for `/health` (root). Remove duplicate registrations from `risk_v31/system.py`, `stock_ratings_api.py`, `technical/routes.py`.
2. **Dependency health**: Consolidate into `/health/ready` endpoint that checks all external dependencies.
3. **Domain status**: Keep `/api/{domain}/health` per domain but rename to `/api/{domain}/status` for semantic clarity.

## OpenSpec

- **required**: yes for P3-C7 (actual convergence of 37 health endpoints)
- **reason**: Changing health endpoint URLs affects load balancers, monitoring dashboards, and operational runbooks.

## Follow-up Issues Unlocked

- [ ] P3-C7: Health endpoint convergence (37 → canonical set)
- [ ] Designate `/health` root owner (remove 3 duplicates)

---

# P3-A6: Trading Canonical Route Owner Decision

> **Date**: 2026-05-18
> **Status**: Proposed
> **Deciders**: Pending review

## Context

Trading domain has 8 full-path duplicate routes between `trading_runtime.py` and `trading_monitor.py` (P3-0.5 output items #4-#11).

## Current Facts

| File | Router Prefix | Registration | Routes |
|------|--------------|-------------|--------|
| `trading_runtime.py` | none (bare `APIRouter(tags=[...])`) | router_modules dict via VERSION_MAPPING → `/api/v1/trading` prefix | 8 routes at `/api/v1/trading/*` |
| `trading_monitor.py` | `APIRouter(prefix="/api/trading")` | **NONE** — orphan | 9 routes at `/api/trading/*` |

**Key finding**: `trading_monitor.py` is NOT registered in `router_registry.py`. It is an orphan file. All 8 "full-path conflicts" are shadow conflicts — `trading_monitor.py` routes serve at `/api/trading/*` (orphan, unreachable) while `trading_runtime.py` routes serve at `/api/v1/trading/*` (registered via VERSION_MAPPING).

The actual full-path duplicates come from the P3-0.5 script composing orphan routes at their self-declared prefix (`/api/trading`) and registered routes at their VERSION_MAPPING prefix (`/api/v1/trading`), but these are actually different URLs.

Wait — re-examining P3-0.5 output: items #4-#11 show same final URL for both files. This means the VERSION_MAPPING prefix for `trading_runtime` equals `/api/trading` (not `/api/v1/trading`). Let me verify.

## Verification Needed

```bash
grep "trading" web/backend/app/api/VERSION_MAPPING.py
# Result: "trading_runtime": { "prefix": "/api/trading" }
```

**Confirmed**: VERSION_MAPPING registers `trading_runtime` at `/api/trading`. `trading_monitor.py` declares `prefix="/api/trading"` but is NOT registered. The 8 full-path conflicts are genuine URL collisions — if `trading_monitor.py` were ever registered, FastAPI would serve the last-registered handler. Currently only `trading_runtime.py` routes are live.

Frontend consumers all use `/api/trading/*` (matching `trading_runtime.py` routes). No frontend references to `trading_monitor.py`-specific functionality.

## Decision

`trading_runtime.py` is the canonical owner (registered via VERSION_MAPPING). `trading_monitor.py` is dead code. Delete after verification.

### Compatibility Policy

- **Canonical URL**: `/api/trading/*` (from trading_runtime.py via VERSION_MAPPING)
- **Dead file**: `trading_monitor.py` — never registered, unreachable
- **No migration needed**: No consumers of trading_monitor.py

## OpenSpec

- **required**: no — dead-code cleanup with zero consumer impact
- **reason**: No API contract change. Only unreachable code is removed.

## Follow-up Issues Unlocked

- [ ] Verify VERSION_MAPPING prefix for trading
- [ ] Verify no frontend/test consumers of trading_monitor.py routes
- [ ] Delete `trading_monitor.py` if orphan confirmed

---

# P3-A7: Backup Route Owner + Security Boundary Decision

> **Date**: 2026-05-18
> **Status**: Proposed
> **Deciders**: Pending review

## Context

Backup domain has 11 full-path duplicate routes between `backup_recovery.py` and `backup_recovery_secure/` (P3-0.5 output items #16-#26).

## Current Facts

| File | Router Prefix | Registration | Routes |
|------|--------------|-------------|--------|
| `backup_recovery.py` | `APIRouter(prefix="/api/backup-recovery")` | **NONE** — orphan | 14 routes |
| `backup_recovery_secure/log_security_event.py` | `APIRouter(prefix="/api/backup-recovery")` | **NONE** — orphan | 13 routes |
| `backup_recovery_secure/cleanup_old_backups.py` | `APIRouter(prefix="/api/backup-recovery")` | **NONE** — orphan | 2 routes |

**Key finding**: ALL three files are orphans — none is registered in `router_registry.py`. The 11 "full-path conflicts" exist in the audit output because both files declare the same prefix, but since neither is registered, **no backup routes are served at runtime**.

This is a **critical finding**: the entire backup/recovery API is unreachable.

## Decision

**Option A**: Register `backup_recovery_secure/` as canonical (it has the security event logging wrapper). Delete `backup_recovery.py` flat file.

- **Pros**: Secure-by-default backup operations with audit logging.
- **Cons**: Need to verify the security wrapper doesn't break existing functionality.

**Option B**: Register `backup_recovery.py` as canonical (simpler, no security wrapper). Keep secure version as optional middleware.

**Recommended**: Option A. Add `backup_recovery_secure` package to router_registry with a single registration.

## OpenSpec

- **required**: yes — registering previously-unreachable routes is effectively a new API surface
- **reason**: Backup routes have never been live. Registering them is a new capability requiring spec review.

## Follow-up Issues Unlocked

- [ ] Register backup_recovery_secure in router_registry.py
- [ ] Verify backup operations work end-to-end after registration
- [ ] Delete `backup_recovery.py` flat file (redundant with secure version)
- [ ] Add E2E test for backup/recovery API
