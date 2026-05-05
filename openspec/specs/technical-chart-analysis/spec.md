# technical-chart-analysis Specification

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

## Purpose
Define reviewed requirements for interactive K-line manual drawing tools and backend-driven chart
pattern overlays rendered on a shared chart surface.
## Requirements
### Requirement: Interactive K-line Drawing Tools

The system SHALL provide interactive manual drawing tools on the K-line chart surface for the approved MVP tool set: `trendline`, `horizontal line`, and `rectangle`.

#### Scenario: User creates a manual drawing overlay
- **WHEN** a user selects one of the approved drawing tools and completes the required chart points
- **THEN** the system SHALL create a manual overlay on the K-line chart
- **AND** that overlay SHALL be rendered through the reviewed chart overlay surface rather than a separate ad-hoc canvas layer

#### Scenario: User manages manual overlays
- **WHEN** a user selects an existing manual overlay
- **THEN** the system SHALL allow that overlay to be deleted individually
- **AND** the system SHALL provide a `clear all` operation for manual overlays created in the current chart session

### Requirement: Backend-Driven Chart Pattern Detection

The system SHALL treat backend analysis as the only reviewed truth source for automatic chart-pattern overlays.

#### Scenario: Backend returns a reviewed pattern detection
- **WHEN** the backend detects one of the approved MVP patterns for a requested symbol and period
- **THEN** the response SHALL include `pattern_name`, `direction`, `confidence`, and `anchor_points`
- **AND** `confidence` SHALL be a float in the inclusive range `0.0-1.0`
- **AND** each anchor point SHALL be chart-renderable with `role`, `timestamp`, and `value`

#### Scenario: Pattern anchor roles are deterministic
- **WHEN** the backend emits one of the approved MVP pattern detections
- **THEN** `double_top` SHALL provide the ordered anchor roles `left_peak`, `neckline`, `right_peak`
- **AND** `double_bottom` SHALL provide the ordered anchor roles `left_bottom`, `neckline`, `right_bottom`
- **AND** `head_shoulders_top` SHALL provide the ordered anchor roles `left_shoulder`, `left_neckline`, `head`, `right_neckline`, `right_shoulder`
- **AND** `head_shoulders_bottom` SHALL provide the ordered anchor roles `left_shoulder`, `left_neckline`, `head`, `right_neckline`, `right_shoulder`

#### Scenario: No approved pattern is detected
- **WHEN** the backend does not detect any approved MVP pattern
- **THEN** the system SHALL return an empty reviewed detection result
- **AND** it SHALL NOT fabricate or infer pattern labels solely from request context such as symbol shape or period name

#### Scenario: Pattern endpoint distinguishes empty results from service failures
- **WHEN** the reviewed pattern endpoint completes successfully but no approved MVP pattern is found
- **THEN** it SHALL return HTTP `200` with an empty `patterns` list
- **AND** it SHALL mark the payload status as `empty`
- **WHEN** the reviewed pattern analysis path is unavailable
- **THEN** it SHALL return HTTP `503` rather than a fabricated detection payload

### Requirement: Shared Overlay Surface With Provenance

The system SHALL render manual drawings and automatic pattern detections on a shared K-line overlay surface while preserving source provenance.

#### Scenario: Manual and automatic overlays coexist
- **WHEN** a chart contains both user-created drawings and backend-detected patterns
- **THEN** both SHALL render on the same K-line chart surface
- **AND** the UI SHALL visually distinguish manual overlays from automatic pattern overlays through a separate palette and stroke treatment
- **AND** automatic overlays SHALL expose an `AUTO` source label or equivalent provenance marker

#### Scenario: Automatic pattern overlays are protected
- **WHEN** automatic pattern overlays are displayed on the chart
- **THEN** they SHALL be read-only by default
- **AND** they SHALL NOT be implicitly converted into editable manual drawings

### Requirement: Graceful Degradation Between Manual and Automatic Layers

The system SHALL preserve manual drawing usability even when automatic pattern detection is unavailable or returns an error.

#### Scenario: Backend pattern detection is unavailable
- **WHEN** the automatic pattern request fails or returns an unavailable state
- **THEN** the chart SHALL continue to support manual drawing tools
- **AND** the system SHALL surface the automatic-pattern failure as a user-facing loading or error state rather than clearing existing manual overlays
