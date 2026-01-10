# Web Frontend Architecture Specification

**Capability**: `web-frontend`
**Version**: 1.0
**Status: Draft

---

## ADDED Requirements

### Requirement: Functional Domain Architecture

The system SHALL organize all frontend pages into **6 functional domains** to reduce cognitive load and improve feature discoverability.

**Functional Domains**:
1. **Dashboard** - 仪表盘（首页概览）
2. **Market Data** - 市场数据域（市场行情、TDX行情、实时监控）
3. **Analysis** - 选股分析域（数据分析、行业概念、技术分析、指标库）
4. **Strategy** - 策略回测域（策略管理、回测分析）
5. **Trading** - 交易管理域（股票管理、交易管理、投资组合）
6. **Risk** - 风险监控域（风险监控、公告监控）
7. **Settings** - 系统设置域（系统设置、架构监控、数据库监控）

#### Scenario: User navigates through functional domains

- **GIVEN** a user is on the Dashboard page
- **WHEN** the user clicks on "市场数据" in the sidebar
- **THEN** the user SHALL be navigated to `/market/list` with the MarketLayout
- **AND** the sidebar SHALL highlight the "市场数据" domain
- **AND** the breadcrumb SHALL display `仪表盘 > 市场数据 > 市场行情`

#### Scenario: User discovers features faster with new architecture

- **GIVEN** a user wants to find the "实时监控" feature
- **WHEN** the user navigates to the "市场数据" domain
- **THEN** the "实时监控" feature SHALL be visible as a sub-menu item
- **AND** the time to discover the feature SHALL be reduced by 40% (from 8.5s to 5.1s)

#### Scenario: System provides backward compatible routing

- **GIVEN** a user has bookmarked the old URL `/realtime`
- **WHEN** the user accesses the old URL
- **THEN** the system SHALL automatically redirect to `/market/realtime`
- **AND** the user SHALL see a toast message explaining the new location

---

### Requirement: Design Token System

The system SHALL implement a **global CSS variable system** (Design Tokens) to ensure visual consistency across all components.

**Token Categories**:
1. **Colors**: Bloomberg dark theme palette (background, text, accent, stock up/down)
2. **Spacing**: 8px baseline grid system (xs, sm, md, lg, xl, 2xl, 3xl)
3. **Typography**: Font families (mono for numbers, sans for UI), sizes, weights
4. **Borders**: Radius system (none, sm, md, lg, xl, full)
5. **Shadows**: Elevation system (sm, md, lg, xl)
6. **Transitions**: Duration curves (fast, base, slow)
7. **Z-index**: Layer system (dropdown, sticky, fixed, modal, popover, tooltip)

#### Scenario: Developer uses Design Tokens for component styling

- **GIVEN** a developer is creating a new Vue component
- **WHEN** the developer applies styles using CSS variables
- **THEN** the component SHALL automatically inherit the Bloomberg dark theme
- **AND** the component SHALL match the visual consistency of other components

#### Scenario: Design Tokens reduce style conflicts

- **GIVEN** the codebase has 30+ components
- **WHEN** all components use Design Tokens instead of hardcoded values
- **THEN** style conflicts SHALL be reduced by 90%
- **AND** theme customization SHALL require changes in only one file

#### Scenario: System enforces Design Token usage via linting

- **GIVEN** a developer attempts to commit code with hardcoded colors
- **WHEN** the pre-commit hook runs
- **THEN** the linter SHALL flag the violation (e.g., "Use var(--color-bg-primary) instead of #1a1a1a")
- **AND** the commit SHALL be blocked until the violation is fixed

---

### Requirement: Command Palette Navigation

The system SHALL provide a **keyboard-driven command palette** (Ctrl+K / Cmd+K) to enable efficient navigation for expert users.

**Features**:
1. **Global hotkey**: Ctrl+K (Windows/Linux) / Cmd+K (macOS)
2. **Fuzzy search**: Search across all pages, menu items, and actions
3. **Quick navigation**: Jump directly to any page or feature
4. **Recent history**: Show recently accessed pages
5. **Keyboard shortcuts**: Display keyboard shortcuts for common actions

#### Scenario: Expert user navigates to a page using Command Palette

- **GIVEN** an expert user is on any page
- **WHEN** the user presses Ctrl+K and types "实时监控"
- **THEN** the Command Palette SHALL display matching results
- **AND** pressing Enter SHALL navigate directly to the RealTime Monitor page
- **AND** the time to navigate SHALL be under 2 seconds

#### Scenario: Command Palette improves expert user efficiency

