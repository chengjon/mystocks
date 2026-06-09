# Q2 Wave 2 Ingest Gate And Storage Rules

Date: 2026-04-26
Wave: `Wave 2 / Data Quality Ownership Closure`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE2_DATA_QUALITY_CLOSURE_BATCH_PLAN_2026-04-25.md`
- `docs/reports/quality/Q2_PHASE_C_DATA_QUALITY_UNIFICATION_2026-04-25.md`
- `src/core/data_classification.py`
- `src/core/data_quality_validator.py`
- `src/monitoring/data_quality_monitor.py`

## Purpose

This note closes Wave 2 Batch 3 at the rule-model layer.

It defines where data-quality ingest gates should conceptually execute and how quality concerns should be split across TDengine-oriented, PostgreSQL-oriented, and cross-storage paths.

It does not claim that all of these gates are already enforced in one unified runtime pipeline.

## Canonical Ingest-Gate Position

The canonical ingest-gate owner for dataset-entry validation should be the validation layer, not the API layer and not the monitoring layer.

Current Q2 closure interpretation:

- gate owner: `src/core/data_quality_validator.py`
- gate invocation can happen from adapters, sync jobs, ingestion flows, or service orchestration
- monitoring is downstream of validation and should record outcomes, thresholds, and alerts
- API routes and service modules may expose or orchestrate quality behavior, but they do not become the canonical gate owner

## Gate Stages

The intended quality-gate sequence for market-data ingestion should be:

1. schema and required-field validation
2. value-rule and domain-rule validation
3. dataset-family-specific validation
4. storage-target-specific checks
5. monitoring/logging and alert emission
6. persistence acceptance or rejection
7. explicit follow-up for repair/backfill if the gate fails and recovery is required

## Dataset-Family Mapping

Based on `src/core/data_classification.py`, the quality model should be interpreted conservatively as follows:

### TDengine-oriented datasets

Primary examples:
- `TICK_DATA`
- `MINUTE_KLINE`
- `DEPTH_DATA`
- `ORDER_BOOK_DEPTH`
- `LEVEL2_SNAPSHOT`
- `INDEX_QUOTES`

Primary concerns:
- freshness and delayed ingest
- timestamp monotonicity or out-of-order arrival detection
- duplicate tick or minute writes
- symbol, market-session, and interval sanity
- realtime completeness within a bounded arrival window

### PostgreSQL / TimescaleDB-oriented datasets

Primary examples:
- `DAILY_KLINE`
- `TECHNICAL_INDICATORS`
- `QUANTITATIVE_FACTORS`
- `MODEL_OUTPUTS`
- `TRADING_SIGNALS`
- `BACKTEST_RESULTS`
- `RISK_METRICS`
- reference and metadata classes such as `SYMBOLS_INFO` and `TRADE_CALENDAR`

Primary concerns:
- required-column completeness
- historical window completeness
- derived-table recomputation lag
- reference-data integrity
- stable primary-key or idempotent-upsert semantics
- lineage visibility for derived outputs

### Cross-Storage Alignment Concerns

When datasets cross the TDengine and PostgreSQL boundary, the quality model must explicitly account for:

- minute or tick input windows aligning with downstream daily or derived datasets
- freshness differences between realtime data and persisted derived outputs
- dataset lineage linking downstream aggregates to upstream source windows
- temporal alignment when one strategy or report depends on both engines
- explicit treatment of partial-day versus end-of-day completeness

## Storage-Specific Rule Guidance

### TDengine Rule Class

TDengine-oriented quality rules should emphasize:

- `timeliness`: whether market data is arriving within the allowed latency window
- `sequence integrity`: whether timestamps are ordered or acceptably bounded when out of order
- `duplication control`: whether repeated tick/minute writes remain within tolerance
- `session validity`: whether rows fall inside expected market or collection sessions

### PostgreSQL / TimescaleDB Rule Class

PostgreSQL-oriented quality rules should emphasize:

- `completeness`: whether required daily or derived records exist for the expected window
- `accuracy`: whether transformed or recomputed outputs satisfy business rules
- `governance traceability`: whether reports and factors can be linked to source inputs
- `rebuild visibility`: whether recomputation lag or stale derived data is measurable

### Cross-Storage Rule Class

Cross-storage quality rules should emphasize:

- `alignment`: whether datasets derived from TDengine inputs are synchronized with PostgreSQL outputs
- `window integrity`: whether the upstream input window is explicit and complete enough for downstream derivation
- `consistency`: whether parallel representations of market state do not materially diverge beyond allowed tolerances

## Acceptance Semantics

The Q2 closure line should use these conservative ingest outcomes:

- `accept`
  - dataset passes entry validation and storage-specific checks
- `accept_with_warning`
  - dataset is admitted but monitoring must record a warning and follow-up expectation
- `reject`
  - dataset violates a hard validation or storage rule and should not be treated as trusted input
- `defer_to_repair`
  - dataset cannot be trusted now and needs explicit repair/backfill ownership

`defer_to_repair` is a governance outcome, not proof that repair logic already exists.

## Explicit Non-Claims

This batch does not claim that:

- one unified ingest pipeline already invokes all of these stages
- TDengine and PostgreSQL quality rules are fully encoded in runtime policy
- cross-storage consistency checks already run automatically for all derived datasets
- repair/backfill ownership has been implemented

## Follow-Up Implications

Any later implementation batch should preserve the following constraints:

- do not move canonical gate ownership into API routers
- do not make monitoring the new validation owner
- do not add another parallel validator vocabulary for storage-specific rules
- if repair/backfill is introduced, assign one canonical owner and one explicit trigger path
