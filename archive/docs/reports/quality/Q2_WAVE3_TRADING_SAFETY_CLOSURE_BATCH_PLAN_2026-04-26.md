# Q2 Wave 3 Batch Plan: Trading Safety Blocking Controls

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Mode: single-CLI execution planning
Related change: `openspec/changes/plan-q2-optimization-closure-program/`
Primary inputs:
- `docs/reports/quality/Q2_PHASE_D_TRADING_SAFETY_CONTRACT_2026-04-25.md`
- `docs/reports/quality/Q2_CORE_CLOSURE_EXECUTION_SEQUENCE_2026-04-25.md`
- `openspec/changes/plan-q2-optimization-closure-program/specs/trading-execution-safety/spec.md`

## Objective

Wave 3 is the safety-blocking wave for trading execution. Its job is not to make live trading production-ready in one step. Its job is to ensure the canonical order-placement path cannot imply a stronger safety class than the controls it actually enforces.

## Scope

### In scope
- idempotent submission contract for canonical order placement
- pre-execution risk gating for configured capital, concentration, and exposure thresholds
- confirmation or approved-bypass policy for safety-sensitive actions
- durable audit binding for submit, reject, confirm, and dedup decisions
- explicit safety classification of execution paths as simulated, experimental, or production-eligible

### Out of scope
- full external broker integration rollout
- HA or disaster-recovery design for trading infrastructure
- portfolio strategy redesign
- unrelated realtime transport refactors
- broad compliance program expansion beyond the blocking controls already specified

## Current Truth To Preserve

- no inspected trading execution path currently qualifies as `production-eligible`
- current execution-capable paths should remain classified as `experimental`
- existing audit infrastructure is reusable, but not yet bound to canonical order-placement decisions
- stop-loss and alert services are supporting controls, not substitutes for pre-order safety gates

## Recommended Batch Sequence

### Batch 1: Safety Classification And Canonical Path Lock

Goal:
- stop governance drift about what the current trading path can claim

Expected edits:
- trading safety docs
- classification notes on inspected execution paths
- explicit identification of the canonical placement path

Success criteria:
- current execution-capable paths remain labeled `experimental`
- no maintained document claims production-grade trading readiness without the required control set

Verification:
- docs and specs consistently use the same safety classification
- no runtime or governance text overstates trading readiness

### Batch 2: Idempotency And Deduplication Contract

Goal:
- ensure duplicate effective trade intent cannot silently create duplicate submissions

Expected edits:
- order request contract
- canonical placement path policy
- deduplication and replay-handling notes

Success criteria:
- the canonical placement path has a declared idempotency identity and deduplication scope
- duplicate submit intent produces an auditable deduplication outcome instead of a second blind submission

Verification:
- request and service contracts mention idempotency identity
- deduplication decisions are included in the audit contract

### Batch 3: Pre-Execution Risk Gate And Confirmation Policy

Goal:
- block unsafe submissions before order placement

Expected edits:
- risk threshold policy
- confirmation or bypass policy
- canonical placement flow documentation

Success criteria:
- configured capital, concentration, or exposure threshold breaches are blocking conditions
- high-risk actions require confirmation or an explicitly justified bypass
- stop-loss or monitoring logic is not misrepresented as equivalent to a pre-order gate

Verification:
- risk gate and confirmation policy are both attached to the canonical placement path
- policy text distinguishes supporting controls from blocking controls

### Batch 4: Durable Audit Binding And Retention Closure

Goal:
- make every critical trading decision reconstructable

Expected edits:
- audit field mapping
- audit persistence binding notes
- retention expectation by safety class

Success criteria:
- submit, reject, confirm, and dedup decisions all map to durable audit records
- audit retention expectations are explicit for the declared safety contract
- audit binding is defined at the decision point, not only after downstream fills or alerts

Verification:
- audit contract covers request identity, actor identity, execution path, decision outcome, and timestamp
- durable storage and retention expectations are documented for the canonical trading path

### Batch 5: Residual Gap Capture

Goal:
- keep unresolved production-readiness gaps visible

Expected outputs:
- explicit follow-up list for:
  - verified external execution adapter closure
  - stronger broker-semantics proof
  - production-eligible promotion criteria beyond the blocking controls

Success criteria:
- no completion statement implies that live trading is already production-ready
- unresolved broker-path gaps remain visible as follow-up

## Suggested Commit Cadence

Recommended micro-batch rhythm:

1. safety classification and canonical path lock
2. idempotency contract
3. risk gate and confirmation policy
4. durable audit binding and retention closure
5. residual gap capture

Practical commit count:
- minimum: 4 commits
- likely: 5 to 7 commits

## Validation Standard For Wave 3

Wave 3 should claim safety-blocking closure only when:

1. the canonical placement path is explicitly identified
2. current execution-capable paths are conservatively classified
3. idempotent submission policy is declared and auditable
4. pre-execution risk gates and confirmation policy are attached to the canonical placement path
5. submit, reject, confirm, and dedup decisions are durably audited with defined retention expectations
6. unresolved external execution gaps remain explicit and are not hidden by stronger safety claims

## Risks During Execution

### 1. False readiness risk
Adding policy text without binding it to the canonical placement path would still allow overstated production claims.

### 2. Scope explosion risk
Wave 3 can easily drift into full broker integration or broader trading redesign. That should be deferred.

### 3. Control-ordering risk
If audit binding or confirmation is added after path expansion, safety claims may outrun actual controls. The blocking controls must land before any stronger execution narrative.

## Recommended Next Action After Planning

If implementation starts, begin with Batch 1 and Batch 2. Do not combine Wave 3 trading-safety controls with Wave 4 function-tree status hardening in the same branch segment.
