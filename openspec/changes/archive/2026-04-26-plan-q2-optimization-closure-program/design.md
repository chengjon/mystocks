## Context

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

The Q2 evaluation report identified that MyStocks is not blocked by missing raw capability breadth, but by missing closure across architecture truths, safety contracts, and governance evidence. The most important gaps are cross-cutting: realtime delivery, backend composition truth, data quality unification, trading execution safety, and completion semantics.

These concerns should not be treated as unrelated backlog fragments. They define whether the project can legitimately claim that its Q2 architecture is "closed enough" for reliable follow-on optimization.

`docs/reports/quality/Q2_CLOSURE_PROGRAM_SPEC_REVIEW.md` reviewed this change as "PASS WITH SUGGESTIONS". The design below absorbs the review items that materially strengthen cross-spec consistency and trading safety, while keeping lower-priority observations as deferred follow-up.

## Goals / Non-Goals

### Goals
- convert the Q2 evaluation into a formal closure program
- define canonical truths before implementation-scale refactors
- formalize data quality and trading safety as explicit capability contracts
- require evidence-backed closure instead of narrative completion claims
- keep execution aligned to a single-CLI staged model until truth-setting work stabilizes

### Non-Goals
- immediate full implementation of all proposed optimizations
- immediate database consolidation or storage-engine replacement
- immediate HA or cluster rollout
- immediate multi-CLI parallelization of core cross-cutting refactors

## Decisions

### Decision: Treat Q2 As A Closure Program, Not A Feature Grab
The evaluation items are tightly coupled. Realtime transport, backend composition, safety contracts, and completion semantics all influence later implementation boundaries. The correct move is to create one umbrella proposal with explicit phase gates.

### Decision: Single-CLI First
Core closure waves will alter canonical truths, governance wording, and likely multiple overlapping modules. This is high-coupling work. Running it as Mongo plus multi-CLI from the outset would increase merge churn and truth conflicts. Single-CLI sequencing is the lower-risk path.

### Decision: Multi-CLI Is Deferred, Not Rejected Forever
Parallel execution may become valuable after the canonical truths are decided and the write scopes narrow. At that point, low-coupling work such as isolated documentation backfill, standalone validations, or bounded adapter cleanup can be parallelized safely.

### Decision: Data Quality And Trading Safety Need First-Class Specs
The report's strongest operational concerns are not cosmetic. Data quality and trading safety are system viability constraints. They need their own capabilities rather than being implicit notes inside broader architecture prose.

### Decision: Apply Review Suggestions Selectively
The review identified several non-blocking improvements. The proposal should absorb the ones that improve contract clarity or safety posture now, especially cross-spec realtime consistency, durable trading audit retention, pre-execution risk gates, and multi-storage data quality concerns. It should defer suggestions that mainly affect future spec taxonomy or later observability expansion.

## Phase Model

### Phase A: Realtime Truth Audit
- identify all active realtime transports and delivery paths
- choose one canonical selection policy
- record fallback and coexistence rules

### Phase B: Backend Composition Closure
- identify duplication or ambiguity between backend composition entrypoints
- pick one source-of-truth for app assembly
- define migration and retirement gates for the non-canonical path

### Phase C: Data Quality Unification
- normalize what belongs to validation, monitoring, repair, and evidence
- define a canonical data quality model and ownership boundary
- include storage-specific quality concerns when data spans multiple storage engines

### Phase D: Trading Safety Contract
- formalize idempotency, confirmation, audit logging, and minimum blocking conditions
- formalize durable audit retention and pre-execution risk gates
- separate experimental or simulated trading paths from production-grade claims

### Phase E: Function Tree And Closure Evidence
- replace subjective completion language with criteria-backed evidence
- treat capabilities involving funds movement, position change, or risk decisions as safety-sensitive by rule
- require closure-wave verification artifacts before status upgrades

## Phase A Audit Findings
Audit date: 2026-04-25
Supporting report: `docs/reports/quality/Q2_PHASE_A_REALTIME_TRUTH_AUDIT_2026-04-25.md`

