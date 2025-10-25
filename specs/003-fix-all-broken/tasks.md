# Tasks: Fix All Broken Web Features

**Input**: Design documents from `/specs/003-fix-all-broken/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Branch**: `003-fix-all-broken`
**Date**: 2025-10-25

**Tests**: E2E tests using chrome-devtools-mcp are explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Web app**: `web/backend/`, `web/frontend/`
- Backend: `web/backend/app/`
- Frontend: `web/frontend/src/`
- Core: `core/`, `db_manager/`, `monitoring/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment verification

- [ ] T001 Verify development environment (Python 3.8+, Node 18+, PostgreSQL 14+, TDengine 3.0+)
- [ ] T002 [P] Install backend dependencies from web/backend/requirements.txt
- [ ] T003 [P] Install frontend dependencies in web/frontend/ with npm install
- [ ] T004 [P] Copy deployment/production.env.template to .env and configure database credentials
- [ ] T005 [P] Convert all SPECKIT bash scripts from CRLF to LF with dos2unix or sed
- [ ] T006 Test database connections (PostgreSQL and TDengine) using health check scripts

**Checkpoint**: Environment ready for development

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Migration Foundation

- [ ] T007 Add 5 table definitions to table_config.yaml (fund_flow, etf_data, dragon_tiger, chip_race, indicator_configs) per data-model.md
- [ ] T008 Export existing MySQL data from 5 tables to JSON/CSV backup files
- [ ] T009 Record row counts from MySQL tables for post-migration validation
- [ ] T010 Create 5 PostgreSQL tables using ConfigDrivenTableManager.batch_create_tables()
- [ ] T011 Import backup data into PostgreSQL tables and verify row counts match

### Backend Core Services

- [ ] T012 [P] Implement get_unified_manager() singleton in web/backend/app/core/database.py
- [ ] T013 [P] Create db_service alias for backwards compatibility in web/backend/app/core/database.py
- [ ] T014 [P] Implement UserFriendlyError exception class in web/backend/app/core/errors.py
- [ ] T015 [P] Add global exception handler to web/backend/app/main.py with user-friendly messages
- [ ] T016 [P] Create error message mapping dictionary in web/backend/app/core/error_messages.py

### Frontend Core Infrastructure

- [ ] T017 [P] Add Axios response interceptor with user-friendly error handling in web/frontend/src/api/index.js
- [ ] T018 [P] Create error message display utility in web/frontend/src/utils/errorHandler.js

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Real-time Market Data on Dashboard (Priority: P1) 🎯 MVP

**Goal**: Replace all mock data on Dashboard with real database queries, showing actual favorite stocks, strategy results, industry stocks, and fund flow

**Independent Test**: Login → Navigate to Dashboard → Verify all 5 data tables show real data from database (not "600519 贵州茅台" or other hardcoded values) → Click refresh → Data updates

### E2E Tests for User Story 1

**NOTE**: Write these tests FIRST, ensure they FAIL before implementation

- [ ] T019 [P] [US1] Create E2E test spec for Dashboard real data in web/frontend/tests/e2e/dashboard.spec.js
- [ ] T020 [P] [US1] Add test case: Login and verify favorites table shows database data
- [ ] T021 [P] [US1] Add test case: Verify strategy stocks table shows real matched stocks
- [ ] T022 [P] [US1] Add test case: Select industry filter and verify real industry stocks load
- [ ] T023 [P] [US1] Add test case: Verify fund flow chart shows real industry fund flow data
- [ ] T024 [P] [US1] Add test case: Click refresh button and verify data updates

### Backend Implementation for User Story 1

- [ ] T025 [P] [US1] Create GET /api/data/dashboard/summary endpoint in web/backend/app/api/data.py
- [ ] T026 [P] [US1] Implement get_favorites() method using get_unified_manager() in web/backend/app/services/data_service.py
- [ ] T027 [P] [US1] Implement get_strategy_matches() method in web/backend/app/services/data_service.py
- [ ] T028 [P] [US1] Implement get_industry_stocks(industry_code) method in web/backend/app/services/data_service.py
- [ ] T029 [P] [US1] Implement get_fund_flow_summary() using fund_flow table in web/backend/app/services/market_data_service.py
- [ ] T030 [US1] Wire dashboard summary endpoint to all service methods with error handling

### Frontend Implementation for User Story 1

- [ ] T031 [P] [US1] Remove all hardcoded mock data from web/frontend/src/views/Dashboard.vue (favoriteStocks, strategyStocks, industryStocks, conceptStocks, industryData)
- [ ] T032 [P] [US1] Create getDashboardSummary() API call in web/frontend/src/api/index.js
- [ ] T033 [US1] Replace onMounted() hook in Dashboard.vue to call getDashboardSummary() API
- [ ] T034 [US1] Connect favorites table to response.data.favorites with proper error handling
- [ ] T035 [US1] Connect strategy stocks table to response.data.strategies with proper error handling
- [ ] T036 [US1] Connect industry stocks table to response.data.industry_stocks with proper error handling
- [ ] T037 [US1] Connect fund flow chart to response.data.fund_flow with ECharts integration
- [ ] T038 [US1] Implement refresh button handler to reload data from API

