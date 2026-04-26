# api-integration Specification

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## Purpose
Define shared frontend-to-backend API integration behavior, including authentication, retries, caching,
and consistent request handling.
## Requirements
### Requirement: Unified API Client
The frontend SHALL provide a unified API client that handles authentication, caching, retries, and error handling consistently across all API calls.

#### Scenario: Authenticated Requests
- **WHEN** making API requests
- **THEN** JWT tokens are automatically included in headers
- **AND** token validity is checked before requests

#### Scenario: Intelligent Caching
- **WHEN** making GET requests
- **THEN** responses are cached based on URL and parameters
- **AND** cache TTL varies by data type (realtime, frequent, reference, etc.)

#### Scenario: Error Recovery
- **WHEN** API requests fail
- **THEN** automatic retries are attempted for network errors
- **AND** user-friendly error messages are provided
- **AND** fallback data is used when available

### Requirement: Pinia Store Factory
The frontend SHALL provide a factory pattern for creating consistent Pinia stores that manage API data with standardized state and actions.

#### Scenario: Store Creation
- **WHEN** creating a new API data store
- **THEN** the store factory provides consistent data/loading/error states
- **AND** standard actions for fetching, refreshing, and clearing data

#### Scenario: Reactive State Management
- **WHEN** store data changes
- **THEN** all subscribed components update automatically
- **AND** loading and error states are properly managed

#### Scenario: Cache Integration
- **WHEN** store fetches data
- **THEN** it leverages the unified API client's caching
- **AND** manual cache invalidation is supported

### Requirement: Data Adapter Pattern
The frontend SHALL implement data adapters that transform API responses into frontend-compatible data structures.

#### Scenario: Response Transformation
- **WHEN** API responses are received
- **THEN** they are transformed to match frontend data models
- **AND** field name mappings are applied consistently

#### Scenario: Error Normalization
- **WHEN** different APIs return errors in different formats
- **THEN** they are normalized to consistent error objects
- **AND** user-friendly messages are generated

#### Scenario: Type Safety
- **WHEN** data is adapted
- **THEN** TypeScript types are maintained throughout the process
- **AND** runtime type validation is performed

### Requirement: Page-Level API Truth Classification
The system SHALL classify each active ArtDeco page's API dependency as `verified` or `pending` and apply page behavior accordingly.

#### Scenario: Verified API page behavior
- **WHEN** an ArtDeco page is marked `verified`
- **THEN** it SHALL use the registered real API endpoint as its primary data source
- **AND** it SHALL NOT silently fall back to mock data for the same user path
- **AND** it SHALL surface loading, error, empty, and request identifier states

#### Scenario: Pending API page behavior
- **WHEN** an ArtDeco page is marked `pending`
- **THEN** the route SHALL remain reachable
- **AND** the page SHALL render shell/loading/error/empty states without fabricating contract fields
- **AND** the unresolved API blocker SHALL be recorded in the optimization list or task report

### Requirement: Shared Adapter Consistency For Batched Pages
The system SHALL consolidate data transformation logic for active ArtDeco pages that consume the same API family.

#### Scenario: Shared signals or positions endpoints
- **WHEN** multiple pages consume `/api/v1/trade/signals` or `/api/v1/trade/positions`
- **THEN** they SHALL reuse a common transformation layer or view-model mapping
- **AND** field normalization SHALL NOT be reimplemented independently on each page

#### Scenario: Shared market data endpoint family
- **WHEN** multiple pages consume the same market or Akshare endpoint family
- **THEN** their adapter logic SHALL be centralized in shared composables or helper modules
- **AND** any endpoint-specific blocker SHALL be tracked once at the batch level instead of duplicated across pages

### Requirement: Scoped ServiceResult Safe Paths
The frontend SHALL support scoped safe service-return paths that expose explicit success/error semantics for selected API integrations with known silent-failure risk.

#### Scenario: Safe service variant is introduced
- **WHEN** a service method with known silent-failure behavior is selected for migration
- **THEN** the frontend SHALL provide a safe path that exposes explicit success/error branching
- **AND** the migration SHALL preserve compatibility for existing callers until the pilot is verified

#### Scenario: Safe path is consumed
- **WHEN** a consumer adopts a safe service path
- **THEN** it SHALL branch on explicit success/error semantics rather than inferring failure from empty data
- **AND** it SHALL surface an actionable user or developer-visible error state

### Requirement: Canonical Realtime Transport Selection
The backend SHALL define a canonical transport selection policy for realtime delivery capabilities.

#### Scenario: Realtime capability is exposed
- **WHEN** a market-data, alerting, or strategy-triggered realtime capability is delivered to clients
- **THEN** the backend SHALL identify the canonical transport used for that capability
- **AND** it SHALL record any approved fallback or coexistence transport
- **AND** the selection SHALL align with the realtime delivery truth registry

#### Scenario: Competing realtime paths exist
- **WHEN** multiple realtime transports or overlapping delivery paths can serve the same capability
- **THEN** the system SHALL declare which path is canonical
- **AND** non-canonical paths SHALL remain compatibility-scoped or cleanup-scoped until retired
- **AND** the canonical designation SHALL match the registered realtime delivery truth

### Requirement: Realtime Latest-Only Coalescing
The frontend SHALL provide a reusable latest-only coalescing mechanism for selected high-frequency realtime channels.

#### Scenario: High-frequency channel is coalesced
- **WHEN** a configured realtime channel emits multiple updates within the coalescing window
- **THEN** the frontend SHALL publish or apply only the latest value at the end of the window
- **AND** it SHALL preserve existing realtime entrypoints instead of requiring a separate global stream runtime

### Requirement: Store Policy Registry
The frontend SHALL provide a reusable store policy registry for cache and realtime metadata used by `PiniaStoreFactory` consumers.

#### Scenario: Store consumes shared policy values
- **WHEN** a factory-created store opts into centralized policy values
- **THEN** its cache TTL, interval, and channel metadata SHALL be sourced from the shared store policy registry
- **AND** the store declaration SHALL remain the execution truth for how those values are applied

### Requirement: Force Refresh Semantics
The frontend SHALL define consistent refresh semantics that distinguish interval-respecting refreshes from user-forced refreshes.

#### Scenario: User triggers force refresh
- **WHEN** a user explicitly requests refresh on a registered capability
- **THEN** the frontend MAY bypass local stale-interval checks for that capability
- **AND** it SHALL still respect backend, upstream, or transport-level throttling constraints where applicable

### Requirement: Frontend Runtime Inspection Surface
The frontend SHALL provide a developer-visible runtime inspection surface for active data capabilities and realtime channels.

#### Scenario: Developer mode inspector is opened
- **WHEN** developer mode is enabled and the inspection surface is viewed
- **THEN** the frontend SHALL expose fetch recency, cache staleness, realtime connection status, and readiness/request metadata for registered capabilities
- **AND** it SHALL reuse actual store/service/realtime state rather than duplicating business logic