### Current repo truth
- `web/backend/app/main.py` is the runtime composition truth used by uvicorn, Docker, PM2, and helper scripts.
- `web/backend/app/app_factory.py` is currently a compatibility or test-oriented factory rather than the primary runtime assembly path.
- Native FastAPI WebSocket routes registered through `router_registry` are the currently active public realtime transport family.
- `MySocketIOManager` and `RealtimeStreamingService` exist and are tested, but no verified public Socket.IO ASGI mount was found in the runtime application assembly.

### Phase A canonicalization outcome
- canonical backend composition entrypoint: `web/backend/app/main.py`
- canonical current realtime transport family: native FastAPI WebSocket routes
- compatibility-retained realtime transport family: Socket.IO manager and streaming service until public runtime mounting and ownership are explicitly closed

### Phase A implications
- Phase B should formalize `app_factory.py` as delegated compatibility or test factory unless later evidence requires a different role.
- Later realtime implementation work should not claim Socket.IO as canonical until the runtime mount and operational ownership are explicit.
- Connection-management duplication across multiple websocket modules is now a confirmed closure concern rather than a speculative one.

## Phase B Audit Findings
Audit date: 2026-04-25
Supporting report: `docs/reports/quality/Q2_PHASE_B_BACKEND_COMPOSITION_CLOSURE_2026-04-25.md`

### Current repo truth
- `web/backend/app/main.py` is the canonical runtime application composition source-of-truth.
- `web/backend/app/app_factory.py` is not a thin equivalent wrapper around canonical composition.
- `app_factory.py` has drifted into a separate compatibility or test-oriented assembly path with different middleware, exception handling, lifecycle, and shared concern implementations.

### Phase B canonicalization outcome
- canonical runtime composition path: `web/backend/app/main.py`
- compatibility-retained composition path: `web/backend/app/app_factory.py`
- disallowed governance claim: treating both files as peer runtime entrypoints without explicit equivalence proof

### Phase B implications
- Later implementation work should not add new runtime-only behavior to `app_factory.py`.
- Tests that require production-faithful app behavior should progressively align to canonical runtime composition.
- Shared platform concerns such as CSRF, exception handling, and startup wiring should eventually converge behind one composition truth.

## Phase C Audit Findings
Audit date: 2026-04-25
Supporting report: `docs/reports/quality/Q2_PHASE_C_DATA_QUALITY_UNIFICATION_2026-04-25.md`

### Current repo truth
- The repo contains multiple overlapping data quality surfaces rather than a single missing capability.
- `src/core/data_quality_validator.py` is the strongest candidate for canonical content validation.
- `src/monitoring/data_quality_monitor.py` is the strongest candidate for canonical monitoring, alerting, and persistence.
- `src/data_governance/quality.py` is the strongest candidate for governance-oriented quality scoring and reporting.
- `src/core/data_source/data_quality_validator.py` and `web/backend/app/services/data_quality_monitor.py` currently act as overlapping compatibility or specialized surfaces.

### Phase C canonicalization outcome
- canonical validation owner: `src/core/data_quality_validator.py`
- canonical monitoring owner: `src/monitoring/data_quality_monitor.py`
- canonical governance/reporting owner: `src/data_governance/quality.py`
- explicit unresolved gap: repair or backfill ownership is not yet first-class

### Phase C implications
- Future implementation work should preserve the validation / monitoring / governance split rather than reintroducing blended responsibilities.
- Dual-engine datasets must carry storage-specific quality concerns and not only generic quality scores.
- Service-layer quality APIs should be treated as operational delivery surfaces, not as the domain truth for quality governance.

## Phase D Audit Findings
Audit date: 2026-04-25
Supporting report: `docs/reports/quality/Q2_PHASE_D_TRADING_SAFETY_CONTRACT_2026-04-25.md`

### Current repo truth
- The repo has trading domain models, application orchestration, stop-loss execution support, and reusable audit infrastructure.
- No inspected trading path currently qualifies as production-eligible.
- The strongest current trading execution paths are experimental because they do not prove idempotent submission, enforced pre-execution risk gates, enforced confirmation policy, or full audit binding.

