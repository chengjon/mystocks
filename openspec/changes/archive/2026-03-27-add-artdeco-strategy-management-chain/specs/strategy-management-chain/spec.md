## ADDED Requirements

> **历史文档说明**:
> 本文件属于已归档变更留下的历史规格、设计附件或过程材料，用于补充还原当时方案与结构。
> 它不再是当前治理口径或当前实现状态的默认真相源；如与现行 specs、共享规则或代码实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际代码实现为准。


### Requirement: StrategyManagement SHALL provide observable strategy list loading

The system SHALL render strategy list data in `ArtDecoStrategyManagement` with explicit request observability metadata.

#### Scenario: Load strategy list with request trace
- **GIVEN** the StrategyManagement page is opened
- **WHEN** the page requests strategy list data from the configured API source
- **THEN** the page SHALL display a strategy list with loading and empty states
- **AND** the page SHALL display request trace metadata (Request ID and/or processing time)
- **AND** the page SHALL preserve a visible trace placeholder when metadata is unavailable.

### Requirement: StrategyManagement SHALL support REAL-first and MOCK fallback behavior

The system SHALL prioritize REAL data and degrade to MOCK data only when REAL data is unavailable or unusable.

#### Scenario: Fallback to mock data when real source fails
- **GIVEN** the real strategy endpoint fails or returns unusable payload
- **WHEN** the page completes its fetch attempt
- **THEN** the page SHALL render fallback mock strategy data
- **AND** the UI SHALL explicitly indicate the current data source as MOCK
- **AND** the user SHALL still be able to browse strategy rows.

#### Scenario: Keep REAL empty state when API succeeds with no records
- **GIVEN** the real strategy endpoint succeeds with a valid empty list
- **WHEN** the page renders the response
- **THEN** the page SHALL show a REAL empty state
- **AND** the system SHALL NOT switch to MOCK fallback.

### Requirement: StrategyManagement SHALL support strategy lifecycle actions

The system SHALL provide row-level lifecycle controls for strategy runtime state transitions.

#### Scenario: Change strategy runtime status
- **GIVEN** a strategy row is displayed in StrategyManagement
- **WHEN** the user executes start, stop, pause, or resume
- **THEN** the corresponding lifecycle API SHALL be called
- **AND** the row status SHALL update after success
- **AND** on failure, the UI SHALL keep prior status and show actionable error feedback.

### Requirement: StrategyManagement SHALL support strategy CRUD flows

The system SHALL allow users to create, edit, and delete strategies with consistent state updates.

#### Scenario: Create and edit strategy configuration
- **GIVEN** the user opens strategy create or edit interaction
- **WHEN** the user submits valid strategy fields and parameters
- **THEN** the system SHALL persist the strategy through API
- **AND** the StrategyManagement list SHALL reflect the updated record without requiring full page reload.

#### Scenario: Delete strategy with confirmation
- **GIVEN** a strategy exists in the list
- **WHEN** the user confirms delete action
- **THEN** the system SHALL remove or deactivate the strategy according to API semantics
- **AND** the list SHALL refresh the strategy visibility state.

### Requirement: StrategyManagement SHALL provide cross-tab handoff consistency

The system SHALL provide consistent navigation and context handoff from StrategyManagement to related strategy tabs.

#### Scenario: Navigate from strategy row to parameter, signal, or backtest tab
- **GIVEN** the user selects a strategy row in StrategyManagement
- **WHEN** the user triggers parameter, signal, or backtest entry
- **THEN** the target tab SHALL receive the selected `strategyId`
- **AND** the target tab SHALL load data scoped to that strategy context
- **AND** strategy status changes from management actions SHALL be reflected consistently across tabs.
