# Implementation Tasks: Fix 5 Critical Issues in OpenStock Demo

**Feature Branch**: `001-fix-5-critical`
**Date**: 2025-10-20
**Total Tasks**: 24
**Estimated Time**: 2-3 hours

## Task Organization

Tasks are organized by user story to enable independent implementation and testing. Each story phase includes all tasks needed to complete that story increment.

---

## Phase 1: Setup & Environment (5 min)

**Goal**: Verify development environment is ready

### T001: Verify Branch and Dependencies [Setup]
**File**: N/A (verification only)
**Description**: Ensure on correct feature branch and all dependencies installed
**Actions**:
1. Verify current branch: `git branch --show-current` → Should be `001-fix-5-critical`
2. Verify Python dependencies: `cd web/backend && pip list | grep -E "(fastapi|psycopg2|akshare)"`
3. Verify Node dependencies: `cd web/frontend && npm list vue element-plus echarts`
4. Verify PostgreSQL connection: `psql -h localhost -U mystocks -d mystocks -c "SELECT version();"`

**Success Criteria**: All checks pass without errors

**Estimated Time**: 5 minutes

---

## Phase 2: Foundational Prerequisites (15 min)

**Goal**: Database schema changes that BLOCK all user stories

**CRITICAL**: These tasks MUST complete before ANY user story can be implemented.

### T002: [BLOCKING] Create Database Migration Script [Foundation]
**File**: `web/backend/migrations/001_watchlist_tables.sql`
**Description**: Create SQL migration script for watchlist_groups and user_watchlist tables
**Actions**:
1. Create migrations directory if not exists: `mkdir -p web/backend/migrations`
2. Create migration file with:
   - `watchlist_groups` table (id, user_id, group_name, created_at, sort_order, stock_count)
   - `user_watchlist` table (id, user_id, group_id, stock_code, stock_name, added_at, notes)
   - Foreign key: user_watchlist.group_id → watchlist_groups.id ON DELETE CASCADE
   - Unique constraints: (user_id, group_name), (user_id, group_id, stock_code)
   - Indexes on: (user_id), (user_id, group_id), (stock_code)
   - Trigger function `update_group_stock_count()` to maintain stock_count
   - Trigger on user_watchlist INSERT/DELETE
   - Insert default group "默认分组" for existing users
3. Wrap entire script in BEGIN/COMMIT transaction

**Reference**: `specs/001-fix-5-critical/research.md` section "PostgreSQL Watchlist Schema Design"

**Success Criteria**: Script is idempotent (can run multiple times safely)

**Estimated Time**: 10 minutes

---

### T003: [BLOCKING] Execute Database Migration [Foundation]
**File**: `web/backend/migrations/001_watchlist_tables.sql`
**Description**: Run migration script to create tables in PostgreSQL
**Dependencies**: T002
**Actions**:
1. Execute migration: `psql -h localhost -U mystocks -d mystocks -f web/backend/migrations/001_watchlist_tables.sql`
2. Verify tables created: `psql -h localhost -U mystocks -d mystocks -c "\dt watchlist*"`
3. Verify default groups inserted: `psql -h localhost -U mystocks -d mystocks -c "SELECT user_id, group_name FROM watchlist_groups;"`
4. Verify trigger created: `psql -h localhost -U mystocks -d mystocks -c "\df update_group_stock_count"`

**Success Criteria**:
- Tables `watchlist_groups` and `user_watchlist` exist
- Default group "默认分组" created for each existing user
- Trigger function exists

**Estimated Time**: 5 minutes

---

## Phase 3: User Story 1 - Add Stocks to Watchlist (P0) (30 min)

**Story Goal**: Users can search for stocks and add them to watchlist groups without "relation does not exist" errors

**Independent Test Criteria**:
1. Search for "茅台" → Results displayed
2. Click "加入自选" on any result → Success message
3. Navigate to watchlist management → Stock appears in group
4. Database query shows stock in `user_watchlist` table

**Priority**: P0 (Blocker)

---

### T004: [US1] Verify WatchlistService Handles New Tables [Story 1]
**File**: `web/backend/app/services/watchlist_service.py`
**Description**: Ensure service methods query the correct tables (watchlist_groups, user_watchlist)
**Dependencies**: T003
**Actions**:
1. Review `get_user_watchlist()` method → Confirm queries `user_watchlist` table
2. Review `get_user_groups()` method → Confirm queries `watchlist_groups` table
3. Review `get_or_create_group()` method → Confirm inserts into `watchlist_groups`
4. Verify datetime serialization helpers are present (from previous fixes)
5. No code changes needed if already correct from previous implementation

