# directory-governance Specification

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

### Requirement: Deletion Evidence Gate

The project SHALL block tracked directory deletion and batches deleting three or more documents unless
exact-path, pre-existing, machine-readable deletion governance artifacts authorize the deletion.

#### Scenario: Block directory deletion without pre-existing evidence
- **WHEN** a tracked directory is fully deleted from the repository
- **AND** `HEAD:governance/deletion-evidence.yaml` does not contain an approved exact-path directory entry
- **THEN** the deletion evidence gate SHALL report a blocking error

#### Scenario: Block document batch deletion without per-document evidence
- **WHEN** three or more documents are deleted outside already-deleted directories
- **AND** any deleted document lacks an approved exact-path document entry in `HEAD:governance/deletion-evidence.yaml`
- **THEN** the deletion evidence gate SHALL report a blocking error

#### Scenario: Ignore in-commit evidence for deletion authorization
- **WHEN** a commit or worktree adds deletion evidence in the same unmerged state as the deletion
- **THEN** the deletion evidence gate SHALL resolve evidence from `HEAD`
- **AND** it SHALL NOT treat in-commit evidence as valid authorization

### Requirement: Exact Machine-Readable Deletion Evidence

The project SHALL use one canonical machine-readable deletion evidence registry with exact-path scope.

#### Scenario: Exact path evidence authorizes deletion
- **WHEN** `HEAD:governance/deletion-evidence.yaml` contains an entry whose `path` and `kind` exactly match the deletion target
- **AND** the entry has `status: approved`
- **AND** the entry has `code_path_verdict: safe_to_delete`
- **AND** the entry has `function_tree_verdict` equal to `重复冗余` or `正式下线`
- **THEN** the gate SHALL allow that deletion target

#### Scenario: Wildcard or fuzzy evidence is rejected
- **WHEN** a deletion evidence entry uses wildcard path syntax or parent-scope approximation
- **THEN** the gate SHALL treat that entry as invalid authorization
- **AND** it SHALL continue searching only for exact-path evidence

### Requirement: Emergency Waiver Registry

The project SHALL support emergency deletion waivers through one fixed YAML registry with exact-path scope and expiry.

#### Scenario: Allow exact-path emergency waiver
- **WHEN** `HEAD:governance/waivers/deletion-evidence-waivers.yaml` contains an exact-path waiver for the deletion target
- **AND** the waiver includes user approval metadata, owner, reason, ticket/context, and a future expiry date
- **THEN** the gate SHALL allow that deletion target through waiver mode

#### Scenario: Expired or invalid waiver is rejected
- **WHEN** a waiver is expired, missing required fields, or uses wildcard path syntax
- **THEN** the gate SHALL treat the waiver as invalid
- **AND** it SHALL continue to require normal deletion evidence

### Requirement: Dual Gate Integration

The project SHALL enforce the same deletion evidence rules in both commit-time and Claude Stop workflows.

#### Scenario: Enforce staged deletion gate in pre-commit
- **WHEN** `.pre-commit-config.yaml` or `.githooks/pre-commit` runs on staged changes
- **THEN** the deletion evidence gate SHALL inspect staged deletions
- **AND** it SHALL block staged directory deletion or document batch deletion without valid authorization

#### Scenario: Enforce worktree deletion gate in Stop hook
- **WHEN** the Claude Stop hook runs for the current worktree
- **THEN** it SHALL inspect current staged and unstaged deletions through the shared engine
- **AND** it SHALL block stopping when governed deletions lack valid authorization

### Requirement: Deletion Waiver Audit

The project SHALL provide a non-blocking waiver audit mode in the shared deletion evidence engine so
that expired or soon-expiring emergency waivers become visible before a governed deletion is attempted.

#### Scenario: Audit canonical waiver registry from HEAD
- **WHEN** automation or a developer runs the shared deletion evidence engine in waiver audit mode
- **THEN** it SHALL load `HEAD:governance/waivers/deletion-evidence-waivers.yaml`
- **AND** it SHALL NOT treat staged or worktree-only waiver edits as canonical audit truth

#### Scenario: Classify waiver expiry health with default warning window
- **WHEN** a waiver entry is structurally valid
- **THEN** the audit SHALL classify it as `expired` when `expires_on` is before the audit date
- **AND** it SHALL classify it as `expiring_soon` when `expires_on` is within the next 7 days inclusive
- **AND** it SHALL classify it as `healthy` when `expires_on` is beyond the warning window

#### Scenario: Allow warning window override
- **WHEN** automation invokes waiver audit mode with an explicit warning window override
- **THEN** the audit SHALL use that override instead of the default 7-day warning window

#### Scenario: Keep debt findings non-blocking
- **WHEN** the waiver registry is readable and the audit finds only `expired` or `expiring_soon` waivers
- **THEN** the audit SHALL emit those findings in machine-readable output
- **AND** it SHALL return a success exit code

#### Scenario: Fail on invalid waiver registry content
- **WHEN** the waiver registry cannot be parsed or contains invalid waiver entries
- **THEN** the audit SHALL return a failure exit code
- **AND** it SHALL describe the invalid registry problem in machine-readable output

### Requirement: Scheduled Waiver Audit Alerting

The project SHALL run a scheduled, non-blocking deletion waiver audit and publish GitHub Actions
diagnostics without introducing a second governance logic source.

#### Scenario: Run waiver audit daily and on manual dispatch
- **WHEN** GitHub Actions evaluates the deletion waiver audit workflow
- **THEN** the workflow SHALL support a daily schedule
- **AND** it SHALL support `workflow_dispatch`

#### Scenario: Reuse the shared engine in workflow execution
- **WHEN** the deletion waiver audit workflow runs
- **THEN** it SHALL invoke `scripts/compliance/deletion_evidence_gate.py`
- **AND** it SHALL NOT define a second waiver expiry classification implementation in workflow YAML

#### Scenario: Publish summary and artifact output
- **WHEN** the deletion waiver audit workflow completes
- **THEN** it SHALL publish a GitHub Actions summary containing waiver totals plus expired and expiring-soon counts
- **AND** it SHALL upload the machine-readable audit report as a workflow artifact
