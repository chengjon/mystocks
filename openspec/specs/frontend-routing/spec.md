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

### Requirement: Canonical Dashboard Route Truth
The system SHALL treat `/dashboard` as the canonical home / trading-room route backed by `ArtDecoDashboard.vue`.

#### Scenario: Canonical dashboard shell
- **WHEN** a user navigates to `/dashboard`
- **THEN** the router resolves the live home-shell page
- **AND** that page is `ArtDecoDashboard.vue`
- **AND** governed route truth and generated page-config truth both identify `/dashboard` as canonical

#### Scenario: Legacy DealingRoom compatibility
- **GIVEN** historical docs or bookmarks still reference `DealingRoom`
- **WHEN** compatibility support is enabled
- **THEN** `/dealing-room` SHALL redirect to or resolve the same canonical dashboard shell
- **AND** the system SHALL NOT treat `DealingRoom` as a separate active page file

### Requirement: Trade Terminal Separation
The system SHALL keep `/trade/terminal` semantics separate from dashboard / DealingRoom semantics.

#### Scenario: Trade terminal remains distinct
- **WHEN** a user navigates to `/trade/terminal`
- **THEN** the router resolves the trade-terminal implementation
- **AND** that implementation SHALL NOT be renamed to `DealingRoom.vue` as part of dashboard truth reconciliation

### Requirement: Evidence-Based Frontend Route Truth
The system SHALL treat the current frontend runtime route truth as the evidence-backed chain
`web/frontend/index.html -> /src/main-standard.ts -> /src/router/index.ts` unless an approved
change updates all linked entry surfaces together.

#### Scenario: Resolve the canonical runtime route chain
- **WHEN** an operator audits the live frontend route entry
- **THEN** they identify `web/frontend/index.html` as the HTML entry
- **AND** that entry loads `/src/main-standard.ts`
- **AND** `/src/main-standard.ts` resolves the live router at `/src/router/index.ts`

#### Scenario: Reject historical router files as live truth
- **GIVEN** historical router assets such as `src/router/index.js`, `src/router/index.js.clean`, `src/router/index.js.backup-phase2.3`, or `src/router/phase4.routes.js` still exist
- **WHEN** the project classifies current route truth
- **THEN** those files SHALL NOT be treated as the current runtime route source
- **AND** they SHALL be handled through lifecycle classification before archive or removal

### Requirement: Historical Route Asset Classification
The system SHALL classify non-canonical router files before they can be archived, relocated, or removed.

#### Scenario: Classify legacy router assets before cleanup
- **WHEN** a frontend closure batch evaluates non-canonical router files
- **THEN** each file SHALL receive an explicit lifecycle status such as historical backup, broken working copy, stale route asset, or retained historical reference
- **AND** cleanup SHALL wait until that status and its retirement conditions are recorded

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

### Requirement: Trade Reconciliation Route
The frontend routing system SHALL expose a dedicated trade reconciliation statement route.

#### Scenario: User navigates to the reconciliation route
- **WHEN** the user opens `/trade/reconciliation`
- **THEN** the router SHALL load the dedicated reconciliation statement page

### Requirement: Trade Navigation Labels
The frontend routing system SHALL keep trade navigation labels aligned with the approved trade-domain surfaces.

#### Scenario: Reconciliation and history labels are rendered
- **WHEN** the frontend renders the trade navigation surfaces
- **THEN** the navigation label for `/trade/reconciliation` SHALL be `对账单`
- **AND** the navigation label for `/trade/history` SHALL be `交易历史`

### Requirement: System Resource Usage Route
The frontend routing system SHALL expose a dedicated system resource usage route.

#### Scenario: User navigates to the resource usage route
- **WHEN** the user opens `/system/resources`
- **THEN** the router SHALL load the dedicated system resource usage page

### Requirement: System Navigation Labels For Resource Usage
The frontend routing system SHALL keep system navigation labels aligned with the approved resource usage surface.

#### Scenario: Resource usage label is rendered
- **WHEN** the frontend renders the active system navigation surfaces
- **THEN** the navigation label for `/system/resources` SHALL be `资源使用`