**Checkpoint**: Dashboard now shows 100% real data - User Story 1 complete and testable

---

## Phase 4: User Story 2 - Access Working Market Data Features (Priority: P1)

**Goal**: Fix 4 broken market data panels (龙虎榜, ETF, 资金流向, 竞价抢筹) by connecting them to PostgreSQL tables instead of MySQL

**Independent Test**: Navigate to each panel (LongHuBang, ETF, FundFlow, ChipRace) → Verify data loads from PostgreSQL → No MySQL connection errors → User-friendly error messages on failures

### E2E Tests for User Story 2

- [ ] T039 [P] [US2] Create E2E test spec for market data panels in web/frontend/tests/e2e/market-data.spec.js
- [ ] T040 [P] [US2] Add test case: Navigate to LongHuBangPanel and verify dragon_tiger data loads
- [ ] T041 [P] [US2] Add test case: Navigate to ETFDataPanel and verify etf_data loads
- [ ] T042 [P] [US2] Add test case: Navigate to FundFlowPanel and verify fund_flow data loads
- [ ] T043 [P] [US2] Add test case: Navigate to ChipRacePanel and verify chip_race data loads
- [ ] T044 [P] [US2] Add test case: Trigger error condition and verify user-friendly error message appears

### Backend Implementation for User Story 2

- [ ] T045 [P] [US2] Create GET /api/market/dragon-tiger endpoint in web/backend/app/api/market.py using dragon_tiger table
- [ ] T046 [P] [US2] Create GET /api/market/etf-data endpoint in web/backend/app/api/market.py using etf_data table
- [ ] T047 [P] [US2] Update GET /api/market/fund-flow endpoint to use PostgreSQL fund_flow table (remove MySQL dependency)
- [ ] T048 [P] [US2] Create GET /api/market/chip-race endpoint in web/backend/app/api/market.py using chip_race table
- [ ] T049 [US2] Add query parameter validation and user-friendly error handling to all 4 endpoints

### Frontend Implementation for User Story 2

- [ ] T050 [P] [US2] Update LongHuBangPanel.vue to call /api/market/dragon-tiger with error handling in web/frontend/src/components/market/LongHuBangPanel.vue
- [ ] T051 [P] [US2] Update ETFDataPanel.vue to call /api/market/etf-data with error handling in web/frontend/src/components/market/ETFDataPanel.vue
- [ ] T052 [P] [US2] Update FundFlowPanel.vue to call /api/market/fund-flow (PostgreSQL) with error handling in web/frontend/src/components/market/FundFlowPanel.vue
- [ ] T053 [P] [US2] Update ChipRacePanel.vue to call /api/market/chip-race with error handling in web/frontend/src/components/market/ChipRacePanel.vue
- [ ] T054 [US2] Remove all MySQL connection code from frontend components
- [ ] T055 [US2] Add loading states and empty state handling to all 4 panels

**Checkpoint**: All 4 market data panels working with PostgreSQL - User Story 2 complete

---

## Phase 5: User Story 5 - Authenticate and Access Personalized Data (Priority: P2)

**Goal**: Fix token refresh mechanism to prevent unexpected logouts and enable seamless 8+ hour sessions

**Independent Test**: Login → Use system for 35+ minutes (past token expiration) → Verify session auto-refreshes without logout → Close browser → Return later → Verify "remember me" or re-auth prompt works

### E2E Tests for User Story 5

- [ ] T056 [P] [US5] Create E2E test spec for authentication in web/frontend/tests/e2e/auth.spec.js
- [ ] T057 [P] [US5] Add test case: Login with valid credentials and verify redirect to Dashboard
- [ ] T058 [P] [US5] Add test case: Simulate 25min wait and verify token auto-refresh before expiration
- [ ] T059 [P] [US5] Add test case: Login with invalid credentials and verify user-friendly error message
- [ ] T060 [P] [US5] Add test case: Close browser, reopen, and verify session handling

### Backend Implementation for User Story 5

- [ ] T061 [P] [US5] Create POST /api/auth/refresh endpoint in web/backend/app/api/auth.py
- [ ] T062 [P] [US5] Implement verify_refresh_token() function in web/backend/app/core/security.py
- [ ] T063 [P] [US5] Implement create_access_token() with 30min expiration in web/backend/app/core/security.py
- [ ] T064 [US5] Add refresh token validation and new access token generation to refresh endpoint
- [ ] T065 [US5] Update login endpoint to return both access_token and refresh_token with expiration times

