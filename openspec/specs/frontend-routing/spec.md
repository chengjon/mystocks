# frontend-routing Specification

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## Purpose
Define frontend routing behavior for authentication, navigation structure, lazy loading, and route-level
experience guarantees in MyStocks.
## Requirements
### Requirement: Authentication Guard System
The frontend SHALL implement JWT-based authentication guards that protect all routes marked as requiring authentication.

#### Scenario: Protected Route Access
- **WHEN** an unauthenticated user attempts to access a protected route
- **THEN** they are redirected to the login page
- **AND** the original destination is preserved for post-login redirect

#### Scenario: Valid Token Access
- **WHEN** an authenticated user with valid token accesses a protected route
- **THEN** they are allowed access to the route
- **AND** user information is available in components

#### Scenario: Expired Token Handling
- **WHEN** a user with expired token accesses a protected route
- **THEN** they are redirected to login page
- **AND** old token is cleared from storage

### Requirement: Standardized API Data Management
The frontend SHALL use Pinia stores for all API data fetching with standardized state management, caching, and error handling.

#### Scenario: Store-Based Data Fetching
- **WHEN** a component needs API data
- **THEN** it uses a Pinia store with consistent data/loading/error states
- **AND** the store handles caching automatically

#### Scenario: Error Handling
- **WHEN** an API call fails
- **THEN** user-friendly error messages are displayed
- **AND** fallback data is provided when available
- **AND** retry options are presented to user

#### Scenario: Loading States
- **WHEN** data is being fetched
- **THEN** loading indicators are shown consistently
- **AND** user interactions are properly disabled during loading

### Requirement: Real-time Data Updates
The frontend SHALL support WebSocket connections for real-time market data updates.

#### Scenario: WebSocket Connection
- **WHEN** the application starts
- **THEN** WebSocket connection is established automatically
- **AND** connection status is tracked and displayed

#### Scenario: Automatic Reconnection
- **WHEN** WebSocket connection is lost
- **THEN** automatic reconnection is attempted
- **AND** exponential backoff is used to prevent spam

#### Scenario: Real-time Data Integration
- **WHEN** real-time data arrives via WebSocket
- **THEN** it updates the corresponding Pinia stores
- **AND** UI components react to the data changes automatically

### Requirement: Single Entry Point Architecture

The frontend SHALL use exactly one active entry point (`main-standard.ts`) that includes all production capabilities: component registration, security initialization, error handling, PWA registration, session restore, version negotiation, and debug access.

The entry point SHALL follow a non-blocking async pattern: the app mounts synchronously (UI renders immediately), then async initialization (security, PWA, session, version) runs after mount without blocking rendering.

Legacy entry points (`main.js`, `main.js.backup`) SHALL be archived in `_entry-archive/` with a rollback README, not deleted.

#### Scenario: Production Boot Sequence
- **WHEN** the application starts via `main-standard.ts`
- **THEN** Vue app mounts synchronously with all component registrations
- **AND** the UI renders before async initialization completes
- **AND** security init runs with a 2-second timeout race
- **AND** PWA service worker registers on window load event
- **AND** session restore runs via dynamic import after security completes
- **AND** version negotiation runs after security completes

#### Scenario: Entry Point Rollback
- **WHEN** a regression is detected in the consolidated entry point
- **THEN** `main.js` can be restored from `_entry-archive/`
- **AND** `index.html` line 67 can be changed back to `/src/main.js`
- **AND** the application boots with the previous behavior

#### Scenario: Error Isolation
- **WHEN** an async initialization step fails (security, PWA, session, version)
- **THEN** the failure is logged with `[MyStocks]` prefix
- **AND** the application continues running (non-blocking)
- **AND** no emoji-based debug logs appear in production