### Phase D canonicalization outcome
- canonical safety classification for current execution-capable paths: experimental
- explicit non-satisfied conditions for production eligibility:
  - idempotent submission contract
  - pre-execution risk gate
  - confirmation policy enforcement
  - durable trading audit binding
  - explicit verified external execution path

### Phase D implications
- Future live trading work must not present orchestration scaffolding as production safety proof.
- Risk monitoring and stop-loss execution remain supporting controls, not substitutes for pre-order safety gates.
- Trading audit infrastructure should be treated as incomplete until bound to actual submission decisions.

## Phase E Audit Findings
Audit date: 2026-04-25
Supporting report: `docs/reports/quality/Q2_PHASE_E_FUNCTION_TREE_EVIDENCE_HARDENING_2026-04-25.md`

### Current repo truth
- Existing function-tree governance is strong on catalog structure, stable IDs, and scope mapping.
- Existing function-tree governance is weak on evidence-backed completion semantics.
- `docs/FUNCTION_TREE.md` uses strong status language, including `✅ 完成 = 功能已实现，测试通过，生产可用`, without a formal evidence model behind every such claim.

### Phase E canonicalization outcome
- function-tree completion claims should be interpreted through four evidence layers:
  - implementation
  - verification
  - runtime
  - safety or governance
- safety-sensitive nodes require all four layers before they can support `✅ 完成`
- A-D closure audit reports should be treated as the first formal evidence set for Q2-sensitive status evaluation

### Phase E implications
- Domain percentages in `docs/FUNCTION_TREE.md` should be treated as informative snapshots unless backed by declared criteria.
- Safety-sensitive trading and execution-related nodes must remain conservative until Phase D blocking conditions are closed.
- Realtime, data-quality, and backend-composition claims should align with the earlier Q2 audit outcomes rather than freeform narrative status labels.

## Risks / Trade-offs
- single-CLI sequencing is slower in the short term
- some attractive optimization ideas will remain deferred until core truths are settled
- adding governance requirements increases up-front documentation work

These trade-offs are acceptable because the alternative is parallelizing unresolved architecture truths and then spending more time reconciling contradictions.

## Follow-Up Use Of Multi-CLI
After the program locks the canonical truths, multi-CLI or Mongo coordination may be used for:

- isolated documentation fill-in
- low-coupling verification tasks
- bounded adapter or report updates with independent write scopes

It should not be the default for the initial closure waves defined by this proposal.

## Deferred Follow-Up
- observability-to-business-chain binding remains a valid P2 follow-up but is not folded into this proposal
- if architecture-governance is later restructured, closure-wave evidence may move there from `code-quality`

## Delivery Discipline Findings
Audit date: 2026-04-25
Supporting report: `docs/reports/quality/Q2_DELIVERY_DISCIPLINE_SINGLE_CLI_SEQUENCE_2026-04-25.md`

### Current repo truth
- The Q2 closure core still concerns unresolved cross-cutting truths rather than isolated implementation tasks.
- Mongo multi-CLI coordination exists as an available control-plane capability, but it is not itself evidence that the current closure waves are safe to parallelize.
- The earlier audit phases already confirmed compatibility-retained and overlapping surfaces in backend composition, realtime delivery, and data-quality ownership.

### Delivery outcome
- canonical delivery model for Q2 core closure: single-CLI, staged, sequential execution
- permitted later delivery mode: constrained multi-CLI follow-up only after canonical truths and write scopes are locked
- disallowed current governance claim: treating Mongo-backed coordination as justification for parallelizing truth-setting waves before closure boundaries stabilize

### Delivery implications
- Core implementation waves should be ordered around truth convergence first, then safety blocking controls, then evidence-backed status hardening.
- Deferred items must remain explicit follow-up and must not be smuggled into Q2 closure claims without their own approval and evidence.
- Multi-CLI remains a tactical accelerator for low-coupling work, not the default governance model for cross-cutting closure.

