# Q2 Delivery Discipline: Single-CLI Sequence

Audit date: 2026-04-25
Related change: `openspec/changes/plan-q2-optimization-closure-program/`
Primary references:
- `docs/reports/quality/MYSTOCKS_PHASE_EVALUATION_2026Q2.md`
- `docs/reports/quality/Q2_CLOSURE_PROGRAM_SPEC_REVIEW.md`
- `docs/guides/multi-cli-tasks/MONGO_MULTICLI_COORDINATION_GUIDE.md`
- `architecture/STANDARDS.md`

## Purpose

This report closes the delivery-discipline portion of the Q2 closure program. The goal is not to reject multi-CLI coordination forever. The goal is to prevent core truth-setting work from being fragmented before the repo has one agreed source-of-truth for realtime delivery, backend composition, data-quality ownership, trading safety gates, and function-tree completion evidence.

## Conclusion

The Q2 core closure program should continue as a single-CLI, staged, sequential sequence until the architecture truths from Phases A-E are implementation-locked.

Mongo-backed multi-CLI coordination is currently a follow-up tool, not the default execution model for the core closure waves.

## Why Single-CLI Is The Correct Default

### 1. Current closure work is high-coupling
- Realtime transport truth and backend composition truth are cross-cutting and share overlapping backend entrypoints.
- Data-quality unification and trading-safety hardening both touch governance language, service boundaries, and production-claim semantics.
- Function-tree evidence hardening depends on the exact outcomes of the earlier truth-setting waves.

### 2. The repo still contains compatibility-retained surfaces
- `web/backend/app/app_factory.py` is not equivalent to `web/backend/app/main.py`.
- Socket.IO-related components exist, but the canonical public runtime transport remains native FastAPI WebSocket routing.
- Data-quality capability still spans canonical and compatibility-oriented modules.

These are not good conditions for parallel writers to redefine truth in separate branches.

### 3. Multi-CLI control-plane value is real, but premature here
- The Mongo control plane is useful when work items have stable ownership, bounded paths, and independent acceptance checks.
- The Q2 closure core is still deciding those ownership boundaries.
- Parallelizing before those decisions are locked would convert governance uncertainty into merge churn.

## Recommended Single-CLI Wave Order

### Wave 1: Truth-locking implementation
- Align runtime-facing backend composition to the canonical source-of-truth selected in Phase B.
- Keep non-canonical composition paths explicitly compatibility-retained until retirement gates are satisfied.
- Do not allow new runtime-only behavior to split across parallel entrypoints.

### Wave 2: Data-quality ownership closure
- Implement the validation / monitoring / governance split selected in Phase C.
- Make repair or backfill ownership explicit instead of leaving it implicit.
- Record storage-specific quality concerns for TDengine / PostgreSQL or any later multi-engine path.

### Wave 3: Trading-safety blocking controls
- Add idempotent submission, pre-execution risk gating, confirmation enforcement, and durable audit binding before any stronger trading claim is made.
- Keep execution-capable paths classified as `experimental` until those gates are verifiably closed.

### Wave 4: Evidence-backed completion closure
- Update function-tree completion semantics and related governance documents to reflect the evidence model defined in Phase E.
- Bind completion claims to implementation, verification, runtime, and safety/governance evidence.

## Work That Must Stay Single-CLI Until Truths Are Locked

- Canonical backend composition selection and convergence
- Realtime transport truth selection and registry updates
- Cross-module data-quality responsibility reassignment
- Trading-safety policy classification and production-eligibility wording
- Function-tree completion criteria changes that depend on the above outcomes

## When Multi-CLI Or Mongo Coordination Becomes Safe

Multi-CLI work may be introduced only after all of the following are true:

1. The canonical truth for the target surface is already documented and approved.
2. The write scope can be partitioned without overlapping ownership of the same truth source.
3. Acceptance checks are local and objective for each work item.
4. Compatibility-retained layers are not being redefined in parallel.
5. A main CLI remains responsible for final integration and status judgment.

## Good Candidates For Later Multi-CLI Follow-Up

- isolated documentation backfill after canonical truth is locked
- standalone test expansion against already-set contracts
- bounded adapter cleanup with explicit allowed-path ownership
- report generation, evidence formatting, or low-risk verification support tasks

## Work That Should Still Avoid Multi-CLI Even Later

- redefining runtime composition truth
- changing canonical realtime transport policy
- changing trading production-eligibility criteria
- moving closure evidence ownership between governance capabilities

## Deferred Follow-Up Items That Must Stay Explicit

The following items remain valid, but are not part of the Q2 core closure completion claim:

- observability-specific spec expansion and architecture-diagram enrichment
- database simplification evaluation such as TimescaleDB-only replacement analysis
- HA, failover, circuit-breaking, and broader deployment-resilience programs
- GPU positioning and workload-mode clarification beyond current governance wording
- use of Mongo + multi-CLI as a default delivery model for cross-cutting closure waves

## Decision Record

### Accepted
- single-CLI first for core Q2 closure waves
- Mongo multi-CLI only after truth-locking and write-scope stabilization
- deferred items must remain visible as follow-up, not implied as closed by the Q2 proposal

### Rejected For Current Core Wave
- starting Q2 core closure as multi-CLI parallel implementation
- treating Mongo coordination capability as sufficient justification for parallelizing unresolved architecture truths
- folding deferred P2 or P3 items into Q2 closure claims without separate evidence

## Final Assessment

The delivery discipline question is now resolved at the proposal level:

- single-CLI sequential execution is the canonical path for the Q2 core closure program
- multi-CLI is permitted later only as a constrained follow-up mode
- deferred work remains visible and intentionally out of the Q2 core completion claim
