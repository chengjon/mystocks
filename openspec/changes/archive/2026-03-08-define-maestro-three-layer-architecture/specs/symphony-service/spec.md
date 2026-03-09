## ADDED Requirements

### Requirement: Stable Layered Extraction Boundary

The system SHALL provide a stable compatibility namespace for future extraction and SHALL define a
three-layer architecture that separates generic orchestration runtime concerns from multi-CLI
collaboration concerns and repository-specific profile concerns.

#### Scenario: Expose long-term runtime namespace
- **WHEN** a caller imports the long-term orchestration namespace
- **THEN** the repository exposes a `maestro` compatibility namespace
- **AND** existing `symphony` imports remain valid during the migration period

#### Scenario: Expose three architectural layers
- **WHEN** a caller inspects the runtime architecture metadata
- **THEN** the system exposes `kernel`, `collab`, and `profiles` as the three long-term layers
- **AND** the MyStocks repository profile defines the formal responsibility model for human, main CLI, worker CLI, and runtime