**Success Criteria**: All service methods reference correct table names

**Estimated Time**: 10 minutes

---

### T005: [US1] Implement Stock Code Normalization in WatchlistService [Story 1] [P]
**File**: `web/backend/app/services/watchlist_service.py`
**Description**: Add stock code normalization when adding stocks to watchlist
**Dependencies**: T003
**Actions**:
1. Import `normalize_stock_code` function (will be created in T008)
2. In `add_to_watchlist()` method, normalize stock_code before INSERT:
   ```python
   normalized_code = normalize_stock_code(stock_code, market)
   ```
3. Store normalized code (with exchange suffix) in database

**Reference**: `specs/001-fix-5-critical/research.md` section "Stock Code Normalization"

**Success Criteria**: Stock codes stored with exchange suffix (e.g., "600519.SH")

**Estimated Time**: 5 minutes

---

### T006: [US1] Verify Watchlist API Routes Registered [Story 1]
**File**: `web/backend/app/main.py`
**Description**: Ensure watchlist router is registered in FastAPI application
**Dependencies**: T003
**Actions**:
1. Check if `from app.api import watchlist` import exists
2. Check if `app.include_router(watchlist.router, prefix="/api/watchlist", tags=["watchlist"])` exists
3. If missing, add registration
4. Restart backend server to load routes

**Success Criteria**: `/api/watchlist/groups` endpoint accessible (returns 200 or 401, not 404)

**Estimated Time**: 5 minutes

---

### T007: [US1] Manual Test - Add Stock to Watchlist [Story 1]
**File**: N/A (manual testing)
**Description**: Verify end-to-end workflow for adding stocks to watchlist
**Dependencies**: T004, T005, T006
**Actions**:
1. Login to frontend: http://localhost:3000/login
2. Navigate to: http://localhost:3000/openstock-demo
3. In "股票搜索" tab, search for "茅台"
4. Click "加入自选" on first result (should be 贵州茅台 600519)
5. Confirm success message appears
6. Navigate to "自选股管理" tab
7. Verify stock appears in "默认分组"
8. Check database: `psql -h localhost -U mystocks -d mystocks -c "SELECT * FROM user_watchlist;"`

**Success Criteria**:
- No "relation does not exist" errors
- Stock appears in watchlist UI
- Stock record exists in database

**Estimated Time**: 10 minutes

---

**✓ CHECKPOINT: User Story 1 Complete**
- Users can add stocks to watchlist
- Database tables working correctly
- No more "relation does not exist" errors

---

## Phase 4: User Story 2 - Manage Watchlist Groups (P0) (20 min)

**Story Goal**: Users can create, rename, and delete watchlist groups without "Not Found" errors

**Independent Test Criteria**:
1. Click "新建分组" → Enter name "测试分组" → Group appears in list
2. Right-click group → Rename to "价值股" → Name updated
3. Delete empty group → Group removed from list
4. All operations complete without "Not Found" errors

**Priority**: P0 (Blocker)

---

### T008: [US2] Verify Group Management Endpoints Exist [Story 2]
**File**: `web/backend/app/api/watchlist.py`
**Description**: Ensure all group management endpoints are implemented
**Dependencies**: T003
**Actions**:
1. Verify `POST /api/watchlist/groups` endpoint exists (create group)
2. Verify `GET /api/watchlist/groups` endpoint exists (list groups)
3. Verify `PUT /api/watchlist/groups/{group_id}` endpoint exists (rename group)
4. Verify `DELETE /api/watchlist/groups/{group_id}` endpoint exists (delete group)
5. Check all endpoints call appropriate service methods
6. Review error handling for 404 cases

**Reference**: `specs/001-fix-5-critical/contracts/watchlist_api.md`

**Success Criteria**: All 4 endpoints exist and return appropriate HTTP status codes

**Estimated Time**: 10 minutes

---

