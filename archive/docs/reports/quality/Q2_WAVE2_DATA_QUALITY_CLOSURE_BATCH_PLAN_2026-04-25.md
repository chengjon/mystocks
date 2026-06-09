# Q2 Wave 2 Batch Plan: Data Quality Ownership Closure

Date: 2026-04-25
Mode: single-CLI execution planning
Related change: `openspec/changes/plan-q2-optimization-closure-program/`
Primary inputs:
- `docs/reports/quality/Q2_PHASE_C_DATA_QUALITY_UNIFICATION_2026-04-25.md`
- `docs/reports/quality/Q2_CORE_CLOSURE_EXECUTION_SEQUENCE_2026-04-25.md`
- `openspec/changes/plan-q2-optimization-closure-program/specs/data-quality-governance/spec.md`

## Objective

Wave 2 is the ownership-closure wave for data quality. Its job is not to build every future data-governance capability. Its job is to make one canonical quality model operational across validation, monitoring, governance, and repair-related follow-up.

## Scope

### In scope
- canonical responsibility split for validation, monitoring, governance, and repair
- classification of overlapping data-quality modules
- storage-specific quality concern modeling for TDengine and PostgreSQL or TimescaleDB paths
- explicit ingestion-quality gate definition
- explicit gap handling for repair or backfill ownership

### Out of scope
- database engine replacement
- broad observability redesign
- full lineage platform expansion
- downstream trading-safety controls
- unrelated backend composition refactors beyond Wave 1 dependencies

## Current Truth To Preserve

- canonical validation surface: `src/core/data_quality_validator.py`
- canonical monitoring surface: `src/monitoring/data_quality_monitor.py`
- canonical governance or reporting surface: `src/data_governance/quality.py`
- compatibility-retained or specialized surfaces:
  - `src/core/data_source/data_quality_validator.py`
  - `web/backend/app/services/data_quality_monitor.py`
- explicit unresolved gap: repair or backfill ownership is not yet first-class

## Recommended Batch Sequence

### Batch 1: Canonical Model And Vocabulary Lock

Goal:
- stop further semantic drift between multiple quality vocabularies

Expected edits:
- governance docs
- quality model notes
- terminology alignment between validation, monitoring, and governance surfaces

Success criteria:
- one declared quality model exists for completeness, accuracy, timeliness, consistency, anomaly handling, and temporal alignment
- overlapping validator vocabularies are explicitly classified as canonical or specialized

Verification:
- docs and spec text use one quality vocabulary
- no maintained guidance implies multiple equal canonical quality models

### Batch 2: Ownership Classification And Boundary Marking

Goal:
- give every current quality surface one role and stop blended responsibility growth

Expected edits:
- module classification notes
- compatibility annotations
- service-boundary documentation

Success criteria:
- validation, monitoring, governance, and repair each have one declared ownership position
- backend service quality APIs are clearly treated as operational delivery surfaces rather than domain truth
- compatibility-retained validators are marked as helper or transitional rather than peer canonical surfaces

Verification:
- targeted file and doc review confirms every known quality module has a declared role
- no new blended “monitor-and-validate-and-report” truth surface is introduced

### Batch 3: Ingestion Gate And Storage-Specific Quality Rules

Goal:
- make the quality model actionable at data-entry boundaries

Expected edits:
- ingestion-quality gate definition
- dataset-family quality requirements
- storage-specific and cross-storage rule documentation

Success criteria:
- TDengine-oriented concerns, PostgreSQL-oriented concerns, and cross-storage alignment concerns are explicitly modeled
- temporal alignment and repair or fallback expectations are not left implicit

Verification:
- quality rules mention storage-specific concerns for multi-engine data
- cross-storage consistency expectations are documented for derived datasets

### Batch 4: Repair And Backfill Gap Capture

Goal:
- make the missing ownership visible without pretending it is already implemented

Expected outputs:
- explicit follow-up list for:
  - repair ownership
  - re-fetch and reconcile policy
  - backfill workflow responsibility
  - fallback-source handling

Success criteria:
- repair or backfill remains visible as an explicit gap or bounded follow-up
- no completion statement implies that recovery workflows are already closed

## Suggested Commit Cadence

Recommended micro-batch rhythm:

1. canonical quality vocabulary lock
2. module ownership classification
3. ingestion gate and storage-specific rule alignment
4. repair or backfill gap capture

Practical commit count:
- minimum: 3 commits
- likely: 4 to 6 commits

## Validation Standard For Wave 2

Wave 2 should claim ownership closure only when:

1. one canonical quality model is declared
2. validation, monitoring, governance, and repair roles are explicitly separated
3. compatibility-retained quality surfaces are clearly scoped
4. storage-specific concerns for dual-engine data are documented and testable
5. repair or backfill remains explicit as either owned work or an acknowledged gap

## Risks During Execution

### 1. Semantic churn risk
Wave 2 can stall if too many existing quality vocabularies are preserved as equal truths. The plan should force classification, not indefinite coexistence.

### 2. Hidden coupling risk
`src/core/data_quality_validator.py` currently triggers monitoring behavior. Untangling that boundary may reveal side effects that later need implementation care.

### 3. False completeness risk
Declaring a quality model without making repair or backfill status explicit would overstate closure.

## Recommended Next Action After Planning

If implementation starts, begin with Batch 1 and Batch 2. Do not mix Wave 2 ownership closure with Wave 3 trading-safety work in the same branch segment.
