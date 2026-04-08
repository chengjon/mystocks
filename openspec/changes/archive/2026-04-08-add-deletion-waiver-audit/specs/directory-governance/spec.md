## ADDED Requirements

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
