# Architecture

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 当前执行口径请优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md`，并结合当前代码实现与主线治理文档使用。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码或主线文档冲突，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、当前代码与主线治理文档为准。


**Last mapped**: 2026-04-05

## High-Level Pattern

MyStocks follows a **layered architecture** with adapter pattern for multi-data-source support:

```
┌─────────────────────────────────────┐
│  Frontend (Vue 3 + Pinia)          │  web/frontend/src/
│  - ArtDeco design system            │
│  - Composables / Stores / Views     │
├─────────────────────────────────────┤
│  Backend API (FastAPI)              │  web/backend/app/
│  - 205 API route files              │
│  - Services / Middleware / Auth     │
├─────────────────────────────────────┤
│  Core Business (Python)             │  src/
│  - Adapters / Algorithms / Domain   │
│  - Unified Manager (entry point)    │
├─────────────────────────────────────┤
│  Data Layer                         │
│  - TDengine (time-series)           │
│  - PostgreSQL/TimescaleDB (rel.)    │
└─────────────────────────────────────┘
```

## Entry Points

### Backend
- `web/backend/app/main.py` (885 lines) — FastAPI application factory
  - Creates app via `app_factory.py`
  - Registers routes via `router_registry.py`
  - Includes CSRFTokenManager (inline class)
  - Socket.IO manager initialization

### Frontend
- `web/frontend/src/main.js` (6883 bytes) — Vue app bootstrap
  - 7 additional main variants exist (main-debug.js, main-enhanced.ts, etc.) — legacy/dev artifacts

### Core
- `src/unified_manager.py` — re-exports `MyStocksUnifiedManager` from `src/core/unified_manager.py`
- Root shims: `core.py`, `data_access.py`, `monitoring.py` — backward compatibility re-exports

## Key Abstractions

### Adapter Pattern
- `src/adapters/` — concrete implementations (akshare, efinance, tdx, financial)
- `src/interfaces/adapters/` — **duplicate** of src/adapters/ with missing imports (causes 500+ F821 errors)
- `src/data_sources/` — data source factory + mock/real strategy

### Factory Pattern
- `src/factories/` — various factories
- `src/data_sources/factory.py` — creates mock or real data sources based on env
- `web/backend/app/services/data_source_factory/` — backend-side data source factory

### Domain-Driven Design (partial)
- `src/domain/` — domain models and services
- `src/application/` — application services (portfolio, watchlist, market data processing)
- `src/infrastructure/` — infrastructure adapters (market data repos, streaming)

## Data Flow

```
User Request
    → FastAPI Route (web/backend/app/api/*.py)
    → Service Layer (web/backend/app/services/)
    → Core Business Logic (src/)
    → Adapter (src/adapters/) → External API (akshare/efinance/TDX)
    → Data Access (src/data_access/) → Database (TDengine/PostgreSQL)
    → Response → User
```

## Known Architectural Issues

1. **Duplicate adapter hierarchies**: `src/interfaces/adapters/` mirrors `src/adapters/` identically
2. **Three data access layers**: `src/data_access/`, `src/data_access_pkg/`, `src/database/`
3. **Routes in wrong layer**: `src/routes/` (19 files) and `src/api/` (5 files) exist alongside `web/backend/app/api/` (205 files)
4. **Root-level shims**: `core.py`, `data_access.py`, `monitoring.py` use bare imports with circular risk
5. **Backend API monolith**: 205 files in flat `app/api/` directory
