# windows-qmt-agent-contract-acceptance Specification

## Purpose
Define the local Windows `qmt` / `miniQMT` contract acceptance harness for WSL operators, including remote health preflight, fail-closed mock-provider safety, authenticated/versioned submit-order result smoke, and machine-readable acceptance summaries.
## Requirements
### Requirement: Local Windows qmt Contract Acceptance Entry Point
The repository SHALL provide a local acceptance entry point that can verify a separately deployed
Windows `qmt` service from `WSL 上的 Ubuntu 24.04.4 LTS`.

#### Scenario: Operator runs local acceptance harness
- **WHEN** an operator points the harness at a Windows `qmt` service URL
- **THEN** the harness SHALL check the remote `/health` payload first
- **AND** it SHALL validate the existing authenticated/versioned `qmt/submit_order -> task_id -> result`
  contract through the repo-owned local bridge adapter and live bridge client

### Requirement: Fail-Closed Acceptance Safety Gate
The local acceptance harness SHALL fail closed by default before running a full order-path smoke
against a Windows `qmt` service that is not explicitly advertising a safe mock provider mode.

#### Scenario: Remote provider mode is not mock
- **WHEN** the remote `/health` payload reports `provider_mode` other than `mock`
- **THEN** the harness SHALL stop before the full execute/result smoke
- **AND** it SHALL report the gating reason in a machine-readable summary

### Requirement: Acceptance Summary Artifact
The local acceptance harness SHALL emit a machine-readable summary of the contract verification
attempt.

#### Scenario: Acceptance run completes
- **WHEN** the harness finishes with success or failure
- **THEN** it SHALL report the health payload, normalized receipt payload, normalized result payload,
  verified fields, and any detected issues
- **AND** the summary SHALL make it clear whether the run stopped at the safety gate or completed the
  full contract smoke