### Frontend Implementation for User Story 5

- [ ] T066 [P] [US5] Add refreshToken and tokenExpiresAt state to web/frontend/src/stores/auth.js
- [ ] T067 [P] [US5] Implement refreshAccessToken() action in auth store with axios call to /api/auth/refresh
- [ ] T068 [P] [US5] Implement scheduleTokenRefresh() to auto-refresh 5min before expiration in auth store
- [ ] T069 [US5] Update login action to store refresh token and schedule auto-refresh
- [ ] T070 [US5] Add error handling to refreshAccessToken() with logout and redirect to /login on failure
- [ ] T071 [US5] Test token refresh with setTimeout() to simulate 25min wait

**Checkpoint**: Token refresh working, sessions last 8+ hours - User Story 5 complete

---

## Phase 6: User Story 3 - Manage Custom Indicators (Priority: P2)

**Goal**: Enable users to save, retrieve, update, and delete custom indicator configurations with 100% reliability

**Independent Test**: Create custom MACD config → Save → Reload page → Verify config appears in library → Apply to chart → Verify renders with saved params → Delete → Verify removed

### E2E Tests for User Story 3

- [ ] T072 [P] [US3] Create E2E test spec for indicator management in web/frontend/tests/e2e/indicators.spec.js
- [ ] T073 [P] [US3] Add test case: Create custom MACD indicator and verify save succeeds
- [ ] T074 [P] [US3] Add test case: Reload page and verify saved indicator appears in library
- [ ] T075 [P] [US3] Add test case: Apply saved indicator to chart and verify parameters correct
- [ ] T076 [P] [US3] Add test case: Delete indicator and verify it's removed from database

### Backend Implementation for User Story 3

- [ ] T077 [P] [US3] Create POST /api/indicators/configs endpoint in web/backend/app/api/indicators.py
- [ ] T078 [P] [US3] Create GET /api/indicators/configs endpoint with filter params in web/backend/app/api/indicators.py
- [ ] T079 [P] [US3] Create PUT /api/indicators/configs/{id} endpoint in web/backend/app/api/indicators.py
- [ ] T080 [P] [US3] Create DELETE /api/indicators/configs/{id} endpoint in web/backend/app/api/indicators.py
- [ ] T081 [US3] Implement indicator config CRUD operations using indicator_configs table via get_unified_manager()
- [ ] T082 [US3] Add JSONB parameter validation for common indicators (MACD, RSI, BOLL, KDJ)

### Frontend Implementation for User Story 3

- [ ] T083 [P] [US3] Update IndicatorPanel.vue to add "Save Config" button in web/frontend/src/components/technical/IndicatorPanel.vue
- [ ] T084 [P] [US3] Create saveIndicatorConfig() method calling POST /api/indicators/configs in IndicatorPanel.vue
- [ ] T085 [P] [US3] Update IndicatorLibrary.vue to call GET /api/indicators/configs on load in web/frontend/src/views/IndicatorLibrary.vue
- [ ] T086 [US3] Add "Apply", "Edit", "Delete" buttons to each config in IndicatorLibrary.vue
- [ ] T087 [US3] Implement applyConfig() to populate indicator panel with saved parameters
- [ ] T088 [US3] Implement deleteConfig() calling DELETE endpoint with confirmation dialog

**Checkpoint**: Indicator config management fully working - User Story 3 complete

---

## Phase 7: User Story 4 - Use Complete Feature Set or Remove Placeholder Pages (Priority: P3)

**Goal**: Replace empty placeholder pages with professional "Coming Soon" UI and provide alternative workflows

**Independent Test**: Navigate to Market.vue → See "Coming Soon" UI with link to MarketData.vue → Navigate to BacktestAnalysis → See "Coming Soon" with link to StrategyManagement → Verify navigation menu shows badges

### Implementation for User Story 4

- [ ] T089 [P] [US4] Create PlaceholderPage.vue component in web/frontend/src/components/layout/PlaceholderPage.vue with "Coming Soon" UI
- [ ] T090 [P] [US4] Replace Market.vue content with PlaceholderPage component, alternative: MarketData.vue
- [ ] T091 [P] [US4] Replace BacktestAnalysis.vue content with PlaceholderPage, alternative: StrategyManagement.vue
- [ ] T092 [P] [US4] Replace RiskMonitor.vue content with PlaceholderPage, alternative: RealTimeMonitor.vue
- [ ] T093 [P] [US4] Replace RealTimeMonitor.vue content with PlaceholderPage, alternative: Dashboard.vue
- [ ] T094 [US4] Add "Coming Soon" badges to navigation menu items in web/frontend/src/config/menu.config.js
- [ ] T095 [US4] Update router to allow placeholder pages but show warnings in console

