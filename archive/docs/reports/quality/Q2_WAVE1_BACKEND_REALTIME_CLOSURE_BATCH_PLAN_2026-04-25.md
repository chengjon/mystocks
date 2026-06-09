# Q2 Wave 1 Batch Plan: Backend Composition And Realtime Closure

Date: 2026-04-25
Mode: single-CLI execution planning
Related change: `openspec/changes/plan-q2-optimization-closure-program/`
Primary inputs:
- `docs/reports/quality/Q2_PHASE_A_REALTIME_TRUTH_AUDIT_2026-04-25.md`
- `docs/reports/quality/Q2_PHASE_B_BACKEND_COMPOSITION_CLOSURE_2026-04-25.md`
- `docs/reports/quality/Q2_CORE_CLOSURE_EXECUTION_SEQUENCE_2026-04-25.md`

## Objective

Wave 1 is the truth-locking wave. Its job is not to redesign all realtime infrastructure. Its job is to remove ambiguity about which backend assembly path and which realtime transport family represent current runtime truth.

## Scope

### In scope
- canonical backend composition declaration and convergence
- compatibility-retained scoping for `app_factory.py`
- canonical realtime transport family declaration
- documentation and registry alignment for non-canonical Socket.IO surfaces
- removal of misleading dual-truth wording in docs and governance artifacts

### Out of scope
- full connection-manager consolidation
- Socket.IO promotion to public canonical runtime transport
- broad realtime feature redesign
- trading-safety control insertion
- data-quality ownership refactor

## Current Truth To Preserve

- canonical runtime composition: `web/backend/app/main.py`
- compatibility-retained backend factory: `web/backend/app/app_factory.py`
- canonical current realtime transport family: native FastAPI WebSocket routes via `router_registry`
- compatibility-retained realtime transport family: Socket.IO manager and related streaming surfaces until verified public runtime mount exists

## Recommended Batch Sequence

### Batch 1: Canonical Truth Labeling

Goal:
- make the truth explicit before changing structure

Expected edits:
- implementation-facing docs
- design and migration notes
- compatibility annotations where appropriate

Success criteria:
- no maintained document still implies `app_factory.py` is a peer runtime truth
- no maintained document claims Socket.IO is the current public canonical transport

Verification:
- targeted doc grep for `app_factory.py`
- targeted doc grep for `Socket.IO` / `socketio`

### Batch 2: Backend Composition Drift Containment

Goal:
- prevent new runtime divergence between `main.py` and `app_factory.py`

Expected edits:
- narrow `app_factory.py` role statement
- identify or extract shared composition helpers where this can be done safely
- stop `app_factory.py` from growing into a feature-bearing alternative runtime path

Success criteria:
- `main.py` remains the only runtime composition truth
- `app_factory.py` is documented and structured as compatibility-retained or test-scoped
- new runtime-only concerns are not introduced into `app_factory.py`

Verification:
- runtime/deployment entrypoints still resolve to `app.main:app`
- tests using `create_app()` are still explicit about compatibility scope

### Batch 3: Realtime Registry Alignment

Goal:
- align router-facing realtime truth with governance wording

Expected edits:
- realtime delivery registry docs
- route-family classification notes
- compatibility tagging for Socket.IO-related code and docs

Success criteria:
- native WebSocket route family is the only canonical public transport family
- Socket.IO remains clearly marked non-canonical unless runtime mount proof is added in a later approved change

Verification:
- runtime composition docs and registry docs agree
- no current runtime artifact claims verified public Socket.IO mount

### Batch 4: Follow-Up Debt Capture

Goal:
- record what Wave 1 intentionally does not solve, so later work does not rediscover it

Expected outputs:
- explicit follow-up list for:
  - connection-manager consolidation
  - `realtime_market.py` inconsistency repair
  - possible future `app_factory.py` delegation or retirement
  - Socket.IO future decision

Success criteria:
- unresolved items are visible and not silently implied as closed

## Suggested Commit Cadence

Recommended micro-batch rhythm:

1. docs and governance truth labeling
2. backend composition containment
3. realtime registry alignment
4. follow-up debt capture

Practical commit count:
- minimum: 3 commits
- likely: 4 to 5 commits

## Validation Standard For Wave 1

Wave 1 should not claim feature completion. It should claim truth convergence only when:

1. deployment-facing runtime truth remains singular
2. compatibility-retained paths are explicitly scoped
3. canonical realtime transport wording is consistent across docs and specs
4. misleading dual-truth claims are removed
5. deferred realtime cleanup items remain visible as follow-up

## Risks During Execution

### 1. Over-refactoring risk
Wave 1 can easily expand into a full backend cleanup. That should be avoided.

### 2. Test breakage risk
`app_factory.py` is currently test-facing. Any structural narrowing must preserve known test bootstrap needs or explicitly migrate them.

### 3. False closure risk
Marking Socket.IO as non-canonical does not mean the underlying code is removed or settled. It only means the repo stops overstating current runtime truth.

## Recommended Next Action After Planning

If implementation starts, begin with Batch 1 and Batch 2 only. Do not mix Wave 1 truth-locking with Wave 2 data-quality work or Wave 3 trading-safety controls in the same branch segment.
