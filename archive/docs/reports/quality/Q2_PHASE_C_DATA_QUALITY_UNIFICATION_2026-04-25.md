# Q2 Phase C Data Quality Unification Audit

Date: 2026-04-25
Scope: `plan-q2-optimization-closure-program` Phase C
Mode: single-CLI sequential audit

## Documents And Code Surfaces Examined
- `docs/reports/quality/MYSTOCKS_PHASE_EVALUATION_2026Q2.md`
- `docs/reports/quality/Q2_CLOSURE_PROGRAM_SPEC_REVIEW.md`
- `docs/reports/quality/Q2_PHASE_A_REALTIME_TRUTH_AUDIT_2026-04-25.md`
- `docs/reports/quality/Q2_PHASE_B_BACKEND_COMPOSITION_CLOSURE_2026-04-25.md`
- `openspec/changes/plan-q2-optimization-closure-program/design.md`
- `openspec/changes/plan-q2-optimization-closure-program/tasks.md`
- `src/core/data_quality_validator.py`
- `src/core/data_source/data_quality_validator.py`
- `src/monitoring/data_quality_monitor.py`
- `src/data_governance/quality.py`
- `src/data_governance/lineage.py`
- `src/monitoring/monitoring_database.py`
- `src/core/data_classification.py`
- `web/backend/app/services/data_quality_monitor.py`
- `web/backend/app/api/data_quality.py`

## Executive Summary
The project does not lack data quality code. It lacks one canonical data quality model and one explicit ownership boundary.

Current repo truth shows four overlapping quality surfaces:

1. `src/core/data_quality_validator.py`
   - content-level validation for stock/realtime datasets
   - tightly coupled to `src.monitoring.data_quality_monitor`
2. `src/core/data_source/data_quality_validator.py`
   - generic validation summary covering logic, business, statistical, and cross-source checks
3. `src/monitoring/data_quality_monitor.py`
   - monitoring, alerting, and monitoring-database persistence
4. `src/data_governance/quality.py`
   - governance-oriented quality dimensions and reports

In addition, backend `web/backend/app/services/data_quality_monitor.py` forms a separate service-side monitoring framework with its own vocabulary and API layer.

## Canonical Model Recommendation

### Recommended responsibility split
- Validation:
  - dataset-level content checks, rule checks, anomaly checks, duplication checks, timestamp/date sanity
- Monitoring:
  - metric logging, alerting, trend aggregation, monitoring DB persistence
- Reporting / Governance:
  - quality dimensions, historical score reporting, lineage-linked governance view
- Repair / Backfill:
  - explicit recovery, re-fetch, reconcile, or fallback workflows

### Recommended canonical owners
- canonical validation surface:
  - `src/core/data_quality_validator.py` for content validation in the core data path
- canonical monitoring surface:
  - `src/monitoring/data_quality_monitor.py`
- canonical governance/reporting abstraction:
  - `src/data_governance/quality.py`
- repair/backfill:
  - not yet implemented as a first-class canonical module and should remain an explicit gap

### Non-canonical or overlapping surfaces
- `src/core/data_source/data_quality_validator.py`
  - useful as a generic checker, but currently overlaps with canonical validation semantics
  - should be classified as compatibility-retained or specialized helper until converged
- `web/backend/app/services/data_quality_monitor.py`
  - backend service health and source quality framework
  - should not be treated as the core domain truth for dataset quality governance

## Key Findings

### 1. Validation and monitoring are coupled but not formally separated
`src/core/data_quality_validator.py` performs validation and immediately logs through `DataQualityMonitor`.

This creates two problems:
- validation cannot be treated as a pure business concern
- monitoring behavior becomes a hidden side effect of content validation

### 2. There are two validator vocabularies
- `src/core/data_quality_validator.py`
  - completeness, accuracy, consistency, duplicates, outliers
- `src/core/data_source/data_quality_validator.py`
  - logic, business, statistical, cross-source

These are not equivalent models, and the repo currently lacks a governing decision about which one is primary.

### 3. Governance quality model is additive but disconnected
`src/data_governance/quality.py` defines four quality dimensions:
- completeness
- accuracy
- timeliness
- consistency

This is the cleanest governance vocabulary, but it is not clearly declared as the system-wide reporting contract over the core validator and monitor.

### 4. Dual-storage concerns are only partially modeled
`src/monitoring/data_quality_monitor.py` explicitly carries:
- `classification`
- `database_type`

and examples refer to:
- `DAILY_KLINE` on `PostgreSQL`
- `TICK_DATA` on `TDengine`

This is useful, but there is no canonical cross-storage rule for:
- temporal alignment between TDengine and PostgreSQL/TimescaleDB datasets
- consistency checks when a derived dataset depends on both storage engines
- explicit storage-specific quality concerns per dataset family

### 5. Repair/backfill is still a governance gap
The Q2 evaluation correctly asked for missing-data repair and recovery handling. Current inspected surfaces mostly stop at:
- validate
- score
- alert
- report

No single repair or backfill module emerged as the canonical owner.

### 6. Backend quality APIs are not the same thing as core quality governance
`web/backend/app/api/data_quality.py` and `web/backend/app/services/data_quality_monitor.py` expose operational quality information for service-side monitoring. They should be treated as delivery/operations surfaces, not as the canonical domain model for quality governance.

## Canonical Data Quality Model For Phase C

The Q2 closure program should use this model:

| Concern | Canonical meaning | Canonical owner |
|---|---|---|
| completeness | required fields, missing values, record presence | validation |
| accuracy | value-rule correctness, OHLC logic, invalid values | validation |
| timeliness | freshness / update delay | monitoring |
| consistency | cross-record, cross-source, and cross-storage consistency | validation + governance |
| anomaly detection | duplicates, outliers, statistical anomalies | validation |
| alerting | threshold breach notification | monitoring |
| historical reporting | score trends and governance reports | governance/reporting |
| repair / fallback | re-fetch, reconcile, backfill, substitute source | explicit gap to be filled later |

## Storage-Specific Quality Concerns

### TDengine-oriented concerns
- realtime freshness
- delayed ingest
- out-of-order timestamp arrival
- duplicate tick/minute writes

### PostgreSQL / TimescaleDB-oriented concerns
- derived table completeness
- daily or factor recomputation lag
- broken historical backfill windows
- metadata/reference-data integrity

### Cross-storage concerns
- TDengine minute/tick data and PostgreSQL derived or daily data time alignment
- consistency between realtime snapshots and persisted downstream aggregates
- traceability of derived datasets to their upstream storage engine and source window

## Classification Decision

### Canonical
- `src/core/data_quality_validator.py` as core validation entrypoint
- `src/monitoring/data_quality_monitor.py` as monitoring and alerting truth
- `src/data_governance/quality.py` as governance/reporting truth

### Compatibility-retained / specialized
- `src/core/data_source/data_quality_validator.py`
- `web/backend/app/services/data_quality_monitor.py`

### Explicit unresolved gap
- repair/backfill ownership is not yet canonicalized

## Recommended Next Steps
1. Bind the OpenSpec data-quality-governance capability to the validation / monitoring / governance split above.
2. Add storage-specific quality concerns to the formal closure evidence for dual-engine datasets.
3. Treat repair/backfill as an explicit next-phase follow-up instead of implicitly assuming it already exists.
4. Avoid adding new parallel validator semantics until the current ownership split is codified.