## Recommended Implementation Sequence
Planning date: 2026-04-25
Supporting report: `docs/reports/quality/Q2_CORE_CLOSURE_EXECUTION_SEQUENCE_2026-04-25.md`

### Recommended wave order
1. Backend composition and realtime truth convergence
2. Data-quality ownership closure
3. Trading-safety blocking controls
4. Function-tree evidence and governance hardening

### Effort posture
- Waves 1 and 3 are the highest coupling and should remain single-CLI.
- Wave 2 should remain single-CLI until ownership and repair boundaries stabilize.
- Wave 4 is the earliest point where bounded multi-CLI support may become attractive, but only after the earlier truths are implementation-locked.

### Sequencing rationale
- Wave 1 defines the runtime and transport truth that later ownership and safety work must target.
- Wave 2 closes quality ownership on top of those runtime boundaries.
- Wave 3 inserts safety-blocking controls into the canonical placement path after the surrounding composition truth is stable.
- Wave 4 converts the earlier verified outcomes into evidence-backed completion semantics.

## Wave 1 Execution Planning
Planning date: 2026-04-25
Supporting report: `docs/reports/quality/Q2_WAVE1_BACKEND_REALTIME_CLOSURE_BATCH_PLAN_2026-04-25.md`

### Wave 1 batch order
1. Canonical truth labeling
2. Backend composition drift containment
3. Realtime registry alignment
4. Follow-up debt capture

### Wave 1 planning constraints
- Wave 1 is a truth-locking wave, not a broad realtime redesign.
- Socket.IO should remain compatibility-retained unless a later approved change adds verified public runtime mounting.
- `app_factory.py` should be narrowed as a compatibility-retained or test-scoped path, not treated as a peer runtime entrypoint.

## Wave 2 Execution Planning
Planning date: 2026-04-25
Supporting report: `docs/reports/quality/Q2_WAVE2_DATA_QUALITY_CLOSURE_BATCH_PLAN_2026-04-25.md`

### Wave 2 batch order
1. Canonical model and vocabulary lock
2. Ownership classification and boundary marking
3. Ingestion gate and storage-specific quality rules
4. Repair and backfill gap capture

### Wave 2 planning constraints
- Wave 2 is an ownership-closure wave, not a full data-governance platform rebuild.
- `src/core/data_quality_validator.py`, `src/monitoring/data_quality_monitor.py`, and `src/data_governance/quality.py` should remain the canonical split unless a later approved change replaces that model.
- Repair or backfill must remain explicit as either owned work or an acknowledged gap; it must not be implied as already closed.

## Wave 3 Execution Planning
Planning date: 2026-04-26
Supporting report: `docs/reports/quality/Q2_WAVE3_TRADING_SAFETY_CLOSURE_BATCH_PLAN_2026-04-26.md`

### Wave 3 batch order
1. Safety classification and canonical path lock
2. Idempotency and deduplication contract
3. Pre-execution risk gate and confirmation policy
4. Durable audit binding and retention closure
5. Residual gap capture

### Wave 3 planning constraints
- Wave 3 is a safety-blocking wave, not a production-readiness declaration wave.
- Current execution-capable paths should remain `experimental` unless a later approved change proves stronger controls and verified external execution closure.
- Stop-loss, alerting, and monitoring logic must remain classified as supporting controls, not as substitutes for pre-order blocking controls.

## Wave 4 Execution Planning
Planning date: 2026-04-26
Supporting report: `docs/reports/quality/Q2_WAVE4_FUNCTION_TREE_EVIDENCE_CLOSURE_BATCH_PLAN_2026-04-26.md`

### Wave 4 batch order
1. Status semantics and evidence layer lock
2. Safety-sensitive rule and downgrade logic
3. Closure-wave evidence binding
4. Percentage interpretation and snapshot policy
5. Residual historical review capture

### Wave 4 planning constraints
- Wave 4 is an evidence-hardening wave, not a broad catalog redesign wave.
- Structural truth in `catalog.yaml` and `schema.json` should remain intact unless a later approved change targets the catalog model itself.
- Percentages and completion wording must become more defensible, but historical review debt should remain explicit rather than being silently assumed closed.
