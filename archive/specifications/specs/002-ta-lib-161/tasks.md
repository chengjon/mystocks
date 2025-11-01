# Tasks: Technical Analysis with 161 Indicators

**Input**: Design documents from `/specs/002-ta-lib-161/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are included in this task list per project testing requirements (pytest for backend, Vitest for frontend)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions
- **Web app**: `web/backend/`, `web/frontend/`
- Backend uses Python 3.11 + FastAPI + TA-Lib
- Frontend uses Vue 3 + Element Plus + klinecharts

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Verify TA-Lib 0.6.7 installation: `python -c "import talib; print(talib.__version__)"`
- [ ] T002 Verify klinecharts 9.8+ in `web/frontend/package.json`
- [ ] T003 [P] Update `table_config.yaml` with `indicator_configurations` table schema per data-model.md
- [ ] T004 [P] Create backend directory structure: `web/backend/app/{services,models,schemas}` if not exists
- [ ] T005 [P] Create frontend directory structure: `web/frontend/src/{components/{chart,indicators,config},composables,types,services}`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create MySQL `indicator_configurations` table: Run `python -c "from core import ConfigDrivenTableManager; mgr = ConfigDrivenTableManager(); mgr.validate_all_table_structures()"`
- [ ] T007 [P] Create indicator registry service in `web/backend/app/services/indicator_registry.py` (161 indicators metadata from TA-Lib introspection)
- [ ] T008 [P] Create base indicator calculator service in `web/backend/app/services/indicator_calculator.py` (TA-Lib wrapper with NumPy integration)
- [ ] T009 [P] Create Pydantic request schemas in `web/backend/app/schemas/indicator_request.py` (IndicatorCalculateRequest, IndicatorSpec)
- [ ] T010 [P] Create Pydantic response schemas in `web/backend/app/schemas/indicator_response.py` (IndicatorCalculationResult, IndicatorMetadata)
- [ ] T011 [P] Create SQLAlchemy model in `web/backend/app/models/indicator_config.py` (IndicatorConfiguration with JSON field)
- [ ] T012 Register indicators router in `web/backend/app/main.py` (import and include_router for /api/indicators)
- [ ] T013 [P] Create TypeScript types in `web/frontend/src/types/indicator.ts` (Indicator, IndicatorMetadata, IndicatorParameter interfaces)
- [ ] T014 [P] Create TypeScript types in `web/frontend/src/types/chart.ts` (ChartData, OHLCVData, DateRange interfaces)
- [ ] T015 [P] Create base API client in `web/frontend/src/services/indicatorService.ts` (axios wrapper for indicator endpoints)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Stock with Basic Trend Indicators (Priority: P1) 🎯 MVP

**Goal**: Users can search for a stock, select a date range, apply basic moving averages (MA5, MA10, MA20), and view K-line chart with indicators overlaid

**Independent Test**: Select stock "600519", choose last 90 days, apply MA(5), MA(10), MA(20), verify chart displays with three colored MA lines overlaid on candlesticks within 3 seconds

### Backend Tests for User Story 1

- [ ] T016 [P] [US1] Unit test for MA calculation in `web/backend/tests/test_indicators.py::test_calculate_ma` (verify NumPy array → TA-Lib → correct MA values)
- [ ] T017 [P] [US1] Unit test for multiple MAs in `web/backend/tests/test_indicators.py::test_calculate_multiple_mas` (verify batch calculation)
- [ ] T018 [P] [US1] Unit test for insufficient data handling in `web/backend/tests/test_indicators.py::test_insufficient_data_error` (MA(200) with 50 days → error)
- [ ] T019 [P] [US1] Integration test for registry endpoint in `web/backend/tests/test_indicators.py::test_get_registry` (verify 161 indicators returned with metadata)
- [ ] T020 [P] [US1] Integration test for calculate endpoint in `web/backend/tests/test_indicators.py::test_calculate_indicators_endpoint` (POST /api/indicators/calculate with MA → verify response schema)

### Backend Implementation for User Story 1

- [ ] T021 [US1] Implement `GET /api/indicators/registry` endpoint in `web/backend/app/api/indicators.py` (return indicator metadata, support category filter)
- [ ] T022 [US1] Implement `POST /api/indicators/calculate` endpoint in `web/backend/app/api/indicators.py` (validate request, load OHLCV, calculate indicators, return result)
- [ ] T023 [US1] Add trend indicator calculation logic to `indicator_calculator.py` (MA, EMA, SMA variants with TA-Lib)
- [ ] T024 [US1] Implement OHLCV data loading via `MyStocksUnifiedManager.load_data_by_classification()` in indicator_calculator service
- [ ] T025 [US1] Add data validation (OHLC relationships, date ordering) in indicator_calculator service
- [ ] T026 [US1] Add error handling for invalid symbols, date ranges, and calculation failures in indicators.py
- [ ] T027 [US1] Add performance monitoring integration with `PerformanceMonitor` in indicators.py

### Frontend Tests for User Story 1

- [ ] T028 [P] [US1] Component test for KLineChart in `web/frontend/tests/components/chart/KLineChart.spec.ts` (mount, verify canvas rendered)
- [ ] T029 [P] [US1] Component test for IndicatorSelector in `web/frontend/tests/components/indicators/IndicatorSelector.spec.ts` (verify trend category displays MA options)
- [ ] T030 [P] [US1] Composable test for useIndicators in `web/frontend/tests/composables/useIndicators.spec.ts` (addIndicator, removeIndicator, updateParameters)
- [ ] T031 [P] [US1] Service test for indicatorService in `web/frontend/tests/services/indicatorService.spec.ts` (mock axios, verify API calls)

### Frontend Implementation for User Story 1

- [ ] T032 [P] [US1] Create `KLineChart.vue` component in `web/frontend/src/components/chart/` (init klinecharts, render candlesticks + volume + overlay indicators)
- [ ] T033 [P] [US1] Create `IndicatorSelector.vue` component in `web/frontend/src/components/indicators/` (5 category tabs, indicator list with parameters, add button)
- [ ] T034 [P] [US1] Create `ChartToolbar.vue` component in `web/frontend/src/components/chart/` (stock search autocomplete, date range picker with presets, zoom/pan controls)
- [ ] T035 [P] [US1] Create `IndicatorLegend.vue` component in `web/frontend/src/components/indicators/` (show active indicators with color codes, visibility toggle, remove button)
- [ ] T036 [P] [US1] Create `useIndicators` composable in `web/frontend/src/composables/useIndicators.ts` (manage selectedIndicators state, loadRegistry, addIndicator, removeIndicator)
- [ ] T037 [P] [US1] Create `useChart` composable in `web/frontend/src/composables/useChart.ts` (manage chartInstance, loadData, updateIndicators, exportChart, dispose)
- [ ] T038 [P] [US1] Implement indicatorService methods in `web/frontend/src/services/indicatorService.ts` (getRegistry, calculateIndicators with axios)
- [ ] T039 [P] [US1] Implement chartService helper in `web/frontend/src/services/chartService.ts` (klinecharts init, data transformation, indicator overlay logic)
- [ ] T040 [US1] Update `TechnicalAnalysis.vue` in `web/frontend/src/views/` (integrate all US1 components, wire up state with composables, implement basic workflow)
- [ ] T041 [US1] Add stock search integration using existing `/api/data/stocks/search` endpoint in TechnicalAnalysis.vue
- [ ] T042 [US1] Add date range validation (start < end, end ≤ today, max 10 years) in TechnicalAnalysis.vue
- [ ] T043 [US1] Add loading states and error handling (ElMessage for user feedback) in TechnicalAnalysis.vue
- [ ] T044 [US1] Add hover tooltip showing OHLC + indicator values in KLineChart.vue (klinecharts crosshair integration)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can view stock charts with MA indicators and all acceptance criteria met

---

## Phase 4: User Story 2 - Apply Momentum and Oscillator Indicators (Priority: P2)

**Goal**: Users can add momentum indicators (RSI, KDJ, CCI) to separate oscillator panels below the main chart with reference lines

**Independent Test**: After loading a stock with MA indicators, add RSI(14) indicator, verify new panel appears below chart with RSI line and 30/70 reference lines

### Backend Tests for User Story 2

- [ ] T045 [P] [US2] Unit test for RSI calculation in `web/backend/tests/test_indicators.py::test_calculate_rsi` (verify overbought/oversold detection)
- [ ] T046 [P] [US2] Unit test for KDJ calculation in `web/backend/tests/test_indicators.py::test_calculate_kdj` (verify K, D, J lines)
- [ ] T047 [P] [US2] Integration test for multi-panel response in `web/backend/tests/test_indicators.py::test_calculate_with_oscillators` (MA + RSI → verify panel_type separation)

### Backend Implementation for User Story 2

- [ ] T048 [US2] Add momentum indicator calculation logic to `indicator_calculator.py` (RSI, KDJ, CCI, STOCH, WILLR, ROC, MOM with TA-Lib)
- [ ] T049 [US2] Update response schema to include `reference_lines` field for oscillators in indicator_response.py
- [ ] T050 [US2] Add reference line metadata to indicator registry for momentum indicators (e.g., RSI: [30, 70], STOCH: [20, 80])

### Frontend Tests for User Story 2

- [ ] T051 [P] [US2] Component test for IndicatorPanel in `web/frontend/tests/components/chart/IndicatorPanel.spec.ts` (render oscillator with reference lines)
- [ ] T052 [P] [US2] Test for panel reordering in KLineChart.spec.ts (drag-and-drop functionality)

### Frontend Implementation for User Story 2

- [ ] T053 [P] [US2] Create `IndicatorPanel.vue` component in `web/frontend/src/components/chart/` (separate pane below main chart, render oscillator lines + reference lines)
- [ ] T054 [P] [US2] Create `IndicatorParameters.vue` component in `web/frontend/src/components/indicators/` (dialog for customizing indicator parameters before adding)
- [ ] T055 [US2] Update KLineChart.vue to support multiple indicator panels (create pane for each oscillator, manage pane layout)
- [ ] T056 [US2] Update IndicatorSelector.vue to include momentum category (RSI, KDJ, CCI, STOCH tabs)
- [ ] T057 [US2] Update chartService.ts to handle oscillator panel creation and reference line rendering
- [ ] T058 [US2] Add visual highlighting for threshold crossings (e.g., RSI > 70 → red marker) in IndicatorPanel.vue

**Checkpoint**: User Stories 1 AND 2 should both work independently - users can view overlay and oscillator indicators

---

## Phase 5: User Story 5 - Identify Candlestick Patterns Automatically (Priority: P2)

**Goal**: System automatically detects and highlights candlestick patterns (Doji, Hammer, Engulfing, etc.) with icons and confidence scores

**Independent Test**: Load stock chart, enable "Candlestick Pattern Detection", verify all detected patterns marked with icons, clicking icon shows pattern details

**Note**: Implementing US5 before US3/US4 because it's P2 and independent of configuration/comparison features

### Backend Tests for User Story 5

- [ ] T059 [P] [US5] Unit test for Doji pattern detection in `web/backend/tests/test_indicators.py::test_detect_doji` (verify TA-Lib CDLDOJI)
- [ ] T060 [P] [US5] Unit test for multiple pattern detection in `web/backend/tests/test_indicators.py::test_detect_all_patterns` (verify all 61 CDL functions)
- [ ] T061 [P] [US5] Integration test for pattern detection endpoint in `web/backend/tests/test_indicators.py::test_calculate_with_patterns` (verify pattern markers in response)

### Backend Implementation for User Story 5

- [ ] T062 [US5] Add all 61 candlestick pattern functions to indicator registry (CDLDOJI, CDLHAMMER, CDLENGULFING, etc.)
- [ ] T063 [US5] Implement pattern detection logic in `indicator_calculator.py` (detect patterns, return date + pattern name + confidence)
- [ ] T064 [US5] Update response schema to include pattern detection results (array of {date, pattern, direction, confidence})

### Frontend Tests for User Story 5

- [ ] T065 [P] [US5] Component test for pattern markers in KLineChart.spec.ts (verify icons rendered on correct candles)
- [ ] T066 [P] [US5] Component test for pattern summary panel in `web/frontend/tests/components/chart/PatternSummary.spec.ts` (list view with filtering)

### Frontend Implementation for User Story 5

- [ ] T067 [P] [US5] Create `PatternSummary.vue` component in `web/frontend/src/components/chart/` (table listing all detected patterns with date, type, direction)
- [ ] T068 [US5] Update KLineChart.vue to render pattern icons on candles (use klinecharts annotation API)
- [ ] T069 [US5] Add pattern tooltip on icon hover (show pattern name, type, confidence score) in KLineChart.vue
- [ ] T070 [US5] Add pattern filtering UI (bullish/bearish/all toggle) in PatternSummary.vue
- [ ] T071 [US5] Update TechnicalAnalysis.vue to include "Enable Pattern Detection" toggle and PatternSummary panel
- [ ] T072 [US5] Update chartService.ts to transform pattern detection results to klinecharts annotations

**Checkpoint**: Pattern detection works independently - users can see automatic candlestick pattern identification

---

## Phase 6: User Story 4 - Save and Load Indicator Configurations (Priority: P3)

**Goal**: Users can save their current indicator setup with a name and quickly apply it to any stock later

**Independent Test**: Configure 5 indicators, click "Save", name it "My Setup", close session, reopen, select different stock, load "My Setup", verify all 5 indicators applied

### Backend Tests for User Story 4

- [ ] T073 [P] [US4] Integration test for save config in `web/backend/tests/test_indicator_config.py::test_save_configuration` (POST /api/indicators/configs → verify MySQL insertion)
- [ ] T074 [P] [US4] Integration test for list configs in `web/backend/tests/test_indicator_config.py::test_list_configurations` (GET /api/indicators/configs → verify user_id filtering)
- [ ] T075 [P] [US4] Integration test for load config in `web/backend/tests/test_indicator_config.py::test_get_configuration` (GET /api/indicators/configs/{id} → verify ownership)
- [ ] T076 [P] [US4] Integration test for update config in `web/backend/tests/test_indicator_config.py::test_update_configuration` (PUT → verify updated_at changes)
- [ ] T077 [P] [US4] Integration test for delete config in `web/backend/tests/test_indicator_config.py::test_delete_configuration` (DELETE → verify cascade)
- [ ] T078 [P] [US4] Integration test for duplicate name error in `web/backend/tests/test_indicator_config.py::test_duplicate_name` (409 Conflict)

### Backend Implementation for User Story 4

- [ ] T079 [US4] Create `indicator_config.py` API router in `web/backend/app/api/` with full CRUD endpoints (GET, POST, PUT, DELETE /api/indicators/configs)
- [ ] T080 [US4] Implement `save_configuration` endpoint (validate indicators against registry, check name uniqueness, insert to MySQL)
- [ ] T081 [US4] Implement `list_configurations` endpoint (filter by user_id, support sorting by last_used_at/created_at/name, limit to 50)
- [ ] T082 [US4] Implement `get_configuration` endpoint (verify ownership, return configuration JSON)
- [ ] T083 [US4] Implement `update_configuration` endpoint (verify ownership, validate indicators, update MySQL)
- [ ] T084 [US4] Implement `delete_configuration` endpoint (verify ownership, soft delete or hard delete)
- [ ] T085 [US4] Add auto-update of `last_used_at` when configuration is applied (UPDATE on load)
- [ ] T086 [US4] Register config router in `web/backend/app/main.py`

### Frontend Tests for User Story 4

- [ ] T087 [P] [US4] Component test for ConfigSaver in `web/frontend/tests/components/config/ConfigSaver.spec.ts` (dialog with name input, save button)
- [ ] T088 [P] [US4] Component test for ConfigLoader in `web/frontend/tests/components/config/ConfigLoader.spec.ts` (list with sort options, load button)
- [ ] T089 [P] [US4] Composable test for useIndicatorConfig in `web/frontend/tests/composables/useIndicatorConfig.spec.ts` (saveConfig, loadConfigs, applyConfig)

### Frontend Implementation for User Story 4

- [ ] T090 [P] [US4] Create `ConfigSaver.vue` component in `web/frontend/src/components/config/` (dialog with ElForm for name input, validate uniqueness, save button)
- [ ] T091 [P] [US4] Create `ConfigLoader.vue` component in `web/frontend/src/components/config/` (ElTable with configs list, sort dropdown, load/delete buttons)
- [ ] T092 [P] [US4] Create `useIndicatorConfig` composable in `web/frontend/src/composables/useIndicatorConfig.ts` (manage savedConfigs state, saveConfig, loadConfigs, applyConfig, deleteConfig)
- [ ] T093 [US4] Update indicatorService.ts to add config management methods (saveConfiguration, listConfigurations, getConfiguration, updateConfiguration, deleteConfiguration)
- [ ] T094 [US4] Update TechnicalAnalysis.vue to add "Save Configuration" and "Load Configuration" buttons in toolbar
- [ ] T095 [US4] Implement config application logic (load config → populate selectedIndicators → trigger calculation) in useIndicatorConfig composable
- [ ] T096 [US4] Add "Recently Used" sorting to ConfigLoader (sort by last_used_at DESC by default)

**Checkpoint**: Configuration persistence works - users can save and reuse indicator setups across sessions

---

## Phase 7: User Story 3 - Compare Multiple Stocks with Same Indicators (Priority: P3)

**Goal**: Users can open 2-4 stock charts side-by-side, apply same indicators to all, synchronize time range and zoom

**Independent Test**: Open stock "600519", apply MA(20) + RSI(14), click "Add comparison", select "000858", verify both charts display side-by-side with same indicators and synchronized zoom

### Frontend Tests for User Story 3

- [ ] T097 [P] [US3] Component test for multi-chart layout in `web/frontend/tests/components/chart/ChartGrid.spec.ts` (2x2 grid, responsive)
- [ ] T098 [P] [US3] Test for synchronized zoom in KLineChart.spec.ts (zoom on chart A → verify chart B zooms)

### Frontend Implementation for User Story 3

- [ ] T099 [P] [US3] Create `ChartGrid.vue` component in `web/frontend/src/components/chart/` (grid layout supporting 1-4 charts, responsive)
- [ ] T100 [US3] Update useChart composable to support multiple chart instances (chartInstances array, syncedZoomRange)
- [ ] T101 [US3] Implement chart synchronization logic in chartService.ts (listen to zoom/pan events, broadcast to other charts)
- [ ] T102 [US3] Add "Add Comparison Chart" button to TechnicalAnalysis.vue toolbar
- [ ] T103 [US3] Add "Apply to All Charts" button in IndicatorSelector.vue (bulk apply current indicators)
- [ ] T104 [US3] Implement comparison chart workflow in TechnicalAnalysis.vue (add chart, select symbol, sync indicators, sync zoom)
- [ ] T105 [US3] Add chart removal functionality (close button on each chart) in ChartGrid.vue

**Checkpoint**: Multi-chart comparison works - users can analyze multiple stocks simultaneously with synchronized indicators

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T106 [P] Implement Redis caching for indicator calculations in `web/backend/app/services/indicator_cache.py` (cache key generation, TTL logic, optional activation)
- [ ] T107 [P] Add response compression (gzip) middleware in `web/backend/app/main.py` (compress responses > 1KB)
- [ ] T108 [P] Add request rate limiting (10 req/min per user) for calculate endpoint in indicators.py
- [ ] T109 [P] Performance optimization: NumPy vectorization for batch indicator calculations in indicator_calculator.py
- [ ] T110 [P] Add comprehensive logging for all API endpoints (request ID, user ID, duration) in main.py middleware
- [ ] T111 [P] Add chart export functionality (PNG/JPG with indicators) in chartService.ts (canvas.toDataURL)
- [ ] T112 [P] Implement parameter validation tooltips in IndicatorParameters.vue (show min/max constraints)
- [ ] T113 [P] Add keyboard shortcuts (Ctrl+S for save config, Ctrl+E for export chart) in TechnicalAnalysis.vue
- [ ] T114 [P] Optimize bundle size: lazy load klinecharts (dynamic import) in TechnicalAnalysis.vue
- [ ] T115 [P] Add loading skeleton for chart initialization in KLineChart.vue
- [ ] T116 Code cleanup: Remove console.log statements, add JSDoc comments to all services
- [ ] T117 Security: Add CSRF protection for POST/PUT/DELETE endpoints in main.py
- [ ] T118 [P] Update CLAUDE.md documentation with new indicator calculation patterns
- [ ] T119 Performance test: Verify <2s calculation for 1 year + 10 indicators in `web/backend/tests/test_indicator_performance.py`
- [ ] T120 Run quickstart.md validation: Execute all test commands and verify success

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - **US1 (Phase 3)**: Can start after Foundational - No dependencies on other stories
  - **US2 (Phase 4)**: Can start after Foundational - Builds on US1 charts but independently testable
  - **US5 (Phase 5)**: Can start after Foundational - Independent pattern detection
  - **US4 (Phase 6)**: Can start after US1 (needs charts to save configs) - Otherwise independent
  - **US3 (Phase 7)**: Can start after US1 (needs single chart working) - Extends to multi-chart
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Basic Trend Indicators**: Foundation complete → Start immediately (MVP target)
- **User Story 2 (P2) - Momentum Indicators**: US1 complete → Extends charting with oscillator panels
- **User Story 5 (P2) - Candlestick Patterns**: US1 complete → Adds pattern detection layer
- **User Story 4 (P3) - Configuration Persistence**: US1 complete → Saves indicator setups
- **User Story 3 (P3) - Multi-Chart Comparison**: US1 complete → Extends to multiple charts

**Recommended Order**: Foundation → US1 (MVP) → US2 → US5 → US4 → US3

### Within Each User Story

- Backend tests before backend implementation (TDD order)
- Frontend tests before frontend implementation (TDD order)
- Models before services
- Services before endpoints/components
- Core functionality before integrations
- Story complete and tested before moving to next priority

### Parallel Opportunities

- **Setup (Phase 1)**: All 5 tasks marked [P] can run in parallel
- **Foundational (Phase 2)**: Tasks T007-T015 marked [P] can run in parallel (after T006 completes)
- **Within User Stories**: All tasks marked [P] can run in parallel
  - Example US1: T016-T020 (tests) + T032-T039 (components) all [P]
- **Across User Stories**: With sufficient team size, US2, US5, US4, US3 can be worked on in parallel after US1 completes

---

## Parallel Example: User Story 1 Backend

```bash
# Launch all backend tests for US1 together (after T015):
Task T016: "Unit test for MA calculation"
Task T017: "Unit test for multiple MAs"
Task T018: "Unit test for insufficient data"
Task T019: "Integration test for registry endpoint"
Task T020: "Integration test for calculate endpoint"

