## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

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
