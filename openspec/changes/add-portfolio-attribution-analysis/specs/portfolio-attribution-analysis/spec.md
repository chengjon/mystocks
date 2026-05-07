## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: Shared Portfolio Attribution Engine
The system SHALL provide a shared one-period attribution-analysis engine for `Brinson attribution` and `five-factor attribution`.

#### Scenario: Strategy and trade domains use one canonical engine
- **WHEN** attribution is requested for a selected backtest result or for a current/date-scoped portfolio snapshot
- **THEN** the system SHALL normalize the request into shared attribution snapshot models
- **AND** SHALL compute attribution through one canonical shared engine
- **AND** SHALL NOT allow parallel strategy-specific or trade-specific attribution math to become separate truth sources

### Requirement: Fixed First-Batch Benchmark And Factor Set
The system SHALL use a fixed benchmark and a fixed factor set for the first attribution-analysis batch.

#### Scenario: First-batch attribution uses approved fixed baseline
- **WHEN** the system computes first-batch attribution analysis
- **THEN** the benchmark SHALL be `沪深300`
- **AND** the factor set SHALL be `size`, `value`, `momentum`, `volatility`, and `quality`

### Requirement: Strategy Backtest Attribution Entry
The system SHALL expose attribution for selected backtest-result snapshots through the v1 backtest route family.

#### Scenario: Backtest attribution is requested
- **WHEN** the user calls `GET /api/v1/backtest/{backtest_id}/attribution`
- **THEN** the system SHALL return an `AttributionAnalysisResponse` for the selected backtest-result snapshot
- **AND** SHALL hard-fail with an explicit error response if required benchmark, factor, or industry data cannot be resolved for that snapshot

### Requirement: Trade Portfolio Attribution Entry
The system SHALL expose attribution for current and historical portfolio snapshots through the v1 positions route family.

#### Scenario: Current portfolio attribution is requested
- **WHEN** the user calls `GET /api/v1/positions/attribution` without a `date` parameter
- **THEN** the system SHALL return attribution for the current portfolio snapshot by default

#### Scenario: Historical portfolio attribution is requested
- **WHEN** the user calls `GET /api/v1/positions/attribution` with `date=YYYY-MM-DD`
- **THEN** the system SHALL return attribution for the historical portfolio snapshot at that date

#### Scenario: Current portfolio attribution uses stale degradation
- **WHEN** the current portfolio snapshot can be computed but its required enrichment data is stale
- **THEN** the system SHALL return attribution with `stale=true`
- **AND** SHALL include a machine-readable `stale_reason`

#### Scenario: Historical portfolio attribution fails instead of degrading
- **WHEN** the requested historical snapshot cannot be enriched consistently for the requested date
- **THEN** the system SHALL return an explicit error response
- **AND** SHALL NOT downgrade the historical result into a stale partial attribution payload

### Requirement: Attribution Response Contract
The system SHALL align all first-batch attribution endpoints on one response structure.

#### Scenario: Attribution response includes canonical sections
- **WHEN** the system returns attribution analysis
- **THEN** the response SHALL include:
  - `analysis_date`
  - `snapshot_meta`
  - `benchmark_meta`
  - `brinson`
  - `factor_attribution`
  - `top_contributors`
  - `top_detractors`

#### Scenario: Contributor ordering uses contribution value
- **WHEN** the system returns `top_contributors` and `top_detractors`
- **THEN** those lists SHALL be ordered by contribution value
- **AND** SHALL NOT be ordered by raw instrument return alone

### Requirement: Shared Frontend Attribution Surface
The system SHALL provide one shared frontend attribution orchestration and presentation layer reused by both the strategy and trade shells.

#### Scenario: Strategy shell reuses shared attribution surface
- **WHEN** the frontend renders attribution for a selected backtest result
- **THEN** the strategy shell SHALL consume the shared attribution orchestration and shared attribution components

#### Scenario: Trade shell reuses shared attribution surface
- **WHEN** the frontend renders attribution for the current or date-scoped portfolio snapshot
- **THEN** the trade shell SHALL consume the shared attribution orchestration and shared attribution components
- **AND** SHALL NOT own a duplicate attribution math or parallel orchestration layer
