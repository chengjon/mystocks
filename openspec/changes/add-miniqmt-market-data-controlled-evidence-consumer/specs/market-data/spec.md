## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: miniQMT Release Dataset Consumption

The system SHALL consume miniQMT Market Data Platform datasets only through explicit immutable release identity and release artifacts.

#### Scenario: Dataset identity is explicit

- **GIVEN** a MyStocks operator starts a miniQMT market-data evidence run
- **WHEN** the run is configured
- **THEN** the run SHALL require an explicit `dataset_version`
- **AND** it SHALL reject missing dataset identity
- **AND** it SHALL reject `latest` as a dataset identity

#### Scenario: Manifest identity is captured

- **GIVEN** a miniQMT release manifest is loaded
- **WHEN** MyStocks prepares a dry-run import rehearsal
- **THEN** the run SHALL record `dataset_version`, `lineage_id`, `payload_hash`, `rows_hash`, `schema_version`, `quality_status`, and `maturity`
- **AND** the run SHALL fail before rehearsal if any required identity field is missing

#### Scenario: Release artifact is verified

- **GIVEN** a release manifest references one or more artifacts
- **WHEN** MyStocks selects an artifact for dry-run import rehearsal
- **THEN** it SHALL prefer Parquet artifacts when available
- **AND** it MAY use JSON or CSV artifacts for development or fixture mode
- **AND** it SHALL calculate SHA-256 for the selected artifact bytes
- **AND** it SHALL compare the calculated hash with the manifest artifact hash
- **AND** it SHALL fail before rehearsal on hash mismatch

#### Scenario: Published manifest and artifact pair is consumed

- **GIVEN** miniQMT provides a published dataset manifest and Parquet artifact path
- **WHEN** MyStocks loads the manifest through local published dataset mode
- **THEN** it SHALL verify the Parquet artifact SHA-256 against the manifest
- **AND** it SHALL preserve the manifest `lineage_id`, `payload_hash`, `rows_hash`, `quality_status`, and `maturity`
- **AND** it SHALL support Parquet row reading for the dry-run rehearsal

#### Scenario: Internal miniQMT state is not consumed

- **GIVEN** a manifest or operator input references a raw, candidate, job, or other internal miniQMT path
- **WHEN** MyStocks evaluates the artifact reference
- **THEN** the run SHALL fail closed
- **AND** it SHALL not build a dry-run conclusion from miniQMT internal state.

### Requirement: miniQMT Dry-Run Import Rehearsal

The system SHALL provide a dry-run import rehearsal for miniQMT market-data release artifacts without writing formal MyStocks market-data tables.

#### Scenario: Daily kline rehearsal maps rows

- **GIVEN** a verified `kline_daily` release artifact
- **WHEN** MyStocks performs the P0 dry-run import rehearsal
- **THEN** the artifact rows SHALL be mapped into the `DataClassification.DAILY_KLINE` field mapping
- **AND** the result SHALL include row count, field mapping version, sample comparison summary, and dry-run status
- **AND** the result SHALL identify the database target as `dry-run-only`

#### Scenario: Formal storage is not written

- **GIVEN** a dry-run import rehearsal is executing
- **WHEN** the rehearsal completes
- **THEN** it SHALL not write formal PostgreSQL market-data tables
- **AND** it SHALL not write formal TDengine market-data tables
- **AND** it SHALL not write formal Redis market-data caches
- **AND** any attempted formal write SHALL fail the evidence run.

#### Scenario: Template-only evidence is rejected

- **GIVEN** an evidence run is requested
- **WHEN** no artifact rows were actually read or no dry-run rehearsal was executed
- **THEN** MyStocks SHALL reject evidence generation
- **AND** it SHALL report the run as failed.
