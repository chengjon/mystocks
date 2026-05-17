## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: OpenAPI Diff Gate For Domain Router Changes

The system SHALL produce a before/after OpenAPI diff for backend domain router changes that add, remove, rename, re-prefix, or alter response models for API endpoints.

#### Scenario: Route registration changes

- **GIVEN** a backend domain router implementation changes FastAPI route registration
- **WHEN** the change is prepared for review
- **THEN** the review evidence SHALL include the baseline OpenAPI schema, proposed OpenAPI schema, and a summarized diff
- **AND** any removed or renamed path SHALL include compatibility and rollback notes
- **AND** the route evidence SHALL identify whether each duplicate is local-decorator-only, a compatibility alias, or a prefix-expanded final URL conflict

#### Scenario: Response contract changes

- **GIVEN** a domain router migration changes response schema, status code, tags, or operation IDs
- **WHEN** OpenAPI diff is generated
- **THEN** the diff SHALL identify the affected endpoint and contract element
- **AND** the migration SHALL not proceed without explicit approval of that contract change

### Requirement: Canonical Router Documentation

The system SHALL document canonical and compatibility API paths after each approved domain router migration batch.

#### Scenario: Documentation is updated after migration

- **GIVEN** a domain router migration batch has completed
- **WHEN** implementation evidence is recorded
- **THEN** documentation SHALL identify the canonical path, retained compatibility paths, retirement candidates, and verification commands

### Requirement: Deferred Domain Documentation

The system SHALL document high-risk route domains that are intentionally deferred from the current migration.

#### Scenario: Domain is deferred

- **GIVEN** route evidence identifies a high-risk domain outside the current implementation scope
- **WHEN** the current OpenSpec change is approved
- **THEN** documentation SHALL list the deferred domain, the evidence artifact, and the required follow-up approval path
