# Q2 Core Closure Execution Sequence

Date: 2026-04-25
Mode: single-CLI first
Related change: `openspec/changes/plan-q2-optimization-closure-program/`
Depends on:
- `docs/reports/quality/MYSTOCKS_PHASE_EVALUATION_2026Q2.md`
- `docs/reports/quality/Q2_PHASE_A_REALTIME_TRUTH_AUDIT_2026-04-25.md`
- `docs/reports/quality/Q2_PHASE_B_BACKEND_COMPOSITION_CLOSURE_2026-04-25.md`
- `docs/reports/quality/Q2_PHASE_C_DATA_QUALITY_UNIFICATION_2026-04-25.md`
- `docs/reports/quality/Q2_PHASE_D_TRADING_SAFETY_CONTRACT_2026-04-25.md`
- `docs/reports/quality/Q2_PHASE_E_FUNCTION_TREE_EVIDENCE_HARDENING_2026-04-25.md`
- `docs/reports/quality/Q2_DELIVERY_DISCIPLINE_SINGLE_CLI_SEQUENCE_2026-04-25.md`

## Purpose

This document turns the Q2 closure proposal into an execution sequence that matches current repo reality. It is intentionally conservative: the repo still has overlapping truths, compatibility-retained paths, and incomplete safety contracts. The right next step is not broad parallelization. The right next step is ordered closure.

## Repo Reality That Drives The Plan

### 1. Runtime truth is not fully converged
- `web/backend/app/main.py` is canonical runtime composition.
- `web/backend/app/app_factory.py` is still compatibility-retained and test-oriented.
- Realtime transport surfaces are present but not governed as one runtime truth.

### 2. Data quality exists, but ownership is split
- validation, monitoring, and governance each have plausible homes
- repair and backfill ownership is still not explicit
- dual-engine concerns still need one governing model

### 3. Trading safety is governance-first, not implementation-last
- current execution-capable paths are `experimental`
- production-grade claims are blocked by missing idempotency, risk gates, confirmation, and audit binding

### 4. Function-tree status needs evidence, not only wording
- completion semantics must follow the earlier closure outcomes
- status hardening should happen after truth and safety closure, not before

## Recommended Execution Order

### Wave 1: Backend Composition And Realtime Truth Convergence

Goal:
- lock runtime assembly truth
- stop further drift between canonical and compatibility-retained backend entrypoints
- align realtime transport governance to the canonical runtime path

Typical work:
- reduce `app_factory.py` to an explicit compatibility or test factory role
- move shared composition concerns toward one canonical assembly path
- document and tag non-canonical realtime surfaces consistently
- update misleading docs that still imply dual runtime truth

Why first:
- every later wave depends on runtime truth being stable
- parallel work before this wave would amplify merge churn

Estimated effort:
- implementation complexity: medium
- verification complexity: medium
- coordination risk: high if parallelized
- practical batch size: 3 to 5 focused commits

Recommended owner mode:
- single CLI only

### Wave 2: Data Quality Ownership Closure

Goal:
- implement one explicit ownership split for validation, monitoring, governance, and repair
- make dual-storage quality concerns first-class instead of incidental

Typical work:
- define and wire the ingestion quality gate
- classify overlapping quality modules as canonical, compatibility-retained, or specialized
- add explicit ownership for repair or backfill
- bind quality evidence to storage-specific concerns when data crosses TDengine and PostgreSQL paths

Why second:
- data-quality closure should align to the canonical runtime and service boundaries selected in Wave 1

Estimated effort:
- implementation complexity: medium
- verification complexity: medium
- coordination risk: medium-high while ownership is still moving
- practical batch size: 3 to 6 focused commits

Recommended owner mode:
- single CLI first

### Wave 3: Trading Safety Blocking Controls

Goal:
- make the canonical placement path incapable of stronger claims than its actual controls support
- install blocking controls before any execution-path expansion

Typical work:
- add idempotency identity to submission
- enforce pre-execution risk gating
- enforce confirmation or approved bypass policy
- bind all submit or reject decisions to durable audit storage
- keep all current execution-capable paths marked `experimental` until verified otherwise

Why third:
- this is the highest safety value wave
- it should sit on top of already-stabilized runtime and service boundaries

Estimated effort:
- implementation complexity: medium-high
- verification complexity: high
- coordination risk: high
- practical batch size: 4 to 7 focused commits

Recommended owner mode:
- single CLI only for core control insertion

### Wave 4: Function-Tree Evidence And Governance Hardening

Goal:
- convert closure outcomes into durable completion semantics and reporting rules

Typical work:
- update function-tree status semantics and evidence rules
- tag safety-sensitive nodes by rule instead of by narrative wording
- align Q2 completion statements to actual verification evidence

Why fourth:
- this wave should describe the truth established by Waves 1 to 3, not guess ahead of them

Estimated effort:
- implementation complexity: low-medium
- verification complexity: low-medium
- coordination risk: medium if statuses are edited in parallel
- practical batch size: 2 to 4 focused commits

Recommended owner mode:
- single CLI preferred, multi-CLI possible only after Waves 1 to 3 are settled

## Suggested Time And Cadence

If handled by one strong maintainer CLI in the current repo state, the realistic cadence is:

1. Wave 1: 2 to 4 working days
2. Wave 2: 2 to 4 working days
3. Wave 3: 3 to 5 working days
4. Wave 4: 1 to 2 working days

Practical total:
- conservative total: 8 to 15 working days
- not including new infrastructure programs such as HA, DB replacement, or major observability expansion

## What Should Not Be Folded Into This Sequence

The following are valid, but should remain out of the core closure sequence:

- replacing dual-storage strategy with a single database
- building HA, failover, or blue-green deployment programs
- broad observability redesign beyond the minimum evidence and safety bindings already identified
- GPU strategy repositioning beyond documentation and governance clarification

## Entry And Exit Gates Per Wave

### Wave 1 entry
- proposal and closure audits are approved

### Wave 1 exit
- one canonical runtime composition truth remains
- compatibility-retained paths are explicitly scoped
- realtime transport governance matches runtime truth

### Wave 2 exit
- one ownership model exists for validation, monitoring, governance, and repair
- storage-specific quality concerns are documented and testable

### Wave 3 exit
- canonical order placement path enforces idempotency, risk gating, confirmation policy, and audit binding
- no execution path is overstated beyond its verified safety class

### Wave 4 exit
- function-tree completion claims reference evidence rather than narrative confidence
- Q2 closure language is aligned to verified status

## When Mongo + Multi-CLI Becomes Reasonable

It becomes reasonable only after Wave 1 is complete, and preferably after Wave 2 for anything touching data-quality ownership.

Safe early candidates:
- documentation backfill
- test additions against already-locked contracts
- report normalization
- isolated cleanup in bounded non-canonical modules

Still unsafe:
- redefining canonical backend composition
- redefining canonical realtime transport truth
- inserting core trading-safety controls in parallel branches

## Final Recommendation

Use a single-CLI closure sequence for the core Q2 program.

After Wave 1 locks runtime truth, reconsider Mongo-backed multi-CLI only for bounded, low-coupling tasks. Do not use multi-CLI as a substitute for unresolved architecture decisions.