# After tests pass, launch all implementation tasks in parallel:
# (These are sequential as they modify same files - but listed for clarity)
```

## Parallel Example: User Story 1 Frontend

```bash
# Launch all frontend component creation together (after T027):
Task T032: "Create KLineChart.vue"
Task T033: "Create IndicatorSelector.vue"
Task T034: "Create ChartToolbar.vue"
Task T035: "Create IndicatorLegend.vue"
Task T036: "Create useIndicators composable"
Task T037: "Create useChart composable"
Task T038: "Implement indicatorService"
Task T039: "Implement chartService"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

**Goal**: Fastest path to demonstrable value

1. ✅ Complete Phase 1: Setup (5 tasks, ~30 mins)
2. ✅ Complete Phase 2: Foundational (10 tasks, ~4 hours) - **CRITICAL MILESTONE**
3. ✅ Complete Phase 3: User Story 1 (29 tasks, ~12 hours)
   - Backend: 12 tasks (tests + implementation)
   - Frontend: 17 tasks (tests + implementation)
4. **STOP and VALIDATE**:
   - Run acceptance test from spec.md (US1, scenario 1-4)
   - Verify <3s chart render, hover tooltips, date range changes work
5. Deploy MVP to staging/demo environment
6. Gather user feedback before proceeding

