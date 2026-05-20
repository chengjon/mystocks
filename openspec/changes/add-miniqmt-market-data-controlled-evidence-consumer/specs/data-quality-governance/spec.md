## ADDED Requirements

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

### Requirement: MyStocks Controlled Evidence Ledger

The system SHALL persist MyStocks-side controlled evidence run metadata for miniQMT Market Data Platform dry-run import rehearsals.

#### Scenario: Evidence run is persisted

- **GIVEN** MyStocks completes a miniQMT dry-run import rehearsal
- **WHEN** the result is converted into controlled evidence
- **THEN** MyStocks SHALL persist an evidence ledger record in PostgreSQL
- **AND** the record SHALL include dataset identity, artifact identity, consumer build metadata, dry-run status, row count, field mapping version, sample comparison summary, raw report hash, evidence JSON hash, source command, environment summary, retention decision, and created timestamp
- **AND** the record SHALL not include credentials, tokens, account identifiers, full local user paths, database secrets, or raw market rows.

#### Scenario: Ledger is not the miniQMT registry

- **GIVEN** a MyStocks evidence ledger record exists
- **WHEN** miniQMT maturity promotion is evaluated
- **THEN** the MyStocks ledger record SHALL be treated as consumer-side audit evidence only
- **AND** miniQMT SHALL still need to validate, preview, and apply the generated evidence JSON to its own promotion evidence registry.

### Requirement: miniQMT Evidence JSON Generation

The system SHALL generate `mystocks_dry_run` `evidence.v1` JSON from real MyStocks dry-run results.

#### Scenario: Evidence JSON contains required identity and audit fields

- **GIVEN** a dry-run evidence run has passed
- **WHEN** MyStocks generates `evidence.v1` JSON
- **THEN** the JSON SHALL include `schema_version`, `evidence_key`, `evidence_type`, `consumer_system`, `dataset_version`, `lineage_id`, `payload_hash`, `result_summary`, `source_command`, `run_at`, `environment`, `raw_source_file`, `hash_or_size`, `related_function_tree_node`, and `retention_decision`
- **AND** `result_summary` SHALL include `evidence_type`, `consumer_system`, `dataset_version`, `lineage_id`, `payload_hash`, `row_count`, `field_mapping_version`, `writes_performed`, and a `dry_run` object with `passed`, `failed_checks`, `artifact_sha256_verified`, and `placeholder_count`
- **AND** `environment` SHALL include `consumer_system` and `field_mapping_version`
- **AND** `hash_or_size` SHALL include the raw report SHA-256 and byte count, plus the verified artifact SHA-256
- **AND** it SHALL include `related_function_tree_node` to anchor the evidence to the miniQMT function tree
- **AND** `consumer_system` SHALL be `mystocks_spec`
- **AND** `evidence_key` SHALL be `mystocks_dry_run`
- **AND** `evidence_type` SHALL be either `promotion_consumer_dry_run` or `mystocks_market_data_dry_run`.

#### Scenario: Evidence JSON is generated from real dry-run output

- **GIVEN** MyStocks attempts to generate controlled evidence
- **WHEN** dry-run result fields, raw report fields, or generated evidence still contain placeholders or no raw report hash exists
- **THEN** evidence generation SHALL fail closed
- **AND** the evidence ledger SHALL record the failure reason.

#### Scenario: miniQMT preview and apply status is tracked

- **GIVEN** an evidence JSON file is handed to miniQMT operator tooling
- **WHEN** miniQMT validation, preview, or apply results are returned to MyStocks
- **THEN** MyStocks SHALL be able to record the validation result, preview status, apply status, and operator notes against the evidence ledger record
- **AND** those preview/apply statuses SHALL be treated as explicit operator-supplied audit updates, not automatic promotion state.
