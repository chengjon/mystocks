# Tasks: Market Data UI/UX Improvements

**Input**: Design documents from `/specs/004-ui-short-name/`
**Prerequisites**: plan.md, spec.md, research.md

**Tests**: Tests are NOT explicitly requested in the feature spec, so only manual acceptance testing is included.

**Organization**: Tasks are grouped by user story (US1-US5) to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- All paths use `web/frontend/src/` or `web/backend/app/` prefixes

## Path Conventions
- **Frontend**: `web/frontend/src/`
- **Backend**: `web/backend/app/`
- **Styles**: `web/frontend/src/styles/`
- **Config**: `web/frontend/src/config/`

---

## Phase 1: Setup (Shared Infrastructure) ✅

**Purpose**: Create shared utilities and styles used across multiple user stories

- [X] T001 [P] Create `web/frontend/src/styles/typography.css` with CSS custom properties for 5 font size levels (FR-014) and font hierarchy (FR-016)
- [X] T002 [P] Create `web/frontend/src/styles/table-common.css` with fixed header styles (position: sticky) and zebra striping (FR-001, FR-009, FR-012)
- [X] T003 [P] Create `web/frontend/src/composables/useUserPreferences.ts` composable for LocalStorage preference management (FR-019)
- [X] T004 [P] Create `web/frontend/src/composables/usePagination.ts` composable for reusable pagination logic (FR-002, FR-010)
- [X] T005 Create `web/frontend/src/stores/preferences.ts` Pinia store for user preferences state management
- [X] T006 Import typography.css and table-common.css in `web/frontend/src/main.js` to apply globally

**Checkpoint**: ✅ Shared infrastructure ready - user story implementation can now begin in parallel

---

## Phase 2: User Story 1 - 资金流向趋势分析与交互 (Priority: P1) 🎯 MVP ✅

**Goal**: Enable users to view fund flow data with fixed table headers, pagination, and click industry names to see trend charts

**Independent Test**:
1. Visit fund flow page, scroll table → header stays fixed (FR-001)
2. Click any industry name → trend chart updates below table (FR-007)
3. Adjust "每页显示" to 20 → table shows 20 items per page (FR-002, FR-003)
4. Verify zebra striping on table rows (FR-004)

### Implementation for User Story 1

- [X] T007 [US1] Modify `web/frontend/src/components/market/FundFlowPanel.vue`:
  - Add `class="sticky-header-table"` to el-table to apply fixed header styles (FR-001)
  - Add `stripe` prop for zebra striping (FR-004)
  - Add explicit height to table wrapper: `height="calc(100vh - 300px)"` for sticky to work

- [X] T008 [US1] Add pagination controls to `web/frontend/src/components/market/FundFlowPanel.vue`:
  - Import `usePagination` composable
  - Add el-select for "每页显示" in card header (options: 10, 20, 50, 100) (FR-002)
  - Add el-pagination component below table with `hide-on-single-page` (FR-003)
  - Compute `paginatedData` from `fundFlowData` based on current page/size
  - Save page size to LocalStorage via `useUserPreferences`

- [X] T009 [US1] Make industry names clickable in `web/frontend/src/components/market/FundFlowPanel.vue`:
  - Wrap "行业名称" column content in `<a>` tag with click handler (FR-005)
  - Add CSS class `.industry-link` with hover styles (underline, pointer cursor)
  - Create `selectedIndustry` ref to track clicked industry
  - Add click handler `handleIndustryClick(industryName)` that updates `selectedIndustry`

