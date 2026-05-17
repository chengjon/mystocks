## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Backend API Domain Router Closure Governance

The project SHALL treat backend API domain router consolidation as a governed migration with source-of-truth selection, compatibility retention, consumer evidence, and rollback criteria.

#### Scenario: Cross-domain router consolidation is planned

- **GIVEN** a consolidation affects multiple backend API domains or shared router registry behavior
- **WHEN** work is planned
- **THEN** the plan SHALL use an approved OpenSpec change before implementation
- **AND** it SHALL identify affected domains, canonical router candidates, compatibility shims, consumer classes, owners, and verification evidence
- **AND** it SHALL cite the cross-change orchestration artifact when the work shares route, OpenAPI, Core import, lifecycle, or rollback surfaces with other proposals

#### Scenario: Deletion candidate is reviewed

- **GIVEN** a flat API module, package router, shim, or mock router is proposed for retirement
- **WHEN** the candidate is reviewed
- **THEN** the review SHALL include code path evidence, function tree or consumer evidence, OpenAPI diff, import smoke, and rollback plan
- **AND** the candidate SHALL not be deleted solely because a replacement file exists

### Requirement: Domain Router Batch Isolation

The project SHALL implement backend domain router consolidation in independently verifiable domain batches.

#### Scenario: A domain batch fails verification

- **GIVEN** a domain migration batch changes router registration or compatibility paths
- **WHEN** import smoke, route smoke, OpenAPI diff, frontend smoke, or tests fail
- **THEN** the batch SHALL be rolled back or paused without requiring unrelated domain batches to revert

### Requirement: Route Evidence Classification

The project SHALL separate local decorator duplicate evidence from prefix-expanded final URL conflict evidence during backend API governance.

#### Scenario: Duplicate route evidence is reviewed

- **GIVEN** a route scan finds the same method and local decorator path in multiple modules
- **WHEN** a router consolidation proposal uses that evidence
- **THEN** the proposal SHALL require prefix-expanded final full-path evidence before classifying it as a runtime route conflict
- **AND** local decorator duplicate evidence SHALL remain valid as migration smell and ownership-risk evidence
