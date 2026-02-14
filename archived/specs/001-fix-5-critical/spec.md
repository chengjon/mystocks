# Feature Specification: Fix 5 Critical Issues in OpenStock Demo

**Feature Branch**: `001-fix-5-critical`
**Created**: 2025-10-20
**Status**: Draft
**Input**: User description: "Fix 5 critical issues in OpenStock Demo page: watchlist database tables, real-time quote API, watchlist group management, K-line chart API, and test buttons"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add Stocks to Watchlist (Priority: P0)

A logged-in user searches for a stock and wants to add it to their watchlist for easy tracking. After finding the desired stock in search results, they click "Add to Watchlist" and expect the stock to be saved successfully.

**Why this priority**: This is a core workflow blocker. Currently fails with database error "relation watchlist_groups does not exist", preventing users from using the primary feature of stock management.

**Independent Test**: Can be fully tested by logging in, searching for any stock (e.g., "茅台"), and clicking "Add to Watchlist". Success means stock appears in watchlist without errors.

**Acceptance Scenarios**:

1. **Given** user is logged in and searches for a stock, **When** user clicks "Add to Watchlist" on search result, **Then** stock is added to default watchlist group successfully
2. **Given** user has existing watchlist groups, **When** user adds a stock, **Then** system uses default group or prompts user to select group
3. **Given** stock is already in watchlist, **When** user tries to add it again, **Then** system shows friendly message indicating stock already exists

---

### User Story 2 - Manage Watchlist Groups (Priority: P0)

A user wants to organize their watchlist by creating custom groups (e.g., "Tech Stocks", "Value Stocks"). They navigate to watchlist management, click "New Group", enter a group name, and expect the group to be created successfully.

**Why this priority**: Core functionality blocker. Currently fails with "Not Found" error, preventing users from organizing their stocks.

**Independent Test**: Can be fully tested by logging in, going to Watchlist Management tab, clicking "New Group", entering name "Test Group", and verifying group appears in the list.

**Acceptance Scenarios**:

1. **Given** user is in Watchlist Management tab, **When** user clicks "New Group" and enters group name, **Then** new group is created and appears in group list
2. **Given** user has existing groups, **When** user creates a new group, **Then** new group appears with 0 stocks initially
3. **Given** user enters duplicate group name, **When** user tries to create group, **Then** system shows validation message about duplicate name

---

### User Story 3 - View Real-Time Stock Quotes (Priority: P1)

A user wants to check current price information for a specific stock. They enter a stock code (e.g., "300892") in the Real-Time Quote tab and click "Query Quote", expecting to see current price, change percentage, and other market data.

**Why this priority**: Important for decision-making but not a complete blocker since users can still search and add stocks. Currently fails with "未找到股票报价" error.

**Independent Test**: Can be fully tested by logging in, going to Real-Time Quote tab, entering stock code "600519" or "300892", and verifying price data displays correctly.

**Acceptance Scenarios**:

1. **Given** user enters valid A-share stock code (e.g., "600519"), **When** user clicks "Query Quote", **Then** system displays current price, change, high, low, volume
2. **Given** user enters stock code without exchange suffix, **When** user queries quote, **Then** system auto-detects and adds appropriate exchange suffix
3. **Given** user enters invalid or non-existent stock code, **When** user queries quote, **Then** system shows user-friendly error message explaining the issue

---

### User Story 4 - View Stock K-Line Charts (Priority: P2)

A user wants to analyze stock price trends using K-line (candlestick) charts. They enter a stock code in the K-Line Chart tab, click "Load Chart", and expect to see historical price data visualized as candlesticks with volume bars.

**Why this priority**: Enhancement feature for technical analysis. Less critical than core watchlist and quote functionalities. Currently returns "接口未实现" message.

**Independent Test**: Can be fully tested by logging in, going to K-Line Chart tab, entering stock code, and verifying chart loads with proper candlesticks and time periods.

**Acceptance Scenarios**:

1. **Given** user enters valid stock code, **When** user clicks "Load Chart", **Then** system displays K-line chart with last 60 trading days of data
2. **Given** chart is loaded, **When** user selects different time period (1 day, 1 week, 1 month), **Then** chart updates to show selected period
3. **Given** stock has no historical data, **When** user loads chart, **Then** system shows message indicating insufficient data

---

### User Story 5 - Test API Functionality (Priority: P2)

A developer or power user wants to verify that all OpenStock APIs are functioning correctly. They navigate to the Test Status tab and want to click "Test" buttons for each API to see real-time test results (pass/fail status).

**Why this priority**: Quality assurance feature for verifying system health. Less critical than user-facing features but important for debugging and monitoring.

**Independent Test**: Can be fully tested by logging in, going to Test Status tab, clicking each "Test" button, and verifying status updates to show test results.

**Acceptance Scenarios**:

1. **Given** user is in Test Status tab, **When** user clicks "Test" button for any API, **Then** system executes test and shows result (✓ Pass or ✗ Fail)
2. **Given** API test is running, **When** test is in progress, **Then** button shows loading state and is disabled
3. **Given** all tests complete, **When** user views results, **Then** system shows summary of total passed/failed tests

---

### Edge Cases

- What happens when database connection fails during watchlist operations?
- How does system handle stock codes with special characters or invalid formats?
- What happens when user tries to create a group while offline?
- How does system behave when market data API (AKShare) is unavailable?
- What happens when user tries to load K-line chart for stock with < 10 days of data?
- How does system handle concurrent group creation with same name by same user?

## Requirements *(mandatory)*

### Functional Requirements

**Database & Data Persistence**:

- **FR-001**: System MUST ensure watchlist_groups table exists in PostgreSQL database with required columns (id, user_id, group_name, created_at, sort_order, stock_count)
- **FR-002**: System MUST ensure user_watchlist table exists in PostgreSQL database with required columns (id, user_id, group_id, stock_code, stock_name, added_at)
- **FR-003**: System MUST create default watchlist group "默认分组" for each user automatically

**Watchlist Management**:

- **FR-004**: Users MUST be able to create new watchlist groups with custom names (max 100 characters)
- **FR-005**: Users MUST be able to add stocks to watchlist groups via search results
- **FR-006**: System MUST validate stock codes before adding to watchlist
- **FR-007**: System MUST prevent duplicate stocks within same watchlist group
- **FR-008**: Users MUST be able to view all their watchlist groups with stock counts

**Real-Time Quotes**:

- **FR-009**: System MUST accept stock codes with or without exchange suffixes (e.g., "300892" or "300892.SZ")
- **FR-010**: System MUST auto-detect exchange for A-share codes (600xxx=SH, 000xxx/002xxx/300xxx=SZ)
- **FR-011**: System MUST fetch real-time quotes from AKShare for valid stock codes
- **FR-012**: System MUST display current price, change amount, change percentage, high, low, open, previous close, volume, and amount
- **FR-013**: System MUST show user-friendly error messages for invalid stock codes or unavailable data

**K-Line Charts**:

- **FR-014**: System MUST implement GET /api/market/kline endpoint accepting stock_code and period parameters
- **FR-015**: System MUST fetch historical K-line data from AKShare (daily frequency minimum)
- **FR-016**: System MUST return data in format compatible with frontend chart library (timestamp, open, high, low, close, volume)
- **FR-017**: System MUST support time periods: 1 day, 5 days, 1 month, 3 months, 6 months, 1 year
- **FR-018**: System MUST handle stocks with insufficient historical data gracefully

**API Testing**:

- **FR-019**: System MUST provide "Test" button for each API in Test Status tab (Search, Quote, News, Watchlist, K-Line)
- **FR-020**: Each test button MUST execute actual API call with sample data and display result
- **FR-021**: System MUST show loading state during test execution
- **FR-022**: System MUST display test results as Pass (✓) or Fail (✗) with error details if failed
- **FR-023**: System MUST update API status indicators based on test results

### Key Entities

- **Watchlist Group**: User-created categories for organizing stocks. Attributes: group name, creation date, stock count, sort order
- **Watchlist Item**: Individual stock saved in a watchlist group. Attributes: stock code, stock name, date added, group association
- **Stock Quote**: Real-time market data for a stock. Attributes: current price, price change, volume, timestamp, trading status
- **K-Line Data Point**: Historical price data for one trading period. Attributes: date/time, opening price, high price, low price, closing price, volume

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully add stocks to watchlist without database errors (100% success rate for valid operations)
- **SC-002**: Users can create and manage watchlist groups with < 2 second response time
- **SC-003**: Real-time quote queries return results within 3 seconds for valid stock codes
- **SC-004**: K-line charts load and display within 5 seconds for 60-day period
- **SC-005**: All 5 API test buttons execute and return results within 10 seconds
- **SC-006**: 90% of valid stock code queries (both with and without exchange suffixes) return correct data
- **SC-007**: Zero "relation does not exist" database errors after deployment
- **SC-008**: Test Status tab provides immediate visual feedback (pass/fail) for each API

### User Experience Goals

- **UX-001**: Users can complete "search → add to watchlist" workflow in under 30 seconds
- **UX-002**: Error messages clearly explain the problem and suggest corrective actions
- **UX-003**: All features work consistently whether user enters stock code with or without exchange suffix
- **UX-004**: Test Status tab serves as self-service troubleshooting tool for users

## Assumptions

- PostgreSQL database is the primary data store (MySQL, TDengine, Redis removed per Week 3 simplification)
- AKShare library is installed and functional for market data retrieval
- User authentication (JWT tokens) is already working correctly
- Frontend chart library (likely ECharts or similar) is already integrated for K-line display
- Stock codes follow standard Chinese market conventions (6-digit codes with optional exchange suffixes)
- System targets logged-in users only (authentication required for all operations)

## Dependencies

- PostgreSQL database server must be running and accessible
- AKShare library must have network access to fetch market data
- Frontend must have valid authentication token in localStorage
- Backend API server must be running on port 8000
- Frontend development server must be running on port 3000

## Out of Scope

- Real-time streaming quotes (WebSocket-based continuous updates)
- Advanced charting features (technical indicators beyond basic K-line)
- Bulk import/export of watchlists
- Watchlist sharing between users
- Mobile app support (web interface only)
- Support for US stocks or other international markets
- Historical performance analytics or backtesting

## Non-Functional Requirements

### Performance

- Database queries must return within 1 second for typical operations (< 100 watchlist items)
- API endpoints must handle at least 10 concurrent users without degradation
- K-line chart data must not exceed 5 MB per request

### Reliability

- System must handle AKShare API failures gracefully with retry logic (3 attempts)
- Database connection pool must recover automatically from temporary network issues
- All user operations must be atomic (all-or-nothing) to prevent data corruption

### Security

- All API endpoints must require valid authentication tokens
- Database queries must use parameterized statements to prevent SQL injection
- User can only access their own watchlist data (enforced by user_id filtering)

### Maintainability

- Database schema changes must include migration scripts
- All error messages must be logged with contextual information for debugging
- API endpoints must follow existing project conventions (FastAPI, /api prefix)