- [X] T010 [P] [US1] Create `web/frontend/src/components/market/FundFlowTrendChart.vue`:
  - Accept props: `industryName: String`, `trendData: Array`
  - Use vue-echarts with LineChart component
  - Configure chart option with: title, xAxis (dates), yAxis (金额), series (net_inflow, main_inflow, retail_inflow)
  - Add autoresize and 400px height (FR-006)
  - Apply smooth curves and 3 color series (#409EFF, #F56C6C, #E6A23C)

- [X] T011 [US1] Integrate trend chart into `web/frontend/src/components/market/FundFlowPanel.vue`:
  - Import FundFlowTrendChart component
  - Add conditional render: `v-if="selectedIndustry"` (FR-006)
  - Fetch trend data when `selectedIndustry` changes via new method `fetchIndustryTrend(industryName)`
  - Pass `selectedIndustry` and `industryTrendData` as props to FundFlowTrendChart
  - Add visual highlight to selected industry row in table (FR-008)
  - Ensure chart updates within 500ms (SC-001)

- [ ] T012 [US1] (Optional Backend) Add API endpoint `GET /api/market/v3/fund-flow/trend?industry_name={name}` in `web/backend/app/api/market_v3.py`:
  - Query PostgreSQL for historical fund flow data for specified industry (last 30 days)
  - Return JSON: `[{date: "2025-10-01", net_inflow: 123.45, main_inflow: 89.12, retail_inflow: 34.33}, ...]`
  - Skip if trend data already available via existing endpoints - **SKIPPED** (using existing data for now)

**Checkpoint**: ✅ **MVP COMPLETE** - fund flow page has fixed headers, pagination, clickable industries, and trend chart integration

---

## Phase 3: User Story 2 - 大数据量表格浏览体验优化 (Priority: P2) ✅

**Goal**: Add fixed table headers and pagination to ETF and Dragon Tiger pages for better large dataset browsing

**Independent Test**:
1. Visit ETF page, scroll table → header stays fixed (FR-009)
2. Adjust "每页显示" to 30 → table shows 30 items per page (FR-010, FR-011)
3. Visit Dragon Tiger page, scroll table → header stays fixed (FR-009)
4. Verify zebra striping on both tables (FR-012)

### Implementation for User Story 2

- [X] T013 [P] [US2] Modify `web/frontend/src/components/market/ETFDataPanel.vue`:
  - Add `class="sticky-header-table"` to el-table (FR-009)
  - Add `stripe` prop for zebra striping (FR-012)
  - Add explicit height: `height="calc(100vh - 300px)"`

- [X] T014 [P] [US2] Add pagination to `web/frontend/src/components/market/ETFDataPanel.vue`:
  - Import `usePagination` composable
  - Add el-select for "每页显示" in card header (options: 10, 20, 50, 100) (FR-010)
  - Add el-pagination with `hide-on-single-page` (FR-011)
  - Compute `paginatedData` from ETF data
  - Save page size preference to LocalStorage

- [X] T015 [P] [US2] Modify `web/frontend/src/components/market/LongHuBangPanel.vue`:
  - Add `class="sticky-header-table"` to el-table (FR-009)
  - Add `stripe` prop for zebra striping (FR-012)
  - Add explicit height: `height="calc(100vh - 300px)"`

- [X] T016 [P] [US2] Add pagination to `web/frontend/src/components/market/LongHuBangPanel.vue`:
  - Import `usePagination` composable
  - Add el-select for "每页显示" in card header (options: 10, 20, 50, 100) (FR-010)
  - Add el-pagination with `hide-on-single-page` (FR-011)
  - Compute `paginatedData` from Dragon Tiger data
  - Save page size preference to LocalStorage

**Checkpoint**: ✅ **User Story 2 COMPLETE** - ETF and Dragon Tiger pages have fixed headers, pagination, and zebra striping

---

## Phase 4: User Story 3 - 自选股组织与管理 (Priority: P2)

**Goal**: Restructure watchlist page with tab-based layout for 4 groups (User/System/Strategy/Monitor)

**Independent Test**:
1. Visit Watchlist page → see 4 tabs, "用户自选" is default active (FR-027)
2. Click "策略自选" tab → content switches, tab highlights (FR-026)
3. Refresh page → last selected tab remembered (FR-030)
4. Verify different stock groups have visual distinction (FR-029)

### Implementation for User Story 3

- [ ] T017 [P] [US3] Rename `web/frontend/src/views/StockManagement.vue` to `web/frontend/src/views/Watchlist.vue` (FR-025)

- [ ] T018 [US3] Update Vue Router in `web/frontend/src/router/index.js`:
  - Change route path from `/stock-management` to `/watchlist`
  - Update component import from `StockManagement` to `Watchlist`
  - Update navigation menu label from "股票管理" to "自选股" (FR-025)

- [ ] T019 [P] [US3] Create `web/frontend/src/components/stock/WatchlistTabs.vue`:
  - Use el-tabs with 4 el-tab-pane components (FR-026)
  - Tab names: 'user', 'system', 'strategy', 'monitor'
  - Tab labels: '用户自选', '系统自选', '策略自选', '监控列表'
  - Default active tab: 'user' (FR-027)
  - Each tab pane contains WatchlistTable component with group-specific data

- [ ] T020 [US3] Add tab state management to `WatchlistTabs.vue`:
  - Use `useRoute` and `useRouter` from vue-router
  - Read initial tab from URL query parameter: `?tab=strategy`
  - If no URL param, read from LocalStorage `lastWatchlistTab`
  - On tab change: update URL query param and save to LocalStorage (FR-030)
  - Watch route.query.tab for browser back/forward navigation

- [ ] T021 [P] [US3] Create or modify `web/frontend/src/components/stock/WatchlistTable.vue`:
  - Accept prop: `group: String` ('user', 'system', 'strategy', 'monitor')
  - Fetch data specific to the group
  - Apply fixed header styles: `class="sticky-header-table"` (FR-028)
  - Add group highlighting: alternate background colors or borders for different groups (FR-029)
  - CSS: `.group-1 { background-color: #f0f9ff; }`, `.group-2 { background-color: #fef3f2; }`, etc.

- [ ] T022 [US3] Integrate `WatchlistTabs` into `web/frontend/src/views/Watchlist.vue`:
  - Replace existing stock management layout with `<WatchlistTabs />`
  - Remove old single-table layout
  - Test tab switching works correctly

**Checkpoint**: User Story 3 complete - Watchlist page has 4 tabs, state persistence, and group highlighting

---

## Phase 5: User Story 4 - 全局字体大小调整 (Priority: P3)

**Goal**: Allow users to adjust global font size with 5 levels (12-20px) and persist preference

**Independent Test**:
1. Visit Settings → Display Settings → see font size options (FR-013)
2. Select "Large (18px)" → all text updates immediately (FR-015, SC-003)
3. Navigate to any page → 18px font applied everywhere (FR-016)
4. Close browser, reopen → font size still 18px (FR-019)

### Implementation for User Story 4

- [ ] T023 [P] [US4] Create `web/frontend/src/components/settings/FontSizeSetting.vue`:
  - Use el-radio-group with 5 el-radio-button options (FR-014):
    - Extra Small (12px), Small (14px), Medium (16px), Large (18px), Extra Large (20px)
  - On change: update CSS variable `--font-size-base` via `document.documentElement.style.setProperty()` (FR-015)
  - Save selection to LocalStorage via `useUserPreferences` (FR-019)
  - Load saved preference on mount and apply immediately
  - Add console log for observability (user interaction tracking)

- [ ] T024 [US4] Create or modify `web/frontend/src/views/Settings.vue`:
  - Add "显示设置" section if not exists
  - Import and render `<FontSizeSetting />` component (FR-013)
  - Add section header: "字体大小"

- [ ] T025 [US4] Update `web/frontend/src/styles/typography.css`:
  - Ensure CSS variables are defined: `--font-size-base`, `--font-size-helper`, `--font-size-body`, etc. (FR-016)
  - Verify font hierarchy formulas: helper = base - 2px, subtitle = base + 2px, etc.
  - Verify line-height: 1.5 (FR-017)
  - Verify font-family: "Helvetica Neue", Helvetica, "PingFang SC"... (FR-018)

- [ ] T026 [US4] Add global font size initialization in `web/frontend/src/main.js`:
  - On app mount, read `userFontSize` from LocalStorage
  - If exists, apply to `--font-size-base` CSS variable
  - Default to `16px` (Medium) if no preference saved

- [ ] T027 [US4] Test responsive layout (FR-020):
  - Verify table column widths auto-adjust at all 5 font sizes
  - Verify no layout breakage on mobile devices (<768px)
  - Verify text remains readable at 12px (smallest) and 20px (largest) (SC-008)

**Checkpoint**: User Story 4 complete - Global font sizing works with 5 levels, immediate updates, and persistence

---

## Phase 6: User Story 5 - 问财筛选快速查询 (Priority: P3)

**Goal**: Restore 9 default query presets (qs_1 to qs_9) in Wencai filter page with one-click execution

**Independent Test**:
1. Visit Market Data → Wencai Filter → see 9 preset query cards (FR-021)
2. Click "qs_3" → query executes, results appear in right panel (FR-022, FR-023)
3. Click "qs_7" → previous results cleared, new results shown (FR-024)

### Implementation for User Story 5

- [ ] T028 [P] [US5] Create `web/frontend/src/config/wencai-queries.json`:
  - Define schema: `{ version: "1.0", queries: [...] }`
  - Each query object: `{ id: "qs_1", name: "...", description: "...", conditions: {...} }`
  - Define all 9 queries (qs_1 to qs_9) based on product requirements (FR-021)
  - Example conditions: market_cap_min, industry, consecutive_up_days, volume_ratio_min, order_by

- [ ] T029 [US5] Modify `web/frontend/src/components/market/WencaiFilter.vue`:
  - Import wencai-queries.json
  - Add "查询列表 - 默认查询" section in el-card header
  - Render 9 query cards in el-row with el-col (3 per row, :span="8") (FR-021)
  - Each card shows: query name (h4), description (p)
  - Add shadow="hover" and clickable cursor

- [ ] T030 [US5] Add query execution to `WencaiFilter.vue`:
  - Create method `executeQuery(query)` that sends query.conditions to backend API (FR-022)
  - Update `queryResults` ref with response data
  - Show results in "查询结果" panel below query cards (FR-023)
  - Add loading state during query execution
  - Clear previous results when new query clicked (FR-024)
  - Add console log for user interaction tracking (observability)
  - Ensure results update within 1 second (SC-006)

- [ ] T031 [US5] (Optional Backend) Create or update API endpoint `POST /api/wencai/filter` in `web/backend/app/api/wencai.py`:
  - Accept JSON body with query conditions
  - Execute query against stock database
  - Return matching stock list with columns: code, name, price, change_percent, market_cap, etc.
  - Skip if endpoint already exists

**Checkpoint**: User Story 5 complete - Wencai filter has 9 preset queries with one-click execution and result display

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements that affect multiple user stories

- [ ] T032 [P] Add user interaction logging to `web/frontend/src/utils/logger.ts`:
  - Log font size changes (US4)
  - Log tab switches (US3)
  - Log pagination adjustments (US1, US2)
  - Log industry clicks (US1)
  - Log Wencai query executions (US5)

- [ ] T033 [P] Performance optimization:
  - Verify chart update times <500ms (US1, SC-001)
  - Verify font change times <200ms (US4, SC-003)
  - Verify tab switch times <300ms (US3, SC-005)
  - Verify page load times <2s (US2, SC-004)
  - Add virtual scrolling if tables exceed 1000 rows (risk mitigation)

- [ ] T034 [P] Browser compatibility testing:
  - Test position: sticky on Chrome 90+, Firefox 88+, Edge 90+, Safari 14+
  - Test mobile responsiveness (<768px) for all features
  - Verify no layout breakage at extreme font sizes (12px, 20px)

- [ ] T035 [P] Create E2E tests in `web/frontend/tests/e2e/ui-ux-scenarios.spec.ts`:
  - US1: Test fixed header scrolling, industry click → chart update, pagination
  - US2: Test ETF/Dragon Tiger fixed headers and pagination
  - US3: Test watchlist tab switching and state persistence
  - US4: Test font size change and global application
  - US5: Test Wencai preset query execution

- [ ] T036 Update user documentation:
  - Document new font size setting in user guide
  - Document watchlist tab structure
  - Document Wencai preset queries
  - Update screenshots showing new UI improvements

- [ ] T037 Code cleanup:
  - Remove debug console.logs (keep only observability logs)
  - Ensure all components follow project coding standards
  - Remove unused imports and variables
  - Run linter and formatter

**Checkpoint**: All polish tasks complete - feature is production-ready

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **User Stories (Phase 2-6)**: All depend on Setup completion
  - User stories can proceed in parallel (if staffed) OR sequentially in priority order
  - US1 (P1) → US2 (P2) → US3 (P2) → US4 (P3) → US5 (P3)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: No dependencies on other stories - Can start after Setup
- **US2 (P2)**: No dependencies on other stories - Can start after Setup
- **US3 (P2)**: No dependencies on other stories - Can start after Setup
- **US4 (P3)**: No dependencies on other stories - Can start after Setup
- **US5 (P3)**: No dependencies on other stories - Can start after Setup

**All user stories are independent and can be implemented/tested in parallel**

### Within Each User Story

- Shared infrastructure (composables, stores) before components
- Component modifications before integration
- Core functionality before polish features

### Parallel Opportunities

- **Phase 1 Setup**: T001, T002, T003, T004 can all run in parallel (different files)
- **US1**: T007, T010 can run in parallel (T007 modifies FundFlowPanel, T010 creates new FundFlowTrendChart)
- **US2**: T013, T015 can run in parallel (different components), T014, T016 can run in parallel
- **US3**: T017, T019, T021 can run in parallel (different files)
- **US4**: T023, T025 can run in parallel (different files)
- **US5**: T028, T029 can run in parallel (config file vs component)
- **Phase 7 Polish**: T032, T033, T034, T035, T036 can all run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch parallel tasks for US1 (different files):
Task T007: "Modify FundFlowPanel.vue for fixed headers and pagination"
Task T010: "Create FundFlowTrendChart.vue component"

# Then sequential tasks (same file or dependencies):
Task T008: "Add pagination controls to FundFlowPanel.vue" (after T007)
Task T009: "Make industry names clickable in FundFlowPanel.vue" (after T007)
Task T011: "Integrate trend chart into FundFlowPanel.vue" (after T010, T009)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: User Story 1 (T007-T012)
3. **STOP and VALIDATE**: Test US1 independently using acceptance scenarios from spec.md
4. Deploy/demo if ready
5. **Estimated time**: 2-3 days for MVP

### Incremental Delivery

1. Complete Setup → Shared infrastructure ready
2. Add US1 (Fund Flow) → Test independently → Deploy/Demo (MVP!)
3. Add US2 (ETF/Dragon Tiger) → Test independently → Deploy/Demo
4. Add US3 (Watchlist Tabs) → Test independently → Deploy/Demo
5. Add US4 (Font Settings) → Test independently → Deploy/Demo
6. Add US5 (Wencai Filter) → Test independently → Deploy/Demo
7. Add Polish (Phase 7) → Final production release

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup together (Phase 1)
2. Once Setup is done:
   - Developer A: User Story 1 (Fund Flow - P1)
   - Developer B: User Story 2 (ETF/Dragon Tiger - P2)
   - Developer C: User Story 3 (Watchlist - P2)
   - Developer D: User Story 4 (Font Settings - P3)
   - Developer E: User Story 5 (Wencai - P3)
3. Stories complete and integrate independently
4. Team reviews and completes Polish phase together

---

## Task Summary

- **Total Tasks**: 37
- **Setup Tasks**: 6 (T001-T006)
- **US1 Tasks**: 6 (T007-T012) - Fund Flow
- **US2 Tasks**: 4 (T013-T016) - ETF & Dragon Tiger
- **US3 Tasks**: 6 (T017-T022) - Watchlist Tabs
- **US4 Tasks**: 5 (T023-T027) - Font Settings
- **US5 Tasks**: 4 (T028-T031) - Wencai Filter
- **Polish Tasks**: 6 (T032-T037)

**Parallel Opportunities**: 15+ tasks can run in parallel across phases

**MVP Scope**: Phase 1 (Setup) + Phase 2 (US1 only) = 12 tasks

**Independent Testing**: Each user story has clear acceptance criteria in spec.md for validation

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- All 5 user stories are independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Focus on MVP first (US1), then incrementally add US2-US5 in priority order
- No formal automated tests requested - rely on manual acceptance testing per spec.md scenarios
