# Q2 Wave 2 Repair Backfill Gap Capture

Date: 2026-04-26
Wave: `Wave 2 / Data Quality Ownership Closure`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE2_DATA_QUALITY_CLOSURE_BATCH_PLAN_2026-04-25.md`
- `docs/reports/quality/Q2_PHASE_C_DATA_QUALITY_UNIFICATION_2026-04-25.md`
- `docs/reports/quality/Q2_WAVE2_OWNERSHIP_BOUNDARY_CAPTURE_2026-04-26.md`
- `docs/reports/quality/Q2_WAVE2_INGEST_GATE_AND_STORAGE_RULES_2026-04-26.md`

## Purpose

This note closes Wave 2 Batch 4 by making the repair/backfill gap explicit.

It does not implement recovery workflows. It defines the missing ownership and trigger space so later work can be planned without overstating current closure.

## Current Gap Statement

The current repository contains validation, monitoring, and governance/reporting surfaces for data quality, but it does not yet expose one canonical first-class owner for:

- repair after failed validation
- historical backfill after incomplete ingest
- cross-source reconcile after divergence detection
- fallback-source substitution after upstream data degradation

Q2 closure must therefore treat repair/backfill as an explicit unresolved capability, not as an implied extension of monitoring.

## What Exists Today

Current repo truth supports:

- validate
- score
- alert
- report

Current repo truth does not yet establish one canonical recovery workflow that:

- decides whether to retry, reject, or reconcile
- owns the recovery state machine
- records repair intent and execution status
- closes the loop from alert to restored data trust

## Why This Must Stay Explicit

If repair/backfill remains unnamed, later work will drift toward one of three failure modes:

- monitoring silently becoming the repair owner
- service/API code inventing ad hoc retry and patch behavior
- data-source-specific helpers becoming parallel truth surfaces

That would directly reopen the ownership drift Wave 2 is trying to close.

## Required Future Ownership Decision

Any future repair/backfill implementation should assign:

- one canonical owner
- one trigger contract
- one persistence or audit trail for repair execution
- one relationship to validation and monitoring outcomes

The future owner may live in a dedicated recovery module, but it should not be split across API routes, monitoring services, and source-specific validators.

## Trigger Conditions To Preserve

The following conditions should be treated as canonical candidates for future repair/backfill triggers:

- validation rejection because of missing required fields
- freshness breach beyond an accepted recovery threshold
- duplicate or out-of-order ingest severe enough to break dataset trust
- incomplete historical window in PostgreSQL or TimescaleDB-derived datasets
- cross-storage divergence between TDengine-origin inputs and downstream persisted outputs
- upstream-source degradation requiring fallback-source substitution or deferred reconciliation

## Conservative Outcome Model

Until a future owner is implemented, quality failures should be interpreted conservatively:

- `warning`
  - monitor and report, but no claim of automated recovery
- `reject`
  - do not trust the dataset, and require manual or future-owned remediation
- `defer_to_repair`
  - governance marker only; not proof of an implemented workflow

## Non-Claims

This gap capture intentionally does not claim:

- automated retry exists
- source fallback is governed by one canonical repair contract
- backfill orchestration is implemented
- reconcile workflows exist for cross-storage divergence
- alert acknowledgment closes the data-quality incident

## Recommended Next Follow-Up

The next approved work item after Wave 2 should decide whether repair/backfill belongs to:

- a dedicated data-recovery application service
- an ingestion orchestration layer with explicit recovery state
- another approved bounded module

But the next phase should make that choice explicitly before implementation begins.