**MVP Scope**: Users can view stock K-line charts with MA indicators - fully functional and testable

**Time Estimate**: ~16-20 hours for single developer, ~8-10 hours with pair programming

### Incremental Delivery

**Goal**: Add value incrementally while maintaining stability

1. **Iteration 1 - Foundation + MVP** (Days 1-3)
   - Setup + Foundational + US1
   - Deploy, test, demo
   - **Deliverable**: Basic trend analysis working

2. **Iteration 2 - Momentum Analysis** (Days 4-5)
   - Add US2 (Momentum Indicators)
   - Test independently, verify US1 still works
   - Deploy, demo
   - **Deliverable**: Oscillator analysis added

3. **Iteration 3 - Pattern Detection** (Days 6-7)
   - Add US5 (Candlestick Patterns)
   - Test independently
   - Deploy, demo
   - **Deliverable**: Automatic pattern recognition

4. **Iteration 4 - Productivity Features** (Days 8-9)
   - Add US4 (Configuration Persistence)
   - Test save/load workflows
   - Deploy, demo
   - **Deliverable**: User can save favorite setups

5. **Iteration 5 - Advanced Comparison** (Days 10-11)
   - Add US3 (Multi-Chart Comparison)
   - Test synchronized charts
   - Deploy, demo
   - **Deliverable**: Side-by-side stock comparison

