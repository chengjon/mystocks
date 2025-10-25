# Implementation Plan: Fix 5 Critical Issues in OpenStock Demo

**Branch**: `001-fix-5-critical` | **Date**: 2025-10-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/opt/claude/mystocks_spec/specs/001-fix-5-critical/spec.md`

## Summary

Fix 5 critical blocking issues preventing OpenStock Demo functionality:
1. Missing database tables (watchlist_groups, user_watchlist) causing "relation does not exist" errors
2. Real-time quote API failing to auto-detect exchange suffixes for A-share stock codes
3. Watchlist group management API returning 404 errors
4. K-line chart endpoint not implemented (GET /api/market/kline)
5. Missing test buttons in Test Status tab for API verification

**Technical Approach**: Create PostgreSQL migration script for missing tables, enhance stock code normalization logic with exchange detection, verify watchlist API routing, implement K-line endpoint using AKShare, and add frontend test button handlers.

## Technical Context

**Language/Version**: Python 3.12 (backend), Node.js 20+ with Vue 3 Composition API (frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.115.0, psycopg2-binary 2.9.9, AKShare (from root project), pydantic 2.9.0
- Frontend: Vue 3, Element Plus, ECharts (for K-line charts)

**Storage**: PostgreSQL database (host: localhost, port: 5432, database: mystocks)
**Testing**: pytest 8.3.0, pytest-asyncio 0.24.0, httpx 0.27.0 (backend); manual frontend testing
**Target Platform**: Linux server (WSL2 Ubuntu), web browsers (Chrome, Firefox)
**Project Type**: Web application (FastAPI backend + Vue 3 frontend)

**Performance Goals**:
- Database queries < 1 second for watchlist operations (< 100 items)
- Real-time quote API < 3 seconds response time
- K-line chart data loading < 5 seconds for 60-day period
- API test execution < 10 seconds total

**Constraints**:
- PostgreSQL only (MySQL, TDengine, Redis removed per Week 3 simplification)
- A-share and H-share markets only (no US stocks)
- Authentication required for all operations (JWT tokens)
- Must maintain compatibility with existing frontend (no breaking changes)

**Scale/Scope**:
- ~10 concurrent users expected
- Up to 100 stocks per user watchlist
- 60-250 trading days of K-line data per query
- 5 API endpoints to fix/implement

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance with MyStocks Project Constitution v1.1.0

**I. 5-Layer Data Classification** ✅ PASS
- **Watchlist data** (user_watchlist, watchlist_groups) → Reference Data (Type 2) → PostgreSQL
  - Justification: Semi-static user preferences, relational lookups required
- **Real-time quotes** → Market Data (Type 1) → AKShare API (no persistent storage, pass-through)
  - Justification: High-frequency data, no historical storage needed for OpenStock demo
- **K-line historical data** → Market Data (Type 1) → AKShare API (no persistent storage, pass-through)
  - Justification: Historical daily/minute bars, fetched on-demand
- **Test results** → Not persisted (in-memory, ephemeral)

**II. Configuration-Driven Design** ✅ PASS
- Watchlist tables will be created via SQL migration script (standard practice)
- Database connection uses .env configuration (already established)
- No manual schema modifications required post-migration

**III. Smart Auto-Routing** ✅ PASS
- Watchlist data naturally routes to PostgreSQL (only database available)
- Market data fetched directly from AKShare (no multi-database routing needed)
- No explicit routing logic required (simplified architecture)

**IV. Multi-Database Orchestration** ✅ PASS (N/A)
- Week 3 simplification reduced system to PostgreSQL only
- No orchestration complexity in this feature
- Constitution principle satisfied by project-wide simplification

**V. Complete Observability** ⚠️ PARTIAL
- Backend API has logging via structlog (already configured)
- No dedicated monitoring integration for watchlist operations
- **Recommendation**: Add logging statements for database operations, but monitoring database integration deferred (out of scope for P0 fixes)

**VI. Unified Access Interface** ✅ PASS
- Watchlist operations via WatchlistService service layer (already exists)
- Stock data via StockSearchService service layer (already exists)
- No direct database access in controllers

**VII. Security-First** ✅ PASS
- Database credentials in .env (never hardcoded)
- JWT authentication on all endpoints (already enforced)
- SQL parameterization via psycopg2 prepared statements

**Performance Standards** ✅ PASS
- Target response times align with constitution:
  - Reference data (watchlist): < 50ms p95 (our target < 1s with safety margin)
  - Complex queries (K-line): < 5s (our target < 5s)

**Conclusion**: All gates PASSED or N/A. Feature complies with constitution principles.

## Project Structure

### Documentation (this feature)

```
specs/001-fix-5-critical/
├── spec.md              # Feature specification (/speckit.specify output)
├── plan.md              # This file (/speckit.plan output)
├── research.md          # Phase 0: Technical decisions and best practices
├── data-model.md        # Phase 1: Watchlist entity definitions
├── quickstart.md        # Phase 1: Developer setup guide
├── contracts/           # Phase 1: API contracts
│   ├── watchlist_api.md # Watchlist group management endpoints
│   ├── quote_api.md     # Real-time quote endpoint specification
│   └── kline_api.md     # K-line chart endpoint specification
├── checklists/
│   └── requirements.md  # Requirements quality validation (completed)
└── tasks.md             # Phase 2: Implementation tasks (/speckit.tasks - NOT YET CREATED)
```

### Source Code (repository root: /opt/claude/mystocks_spec)

```
web/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── watchlist.py        # ✅ EXISTS - Watchlist CRUD endpoints
│   │   │   ├── stock_search.py     # ✅ EXISTS - Quote/search endpoints
│   │   │   └── market.py           # ⚠️ NEEDS ENHANCEMENT - Add kline endpoint
│   │   ├── services/
│   │   │   ├── watchlist_service.py # ✅ EXISTS - Business logic for watchlist
│   │   │   └── stock_search_service.py # ⚠️ NEEDS ENHANCEMENT - Add exchange detection
│   │   ├── models/                 # Database models (if using ORM)
│   │   └── schemas/                # Pydantic schemas for API
│   ├── migrations/                 # SQL migration scripts
│   │   ├── 001_watchlist_tables.sql # 🆕 NEW - Create watchlist_groups + user_watchlist
│   │   └── README.md               # Migration execution guide
│   └── tests/
│       ├── test_watchlist_api.py   # Unit tests for watchlist endpoints
│       ├── test_stock_search.py    # Unit tests for quote/search
│       └── test_market_api.py      # Unit tests for K-line endpoint
│
└── frontend/
    └── src/
        ├── views/
        │   └── OpenStockDemo.vue   # ⚠️ NEEDS ENHANCEMENT - Add test button handlers
        └── services/
            └── api.ts              # API client (if centralized)
