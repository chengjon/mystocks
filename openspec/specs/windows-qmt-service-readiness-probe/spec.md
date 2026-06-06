# windows-qmt-service-readiness-probe Specification

## Purpose
Define the read-only Windows `qmt` / `miniQMT` service readiness probe contract for validating L1/L2/L3 readiness evidence from WSL before formal cross-project contract acceptance.
## Requirements
### Requirement: Read-Only Windows qmt Service Readiness Entry Point
The repository SHALL provide a read-only Windows `qmt` / `miniQMT` service readiness probe that
operators can run from `WSL 上的 Ubuntu 24.04.4 LTS` before attempting any formal contract
acceptance sequence.

#### Scenario: Operator probes Windows qmt readiness
- **WHEN** an operator launches the Windows `qmt` service readiness probe
- **THEN** the probe SHALL validate local configuration and remote `/health` reachability
- **AND** it SHALL emit a machine-readable readiness verdict
- **AND** it SHALL not trigger `qmt/submit_order` or any `task/result` smoke path

### Requirement: L1 L2 L3 Readiness Verdict Semantics
The readiness probe SHALL classify the Windows-side service against the documented `L1 / L2 / L3`
gates instead of returning an unstructured pass/fail string.

#### Scenario: Readiness evidence is incomplete
- **WHEN** remote `/health` is unreachable, malformed, or missing required disclosure fields
- **THEN** the probe SHALL record which readiness level failed
- **AND** it SHALL preserve explicit issues describing the missing evidence

#### Scenario: Readiness evidence is sufficient for first acceptance
- **WHEN** the Windows-side service satisfies the documented `L1 / L2 / L3` contract requirements
- **THEN** the probe SHALL mark those levels as satisfied
- **AND** it SHALL make clear that the result is a pre-acceptance readiness verdict, not broker
  lifecycle proof

### Requirement: Standard Readiness Artifacts
The readiness probe SHALL preserve its verdict in standard report artifacts so operators can review
the latest readiness state and compare runs manually if needed.

#### Scenario: Readiness probe completes
- **WHEN** the readiness probe exits with success, partial readiness, or failure
- **THEN** it SHALL emit a JSON summary with verdict details, issues, and artifact paths
- **AND** it SHALL write both a timestamped report artifact and a stable latest pointer