6. **Iteration 6 - Polish** (Day 12)
   - Phase 8 tasks (caching, optimization, security)
   - Performance validation
   - Final demo

**Total Estimate**: 12-15 development days (single developer), 6-8 days (pair programming)

### Parallel Team Strategy

With 3 developers after Foundation completes:

**Week 1: Parallel Stories**
- Developer A: US1 (P1 MVP) - Days 1-3
- Developer B: US2 (P2 Momentum) - Days 1-2 (depends on US1 completion)
- Developer C: US5 (P2 Patterns) - Days 1-2 (independent)

**Week 2: Parallel Features**
- Developer A: US4 (P3 Config) - Days 4-5
- Developer B: US3 (P3 Comparison) - Days 3-5 (depends on US1)
- Developer C: Polish (Phase 8) - Days 3-5

**Result**: All features complete in ~5 days vs 12-15 days solo

---

## Task Count Summary

- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 10 tasks ⚠️ CRITICAL PATH
- **Phase 3 (US1 - P1 MVP)**: 29 tasks (12 backend + 17 frontend)
- **Phase 4 (US2 - P2)**: 11 tasks (3 backend + 3 backend impl + 2 frontend tests + 3 frontend impl)
- **Phase 5 (US5 - P2)**: 11 tasks (3 backend + 3 backend impl + 2 frontend tests + 3 frontend impl)
- **Phase 6 (US4 - P3)**: 18 tasks (6 backend tests + 8 backend impl + 3 frontend tests + 3 frontend impl)
- **Phase 7 (US3 - P3)**: 9 tasks (2 frontend tests + 7 frontend impl)
- **Phase 8 (Polish)**: 15 tasks
- **TOTAL**: 120 tasks

