# Q2 Wave 2 Ownership Boundary Capture

Date: 2026-04-26
Wave: `Wave 2 / Data Quality Ownership Closure`
Mode: single-CLI execution
Related plan:
- `docs/reports/quality/Q2_WAVE2_DATA_QUALITY_CLOSURE_BATCH_PLAN_2026-04-25.md`
- `docs/reports/quality/Q2_PHASE_C_DATA_QUALITY_UNIFICATION_2026-04-25.md`

## Purpose

This note closes the Wave 2 ownership-classification batch at the documentation and boundary-marking layer.

It does not claim runtime decoupling is complete. It only locks the intended ownership map so later implementation batches can reduce overlap without re-opening vocabulary drift.

## Canonical Ownership Map

The canonical system-wide ownership split for data quality is:

- validation: `src/core/data_quality_validator.py`
- monitoring: `src/monitoring/data_quality_monitor.py`
- governance/reporting: `src/data_governance/quality.py`

This split is now the canonical interpretation for Q2 closure work and for future follow-up tasks unless a later approved change supersedes it.

## Classified Surfaces

### Canonical Domain Truth

- `src/core/data_quality_validator.py`
  - canonical validation vocabulary and reusable system-level validation rules
- `src/monitoring/data_quality_monitor.py`
  - canonical monitoring truth for data-quality operational measurement and alerting semantics
- `src/data_governance/quality.py`
  - canonical governance/reporting truth for quality scoring, dimensions, and cross-dataset reporting semantics

### Compatibility-Retained / Specialized Surface

- `src/core/data_source/data_quality_validator.py`
  - useful specialized validator surface for adapter-facing or source-scoped checks
  - must not be interpreted as a peer canonical system-wide validation owner
  - may remain during transition, but should not accumulate new cross-system ownership claims without approval

### Operational Delivery Surfaces

- `web/backend/app/services/data_quality_monitor.py`
  - backend/service operational delivery surface
  - useful for service orchestration, transport-facing monitoring flows, and API support
  - not the canonical domain truth for system-wide data-quality governance
- `web/backend/app/api/data_quality.py`
  - API delivery surface for operator-facing inspection and control endpoints
  - not a canonical owner of validation, monitoring, or governance semantics

## Explicit Non-Claims

This batch does not claim that:

- validation and monitoring code paths are already fully decoupled
- service-layer and domain-layer monitor responsibilities are already unified
- all duplicated quality terminology has been eliminated
- repair/backfill is implemented as a first-class capability

## Unresolved Gap

Repair/backfill remains an explicit unresolved ownership gap.

Current Q2 closure language must be interpreted conservatively:
- validation is named
- monitoring is named
- governance/reporting is named
- repair/backfill is still not first-class in the current implementation line

Any later proposal that introduces automated remediation, backfill orchestration, or ingest repair should assign one canonical owner rather than adding another blended quality surface.

## Why This Classification Is Preferred

- It prevents API/service delivery modules from being mistaken for the long-term domain truth.
- It reduces the chance of parallel ownership drift between adapter validators, monitoring services, and governance metrics.
- It preserves current behavior while making future decoupling work much easier to scope.
- It aligns Wave 2 execution with the Phase C audit and with the conservative Q2 function-tree interpretation.

## Follow-Up Direction

The next implementation batch should move from ownership labeling into ingest-gate and storage-specific rule closure:

- define where source-ingest quality gates execute
- define which rules are storage-specific versus source-agnostic
- keep repair/backfill explicitly out of scope unless a separate approved task assigns ownership
