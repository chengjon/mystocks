# Q2 Wave 3 Broker Acknowledgement And Reconciliation Implementation Plan

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-27
Mode: single-CLI planning
Related change:
- `openspec/changes/add-broker-acknowledgement-reconciliation-contract/`
Primary inputs:
- `openspec/changes/add-broker-acknowledgement-reconciliation-contract/proposal.md`
- `openspec/changes/add-broker-acknowledgement-reconciliation-contract/design.md`
- `openspec/changes/add-broker-acknowledgement-reconciliation-contract/specs/broker-acknowledgement-reconciliation/spec.md`
- `docs/reports/quality/Q2_WAVE3_IMPLEMENTATION_PROGRESS_2026-04-26.md`
- `src/application/trading/order_mgmt_service.py`
- `src/application/trading/decision_audit.py`
- `src/application/trading/order_state_evidence.py`

## Objective

Define the narrowest safe implementation sequence that moves Wave 3 from local runtime truth
to broker acknowledgement and reconciliation truth without pretending the repository already
has a production-grade broker adapter.

## Current Repo Truth

### 1. Canonical local execution truth exists only at the application-service layer

The strongest verified trading lifecycle path currently runs through:

- `src/application/trading/order_mgmt_service.py`

This path already provides:

- local order creation and lifecycle mutation
- local durable audit evidence
- local order-state evidence
- local cash reservation reconciliation

It is the correct starting line for later broker binding work.

### 2. Existing API entrypoints are not yet canonical broker execution paths

Observed non-canonical or incomplete surfaces:

- `src/interfaces/api/trading_router.py`
  - still returns `501`
  - not suitable as the first broker-truth implementation target
- `web/backend/app/api/trading_runtime.py`
  - intentionally lightweight runtime availability API
  - keeps in-memory demo state and avoids heavy trading dependencies
  - not the broker acknowledgement source of truth
- `src/trading/live_trading_engine.py`
  - describes higher-level realtime orchestration concepts
  - not currently verified as the canonical broker-facing execution chain

### 3. Existing durable ledgers are local, not broker-reconciled

Reusable local evidence surfaces already exist:

- `src/application/trading/decision_audit.py`
- `src/application/trading/order_state_evidence.py`
- `src/application/trading/cash_reservation.py`

These are useful integration points for later broker truth binding, but they currently remain:

- process-local
- repository-local
- intentionally non-distributed
- explicitly not broker truth

## Canonical Target Recommendation

The first implementation wave should target the local application trading path, not the
runtime demo APIs and not the incomplete interface stubs.

Recommended canonical implementation target:

- `OrderManagementService` plus new broker-binding support files under `src/application/trading/`

Recommended first-class extension seam:

- add a broker acknowledgement correlation surface adjacent to:
  - decision audit
  - order-state evidence
  - reservation evidence

Avoid starting with:

- frontend runtime endpoints
- `live_trading_engine` orchestration
- speculative queueing, distributed replay suppression, or broker-specific HA

## Narrow Implementation Sequence

### Batch 1: Broker Path Inventory And Canonical Registry Seed

Goal:
- freeze which path is canonical before writing broker-truth code

Expected edits:
- architecture / quality docs
- broker execution truth registry seed
- trading path classification notes

Success criteria:
- one canonical broker-facing execution candidate is named
- known non-canonical paths are explicitly classified as stub, demo, compatibility-only, or experimental
- no document implies that runtime demo APIs are broker truth

### Batch 2: Local-To-External Order Identity Persistence

Goal:
- persist the correlation between local `order_id` and broker-facing submission identity

Expected edits:
- new correlation ledger under `src/application/trading/`
- runtime config for local broker correlation storage path if needed
- application-path tests around correlation creation and lookup

Success criteria:
- a local submission can remain in an explicit `awaiting broker acknowledgement` state
- external order identity can be attached later without heuristic matching
- no broker-specific business logic is required for the first ledger shape

### Batch 3: Broker Lifecycle Event Envelope

Goal:
- define and persist the minimum broker event shape before state mutation claims get stronger

Expected edits:
- broker lifecycle event DTO / envelope
- ingestion-side correlation helpers
- tests for acknowledgement, reject, cancel, and execution identity preservation

Success criteria:
- broker event ingestion preserves external order identity or correlation token
- source timestamp and available sequencing metadata are preserved
- missing identity is explicitly classified instead of treated as replay-safe

### Batch 4: Divergence Ledger And Review Surface

Goal:
- classify local-vs-broker mismatches without auto-fixing them too early

Expected edits:
- divergence classification model
- durable divergence evidence sink or extension of current audit payload model
- tests for unmatched external order, locally-terminal-externally-open, externally-terminal-locally-open, and quantity divergence

Success criteria:
- divergence categories are machine-readable
- review-required incidents are durable and queryable
- no silent local state rewrite occurs for unsafe mismatches

### Batch 5: Bounded Auto-Resolution And Replay-Suppression Gate

Goal:
- permit stronger behavior only when broker identity evidence is sufficient

Expected edits:
- explicit policy checks on when auto-resolution is allowed
- explicit policy checks on when replay suppression is justified
- tests proving that quantity/price coincidence alone is insufficient

Success criteria:
- replay suppression can only use declared broker-side identity or sequencing fields
- auto-resolution is limited to explicitly authorized divergence classes
- unsupported cases remain auditable review-required incidents

### Batch 6: Residual Gap Capture And Promotion Gate

Goal:
- make the remaining production-readiness gaps explicit after the first broker-truth wave

Expected outputs:
- explicit unresolved-gap report for:
  - real adapter selection
  - broker session / account scoping
  - external sequencing limits
  - HA / distributed delivery semantics
  - operational response workflow

Success criteria:
- no completion report overstates production readiness
- production-eligible promotion criteria remain blocked until broker truth evidence is real

## Testing Strategy

### Keep TDD at the application boundary

The first implementation waves should remain test-first at:

- `tests/ddd/test_phase_7_application.py`

Add new narrow test groups for:

- local-to-external correlation creation
- broker acknowledgement binding
- unmatched external execution classification
- divergence incident retention
- replay suppression refusal when identity is insufficient

### Add isolated unit coverage for new local ledgers

Prefer separate focused unit tests for:

- broker correlation ledger
- divergence classification helpers
- broker lifecycle event envelope normalization

### Do not require live broker integration for the first wave

Early implementation should verify:

- local persistence shape
- correlation behavior
- classification behavior
- audit evidence

It should not require:

- actual broker connectivity
- COM/HID automation
- realtime exchange connectivity

## Acceptance Evidence Before Stronger Claims

The project should not claim replay-safe broker lifecycle handling or production-eligible
trading truth until all of the following exist:

1. canonical broker-facing execution path is published
2. local-to-external order identity binding is durable
3. broker lifecycle events preserve external identity and available sequencing fields
4. divergence classes are durable and auditable
5. replay suppression policy names the broker-side identity basis explicitly
6. unresolved identity gaps remain explicit where the adapter cannot provide enough truth

## What Not To Do Next

Avoid the following in the next micro-batch:

- adding heuristic execution-report dedup based only on `filled_qty`, `price`, or timing
- expanding runtime demo APIs and calling that broker integration
- wiring frontend pages before the backend correlation contract exists
- adding distributed queue semantics before a single canonical broker truth path is stabilized

## Recommended Immediate Next Batch

If implementation planning proceeds, start with:

1. `Batch 1: Broker Path Inventory And Canonical Registry Seed`
2. `Batch 2: Local-To-External Order Identity Persistence`

Do not start with replay suppression logic.
