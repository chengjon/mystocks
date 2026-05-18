> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## ADDED Requirements

### Requirement: Backend Health/Status Endpoint Taxonomy

The system SHALL classify backend health-like and status-like endpoints before changing or retiring them.

#### Scenario: Health-like or status-like endpoint is reviewed

- **GIVEN** a route path or operation includes `health`, `ready`, `readiness`, `status`, or a related probe term
- **WHEN** it is reviewed for consolidation
- **THEN** it SHALL be classified as platform liveness/readiness, system service health, platform status, domain smoke/status, metrics/observability, adapter/database diagnostic, example, or embedded app
- **AND** unclassified endpoints SHALL NOT be deleted or re-prefixed

### Requirement: Readiness Probe Compatibility

The system SHALL preserve active readiness probe paths until every configured consumer has migrated.

#### Scenario: Readiness path migration is planned

- **GIVEN** `/health/ready` or `/api/health/ready` is used by runtime checks
- **WHEN** a migration proposes to alter readiness paths
- **THEN** the old path SHALL remain available or have an approved compatibility alias
- **AND** PM2, monitoring, CI, tests, and frontend consumers SHALL be updated or explicitly exempted

### Requirement: Services Health Probe Canonical Path

The system SHALL treat `/api/health/services` as the current services health probe unless a later approved migration changes the canonical path.

#### Scenario: Services health is checked

- **GIVEN** a smoke test or documentation references service health
- **WHEN** it selects a URL
- **THEN** it SHALL use `/api/health/services`
- **AND** root `/health/services` SHALL NOT be treated as available unless an approved compatibility route exists

### Requirement: Final Route Evidence For Probe Changes

The system SHALL use prefix-expanded final route evidence before treating health/status duplicates as runtime conflicts.

#### Scenario: Duplicate probe route is reviewed

- **GIVEN** local decorator evidence shows repeated `GET /health` or `GET /status`
- **WHEN** an implementation proposes endpoint deletion, redirection, or prefix changes
- **THEN** it SHALL consult the prefix-expanded full-path route table and OpenAPI diff
- **AND** the implementation SHALL classify the duplicate as local-decorator-only, compatibility alias, domain-owned endpoint, or final runtime conflict
