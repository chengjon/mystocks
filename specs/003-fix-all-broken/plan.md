# Implementation Plan: Fix All Broken Web Features

**Branch**: `003-fix-all-broken` | **Date**: 2025-10-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-fix-all-broken/spec.md`

**Note**: This plan addresses 35 broken features identified in the comprehensive code review report.

## Summary

**Primary Requirement**: Fix all broken features in MyStocks web application to provide users with real, working market data and trading analysis tools instead of mock/placeholder content.

**Technical Approach**:
1. Complete MySQL to PostgreSQL migration (5 tables remaining)
2. Connect Dashboard and market data panels to real database queries
3. Implement missing backend services (db_service, indicator persistence)
4. Fix authentication token refresh mechanism
5. Remove or properly mark placeholder pages
6. Implement comprehensive E2E testing with automated browser tools

**Impact**: Transforms MyStocks from a prototype with 29% broken features into a production-ready quantitative trading platform.

## Technical Context

**Language/Version**:
- Backend: Python 3.8+ (currently using 3.10)
- Frontend: JavaScript ES2020+ with Vue 3 Composition API

**Primary Dependencies**:
- Backend: FastAPI 0.100+, SQLAlchemy 2.0+, Pydantic v2, psycopg2-binary, taospy
- Frontend: Vue 3.3+, Vite 4.5+, Vue Router 4, Pinia, Axios, ECharts 5
- Testing: pytest (backend), Vitest (frontend), chrome-devtools-mcp/playwright (E2E)

**Storage**:
- PostgreSQL 14+ (relational data: users, strategies, indicators, market metadata)
- TDengine 3.0+ (time-series data: tick/minute market data)
- Monitoring: Separate PostgreSQL database for system metrics

**Testing**:
- Backend: pytest with coverage ≥80%, unit + integration tests
- Frontend: Vitest for components, chrome-devtools-mcp/playwright for E2E
- Performance: Automated load testing with 50+ concurrent users

**Target Platform**:
- Server: Linux (Ubuntu 20.04+ / WSL2)
- Browser: Chrome 100+, Firefox 100+, Safari 15+, Edge 100+
- Node: v18+ for frontend build

**Project Type**: Web application (backend API + frontend SPA)

**Performance Goals**:
- Dashboard page load: < 2 seconds (including real data fetch)
- API response time: < 3 seconds for standard queries (100 stocks)
- Database query: < 100ms for time-series (10k records)
- Concurrent users: Support 50+ without degradation

**Constraints**:
- Zero MySQL dependencies (full PostgreSQL migration required)
- Zero "undefined" or "null" errors in production
- 100% data integrity during migration
- No breaking changes to working features (TDX, Wencai, Tasks, Indicators)
- Must follow code modification rules from `代码修改规则-new.md`

**Scale/Scope**:
- 14 frontend pages (23 total in system)
- 28 functional requirements
- 5 user stories (P1-P3 prioritized)
- ~8,000 lines of backend Python code affected
- ~5,000 lines of frontend Vue code affected
- 5 database tables to migrate
- 35 broken features to fix

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Design Principles

| Principle | Status | Notes |
|-----------|--------|-------|
| **配置驱动原则** (Configuration-Driven) | ✅ **PASS** | All database tables defined in `table_config.yaml`. MySQL migration will update config, not bypass it. |
| **数据分类存储原则** (Data Classification) | ✅ **PASS** | Dual-database architecture maintained: PostgreSQL (relational), TDengine (time-series). No changes to storage strategy. |
| **分层架构原则** (Layered Architecture) | ✅ **PASS** | Fixes maintain existing layers: API → Service → DataManager → Storage. No cross-layer dependencies introduced. |
| **智能路由原则** (Smart Routing) | ✅ **PASS** | `MyStocksUnifiedManager` routing preserved. Fixes add missing data sources, don't bypass routing. |
| **完整可观测性原则** (Observability) | ✅ **PASS** | Monitoring database integration already exists. Fixes will use existing `MonitoringDatabase` for new operations. |
| **安全容错原则** (Security & Fault Tolerance) | ✅ **PASS** | Authentication fixes improve security. Error handling improvements add fault tolerance without breaking existing patterns. |

### Development Implementation Standards

| Standard | Status | Notes |
|----------|--------|-------|
| **Documentation** | ✅ **PASS** | All fixes documented in code review report. API changes will update OpenAPI spec. |
| **Code Quality** | ✅ **PASS** | Python ≥3.8, PEP8 compliance, type hints. Automated linting with flake8/pylint. |
| **Version Control** | ✅ **PASS** | Feature branch `003-fix-all-broken` follows naming convention. Commits will use standard format. |
| **Testing Requirements** | ✅ **PASS** | Unit tests ≥80% coverage. Integration tests for all fixed features. E2E tests with chrome-devtools-mcp. |
| **Code Modification Rules** | ✅ **PASS** | Following `代码修改规则-new.md`: minimal changes, no protected modules, architecture compliance, BUG tracking. |

### Constitution Compliance Summary

**Status**: ✅ **ALL GATES PASSED**

**No violations detected**. This is a bug-fix and data-migration project that:
- Maintains existing architecture patterns
- Follows configuration-driven approach for MySQL → PostgreSQL migration
- Adds missing features without breaking working ones
- Improves observability and error handling within existing frameworks

**Re-evaluation after Phase 1**: Will verify that design decisions continue to comply with all principles.

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
web/
├── backend/                         # FastAPI backend application
│   ├── app/
│   │   ├── api/                     # API route handlers
│   │   │   ├── auth.py              # ✅ Working - JWT authentication
│   │   │   ├── data.py              # ❌ BROKEN - db_service undefined
│   │   │   ├── market.py            # ⚠️  PARTIAL - MySQL dependencies
│   │   │   ├── market_v2.py         # ✅ Working - Direct API
│   │   │   ├── indicators.py        # ⚠️  PARTIAL - Config save broken
│   │   │   ├── strategy.py          # ✅ Working
│   │   │   ├── strategy_management.py # ✅ Working
│   │   │   ├── risk_management.py   # ✅ Working
│   │   │   ├── technical_analysis.py # ✅ Working
│   │   │   ├── wencai.py            # ✅ Working
│   │   │   ├── tdx.py               # ✅ Working
│   │   │   ├── tasks.py             # ✅ Working
│   │   │   ├── ml.py                # ✅ Working
│   │   │   ├── monitoring.py        # ✅ Working
│   │   │   ├── sse_endpoints.py     # ⚠️  PARTIAL - Needs testing
│   │   │   ├── multi_source.py      # ✅ Working
│   │   │   └── announcement.py      # ✅ Working
│   │   ├── core/
│   │   │   ├── config.py            # Configuration management
│   │   │   ├── database.py          # ❌ NEEDS FIX - db_service missing
│   │   │   ├── security.py          # ⚠️  PARTIAL - Token refresh needs fix
│   │   │   ├── cache_utils.py       # ✅ Working
│   │   │   └── sse_manager.py       # ✅ Working
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   ├── base.py
│   │   │   ├── strategy.py
│   │   │   ├── market_data.py
│   │   │   └── ...
│   │   ├── services/                # Business logic layer
│   │   │   ├── data_service.py      # ❌ NEEDS FIX - Real data integration
│   │   │   ├── market_data_service.py
│   │   │   ├── indicator_calculator.py
│   │   │   └── ...
│   │   ├── adapters/                # External data source adapters
│   │   └── main.py                  # FastAPI app entry point
│   ├── tests/
│   │   ├── test_api_endpoints.py    # ❌ NEEDS CREATION - E2E tests
│   │   ├── test_data_migration.py   # ❌ NEEDS CREATION - Migration tests
│   │   └── ...
│   └── requirements.txt
│
├── frontend/                        # Vue 3 + Vite SPA
│   ├── src/
│   │   ├── views/                   # Page components
│   │   │   ├── Dashboard.vue        # ❌ BROKEN - Mock data only
│   │   │   ├── Market.vue           # ❌ BROKEN - Empty placeholder
│   │   │   ├── MarketData.vue       # ⚠️  PARTIAL - MySQL tables broken
│   │   │   ├── TechnicalAnalysis.vue # ⚠️  PARTIAL - Config save broken
│   │   │   ├── StrategyManagement.vue # ✅ Working
│   │   │   ├── BacktestAnalysis.vue # ❌ BROKEN - Empty placeholder
│   │   │   ├── RiskMonitor.vue      # ❌ BROKEN - Empty placeholder
│   │   │   ├── RealTimeMonitor.vue  # ❌ BROKEN - Empty placeholder
│   │   │   ├── TaskManagement.vue   # ✅ Working
│   │   │   ├── Wencai.vue           # ✅ Working
│   │   │   ├── TdxMarket.vue        # ✅ Working
│   │   │   ├── IndicatorLibrary.vue # ✅ Working
│   │   │   ├── Settings.vue         # ✅ Working
│   │   │   └── Login.vue            # ⚠️  PARTIAL - Token refresh issue
│   │   ├── components/              # Reusable components
│   │   │   ├── technical/
│   │   │   │   ├── KLineChart.vue   # ✅ Working
│   │   │   │   ├── IndicatorPanel.vue # ⚠️  PARTIAL - Config save broken
│   │   │   │   └── StockSearchBar.vue # ✅ Working
│   │   │   ├── market/
│   │   │   │   ├── WencaiPanel.vue  # ✅ Working
│   │   │   │   ├── LongHuBangPanel.vue # ❌ BROKEN - MySQL dependency
│   │   │   │   ├── FundFlowPanel.vue # ❌ BROKEN - MySQL dependency
│   │   │   │   ├── ETFDataPanel.vue # ❌ BROKEN - MySQL dependency
│   │   │   │   └── ChipRacePanel.vue # ❌ BROKEN - MySQL dependency
│   │   │   ├── task/
│   │   │   ├── watchlist/
│   │   │   └── sse/
│   │   ├── api/
│   │   │   └── index.js             # ⚠️  NEEDS UPDATE - Error handling
│   │   ├── stores/
│   │   │   ├── auth.js              # ⚠️  NEEDS FIX - Token refresh
│   │   │   └── ...
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── App.vue
│   │   └── main.js
│   ├── tests/
│   │   ├── e2e/                     # ❌ NEEDS CREATION - E2E tests
│   │   │   ├── dashboard.spec.js
│   │   │   ├── market-data.spec.js
│   │   │   └── ...
│   │   └── components/
│   ├── package.json
│   └── vite.config.js
│
├── core/                            # Shared business logic (Python)
│   ├── data_manager.py              # ✅ Working - Unified data access
│   ├── cached_data_manager.py       # ✅ Working - LRU cache layer
│   ├── cache_manager.py             # ✅ Working
│   └── ...
│
├── db_manager/                      # Database infrastructure
│   ├── database_manager.py          # ✅ Working
│   └── ...
│
├── monitoring/                      # Monitoring and observability
│   └── ...
│
├── table_config.yaml                # ❌ NEEDS UPDATE - Add 5 PostgreSQL tables
│
└── docs/
    ├── COMPREHENSIVE_CODE_REVIEW_REPORT.md  # Source of truth for broken features
    ├── P1_P2_COMPLETION_SUMMARY.md
    ├── P3_PERFORMANCE_OPTIMIZATION_COMPLETION.md
    └── P5_API_DOCUMENTATION.md
```