**Checkpoint**: Professional placeholder pages with alternatives - User Story 4 complete

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, testing, documentation, and deployment preparation

### Integration & System Testing

- [ ] T096 [P] Run all E2E tests (Dashboard, Market Data, Auth, Indicators) and verify 100% pass rate
- [ ] T097 [P] Run backend unit tests with pytest and verify ≥80% coverage
- [ ] T098 [P] Run frontend component tests with Vitest and verify all pass
- [ ] T099 [P] Perform manual smoke test of all critical user flows
- [ ] T100 [P] Test with 50+ concurrent users using load testing tool

### Performance Validation

- [ ] T101 Test Dashboard page load < 2 seconds with real data
- [ ] T102 Test API response time < 3 seconds for 100-stock queries
- [ ] T103 Test database query performance < 100ms for time-series data
- [ ] T104 Verify zero "undefined" or "null" errors in browser console
- [ ] T105 Verify zero MySQL connection errors in logs

### Documentation & Deployment

- [ ] T106 [P] Update API documentation (OpenAPI spec) with new endpoints
- [ ] T107 [P] Update COMPREHENSIVE_CODE_REVIEW_REPORT.md to mark all 35 features as fixed
- [ ] T108 [P] Create deployment checklist from deployment/DEPLOYMENT_CHECKLIST.md
- [ ] T109 [P] Verify all environment variables documented in deployment/production.env.template
- [ ] T110 [P] Test health_check.py script with production configuration
- [ ] T111 Run deployment/verify_config.py and ensure all checks pass

### Git & Version Control

- [ ] T112 Create commit for Phase 2 (Foundation) following code modification rules
- [ ] T113 Create commit for Phase 3 (User Story 1 - Dashboard)
- [ ] T114 Create commit for Phase 4 (User Story 2 - Market Data)
- [ ] T115 Create commit for Phase 5 (User Story 5 - Authentication)
- [ ] T116 Create commit for Phase 6 (User Story 3 - Indicators)
- [ ] T117 Create commit for Phase 7 (User Story 4 - Placeholders)
- [ ] T118 Create final commit for Phase 8 (Polish & Testing)

**Final Checkpoint**: All 35 broken features fixed, all tests passing, ready for production deployment

---

## Dependencies & Parallel Execution

### Story Completion Order

```
Phase 1 (Setup)
  ↓
Phase 2 (Foundation) ← MUST complete before any user story
  ↓
  ├─→ Phase 3 (US1: Dashboard) ━━━━━━┓
  ├─→ Phase 4 (US2: Market Data) ━━━┫  Can run in parallel
  ├─→ Phase 5 (US5: Auth) ━━━━━━━━━┫
  ├─→ Phase 6 (US3: Indicators) ━━━┫
  └─→ Phase 7 (US4: Placeholders) ━┛
                 ↓
          Phase 8 (Polish)
```

### Parallel Execution Examples

**Phase 2 (Foundation)**: Tasks T007-T011 (DB migration), T012-T016 (Backend), T017-T018 (Frontend) can all run in parallel

**Phase 3 (US1)**:
- E2E tests T019-T024 (parallel)
- Backend T025-T029 (parallel)
- Frontend T031-T032 (parallel), then T033-T038 (sequential)

**Phase 4 (US2)**:
- E2E tests T039-T044 (parallel)
- Backend T045-T048 (parallel)
- Frontend T050-T053 (parallel)

**Phases 3-7**: All user story phases (US1, US2, US3, US5, US4) can run in parallel after Phase 2 completes

---

## Implementation Strategy

### MVP Scope (Week 1)

Focus on **Phase 3 (User Story 1)** only:
- Tasks T001-T038 (Setup + Foundation + Dashboard real data)
- Estimated: 13 hours
- Delivers: Dashboard shows real data - immediate user value

### Incremental Delivery

- **Week 1**: MVP (US1) - Dashboard real data
- **Week 2**: US2 (Market Data) + US5 (Auth) - Core features working
- **Week 3**: US3 (Indicators) + US4 (Placeholders) - Polish
- **Week 4**: Phase 8 (Testing, Documentation, Deployment)

---

## Task Summary

- **Total Tasks**: 118
- **Setup & Foundation**: 18 tasks
- **User Story 1 (P1)**: 20 tasks
- **User Story 2 (P1)**: 17 tasks
- **User Story 5 (P2)**: 16 tasks
- **User Story 3 (P2)**: 17 tasks
- **User Story 4 (P3)**: 7 tasks
- **Polish & Integration**: 23 tasks

**Parallel Opportunities**: 67 tasks marked [P] can run in parallel (57% parallelizable)

**Independent Test Criteria**: Each user story phase includes specific, testable acceptance criteria that can be verified without dependencies on other stories

**Format Validation**: ✅ All 118 tasks follow checklist format with checkbox, ID, story label (where applicable), and file paths
