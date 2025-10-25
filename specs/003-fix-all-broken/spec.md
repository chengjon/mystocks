# Feature Specification: Fix All Broken Web Features

**Feature Branch**: `003-fix-all-broken`
**Created**: 2025-10-25
**Status**: Draft
**Input**: User description: "Fix all broken features in MyStocks web application based on code review - Dashboard mock data, missing API integrations, MySQL migration cleanup, broken pages"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Real-time Market Data on Dashboard (Priority: P1)

As a quantitative trader, I need to see real-time market data and my actual portfolio on the dashboard so I can make informed trading decisions based on current market conditions and my real holdings.

**Why this priority**: Dashboard is the primary landing page and currently shows only fake data. Without real data, the entire system provides zero value to users. This is the foundation that all other features build upon.

**Independent Test**: Can be fully tested by logging in and verifying that Dashboard shows actual stock data from the database (not hardcoded values). Delivers immediate value by providing visibility into real market conditions.

**Acceptance Scenarios**:

1. **Given** I am logged into MyStocks, **When** I navigate to the Dashboard, **Then** I see my actual favorite stocks with current prices (not mock data like "600519 贵州茅台")
2. **Given** I am viewing the Dashboard, **When** I click the refresh button, **Then** the stock prices update with current market data from the database
3. **Given** I am viewing strategy-matched stocks, **When** the data loads, **Then** I see stocks that actually match my configured strategies (not hardcoded "002594 比亚迪")
4. **Given** I am viewing industry stocks, **When** I select "科技" industry, **Then** I see real stocks from that industry pulled from the database
5. **Given** I am viewing the fund flow chart, **When** the page loads, **Then** I see actual fund flow data by industry (not static mock data)

---

### User Story 2 - Access Working Market Data Features (Priority: P1)

As a trader, I need all market data features (龙虎榜, ETF, 资金流向, 竞价抢筹) to work properly so I can analyze market sentiment and capital flows across different dimensions.

**Why this priority**: Market data features are core to quantitative trading analysis. Currently 4 major market data tables don't work due to database migration issues. These features directly support trading decisions.

**Independent Test**: Can be tested by navigating to each market data panel and verifying data loads from the database. Delivers value by providing multiple angles of market analysis.

**Acceptance Scenarios**:

1. **Given** I navigate to 龙虎榜 (Dragon Tiger List), **When** the panel loads, **Then** I see actual dragon-tiger trading data from the database
2. **Given** I navigate to ETF data panel, **When** the panel loads, **Then** I see real ETF holdings and performance data
3. **Given** I navigate to 资金流向 (Fund Flow), **When** the panel loads, **Then** I see actual capital flow by sector and individual stocks
4. **Given** I navigate to 竞价抢筹 (Chip Race), **When** the panel loads, **Then** I see real auction bidding data
5. **Given** any market data feature encounters an error, **When** the error occurs, **Then** I see a helpful error message (not database connection failures)

---

### User Story 3 - Manage Custom Indicators (Priority: P2)

As a quantitative analyst, I need to save and manage my custom technical indicators so I can reuse my analysis configurations across different stocks and time periods.

**Why this priority**: Indicator configuration is currently broken due to database migration issues. This feature supports advanced users who create custom analysis tools.

**Independent Test**: Can be tested by creating a custom indicator configuration and verifying it's saved and retrievable. Delivers value by enabling repeatable analysis workflows.

**Acceptance Scenarios**:

1. **Given** I create a custom MACD indicator with specific parameters, **When** I save it, **Then** the configuration is persisted and appears in my saved indicators list
2. **Given** I have saved indicator configurations, **When** I navigate to the indicator library, **Then** I see all my saved configurations
3. **Given** I select a saved indicator, **When** I apply it to a stock chart, **Then** the indicator renders with my saved parameters
4. **Given** I want to delete an indicator configuration, **When** I delete it, **Then** it's removed from the database and no longer appears

---

### User Story 4 - Use Complete Feature Set or Remove Placeholder Pages (Priority: P3)

As a user, I need either working implementations of all advertised features or clear indication that features are under development, so I don't waste time trying to use broken pages.

**Why this priority**: Currently 4 major pages (Market, BacktestAnalysis, RiskMonitor, RealTimeMonitor) are blank "under construction" placeholders. This creates poor user experience but doesn't block core trading functionality.

**Independent Test**: Can be tested by navigating to each page and verifying it either works fully or is clearly marked as "coming soon" with alternative workflows provided.

**Acceptance Scenarios**:

