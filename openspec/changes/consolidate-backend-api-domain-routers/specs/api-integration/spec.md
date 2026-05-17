## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Backend Domain Router Canonicalization

The system SHALL define a canonical router contract for each in-scope backend API domain before changing router registration, API file layout, URL prefix, or compatibility shim behavior.

#### Scenario: Canonical router is selected after evidence

- **GIVEN** a backend API domain has both flat modules and package routers
- **WHEN** an implementation batch proposes to change router registration or canonical path
- **THEN** the batch SHALL include route inventory, endpoint parity, OpenAPI diff, and consumer matrix evidence
- **AND** the batch SHALL identify the canonical router and compatibility surfaces before code mutation
- **AND** route inventory SHALL distinguish local decorator duplicates from prefix-expanded final full-path conflicts

#### Scenario: Router mutation is blocked without approval

- **GIVEN** a domain router consolidation proposal has not been approved
- **WHEN** a change attempts to delete a router, remove a shim, change a prefix, or alter response models
- **THEN** the change SHALL be rejected until the OpenSpec proposal is approved

### Requirement: Domain API Compatibility Retention

The system SHALL retain legacy API paths, compatibility shims, and mock routers until their consumers are classified and cleanup exit criteria are met.

#### Scenario: Legacy consumer still exists

- **GIVEN** a legacy API path or shim is referenced by backend code, frontend code, tests, or scripts
- **WHEN** a canonical router is introduced
- **THEN** the legacy path or shim SHALL remain available
- **AND** the migration notes SHALL identify the consumer and planned retirement condition

#### Scenario: Compatibility surface is cleanup-ready

- **GIVEN** a legacy path, flat module, or shim has no runtime consumers
- **AND** import smoke and OpenAPI diff show that canonical behavior is available
- **WHEN** the cleanup batch is reviewed
- **THEN** the compatibility surface MAY be retired with a rollback plan

### Requirement: Domain Consumer Matrix

The system SHALL maintain a consumer matrix for backend domain router migrations that separates runtime consumers from documentation-only references.

#### Scenario: Consumer references are classified

- **GIVEN** a domain migration affects API paths or import paths
- **WHEN** references are collected
- **THEN** they SHALL be classified as backend imports, frontend API calls, tests, scripts, or documentation references
- **AND** only documentation-only references SHALL be excluded from runtime compatibility decisions

### Requirement: Deferred High-Risk Domain Ownership

The system SHALL explicitly include or defer high-risk API domains found during route scans so proposal names do not imply hidden implementation scope.

#### Scenario: High-risk domain is not implemented by the current change

- **GIVEN** a route scan identifies a high-risk API domain such as `trading` or `backup`
- **WHEN** the current OpenSpec change does not implement that domain
- **THEN** the change SHALL record the domain as a deferred follow-up
- **AND** the follow-up SHALL cite route evidence and remain blocked until separately approved
