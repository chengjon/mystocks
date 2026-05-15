# MyStocks Backend - Shared Context

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

> This file establishes a shared language between developers and AI agents.
> It is the authoritative reference for jargon and architectural concepts.

## Architecture Terms

- **canonical route**: The single authoritative route path defined in `VERSION_MAPPING.py` and registered via `router_registry.py`
- **flat file**: A single `.py` route module directly under `app/api/` (pre-migration form)
- **package directory**: A route package under `app/api/xxx/` with `__init__.py` and sub-modules (post-migration target)
- **dual registration**: The same functional domain registered as both flat file and package directory in `router_registry.py` — a migration anti-pattern
- **singleton service**: A module-level `global _xxx` variable with a `get_xxx()` lazy-init getter function (32 instances found)
- **Core directory**: `app/core/` — currently 64 files + 4 subdirectories (`cache/`, `logging/`, `middleware/`, plus a private singleton). Needs responsibility-based splitting

## Router Registration Truth

All API routes are registered in `app/router_registry.py` via `register_api_routes()`.

Key prefix assignments (from VERSION_MAPPING):
- auth → `/api/v1/auth`
- market → `/api/v1/market`
- strategy → `/api/v1/strategy`
- trade → `/api/v1/trade`
- monitoring → registered directly (no VERSION_MAPPING entry for base monitoring)
- health → `/api` prefix (so health.py routes become `/api/health/*`)
- system → `/api/v1/system`

Direct app-level routes in `main.py` (bypass router_registry):
- `GET /health` — liveness probe
- `GET /health/ready` — readiness probe
- `GET /api/health/ready` — readiness probe (duplicate path)

## Health Endpoint Landscape

**[CONFIRMED 2026-05-15]** Canonical health endpoints (3 groups, 6 endpoints):

| Canonical Endpoint | Location | Purpose |
|---|---|---|
| `GET /health` | `main.py:637` @app.get | Liveness probe |
| `GET /health/ready` | `main.py:673` @app.get | Readiness probe |
| `GET /api/health/ready` | `main.py:688` same handler | Readiness probe (compat) |
| `GET /api/health/services` | `health.py` via router_registry prefix=/api | Service dependency check |
| `GET /api/health/detailed` | `health.py` via router_registry prefix=/api | Detailed health (auth required) |
| `GET /api/reports/health/{ts}` | `health.py` via router_registry prefix=/api | Historical health reports |

18 fragmented health endpoints in other modules — pending convergence to canonical `health.py` router.

Fragmented health endpoints in other modules (18 found):
- `routes/sse_monitoring.py`: `/health`, `/health/channel/{channel}`, `/health/system`
- `api/system/system_health.py`: `/health`, `/adapters/health`
- `api/system/get_system_architecture.py`: `/database/health`
- `api/market/health_check.py`: market health
- `api/monitoring_old/routes.py`: `/health`
- `api/technical/routes.py`: `/health`
- `api/risk_v31/system.py`: `/health`
- `api/advanced_analysis.py`: `/health`
- `api/advanced_analysis_api.py`: `/health`
- `api/stock_ratings_api.py`: `/health`
- `api/algorithms/get_algorithms_module.py`: `/health`
- `api/multi_source.py`: `/health`, `/health/{source_type}`
- `api/signal_monitoring/get_signal_statistics.py`: strategy health
- `api/backup_recovery_secure/cleanup_old_backups.py`: `/health`

## Logging Ecosystem

**[CONFIRMED 2026-05-15]** Unified logger facade created: `from app.core.logger import logger`

Three underlying frameworks coexist (long-term migration target: unify to loguru via StructuredLogger):
- **stdlib `logging`**: 165 files — `logging.getLogger(__name__)`
- **structlog**: 84 files — `structlog.get_logger()`
- **loguru**: `app/core/logging/structured.py` — `StructuredLogger` (canonical via facade)

`print()` violations: **0** (was 115, all cleaned 2026-05-15)

## Residual Files (Current Scan)

Backup files (delete candidates):
- `api/mystocks_complete.py.bak`
- `api/risk_management.py.bak`
- `api/strategy_management.py.backup`
- `api/data_source_config.py.backup`
- `services/data_adapter.py.backup.20260130`

Old versions:
- `api/data_source_config.old.py`

New versions (need migration plan):
- `api/data/data_api_new.py`
- `services/data_adapter_new.py`
- `services/risk_management_new.py`
- `services/data_api_new.py`

Compat shims:
- `api/auth_compat.py` (registered as `/api/auth` compat router)

## Schema Dual Directory

- `app/schema/`: 2 files (`__init__.py`, `validation_models.py`)
- `app/schemas/`: 16 files (business schemas — canonical location)
- Action: merge `validation_models.py` into `schemas/`, then remove `schema/`

## Governance Terms

- **migration closure** (迁移收口): STANDARDS.md §3 requires every migration to have an exit condition and deadline
- **deletion judgment** (删除判定): Before deleting any file, must verify: (1) no code path imports it, (2) FUNCTION_TREE.md marks the domain as migrated
- **OpenSpec approval**: Architecture changes require proposal → design → tasks three-step approval via `openspec/AGENTS.md`
- **canonical runtime truth**: `app.main:app` is the single composition root (defined in `main.py:61`)

## Key File Locations

| Purpose | Path |
|---------|------|
| App entry | `web/backend/app/main.py` |
| Router registry | `web/backend/app/router_registry.py` |
| VERSION_MAPPING | `web/backend/app/api/VERSION_MAPPING.py` |
| Settings | `web/backend/app/core/config.py` |
| Unified response | `web/backend/app/core/responses.py` |
| Exception handlers | `web/backend/app/core/exception_handler.py` |
| Readiness checks | `web/backend/app/core/readiness.py` |
| Performance middleware | `web/backend/app/core/middleware/performance.py` |
| Health API | `web/backend/app/api/health.py` |
