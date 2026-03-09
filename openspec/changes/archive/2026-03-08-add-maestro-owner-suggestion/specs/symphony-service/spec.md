## ADDED Requirements

### Requirement: Advisory Owner Suggestion

The system SHALL provide an advisory owner suggestion capability for the main CLI, using repository
ownership rules and task path hints to recommend likely owners without automatically assigning them.

#### Scenario: Suggest owner from file ownership matches
- **WHEN** an operator requests an owner suggestion for a task
- **THEN** the system evaluates `.FILE_OWNERSHIP` matches against the provided or derived task paths
- **AND** returns a ranked owner suggestion with reasons

#### Scenario: Keep assignment explicit
- **WHEN** the system produces an owner suggestion
- **THEN** the suggestion does not automatically modify assignment state
- **AND** the operator still decides whether to apply the recommendation
