# directory-governance Specification

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。

## Purpose
Define machine-readable directory governance rules, enforcement surfaces, and change-scoped validation
for maintaining repository structure in MyStocks.
## Requirements
### Requirement: Policy-Driven Directory Governance

The project SHALL define directory governance rules in a machine-readable policy file instead of
hardcoding all checks inside shell logic.

#### Scenario: Load repository-owned governance policy
- **WHEN** the directory governance checker starts
- **THEN** it SHALL load a repository-owned policy file
- **AND** it SHALL evaluate directory rules from that policy

#### Scenario: Separate new violations from tolerated legacy debt
- **WHEN** a path matches a tolerated legacy entry in the policy
- **THEN** the checker SHALL report it as a warning
- **AND** it SHALL NOT classify it as a blocking error

### Requirement: Root Directory Guardrails

The project SHALL protect the repository root with explicit allowlists and forbidden artifact rules.

#### Scenario: Reject unexpected root files
- **WHEN** a new non-hidden file appears in the project root
- **AND** it is not listed in the allowed or tolerated root entries
- **THEN** the checker SHALL report a blocking error

#### Scenario: Reject runtime artifacts in the root
- **WHEN** a root-level runtime artifact such as a log, coverage file, or temp file appears
- **THEN** the checker SHALL report a blocking error
- **AND** it SHALL include a recommendation for the correct target location

### Requirement: Recursive Convergence Rules

The project SHALL support recursive path-based rules that flag directories requiring future
convergence without immediately blocking the repository.

#### Scenario: Flag report sprawl as warning
- **WHEN** a path matches a report-sprawl rule such as `docs/completion_reports/**`
- **THEN** the checker SHALL report a warning
- **AND** it SHALL recommend consolidation into `reports/`

#### Scenario: Flag archive or backup sprawl as warning
- **WHEN** a path matches an archive or backup convergence rule
- **THEN** the checker SHALL report a warning
- **AND** it SHALL recommend the target lifecycle location

### Requirement: Stable CLI Contract

The project SHALL preserve a stable command entrypoint for directory checks while enabling richer
structured output.

#### Scenario: Support text output for local use
- **WHEN** a developer runs `scripts/maintenance/check-structure.sh`
- **THEN** the checker SHALL emit a human-readable summary
- **AND** it SHALL return exit code `0` when no blocking errors are present

#### Scenario: Support JSON output for automation
- **WHEN** a developer or CI runs the checker with `--format json`
- **THEN** the checker SHALL emit machine-readable JSON
- **AND** the JSON SHALL include summary counts and individual findings

### Requirement: Delta-Aware Enforcement

The project SHALL support change-scoped directory governance checks so that local hooks and CI can
block newly introduced violations without being blocked by unrelated historical debt.

#### Scenario: Evaluate only staged changes in hook mode
- **WHEN** a developer runs the checker with `--staged`
- **THEN** the checker SHALL evaluate only staged paths
- **AND** it SHALL ignore unrelated existing violations outside that path scope

#### Scenario: Evaluate only changed paths in CI
- **WHEN** CI provides a changed file list via repeated `--path` arguments
- **THEN** the checker SHALL evaluate only those changed paths
- **AND** it SHALL report violations triggered by those paths

### Requirement: Hook and Workflow Integration

The project SHALL wire directory governance into local and CI automation entrypoints.

#### Scenario: Register pre-commit hook
- **WHEN** `.pre-commit-config.yaml` is evaluated
- **THEN** it SHALL include a `directory-governance` local hook
- **AND** that hook SHALL invoke the staged directory governance check

#### Scenario: Register repository hook path entrypoint
- **WHEN** `.githooks/pre-commit` executes
- **THEN** it SHALL delegate to the staged directory governance checker
- **AND** it SHALL support `DISABLE_DIR_STRUCTURE_CHECK=1` for explicit bypass

#### Scenario: Run directory governance in code quality workflow
- **WHEN** `.github/workflows/code-quality.yml` runs on CI
- **THEN** it SHALL execute a changed-files directory governance check
- **AND** it SHALL produce a JSON report artifact for diagnostics

### Requirement: Governed Repository Hygiene Automation

The project SHALL provide canonical repository hygiene entrypoints that align with directory-governance
policy and operate safely by default.

#### Scenario: Preview cleanup actions before mutation
- **WHEN** an operator runs the repository cleanup workflow in dry-run mode
- **THEN** the system SHALL report planned deletions, moves, or archives
- **AND** it SHALL NOT mutate repository state

#### Scenario: Detect oversized artifacts through a canonical monitor
- **WHEN** an operator runs the canonical file-size monitoring entrypoint
- **THEN** the system SHALL report files that exceed configured thresholds
- **AND** it SHALL support machine-readable output for automation

### Requirement: Policy-Aligned Canonical Targets

Directory governance SHALL permit the canonical lifecycle directories required by the hygiene rollout.

#### Scenario: Allow canonical lifecycle targets
- **WHEN** the repository introduces approved lifecycle directories such as `archive/`, `reports/`, or `var/`
- **THEN** the checker SHALL recognize them as governed targets
- **AND** it SHALL NOT classify those canonical targets as unexpected root entries

