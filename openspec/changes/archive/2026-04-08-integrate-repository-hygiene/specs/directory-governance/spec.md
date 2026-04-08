## ADDED Requirements

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