### Requirement: AI Sentiment Workbench Route
The frontend routing system SHALL expose a dedicated AI-domain sentiment workbench route.

#### Scenario: User navigates to the AI sentiment workbench
- **WHEN** the user opens `/ai/sentiment`
- **THEN** the router SHALL load the canonical AI sentiment workbench page
- **AND** that page SHALL be the AI-domain truth source for `7.3 情感分析`

### Requirement: AI Navigation Label For Sentiment Workbench
The frontend routing system SHALL expose a visible AI navigation entry for the canonical sentiment workbench.

#### Scenario: AI navigation label is rendered
- **WHEN** the frontend renders the active navigation surfaces
- **THEN** the navigation label for `/ai/sentiment` SHALL be `情感分析`
- **AND** the AI navigation entry SHALL be treated as the canonical route-level entry for this capability

### Requirement: Risk News Wrapper Preservation
The frontend routing system SHALL keep `/risk/news` reachable as a risk-domain wrapper surface.

#### Scenario: User navigates to the risk news wrapper
- **WHEN** the user opens `/risk/news`
- **THEN** the router SHALL continue to load a risk-domain page
- **AND** that page SHALL remain reachable from risk navigation
- **AND** that page SHALL NOT replace `/ai/sentiment` as the canonical AI-domain route

### Requirement: Trade Execution Tracking Route
The frontend routing system SHALL expose a dedicated trade execution tracking route under the trade domain.

#### Scenario: User navigates to execution tracking
- **WHEN** the user opens `/trade/execution`
- **THEN** the router SHALL load the execution tracking workbench
- **AND** the trade navigation shall surface the new route as a canonical trade-domain surface

### Requirement: Execution Tracking Navigation Label
The trade navigation SHALL expose an execution tracking label for the dedicated workbench.

#### Scenario: Trade menu renders execution tracking
- **WHEN** the trade menu is rendered
- **THEN** the menu SHALL include an execution tracking entry
- **AND** the label SHALL distinguish the workbench from trade history and reconciliation

### Requirement: AI ML Training And Prediction Workbench Route
The frontend routing system SHALL expose a dedicated AI-domain ML training and prediction workbench route.

#### Scenario: User navigates to the ML workbench
- **WHEN** the user opens `/ai/ml`
- **THEN** the router SHALL load the canonical ML training and prediction workbench page
- **AND** that page SHALL be the AI-domain route truth source for `7.1 模型训练 / 预测推理`

### Requirement: AI Navigation Label For ML Workbench
The frontend navigation SHALL expose a visible AI entry for the canonical ML workbench.

#### Scenario: AI navigation label is rendered
- **WHEN** the frontend renders the active navigation surfaces
- **THEN** the menu SHALL include a `/ai/ml` entry labelled `模型训练 / 预测`
- **AND** the entry SHALL be grouped under the AI domain

### Requirement: Legacy ML Menu Entries Do Not Become Route Truth
Historical `/ml/training` and `/ml/prediction` entries SHALL NOT be treated as canonical route truth for first-batch 7.1 unless a separate compatibility decision is approved.

#### Scenario: Route truth is audited
- **WHEN** the project audits 7.1 frontend route truth
- **THEN** `/ai/ml` SHALL be treated as canonical
- **AND** historical `/ml/training` and `/ml/prediction` menu entries SHALL be classified as legacy or redirected explicitly before use

### Requirement: AI Batch Analysis Workbench Route
The frontend routing system SHALL expose a dedicated AI-domain batch analysis workbench route.

#### Scenario: User navigates to the batch analysis workbench
- **WHEN** a user navigates to `/ai/batch`
- **THEN** the router SHALL render the canonical AI batch analysis workbench
- **AND** that page SHALL be the AI-domain route truth source for `7.2 批量分析`

### Requirement: AI Navigation Label For Batch Analysis Workbench
The frontend navigation SHALL expose a visible AI entry for the canonical batch analysis workbench.

#### Scenario: AI navigation label is rendered
- **WHEN** the frontend renders the active navigation surfaces
- **THEN** the menu SHALL include a `/ai/batch` entry labelled `批量分析`
- **AND** the entry SHALL be grouped under the AI domain