1. **Given** I navigate to the Market page, **When** the page loads, **Then** I either see working market data OR a clear message about feature availability with a link to alternative features
2. **Given** I navigate to BacktestAnalysis, **When** the page loads, **Then** I either can run backtests OR see a roadmap of when this will be available
3. **Given** I navigate to RiskMonitor, **When** the page loads, **Then** I either see risk metrics OR understand what alternative monitoring options exist
4. **Given** I access the navigation menu, **When** I view available features, **Then** unavailable features are clearly marked with a badge (e.g., "Coming Soon", "Beta")

---

### User Story 5 - Authenticate and Access Personalized Data (Priority: P2)

As a user, I need a working authentication system so I can securely access my personalized trading data and configurations.

**Why this priority**: Authentication is partially working but the token refresh mechanism and session management need fixes. This affects security and user experience across all features.

**Independent Test**: Can be tested by logging in, using the system for an extended period, and verifying the session remains valid without unexpected logouts.

**Acceptance Scenarios**:

1. **Given** I enter valid credentials, **When** I click login, **Then** I am authenticated and redirected to the Dashboard
2. **Given** I am logged in, **When** my session approaches expiration, **Then** my session is automatically refreshed without interrupting my work
3. **Given** I am logged in, **When** I close the browser and return later, **Then** I can either auto-login (if "remember me") or am prompted to re-authenticate
4. **Given** I enter invalid credentials, **When** I attempt to login, **Then** I see a clear error message without technical details
5. **Given** I am inactive for an extended period, **When** the session expires, **Then** I see a friendly message and can easily re-authenticate

---

### Edge Cases

- What happens when the database connection fails while loading Dashboard data? (Should show cached data with a warning banner, not crash the page)
- How does the system handle concurrent users trying to save indicator configurations with the same name? (Should either auto-increment name or show conflict resolution UI)
- What happens when market data APIs are temporarily unavailable? (Should fall back to last known good data with a freshness indicator)
- How does the system behave when a user's favorite stocks list is empty? (Should show an empty state with helpful guidance on adding stocks)
- What happens when a strategy matches zero stocks? (Should show "No matches" with suggestions to adjust strategy parameters)
- How does the system handle users accessing placeholder pages directly via URL? (Should redirect to working pages or show informative placeholder)

## Requirements *(mandatory)*

### Functional Requirements

#### Dashboard & Data Display (P1)

- **FR-001**: System MUST display actual stock data from the database on the Dashboard, not hardcoded mock values
- **FR-002**: System MUST show user's actual favorite stocks when the favorites table is loaded
- **FR-003**: System MUST display stocks that match saved strategies when the strategy results table is loaded
- **FR-004**: System MUST fetch and display real industry-filtered stocks when users select an industry
- **FR-005**: System MUST show actual fund flow data by industry on the fund flow chart
- **FR-006**: System MUST update all Dashboard data when the user clicks the refresh button

#### Market Data Features (P1)

- **FR-007**: System MUST display dragon-tiger list (龙虎榜) data from the PostgreSQL database
- **FR-008**: System MUST show ETF holdings and performance data
- **FR-009**: System MUST display capital flow (资金流向) by sector and individual stocks
- **FR-010**: System MUST show auction bidding (竞价抢筹) data
- **FR-011**: System MUST handle all market data queries without MySQL dependency errors

#### Indicator Management (P2)

- **FR-012**: System MUST allow users to save custom indicator configurations to the database
- **FR-013**: System MUST retrieve and display all saved indicator configurations for a user
- **FR-014**: System MUST allow users to update existing indicator configurations
- **FR-015**: System MUST allow users to delete indicator configurations
- **FR-016**: System MUST validate indicator parameters before saving

#### Authentication & Session Management (P2)

- **FR-017**: System MUST authenticate users with valid credentials
- **FR-018**: System MUST automatically refresh user sessions before expiration
- **FR-019**: System MUST handle session expiration gracefully with re-authentication prompts
- **FR-020**: System MUST provide clear error messages for authentication failures
- **FR-021**: System MUST maintain user session state across page navigations

#### Placeholder Pages (P3)

- **FR-022**: System MUST either implement working functionality for placeholder pages OR clearly mark them as unavailable
- **FR-023**: System MUST provide alternative workflows or links when features are unavailable
- **FR-024**: System MUST indicate feature status (Working, Beta, Coming Soon) in navigation menus

#### Error Handling (P1)