**Structure Decision**: Web application structure (Option 2) is used. The codebase is organized as:
- `web/backend/`: FastAPI backend with layered architecture (API → Services → Core → Storage)
- `web/frontend/`: Vue 3 SPA with component-based architecture
- `core/`: Shared Python business logic used by both backend and standalone scripts
- `db_manager/`, `monitoring/`: Infrastructure modules

**Key Affected Areas** (based on code review):
- Backend: `app/api/data.py`, `app/core/database.py`, `app/core/security.py`, `app/services/data_service.py`
- Frontend: `src/views/Dashboard.vue`, `src/components/market/*Panel.vue`, `src/stores/auth.js`
- Config: `table_config.yaml` (add 5 tables)
- Tests: Create comprehensive E2E test suite

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

**Status**: N/A - No constitution violations detected.

This feature maintains existing architecture patterns and does not introduce unnecessary complexity. All fixes work within the established layered architecture and configuration-driven approach.

---

## Phase 0: Research & Technical Decisions

**Status**: ✅ Complete (see [research.md](./research.md))

All technical unknowns have been resolved through analysis of the existing codebase and comprehensive code review report. Key decisions documented in research.md include:

1. **Database Migration Strategy**: MySQL tables → PostgreSQL with schema preservation
2. **Testing Tool Selection**: chrome-devtools-mcp for E2E automation
3. **Error Handling Pattern**: User-friendly messages + structured logging
4. **Authentication Fix**: Token refresh with exponential backoff
5. **Placeholder Page Strategy**: Remove routes, add "Coming Soon" indicators

---

## Phase 1: Design Artifacts

**Status**: ✅ Complete

Generated artifacts:
- [data-model.md](./data-model.md) - Database schema for 5 migrated tables
- [contracts/](./contracts/) - API endpoint specifications
- [quickstart.md](./quickstart.md) - Developer setup and testing guide

---

## Next Steps

This plan is complete. Ready to proceed to `/speckit.tasks` for task breakdown and implementation tracking.
