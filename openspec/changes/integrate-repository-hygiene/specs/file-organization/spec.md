## ADDED Requirements

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


### Requirement: Canonical Lifecycle Directories

The repository SHALL organize assets by lifecycle using stable top-level targets instead of ad-hoc placement.

#### Scenario: Store active documentation in docs
- **WHEN** a project-wide explanatory or operational document is active
- **THEN** it SHALL remain under the approved `docs/` taxonomy
- **AND** it SHALL NOT be mixed with generated evidence or frozen historical assets

#### Scenario: Store versioned evidence in reports
- **WHEN** a report is retained as versioned project evidence
- **THEN** it SHALL be placed under `reports/`
- **AND** `docs/` SHALL remain focused on explanatory and instructional content

#### Scenario: Store historical assets in archive
- **WHEN** a document or artifact becomes historical or frozen
- **THEN** it SHALL be archived under `archive/`
- **AND** active working directories SHALL not remain responsible for that historical payload

#### Scenario: Store runtime artifacts in var
- **WHEN** a log, coverage output, temporary report, or operational backup is generated locally
- **THEN** it SHALL be placed under `var/`
- **AND** the repository root SHALL not accumulate those runtime artifacts

### Requirement: Documentation Lifecycle Convergence

The project SHALL govern documentation by both taxonomy and lifecycle.

#### Scenario: Converge stale historical docs out of active docs trees
- **WHEN** historical documents remain in active `docs/` locations
- **THEN** the project SHALL plan and execute phased archival into `archive/docs/`
- **AND** explanatory indexes MAY retain links or references to the archived material

#### Scenario: Keep docs taxonomy distinct from report storage
- **WHEN** a document primarily serves as phase evidence, verification output, or governance proof
- **THEN** it SHALL be placed under `reports/`
- **AND** `docs/` SHALL not be used as a long-term catch-all evidence store
