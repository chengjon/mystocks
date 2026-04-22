## ADDED Requirements

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