- **FR-025**: System MUST display user-friendly error messages when database operations fail (not technical stack traces)
- **FR-026**: System MUST log all errors for debugging without exposing details to end users
- **FR-027**: System MUST provide fallback behavior when real-time data is unavailable (cached data with freshness indicator)
- **FR-028**: System MUST validate all user inputs before sending to backend APIs

### Key Entities

- **Stock Data**: Represents market data for individual stocks including symbol, name, price, volume, and derived metrics
- **User Favorites**: Collection of stocks a user has marked for tracking, with metadata like add date and custom notes
- **Strategy Results**: Stocks that match user-defined trading strategies, with match score and criteria details
- **Indicator Configuration**: Custom technical indicator definitions including indicator type, parameters, and visualization preferences
- **Market Data Tables**: Various market analysis data including dragon-tiger list, ETF data, fund flows, and auction data
- **User Session**: Authentication state including access tokens, permissions, and expiration times

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view their actual favorite stocks on Dashboard within 2 seconds of page load (not mock data)
- **SC-002**: All 5 Dashboard data tables (favorites, strategies, industry, concept, fund flow) display real data from the database
- **SC-003**: All 4 market data features (龙虎榜, ETF, 资金流向, 竞价抢筹) load successfully without database errors
- **SC-004**: Users can save and retrieve custom indicator configurations with 100% reliability
- **SC-005**: User sessions remain active for at least 8 hours of continuous use without unexpected logouts
- **SC-006**: Zero database connection errors related to MySQL (all migrated to PostgreSQL)
- **SC-007**: Users can clearly distinguish between working features and placeholder pages on first use
- **SC-008**: Error messages shown to users contain zero technical jargon (no stack traces, SQL errors, or undefined variable names)
- **SC-009**: Dashboard refresh completes within 3 seconds for standard data sets (up to 100 stocks)
- **SC-010**: System handles at least 50 concurrent users accessing Dashboard without degradation

### User Experience Metrics

- **SC-011**: 90% of users successfully view their portfolio data on first Dashboard visit
- **SC-012**: Users encounter zero "undefined" or "null" errors when navigating between pages
- **SC-013**: Support tickets related to "data not loading" decrease by 80%
- **SC-014**: Users can complete common workflows (view stocks → apply indicator → save configuration) without encountering broken features

## Assumptions

- The PostgreSQL database schema is already updated to support all required tables (from Week 3 migration)
- The dual-database architecture (PostgreSQL + TDengine) is correctly configured
- Backend API endpoints exist for core data operations (may need bug fixes but not complete rewrites)
- Frontend components are structurally correct and only need data integration fixes
- Users access the system via modern web browsers (Chrome, Firefox, Safari, Edge - latest 2 versions)
- Real-time market data APIs or data sources are available and accessible
- System operates in a single timezone (can be extended later)
- User permissions and role management are not part of this fix (authentication only)

## Dependencies

- **Code Review Report**: `COMPREHENSIVE_CODE_REVIEW_REPORT.md` provides detailed breakdown of all broken features
- **Code Modification Rules**: Must follow guidelines in `代码修改规则-new.md` for all fixes
- **Database Architecture**: Dual-database setup (PostgreSQL + TDengine) must be operational
- **Backend Services**: MyStocksUnifiedManager and data access layers must be available
- **Testing Tools**: Will use chrome-devtools-mcp, puppeteer, or playwright for automated E2E testing (TBD during implementation)

## Out of Scope

The following are explicitly NOT included in this feature:

- Adding new features beyond fixing existing broken ones
- Performance optimization beyond basic functionality (covered separately in P3)
- UI/UX redesign (only fixing broken interactions, not improving design)
- Mobile responsiveness improvements
- Implementing placeholder pages (Market, BacktestAnalysis) from scratch - only deciding to implement or remove
- Adding new market data sources beyond existing ones
- Implementing real-time streaming data (SSE already exists, just needs testing)
- Multi-language support
- Advanced user permissions and role-based access control

## Notes

**Priority Rationale**:
- P1 (Dashboard, Market Data, Error Handling): Core user-facing functionality that provides immediate value
- P2 (Indicator Management, Authentication): Important for power users and security but not blocking basic usage
- P3 (Placeholder Pages): UX improvement but doesn't affect working features

**Testing Strategy**:
- Each user story can be tested independently
- Automated E2E tests will be created for all P1 and P2 acceptance scenarios
- Manual testing required for P3 (placeholder page decisions)

**Migration Notes**:
- MySQL to PostgreSQL migration is partially complete (Week 3)
- 5 tables still need migration: fund_flow, etf_data, dragon_tiger, chip_race, indicator_configs
- Migration should not cause data loss; all legacy data must be preserved
