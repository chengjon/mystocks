## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Dependency Override Verification

Backend dependency migrations SHALL include tests or smoke checks that prove dependencies can be overridden without mutating global singleton state.

#### Scenario: Route dependency is migrated

- **GIVEN** a FastAPI route uses a migrated dependency provider
- **WHEN** the route is tested
- **THEN** the test SHALL be able to override the provider through `dependency_overrides` or a documented equivalent
- **AND** the test SHALL NOT require direct mutation of private module-level singleton variables

### Requirement: Lifecycle Teardown Evidence

Backend services that own resources SHALL include teardown evidence when their lifecycle changes.

#### Scenario: Resource-owning service changes lifecycle

- **GIVEN** a migrated service owns a client, connection, cache, scheduler, or pool
- **WHEN** its lifecycle owner changes
- **THEN** verification SHALL prove startup succeeds and teardown releases the owned resource
- **AND** the verification result SHALL be attached as a reviewable artifact

### Requirement: Stable Dependency Import Surface

Backend dependency migrations SHALL coordinate with Core import compatibility when dependency providers live in shared Core modules.

#### Scenario: Dependency provider lives in Core

- **GIVEN** a provider or getter imports database, cache, security, socketio, or logging Core modules
- **WHEN** the provider lifecycle is changed
- **THEN** the implementation SHALL use an import path approved by the Core compatibility matrix
- **AND** import smoke SHALL cover both retained compatibility paths and the new canonical provider path