### T009: [US2] Manual Test - Create and Manage Groups [Story 2]
**File**: N/A (manual testing)
**Description**: Verify group management functionality works end-to-end
**Dependencies**: T008
**Actions**:
1. Navigate to "自选股管理" tab in OpenStock Demo
2. Click "新建分组" button
3. Enter group name "测试分组" and submit
4. Verify group appears in groups list with stock_count = 0
5. Select group and click rename
6. Change name to "价值股" and submit
7. Verify name updated in UI
8. Delete the group (ensure it's empty first)
9. Verify group removed from list

**Success Criteria**:
- Can create groups without "Not Found" errors
- Can rename groups
- Can delete empty groups
- All operations complete successfully

**Estimated Time**: 10 minutes

---

**✓ CHECKPOINT: User Story 2 Complete**
- Users can create watchlist groups
- Groups can be renamed and deleted
- No more "Not Found" errors for group operations

---

## Phase 5: User Story 3 - Real-Time Stock Quotes (P1) (30 min)

**Story Goal**: Users can query stock quotes using 6-digit codes without exchange suffixes, and system auto-detects the correct exchange

**Independent Test Criteria**:
1. Enter "300892" (without .SZ suffix) → Quote data displays successfully
2. Enter "600519" (without .SH suffix) → Quote data displays successfully
3. Enter "300892.SZ" (with suffix) → Quote data displays (backward compatible)
4. Invalid code "600999" → Clear error message "未找到股票报价"

**Priority**: P1 (Important for decision-making)

---

### T010: [US3] Implement Stock Code Normalization Function [Story 3]
**File**: `web/backend/app/services/stock_search_service.py`
**Description**: Create function to auto-detect exchange suffix based on stock code pattern
**Dependencies**: None (independent)
**Actions**:
1. Add `normalize_stock_code(code: str, market: str = "cn") -> str` function
2. Implement first-digit detection logic:
   - 600-603, 688 → .SH (Shanghai)
   - 000-003, 300-301 → .SZ (Shenzhen)
   - Other 6xxx → .SH
   - Other 0xxx, 3xxx → .SZ
3. Validate input format: `^\d{6}(\.(SH|SZ|HK))?$`
4. If code already has suffix, return as-is (idempotent)
5. Raise ValueError for invalid formats

**Reference**: `specs/001-fix-5-critical/research.md` section "Stock Code Normalization & Exchange Detection"

**Success Criteria**: Function correctly maps all test codes to exchanges

**Estimated Time**: 10 minutes

---

### T011: [US3] Update Quote API to Use Normalization [Story 3]
**File**: `web/backend/app/api/stock_search.py` (and underlying service)
**Description**: Integrate stock code normalization into quote retrieval
**Dependencies**: T010
**Actions**:
1. In `get_stock_quote()` endpoint handler, call `normalize_stock_code(stock_code, market)`
2. Use normalized code for AKShare query (remove suffix for akshare: `code.split('.')[0]`)
3. Return normalized code in response `symbol` field
4. Update error handling:
   - ValueError (invalid format) → 400 Bad Request
   - Not found in akshare → 404 with "未找到股票报价: {code} 不存在或数据源暂未提供报价"
   - AKShare error → 500 with "数据源暂时不可用，请稍后重试"

**Reference**: `specs/001-fix-5-critical/contracts/quote_api.md`

**Success Criteria**: Quote API accepts codes with or without exchange suffix

**Estimated Time**: 10 minutes

---

### T012: [US3] Manual Test - Quote with Auto-Detection [Story 3]
**File**: N/A (manual testing)
**Description**: Verify auto-detection works for various stock code formats
**Dependencies**: T011
**Actions**:
1. Navigate to "实时行情" tab
2. Test case 1: Enter "300892" → Click "查询行情"
   - Expected: Quote displays, symbol shows "300892.SZ"
3. Test case 2: Enter "600519" → Click "查询行情"
   - Expected: Quote displays, symbol shows "600519.SH"
4. Test case 3: Enter "000858" → Click "查询行情"
   - Expected: Quote displays, symbol shows "000858.SZ"
5. Test case 4: Enter "600999" (invalid) → Click "查询行情"
   - Expected: Error message "未找到股票报价"
6. Test case 5: Enter "600519.SH" (with suffix) → Click "查询行情"
   - Expected: Quote displays (backward compatible)

**Success Criteria**: All test cases pass with correct exchange detection

**Estimated Time**: 10 minutes

---

**✓ CHECKPOINT: User Story 3 Complete**
- Stock quotes work with or without exchange suffix
- Auto-detection correctly identifies Shanghai vs Shenzhen
- Clear error messages for invalid codes

---

## Phase 6: User Story 4 - K-Line Charts (P2) (40 min)

**Story Goal**: Users can view historical K-line (candlestick) charts for stocks with configurable time periods

**Independent Test Criteria**:
1. Enter stock code "600519" → Click "加载图表" → Chart displays with candlesticks
2. Chart shows last 60 trading days by default
3. Volume bars appear below price chart
4. Red candles for price increases, green for decreases (Chinese convention)
5. Can select different time periods (if frontend supports)

**Priority**: P2 (Enhancement)

---

### T013: [US4] Implement K-Line Data Fetching Service Method [Story 4]
**File**: `web/backend/app/services/stock_search_service.py` (or create new `market_service.py`)
**Description**: Create async service method to fetch K-line data from AKShare
**Dependencies**: T010 (uses normalize_stock_code)
**Actions**:
1. Add method `async def get_kline_data(stock_code, period="daily", adjust="qfq", start_date=None, end_date=None)`
2. Normalize stock code using `normalize_stock_code()`
3. Set default date range: last 180 days if not provided
4. Use `asyncio.get_event_loop().run_in_executor()` to call synchronous akshare function:
   ```python
   df = ak.stock_zh_a_hist(symbol=code.split('.')[0], period=period, start_date=..., end_date=..., adjust=adjust)
   ```
5. Transform DataFrame to list of dicts with fields: date, timestamp, open, high, low, close, volume, amount, amplitude, change_percent
6. Fetch stock name from spot data
7. Return dict with: stock_code, stock_name, period, adjust, data (list), count

**Reference**: `specs/001-fix-5-critical/research.md` section "AKShare API Integration Patterns"

**Success Criteria**: Method returns properly formatted K-line data

**Estimated Time**: 15 minutes

---

### T014: [US4] Create K-Line API Endpoint [Story 4]
**File**: `web/backend/app/api/market.py`
**Description**: Add GET /api/market/kline endpoint
**Dependencies**: T013
**Actions**:
1. Add `@router.get("/kline")` endpoint
2. Query parameters: stock_code (required), period (default "daily"), adjust (default "qfq"), start_date (optional), end_date (optional)
3. Validate period: must be "daily", "weekly", or "monthly" → 400 if invalid
4. Call service method from T013
5. Handle errors:
   - Invalid stock code format → 400
   - Stock not found → 404 with "股票代码 {code} 不存在或暂无K线数据"
   - Empty DataFrame → 422 with "该股票历史数据不足10个交易日"
   - AKShare error → 500 with "数据源暂时不可用"
6. Return JSON response with stock_code, stock_name, period, adjust, data, count

**Reference**: `specs/001-fix-5-critical/contracts/kline_api.md`

**Success Criteria**: Endpoint accessible and returns K-line data in correct format

**Estimated Time**: 15 minutes

---

### T015: [US4] Verify Market Router Registered [Story 4]
**File**: `web/backend/app/main.py`
**Description**: Ensure market router (with kline endpoint) is registered
**Dependencies**: T014
**Actions**:
1. Check if `from app.api import market` exists
2. Check if `app.include_router(market.router, prefix="/api/market", tags=["market"])` exists
3. If missing, add registration
4. Restart backend server

**Success Criteria**: `/api/market/kline` endpoint accessible (not 404)

**Estimated Time**: 5 minutes

---

### T016: [US4] Manual Test - K-Line Chart Display [Story 4]
**File**: N/A (manual testing + frontend verification)
**Description**: Verify K-line chart loads and displays correctly
**Dependencies**: T015
**Actions**:
1. Navigate to "K线图表" tab
2. Enter stock code "600519"
3. Click "加载图表" button
4. Verify:
   - Chart area displays (not blank)
   - Candlesticks visible with red (up) and green (down) colors
   - Volume bars appear below price chart
   - X-axis shows dates (MM-DD format)
   - Y-axis shows prices
   - Can hover over candles to see OHLC values
5. Test with different stock codes (300750, 000858)
6. Verify error handling for invalid codes

**Success Criteria**:
- Chart displays correctly with Chinese color conventions
- No "接口未实现" errors
- Data loads within 5 seconds

**Estimated Time**: 10 minutes

---

**✓ CHECKPOINT: User Story 4 Complete**
- K-line endpoint implemented and working
- Charts display historical price data
- Frontend can visualize candlestick patterns

---

## Phase 7: User Story 5 - Test API Functionality (P2) (25 min)

**Story Goal**: Users can test all OpenStock APIs via UI buttons to verify system health

**Independent Test Criteria**:
1. "测试状态" tab displays list of 5 APIs
2. Each API row has a "Test" button
3. Clicking "Test" executes real API call and shows result
4. Pass/Fail status displayed with visual indicators (✓/✗)
5. Error messages shown for failed tests

**Priority**: P2 (Quality assurance feature)

---

### T017: [US5] Add Test Button Handlers in Frontend [Story 5]
**File**: `web/frontend/src/views/OpenStockDemo.vue`
**Description**: Implement test button click handlers that execute real API calls
**Dependencies**: T007, T009, T012, T016 (APIs must be working)
**Actions**:
1. Add reactive state for test results:
   ```javascript
   const testStatus = ref({ search: 'pending', quote: 'pending', news: 'pending', watchlist: 'pending', kline: 'pending' });
   const testErrors = ref({});
   ```
2. Create `testAPI(apiName)` async function:
   - Set status to 'testing'
   - Execute API call with sample data based on apiName:
     - search: `/api/stock-search/search?q=茅台&market=cn`
     - quote: `/api/stock-search/quote/600519?market=cn`
     - news: `/api/stock-search/news/600519?market=cn`
     - watchlist: `/api/watchlist/groups`
     - kline: `/api/market/kline?stock_code=600519&period=daily`
   - Get token from localStorage: `getToken()`
   - Include Authorization header: `Bearer ${token}`
   - On success: Set status to 'pass'
   - On error: Set status to 'fail', store error message
3. Add error handling for network failures, 401 Unauthorized, etc.

**Reference**: `specs/001-fix-5-critical/research.md` section "Frontend Test Button Implementation"

**Success Criteria**: Function executes API calls and updates status

**Estimated Time**: 15 minutes

---

### T018: [US5] Update Test Status UI with Buttons [Story 5]
**File**: `web/frontend/src/views/OpenStockDemo.vue`
**Description**: Add "Test" buttons and status indicators to test status table
**Dependencies**: T017
**Actions**:
1. Locate test status table in "测试状态" tab
2. Add "操作" column with button:
   ```vue
   <el-button
     size="small"
     :type="testStatus[row.api] === 'pass' ? 'success' : 'primary'"
     :loading="testStatus[row.api] === 'testing'"
     @click="testAPI(row.api)"
   >
     <span v-if="testStatus[row.api] === 'pass'">✓ Pass</span>
     <span v-else-if="testStatus[row.api] === 'fail'">✗ Retry</span>
     <span v-else>Test</span>
   </el-button>
   ```
3. Add "Status" column with tag:
   ```vue
   <el-tag :type="testStatus[row.api] === 'pass' ? 'success' : testStatus[row.api] === 'fail' ? 'danger' : 'info'">
     {{ testStatus[row.api] }}
   </el-tag>
   ```
4. Show error details below table if any test fails

**Success Criteria**: Buttons visible, status indicators update on click

**Estimated Time**: 10 minutes

---

### T019: [US5] Manual Test - All API Tests [Story 5]
**File**: N/A (manual testing)
**Description**: Verify all test buttons work and show correct status
**Dependencies**: T018
**Actions**:
1. Navigate to "测试状态" tab
2. Ensure user is logged in (check for auth warning)
3. Click "Test" button for "股票搜索API"
   - Expected: Button shows loading, then "✓ Pass", status tag shows "pass"
4. Click "Test" button for "实时行情API"
   - Expected: Pass (if AKShare accessible)
5. Click "Test" button for "股票新闻API"
   - Expected: Pass or appropriate error
6. Click "Test" button for "自选股管理API"
   - Expected: Pass (lists watchlist groups)
7. Click "Test" button for "K线图表API"
   - Expected: Pass (returns K-line data)
8. If any test fails, verify error message is displayed

**Success Criteria**:
- All 5 test buttons functional
- Status indicators update correctly
- Pass/Fail clearly displayed
- No console errors

**Estimated Time**: 10 minutes

---

**✓ CHECKPOINT: User Story 5 Complete**
- Test buttons implemented for all APIs
- Users can verify system health via UI
- Self-service troubleshooting tool functional

---

## Phase 8: Polish & Integration (15 min)

**Goal**: Cross-cutting concerns and final verification

---

### T020: [Polish] Review and Update Error Messages [Cross-Cutting]
**File**: Multiple files (all API endpoints)
**Description**: Ensure all error messages are user-friendly and in Chinese
**Dependencies**: All previous tasks
**Actions**:
1. Review error messages in:
   - `web/backend/app/api/watchlist.py`
   - `web/backend/app/api/stock_search.py`
   - `web/backend/app/api/market.py`
2. Verify Chinese error messages for:
   - "未找到股票报价"
   - "无效的股票代码格式"
   - "数据源暂时不可用，请稍后重试"
   - "relation does not exist" → Should never appear (fixed by migration)
3. Ensure 400/404/500 status codes used appropriately
4. Add context to error messages (e.g., include stock code in message)

**Success Criteria**: All error messages clear and user-friendly

**Estimated Time**: 10 minutes

---

### T021: [Polish] Add Backend Logging for Key Operations [Cross-Cutting] [P]
**File**: Multiple files (service and API layers)
**Description**: Add logging statements for debugging and monitoring
**Dependencies**: None (can run in parallel with T020)
**Actions**:
1. Add logger imports: `from app.core.logging import logger` (or structlog)
2. Log key events:
   - Watchlist operations: "User {user_id} added stock {code} to group {group_id}"
   - Quote queries: "Fetching quote for {normalized_code}"
   - K-line requests: "Fetching K-line for {code}, period={period}"
   - Errors: "AKShare failed for {code}: {error_message}"
3. Use appropriate log levels (INFO for operations, ERROR for failures)
4. Don't log sensitive data (passwords, full tokens)

**Success Criteria**: Key operations logged without performance impact

**Estimated Time**: 10 minutes

---

### T022: [Integration] End-to-End Smoke Test [Cross-Cutting]
**File**: N/A (manual testing)
**Description**: Verify complete workflow from search to watchlist to charts
**Dependencies**: All user story tasks
**Actions**:
1. Start fresh browser session (clear localStorage)
2. Login to application
3. Navigate to OpenStock Demo page
4. **Workflow Test**:
   a. Search for "茅台" → Verify results
   b. Add 贵州茅台 to watchlist → Verify success
   c. Create new group "测试组" → Verify created
   d. Move stock to "测试组" (if supported) or add another stock
   e. Query real-time quote for "600519" → Verify displays
   f. Load K-line chart for "600519" → Verify chart displays
   g. Run all 5 API tests → Verify all pass
5. Check browser console for errors
6. Check backend logs for errors

**Success Criteria**:
- Complete workflow executes without errors
- All 5 critical issues resolved
- No "relation does not exist" errors
- No "接口未实现" errors
- No "Not Found" errors for valid operations

**Estimated Time**: 15 minutes

---

### T023: [Documentation] Update README or CHANGELOG [Cross-Cutting] [P]
**File**: `CHANGELOG.md` or `web/README.md`
**Description**: Document the fixes made in this feature
**Dependencies**: T022 (after verification complete)
**Actions**:
1. Add entry to CHANGELOG.md:
   ```markdown
   ## [Version] - 2025-01-20
   ### Fixed
   - Fixed missing watchlist database tables causing "relation does not exist" errors
   - Implemented automatic exchange suffix detection for stock codes
   - Fixed watchlist group management returning "Not Found" errors
   - Implemented K-line chart API endpoint
   - Added test buttons for API functionality verification
   ```
2. Update web/README.md if setup instructions changed
3. No need to create new documentation files (per project guidelines)

**Success Criteria**: Changes documented in appropriate files

**Estimated Time**: 5 minutes

---

### T024: [Deployment] Create Pull Request [Cross-Cutting]
**File**: N/A (Git operations)
**Description**: Prepare feature for code review and merge
**Dependencies**: T022, T023
**Actions**:
1. Review all changed files: `git status`
2. Stage all changes: `git add .`
3. Create commit with descriptive message:
   ```bash
   git commit -m "Fix 5 critical OpenStock Demo issues

   - Create watchlist database tables (watchlist_groups, user_watchlist)
   - Implement stock code normalization with auto-detection
   - Fix watchlist group management APIs
   - Implement K-line chart endpoint (GET /api/market/kline)
   - Add test buttons for API functionality verification

   Resolves: #001-fix-5-critical

   🤖 Generated with Claude Code
   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```
4. Push to remote: `git push origin 001-fix-5-critical`
5. Create pull request via GitHub/GitLab (or use `gh pr create` if available)
6. Add PR description from spec.md summary
7. Request code review from team

**Success Criteria**: Pull request created and ready for review

**Estimated Time**: 10 minutes

---

## Task Dependencies

### Critical Path (Sequential)
```
T001 (Verify) → T002 (Migration Script) → T003 (Execute Migration) → [All User Stories]
```

### User Story Dependencies

**Phase 3 (US1 - Watchlist)**: Sequential within story
```
T003 → T004 → T005 → T006 → T007
       T004 [P] T005 (different files, can parallelize)
```

**Phase 4 (US2 - Groups)**: Sequential within story
```
T003 → T008 → T009
```

**Phase 5 (US3 - Quotes)**: Sequential within story
```
T010 → T011 → T012
```

**Phase 6 (US4 - K-Line)**: Mostly sequential
```
T010 → T013 → T014 → T015 → T016
```

**Phase 7 (US5 - Tests)**: Depends on all APIs working
```
T007, T009, T012, T016 → T017 → T018 → T019
```

**Phase 8 (Polish)**: Can run in parallel after user stories
```
All User Stories → T020 [P] T021 → T022 → T023 → T024
```

### Parallelization Opportunities

**After T003 (Migration)**:
- T004, T005 (different files in same service) [P]
- T010 (completely independent) [P]

**Polish Phase**:
- T020, T021 (different files) [P]

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)
**User Story 1 (P0)** only:
- Tasks: T001, T002, T003, T004, T005, T006, T007
- **Estimated Time**: 1 hour
- **Deliverable**: Users can add stocks to watchlist without database errors

