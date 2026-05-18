> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## ADDED Requirements

### Requirement: Health/Status Probe Migration Governance

The project SHALL treat backend health/status endpoint consolidation as an operations-sensitive migration with route inventory, consumer evidence, compatibility paths, and rollback criteria.

#### Scenario: Health or status endpoint retirement is proposed

- **GIVEN** a health-like or status-like endpoint is proposed for retirement
- **WHEN** the retirement is reviewed
- **THEN** the review SHALL include route table evidence, consumer matrix, OpenAPI diff, smoke checks, and rollback plan
- **AND** the endpoint SHALL not be removed solely because another health/status endpoint exists

### Requirement: Health/Status Endpoint Batch Isolation

The project SHALL implement health/status endpoint consolidation in independently reversible batches.

#### Scenario: Probe smoke fails

- **GIVEN** a health/status endpoint batch changes route registration or compatibility paths
- **WHEN** `/health/ready`, `/api/health/ready`, `/api/health/services`, PM2 status, or affected consumer smoke fails
- **THEN** the batch SHALL be rolled back or paused without requiring unrelated endpoint classes to change

### Requirement: Domain-Owned Probe Boundary

The project SHALL separate platform health/status probe consolidation from domain route ownership decisions.

#### Scenario: Domain endpoint appears health-like

- **GIVEN** a domain endpoint such as backup cleanup exposes a health-like or status-like route
- **WHEN** the endpoint is reviewed
- **THEN** the review SHALL decide whether it is a platform probe, domain smoke/status endpoint, or domain route ownership issue
- **AND** domain route ownership issues SHALL be deferred to the relevant domain router OpenSpec change instead of being deleted by health/status consolidation alone
