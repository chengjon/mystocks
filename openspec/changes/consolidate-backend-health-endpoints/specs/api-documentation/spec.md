> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## ADDED Requirements

### Requirement: Health/Status Endpoint OpenAPI Diff

The system SHALL produce an OpenAPI diff for health/status endpoint additions, removals, prefix changes, or response contract changes.

#### Scenario: Health or status endpoint changes

- **GIVEN** a health-like or status-like endpoint is added, removed, re-prefixed, or changes response schema
- **WHEN** the change is reviewed
- **THEN** the review SHALL include baseline and proposed OpenAPI evidence
- **AND** each changed endpoint SHALL be marked as canonical, compatibility, retired, domain smoke/status, or domain-owned follow-up

### Requirement: Health/Status Endpoint Documentation Accuracy

The system SHALL document current health/status endpoint paths using actual registered routes rather than decorator-local paths alone.

#### Scenario: Health documentation is updated

- **GIVEN** `api/health.py` defines `/health/services` under an `/api` router prefix
- **WHEN** documentation describes the externally available URL
- **THEN** it SHALL document `/api/health/services`
- **AND** it SHALL avoid documenting `/health/services` as available unless a route table confirms it

#### Scenario: Status documentation is updated

- **GIVEN** `GET /status` appears in route evidence
- **WHEN** documentation is updated
- **THEN** it SHALL identify whether each status path is platform status, domain status, compatibility, or deferred domain ownership
- **AND** it SHALL cite prefix-expanded full-path route evidence for runtime-conflict claims