- **GIVEN** an expert user needs to access 10 different features per hour
- **WHEN** using Command Palette instead of mouse navigation
- **THEN** the user's navigation efficiency SHALL increase by 30%
- **AND** the user SHALL report higher satisfaction scores

#### Scenario: Command Palette provides keyboard shortcuts

- **GIVEN** a user opens the Command Palette
- **WHEN** the user types "dashboard"
- **THEN** the result SHALL display "仪表盘 Ctrl+1"
- **AND** pressing Ctrl+1 SHALL directly navigate to the Dashboard

---

### Requirement: WebSocket Connection Manager

The system SHALL implement a **singleton WebSocket manager** to maintain a single WebSocket connection across all components.

**Features**:
1. **Singleton pattern**: Global unique connection
2. **Multi-component subscription**: Multiple components can subscribe to the same connection
3. **Auto-reconnect**: Exponential backoff reconnection strategy
4. **Heartbeat detection**: 30-second ping to detect connection health
5. **Connection status**: Online/offline status indicators

#### Scenario: Multiple components share a single WebSocket connection

- **GIVEN** a user has 3 browser tabs open
- **WHEN** each tab subscribes to market data updates
- **THEN** the system SHALL maintain only 1 WebSocket connection (not 3)
- **AND** the connection resource usage SHALL be reduced by 90%

#### Scenario: WebSocket manager automatically reconnects

- **GIVEN** the WebSocket connection is lost due to network issues
- **WHEN** the manager detects the disconnection
- **THEN** the manager SHALL attempt to reconnect with exponential backoff (1s, 2s, 4s, 8s, 16s)
- **AND** after 5 failed attempts, the manager SHALL notify the user of connection failure

#### Scenario: Components subscribe to specific message types

- **GIVEN** a Dashboard component needs real-time stock quotes
- **WHEN** the component calls `wsManager.subscribe('market.quote', callback)`
- **THEN** the component SHALL receive only market.quote messages
- **AND** when the component is unmounted, the subscription SHALL be automatically cancelled

---

### Requirement: TypeScript Type Safety

The system SHALL achieve **90% TypeScript coverage** through gradual migration while maintaining JavaScript compatibility.

**Migration Strategy**:
1. **Phase 1**: Enable `allowJs: true` and `checkJs: false` (JS/TS coexistence)
2. **Phase 2**: Migrate 30% core components to TypeScript
3. **Phase 3**: Enable `strict: true` for TypeScript files only
4. **Phase 4**: Migrate remaining components to reach 90% coverage

#### Scenario: TypeScript prevents runtime type errors

- **GIVEN** a developer is working on a Vue component
- **WHEN** the developer incorrectly types a prop as `String` instead of `Number`
- **THEN** the TypeScript compiler SHALL flag the error at compile time
- **AND** the IDE SHALL provide autocomplete suggestions based on the correct type

#### Scenario: JavaScript and TypeScript coexist during migration

- **GIVEN** the codebase has both .js and .ts files
- **WHEN** the TypeScript compiler runs
- **THEN** .ts files SHALL be type-checked
- **AND** .js files SHALL be ignored (checkJs: false)
- **AND** the build SHALL succeed without errors

#### Scenario: TypeScript migration improves developer experience

- **GIVEN** a developer is refactoring a component
- **WHEN** the component has full type definitions
- **THEN** the IDE SHALL provide accurate autocomplete for all props, methods, and return values
- **AND** the developer's productivity SHALL increase by 40%

---

### Requirement: Performance Optimization

The system SHALL achieve the following performance targets through code splitting, lazy loading, and bundle optimization.

**Performance Targets**:
1. **Bundle size**: 5.0MB → 2.0MB (↓60%)
2. **First Contentful Paint (FCP)**: < 1.5s
3. **Largest Contentful Paint (LCP)**: < 2.5s
4. **Time to Interactive (TTI)**: < 3.5s
5. **Lighthouse Performance Score**: > 85

#### Scenario: System implements route-based code splitting

- **GIVEN** the application has 30+ pages
- **WHEN** the user navigates to a specific page (e.g., /market/list)
- **THEN** the browser SHALL download only the JavaScript chunks for that page
- **AND** the initial bundle SHALL be reduced by 60%

#### Scenario: ECharts is tree-shaken to reduce bundle size

- **GIVEN** the application uses ECharts for visualization
- **WHEN** the build runs with tree-shaking enabled
- **THEN** only the used ECharts modules (e.g., LineChart, GridComponent) SHALL be included
- **AND** the ECharts bundle SHALL be reduced from 3MB to 500KB

#### Scenario: API caching reduces redundant network requests