### Phase 1 Release (P0 Issues)
**User Stories 1 & 2**:
- Tasks: T001-T009
- **Estimated Time**: 1.5 hours
- **Deliverable**: Complete watchlist management functionality

### Phase 2 Release (All Issues)
**All User Stories (P0, P1, P2)**:
- Tasks: T001-T024
- **Estimated Time**: 2-3 hours
- **Deliverable**: All 5 critical issues fixed and production-ready

---

## Testing Summary

**Manual Tests** (No automated tests per spec.md):
- T007: Add stock to watchlist
- T009: Create and manage groups
- T012: Quote with auto-detection
- T016: K-line chart display
- T019: All API tests
- T022: End-to-end smoke test

**Automated Tests**: None generated (not requested in spec.md)

---

## Success Metrics

After completing all tasks, verify:

1. ✅ **User Story 1**: Can add stocks to watchlist without "relation does not exist" errors
2. ✅ **User Story 2**: Can create/rename/delete watchlist groups without "Not Found" errors
3. ✅ **User Story 3**: Can query quotes using 6-digit codes (auto-detection working)
4. ✅ **User Story 4**: K-line charts load and display correctly
5. ✅ **User Story 5**: All 5 API test buttons show "Pass" status

**Performance Targets**:
- Watchlist operations: < 1 second
- Quote queries: < 3 seconds
- K-line loading: < 5 seconds
- API tests: < 10 seconds total

---

## Rollback Plan

If issues occur after deployment:

1. **Database rollback**:
   ```sql
   BEGIN;
   DROP TRIGGER IF EXISTS trg_update_stock_count ON user_watchlist;
   DROP FUNCTION IF EXISTS update_group_stock_count();
   DROP TABLE IF EXISTS user_watchlist CASCADE;
   DROP TABLE IF EXISTS watchlist_groups CASCADE;
   COMMIT;
   ```

2. **Code rollback**: Revert to previous commit
   ```bash
   git revert HEAD
   git push origin 001-fix-5-critical
   ```

3. **Frontend rollback**: Deploy previous frontend build

---

## Notes

- **No Test Tasks**: Tests not explicitly requested in spec.md, so no automated test tasks generated
- **Parallel Execution**: Limited opportunities due to sequential dependencies within stories
- **Independent Stories**: US3, US4, US5 are largely independent after foundation (T003)
- **MVP First**: Recommend implementing P0 stories (US1, US2) before P1/P2
- **Time Estimates**: Based on experienced developer; adjust for your team

---

**Ready to implement!** Start with T001 and proceed sequentially through each phase.