```

**Structure Decision**: Web application structure (Option 2) selected due to clear separation of FastAPI backend and Vue 3 frontend. Backend changes focus on `app/api/` endpoints and `app/services/` business logic. Frontend changes isolated to `OpenStockDemo.vue` test button functionality. Migration scripts in `migrations/` directory follow existing pattern.

## Complexity Tracking

*This feature has NO constitution violations. This section intentionally left empty.*

## Phase 0: Research & Decisions

*(Will be generated in research.md)*

Key research topics:
1. PostgreSQL best practices for watchlist schema (foreign keys, indexes, cascading deletes)
2. AKShare API patterns for real-time quotes and K-line data retrieval
3. Stock code normalization standards (exchange suffix detection logic)
4. FastAPI async patterns for external API calls (AKShare)
5. ECharts K-line configuration for Chinese stock market conventions

## Phase 1: Design Artifacts

*(Will be generated in data-model.md, contracts/, quickstart.md)*

Key deliverables:
- **data-model.md**: Entity definitions for WatchlistGroup, WatchlistItem, StockQuote, KLineDataPoint
- **contracts/watchlist_api.md**: POST /api/watchlist/groups, GET /api/watchlist/groups, DELETE /api/watchlist/groups/{id}
- **contracts/quote_api.md**: Enhanced GET /api/stock-search/quote/{code} with auto-detection
- **contracts/kline_api.md**: New GET /api/market/kline endpoint specification
- **quickstart.md**: Developer guide for running migrations, testing endpoints, and verifying frontend integration