- **GIVEN** a user navigates between pages that fetch the same data
- **WHEN** the data is already in the cache (TTL < 5 minutes)
- **THEN** the system SHALL return the cached data instead of making a network request
- **AND** the page load time SHALL be reduced by 50%

---

### Requirement: Bloomberg Terminal Design Style

The system SHALL adopt the **Bloomberg Terminal design style** to create a professional financial trading interface.

**Design Characteristics**:
1. **Dark theme**: Deep gray/black backgrounds (#1a1a1a, #2d2d2d)
2. **High contrast**: White text on dark backgrounds (#ffffff on #1a1a1a)
3. **Accent colors**: Orange-red for highlights (#ff6b35)
4. **Stock colors**: Green for up (#00d924), Red for down (#ff4757)
5. **Monospace fonts**: JetBrains Mono for numerical data
6. **Information density**: High-density layouts optimized for 1920x1080 displays

#### Scenario: Dark theme reduces eye strain during long sessions

- **GIVEN** a trader uses the application for 8+ hours per day
- **WHEN** using the Bloomberg dark theme
- **THEN** the user SHALL report reduced eye strain compared to light themes
- **AND** the color contrast SHALL meet WCAG 2.1 AA standards (4.5:1 for normal text)

#### Scenario: Monospace fonts improve numerical data readability

- **GIVEN** a page displays stock prices, percentages, and ratios
- **WHEN** the numerical data uses JetBrains Mono font
- **THEN** the numbers SHALL be vertically aligned (monospaced)
- **AND** the user SHALL be able to quickly compare values across rows

#### Scenario: Information density matches professional tools

- **GIVEN** a 1920x1080 display
- **WHEN** the Dashboard page renders
- **THEN** the page SHALL display 50+ data points without scrolling
- **AND** the layout SHALL match the information density of Bloomberg Terminal

---

### Requirement: Desktop-Only Platform Strategy

The system SHALL explicitly **support desktop browsers only** (1280x720+ resolution) and SHALL NOT implement mobile/responsive features.

**Supported Platforms**:
- ✅ Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- ✅ Minimum resolution: 1280x720
- ✅ Recommended resolution: 1920x1080 or higher

**Unsupported Platforms**:
- ❌ Mobile devices (phones, tablets)
- ❌ Touch-optimized interactions
- ❌ Responsive layouts (@media queries for mobile)

#### Scenario: System declares desktop-only support in documentation

- **GIVEN** a user reviews the project documentation
- **WHEN** reading the platform support section
- **THEN** the documentation SHALL clearly state "本项目仅支持 Web 桌面端 (1280x720+)"
- **AND** mobile devices SHALL be listed as unsupported

#### Scenario: Developers are prohibited from adding mobile code

- **GIVEN** a developer attempts to add responsive CSS code
- **WHEN** the pre-commit hook runs
- **THEN** the linter SHALL flag the violation (e.g., "Mobile responsive code is not allowed: @media (max-width: 768px)")
- **AND** the commit SHALL be blocked until the mobile code is removed

#### Scenario: Application works optimally on desktop browsers

- **GIVEN** a user accesses the application on a desktop browser (1920x1080)
- **WHEN** the page loads
- **THEN** all components SHALL be visible without horizontal scrolling
- **AND** the layout SHALL utilize the full screen width efficiently

---

### Requirement: Testing Infrastructure

The system SHALL achieve **60% test coverage** through unit tests, integration tests, and E2E tests.

**Testing Targets**:
1. **Unit test coverage** (Vitest): > 70%
2. **E2E test coverage** (Playwright): > 80% (core scenarios)
3. **Overall coverage**: > 60%
4. **Test execution time**: < 5 minutes

#### Scenario: Unit tests verify component logic

- **GIVEN** a component has complex business logic (e.g., Command Palette search)
- **WHEN** the unit tests run
- **THEN** all branches and edge cases SHALL be covered
- **AND** the test coverage for that component SHALL be > 80%

#### Scenario: E2E tests verify critical user journeys

- **GIVEN** a user needs to navigate from Dashboard to Market Data to Stock Detail
- **WHEN** the E2E test runs
- **THEN** the test SHALL simulate the user journey end-to-end
- **AND** the test SHALL verify: navigation, API calls, data rendering, and error handling

#### Scenario: CI/CD enforces test coverage gates

- **GIVEN** a developer creates a pull request
- **WHEN** the CI/CD pipeline runs
- **THEN** the pipeline SHALL fail if test coverage drops below 60%
- **AND** the developer SHALL receive a report showing which files lack coverage

---

## MODIFIED Requirements

*(None - this is a new capability specification)*

---

## REMOVED Requirements

*(None - this is a new capability specification)*

---

## RENAMED Requirements

*(None - this is a new capability specification)*
