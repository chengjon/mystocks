# frontend-routing Specification

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
- **AND** UI components react to the data changes automatically</content>
<parameter name="filePath">openspec/changes/implement-frontend-routing-optimization/specs/frontend-routing/spec.md

### Requirement: ArtDeco Route Metadata SSOT
The system SHALL keep active ArtDeco page metadata aligned across the router, page configuration, and optimization status tracking.

#### Scenario: P0/P1 page metadata alignment
- **WHEN** a P0/P1 ArtDeco page is prepared for optimization
- **THEN** `web/frontend/src/router/index.ts`, `web/frontend/src/config/pageConfig.ts`, and `docs/plans/frontend-page-optimization-list.md` SHALL identify the same route path, page component, and API truth classification
- **AND** the route title and functional domain grouping SHALL remain consistent across those sources

#### Scenario: Executable route batching
- **WHEN** multiple active ArtDeco pages share the same parent container, reusable domain block, or API family
- **THEN** they SHALL be grouped into the same executable optimization batch
- **AND** that batch SHALL declare its primary verification entrypoints before implementation starts

### Requirement: Route And Layout Regression Gate
The system SHALL validate ArtDeco route or layout changes with PM2 smoke and page-level E2E evidence.

#### Scenario: Route or layout change verification
- **WHEN** a change modifies an ArtDeco route, layout shell, or parent container
- **THEN** `scripts/run_e2e_pm2.sh` SHALL be executed against the PM2 environment
- **AND** the change report SHALL record the actual browser project, executed suite names, and pass/fail counts

#### Scenario: Service availability reporting
- **WHEN** route or layout verification results are reported
- **THEN** the report SHALL include `http://localhost:3020` and `http://localhost:8020`
- **AND** it SHALL distinguish newly introduced regressions from pre-existing technical debt
