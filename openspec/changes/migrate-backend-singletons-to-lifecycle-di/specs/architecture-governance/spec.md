## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Backend Dependency Lifecycle Governance

The project SHALL classify backend singleton, getter, factory, and dependency-provider candidates by lifecycle before modifying them.

#### Scenario: Dependency candidate is selected

- **GIVEN** a module-level singleton, getter, factory, or dependency provider is selected for migration
- **WHEN** implementation is planned
- **THEN** the candidate SHALL be classified as stateless helper, heavy service, adapter factory, cache-backed service, connection-backed service, or compatibility getter
- **AND** the implementation SHALL document the selected lifecycle owner before code mutation
- **AND** candidates in shared Core modules SHALL identify whether they are blocked by the Core import compatibility matrix

#### Scenario: Heavy service is migrated

- **GIVEN** a service has warmup cost, connection pools, external clients, schedulers, or long-lived state
- **WHEN** it is migrated away from a module-level singleton
- **THEN** it SHALL NOT be recreated per request
- **AND** startup and teardown behavior SHALL be verified
- **AND** teardown verification SHALL produce an artifact such as test output, shutdown smoke output, log excerpt, or resource close assertion

### Requirement: Backend Dependency Compatibility Retention

The project SHALL retain old dependency getter surfaces until route, service, and test consumers have migrated or a rollback plan is approved.

#### Scenario: Existing getter has consumers

- **GIVEN** an existing `get_xxx` dependency getter is still imported by backend code, tests, or scripts
- **WHEN** a new provider is introduced
- **THEN** the old getter SHALL remain as a compatibility wrapper
- **AND** the wrapper SHALL have an explicit retirement condition

### Requirement: Dependency Migration Pilot Limit

The project SHALL prove lifecycle migration with one low-risk representative pilot before expanding to additional singleton or getter candidates.

#### Scenario: First DI implementation batch is planned

- **GIVEN** lifecycle inventory is complete
- **WHEN** the first implementation batch is selected
- **THEN** it SHALL include only one approved pilot candidate
- **AND** additional candidates SHALL remain blocked until the pilot passes override, startup, teardown, import, and rollback verification
