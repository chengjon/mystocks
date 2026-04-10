# file-organization Specification

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## Purpose
Define canonical file placement, root-directory hygiene, and documentation/script organization rules
for the MyStocks repository layout.
## Requirements
### Requirement: Root Directory Minimalism

The project root directory SHALL remain limited to explicitly allowlisted core files, and non-allowlisted
artifacts MUST be organized into governed subdirectories.

#### Scenario: Keep the root directory compliant
- **WHEN** a new repository file is introduced
- **THEN** it SHALL be placed in an approved subdirectory according to file-organization rules
- **AND** the project root SHALL not accumulate non-allowlisted artifacts

#### Scenario: Audit root directory violations
- **WHEN** the structure checker runs
- **THEN** it SHALL report root-directory violations
- **AND** fail with a non-zero exit status when violations are present

### Requirement: File Classification System

Project files SHALL be classified into canonical directories according to their purpose.

#### Scenario: Classify documentation files
- **WHEN** a project-level Markdown document is created
- **THEN** it SHALL be placed in an approved `docs/` subtree
- **AND** submodule-local documentation may remain inside the relevant submodule scope

#### Scenario: Classify scripts and configuration
- **WHEN** a script or configuration file is created
- **THEN** scripts SHALL be placed in approved `scripts/` buckets
- **AND** configuration files SHALL be placed in governed configuration locations unless explicitly allowlisted at root

### Requirement: Automated Structure Enforcement

The project SHALL provide automated enforcement for file-organization rules through local and CI automation.

#### Scenario: Enforce structure during commit workflows
- **WHEN** a commit-time or local structure check runs
- **THEN** the automation SHALL validate directory-structure rules
- **AND** block or fail when violations are detected

#### Scenario: Preview automated organization
- **WHEN** an operator runs the organizer in dry-run mode
- **THEN** the system SHALL report the planned moves without mutating repository state

### Requirement: Path-Independent Tooling

Structure-governance scripts SHALL resolve project context dynamically and SHALL not depend on fragile
execution-location-relative paths.

#### Scenario: Resolve project root dynamically
- **WHEN** a governance script is executed from an arbitrary working directory
- **THEN** it SHALL still locate the project root and required configuration correctly
- **AND** it SHALL not rely on hard-coded relative traversal such as `../config/`

### Requirement: Documentation Taxonomy

Documentation SHALL be organized according to approved project taxonomy and scope boundaries.

#### Scenario: Place project-wide documentation in canonical docs trees
- **WHEN** project-wide documentation is added or migrated
- **THEN** it SHALL be stored in the approved `docs/` taxonomy
- **AND** indexes or trace files SHALL be updated to reflect the canonical location

#### Scenario: Preserve submodule-local documentation boundaries
- **WHEN** documentation is specific to a submodule or embedded subsystem
- **THEN** it MAY remain in that subsystem's local documentation area
- **AND** main-project automation SHALL respect that boundary

### Requirement: Active Route Deprecation Safety
The system SHALL NOT move a frontend page into `deprecated/` while that page remains referenced by canonical router truth, generated page-config truth, or governed page inventory truth.

#### Scenario: Prevent deprecating a live route shell
- **WHEN** a page is still bound by router truth or generated page-config truth as a live route
- **THEN** deprecation work SHALL be blocked until a replacement or alias decision is approved
- **AND** the migration task SHALL record the blocker instead of moving the file

#### Scenario: Prevent deprecating a governed mainline page
- **GIVEN** a page is still tracked as a verified mainline page in governed inventory documentation
- **WHEN** a restructure task proposes moving that page to `deprecated/`
- **THEN** the task SHALL remain blocked until page-inventory truth is reconciled with router truth

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

### Requirement: Legacy Frontend Asset Lifecycle Classification
The project SHALL classify legacy frontend assets by functional role before relocating, archiving, or removing them.

#### Scenario: Classify monitoring and legacy route-bound pages
- **WHEN** the project evaluates `src/views/monitoring/` or other route-adjacent legacy page groups
- **THEN** it SHALL classify each page as canonical runtime truth, historical route target, test-guarded artifact, or another explicit lifecycle role
- **AND** it SHALL NOT treat missing imports from the live router alone as deletion proof

#### Scenario: Classify duplicate page forks before relocation
- **WHEN** the project evaluates duplicate or forked page sets such as `Phase4Dashboard` or `TechnicalAnalysis`
- **THEN** it SHALL classify each member as canonical, historical retention, demo/example asset, or independent fork pending judgment
- **AND** it SHALL record retirement conditions before structural cleanup begins

#### Scenario: Classify view-local composables before migration
- **WHEN** the project evaluates `src/views/composables/`
- **THEN** it SHALL distinguish legacy page support, support modules, test-guarded modules, and duplicate-candidates
- **AND** it SHALL NOT bulk-migrate the directory without consumer and lifecycle alignment

