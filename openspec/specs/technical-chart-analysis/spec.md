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

### Requirement: Reviewed Gap Detection On The Existing Technical Pattern Route

The system SHALL expose reviewed gap detections on the existing technical pattern route rather than through a parallel gap-specific endpoint.

#### Scenario: Backend returns a reviewed gap detection
- **WHEN** the backend identifies a reviewed gap event for the requested symbol and period
- **THEN** it SHALL return that detection inside the existing reviewed pattern payload
- **AND** the detection SHALL include a reviewed gap classification of `common_gap`, `breakaway_gap`, `runaway_gap`, or `exhaustion_gap`
- **AND** it SHALL include typed gap fields for `gap_side`, `gap_fill_status`, and `gap_zone`
- **AND** `confidence` SHALL remain a deterministic reviewed heuristic value rather than a fixed `1.0`
- **AND** `anchor_points` SHALL be an empty list for gap detections because `gap_zone` is the renderable geometry

#### Scenario: Backend returns no reviewed gap detection
- **WHEN** no reviewed gap event is identified for the requested symbol and period
- **THEN** the backend SHALL continue to return a reviewed `200` payload
- **AND** it SHALL NOT fabricate gap labels or free-form gap descriptions from request context alone

### Requirement: Gap Detection SHALL Distinguish Direction, Classification, And Fill State

The system SHALL classify each reviewed gap detection by gap category, gap side, and fill state.

#### Scenario: Gap side and fill status are explicit
- **WHEN** a reviewed gap detection is returned
- **THEN** `gap_side` SHALL be either `up` or `down`
- **AND** `gap_fill_status` SHALL be either `open`, `partially_filled`, or `filled`
- **AND** `direction` SHALL remain present as the reviewed chart-bias compatibility field

#### Scenario: Gap confidence uses deterministic reviewed bands
- **WHEN** a reviewed gap detection is returned
- **THEN** `confidence` SHALL be in the inclusive range `0.55-0.95`
- **AND** it SHALL be derived from deterministic reviewed heuristics rather than emitted as a constant sentinel value

#### Scenario: One raw gap emits one reviewed classification
- **WHEN** a single raw gap event satisfies more than one heuristic family
- **THEN** the system SHALL emit at most one reviewed gap classification for that gap event
- **AND** the reviewed classifier SHALL apply a deterministic precedence order instead of returning duplicate category variants

#### Scenario: Reviewed gap classification uses locked heuristic constants
- **WHEN** the reviewed classifier evaluates a raw gap event
- **THEN** it SHALL require `raw_gap_size_ratio >= 0.005`
- **AND** it SHALL evaluate `breakaway` using a `10`-bar pre-gap range window with `pre_range_ratio <= 0.08`
- **AND** it SHALL evaluate `runaway` using a `5`-bar trend window with `trend_strength_ratio >= 0.04`
- **AND** it SHALL evaluate `exhaustion` using a `5`-bar trend window with `trend_strength_ratio >= 0.06`
- **AND** it SHALL apply the reviewed precedence order `exhaustion -> breakaway -> runaway -> common`

### Requirement: Reviewed Gap Detections SHALL Include A Renderable Gap Zone

The system SHALL provide a typed gap zone that the frontend can render directly on the shared K-line overlay surface.

#### Scenario: Gap zone is chart-renderable
- **WHEN** a reviewed gap detection is returned
- **THEN** `gap_zone` SHALL include `start_timestamp`, `end_timestamp`, `upper_value`, and `lower_value`
- **AND** it SHALL always include `filled_at`
- **AND** `filled_at` SHALL be a millisecond epoch timestamp when the reviewed gap has been fully filled
- **AND** `filled_at` SHALL be `null` when the reviewed gap is not fully filled
- **AND** the zone values SHALL be sufficient for the frontend to render a read-only rectangular gap overlay without inventing local geometry

#### Scenario: Gap zone replaces anchor-point geometry
- **WHEN** the frontend receives a reviewed gap detection
- **THEN** it SHALL derive automatic gap rendering from `gap_zone`
- **AND** it SHALL NOT require synthetic gap corner anchor points to reconstruct the geometry

### Requirement: Frontend SHALL Render Reviewed Gap Zones On The Shared Overlay Surface

The frontend SHALL render reviewed gap detections on the same K-line overlay surface used by manual drawings and automatic chart patterns.

#### Scenario: Reviewed gap zone is rendered without breaking manual drawings
- **WHEN** the frontend receives a reviewed gap detection from the existing technical pattern route
- **THEN** it SHALL render the gap as a read-only automatic overlay on the K-line chart
- **AND** manual drawing tools SHALL remain usable on the same chart surface
- **AND** the automatic gap overlay SHALL preserve reviewed provenance such as an `AUTO` marker or equivalent label
- **AND** the frontend reviewed type surface SHALL accept the additive `PatternName` expansion without assuming only the original four chart-pattern values exist

#### Scenario: Automatic gap overlay degrades gracefully
- **WHEN** the reviewed gap request fails or the current frontend chart period is unsupported by the automatic overlay path
- **THEN** the frontend SHALL surface a user-facing unavailable or unsupported state
- **AND** it SHALL NOT clear or disable existing manual drawings as a side effect