**Parallel Opportunities**: 47 tasks marked [P] (39% can run in parallel)

**MVP Scope** (US1 only): 44 tasks (Setup + Foundational + US1)

---

## Notes

- [P] tasks = different files, no dependencies, safe to parallelize
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests use TDD approach: write test → verify failure → implement → verify pass
- Commit after each logical task or group of related tasks
- Stop at any checkpoint to validate story independently
- Backend uses `pytest`, Frontend uses `Vitest`
- All API endpoints require JWT authentication (extracted from existing system)
- Cache implementation (T106) is optional - feature works without Redis
- Chart export (T111) uses HTML canvas API (browser-native, no external dependencies)

---

## Acceptance Validation Checklist

After completing each user story, validate against spec.md acceptance scenarios:

### User Story 1 Validation
- [ ] Scenario 1: Search "600519", select 90 days, apply MA5/MA10/MA20 → 3 colored lines displayed
- [ ] Scenario 2: Hover over data point → tooltip shows date, OHLC, all indicator values
- [ ] Scenario 3: Change date range to 6 months → chart refreshes with same indicators
- [ ] Scenario 4: Search invalid code → friendly error + suggestions

### User Story 2 Validation
- [ ] Scenario 1: Add RSI(14) → new panel below chart with 30/70 reference lines
- [ ] Scenario 2: RSI crosses 70 → crossing point visually highlighted
- [ ] Scenario 3: Drag panels → panels reorder accordingly
- [ ] Scenario 4: Apply KDJ → three lines (K, D, J) in dedicated panel

### User Story 5 Validation
- [ ] Scenario 1: Enable pattern detection → all patterns marked with icons
- [ ] Scenario 2: Click pattern icon → tooltip shows name, type, confidence
- [ ] Scenario 3: View pattern summary → chronological list with dates and types
- [ ] Scenario 4: Filter "bullish only" → chart + summary show only bullish patterns

### User Story 4 Validation
- [ ] Scenario 1: Save 5 indicators as "My Setup" → appears in config list
- [ ] Scenario 2: Load "My Setup" on different stock → all 5 indicators applied
- [ ] Scenario 3: View 10 configs → shows name, count, last used date
- [ ] Scenario 4: Update config → saved with same name, updated_at changes

### User Story 3 Validation
- [ ] Scenario 1: Add comparison → second chart appears side-by-side
- [ ] Scenario 2: Scroll/zoom chart 1 → all charts synchronize time range
- [ ] Scenario 3: "Apply to all" → all comparison charts get same indicators
- [ ] Scenario 4: Change time range on any chart → all charts update
