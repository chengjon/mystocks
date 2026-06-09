# Q2 Wave 3 Broker Truth Line Summary

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-28
Line: `Wave 3 / Trading Safety -> Broker Acknowledgement And Reconciliation`
Mode: single-CLI execution
Audience: review / closure alignment

Related references:
- `docs/FUNCTION_TREE.md`
- `docs/reports/quality/Q2_WAVE3_IMPLEMENTATION_PROGRESS_2026-04-26.md`
- `docs/reports/quality/Q2_WAVE3_BROKER_ACK_RECONCILIATION_IMPLEMENTATION_PLAN_2026-04-27.md`
- `openspec/changes/add-broker-acknowledgement-reconciliation-contract/specs/broker-acknowledgement-reconciliation/spec.md`

## 1. Purpose

This document summarizes what has been completed on the current Wave 3 trading-runtime and
broker-truth line, where the line currently sits in the project function map, and why the next
task matters.

This summary is intentionally conservative. It does not claim that the repository now has a
production-ready broker adapter, production-grade reconciliation, or replay-safe execution
handling.

## 2. What This Line Has Completed

The line has progressed in two layers.

### 2.1 Local trading-safety and runtime evidence closure

The first layer established the canonical local execution truth at:

- `src/application/trading/order_mgmt_service.py`

Completed outcomes on that local runtime line include:

- canonical placement-path and `experimental` classification lock
- idempotency and deduplication audit semantics
- pre-submit risk gate and confirmation / approved-bypass boundaries
- durable local trading decision audit
- local cash-reservation persistence and reconciliation
- local order-state evidence persistence
- denial-audit evidence for:
  - cancel
  - reject
  - execution report
- structured denial reason taxonomy

Business value:

- the project no longer depends on UI presence or coarse route existence to imply trading
  readiness
- the canonical application path now has explicit decision evidence and safety controls
- later broker-binding work has a stable local anchor instead of spreading across demo or stub
  surfaces

### 2.2 Broker acknowledgement and reconciliation foundation

The second layer moved outward from local runtime truth into broker-facing evidence contracts.

#### Batch 1: Canonical broker-truth registry seed

Completed outcomes:

- the repo now explicitly names the first canonical broker-truth target
- non-canonical paths are documented as stub, demo, compatibility-only, or experimental

Meaning:

- prevents future broker-truth work from drifting into `trading_runtime.py`, legacy API
  surfaces, or incomplete router stubs

#### Batch 2: Local-to-external identity persistence

Completed outcomes:

- local order submission now persists a correlation record
- correlation can remain in explicit `awaiting_broker_acknowledgement`
- external order id can be bound later without heuristic matching

Meaning:

- the system can now distinguish “local submit happened” from “broker identity is already
  known”
- this is the first hard prerequisite for safe broker lifecycle ingestion

#### Batch 3: Broker lifecycle event envelope

Completed outcomes:

- a bounded broker lifecycle event envelope now exists
- acknowledgement, reject, cancel, and execution events can preserve:
  - external order identity
  - local submission identity
  - source timestamp
  - event / sequence metadata when available
- missing identity or sequencing is classified explicitly

Meaning:

- the system can now retain broker lifecycle facts without pretending they are replay-safe
- future suppression or reconciliation work can no longer rely on vague free-text matching alone

#### Batch 4: Divergence ledger and review surface

Completed outcomes:

- a dedicated durable broker divergence ledger now exists
- local-versus-broker mismatches can now be retained as `review_required` incidents
- current machine-readable divergence categories include:
  - `awaiting_broker_acknowledgement`
  - `unmatched_external_order`
  - `locally_terminal_externally_open`
  - `externally_terminal_locally_open`
  - `quantity_or_fill_divergence`

Meaning:

- the system can now detect and preserve mismatches instead of silently discarding them
- broker lifecycle evidence is no longer limited to “event arrived”; it now captures whether
  that event conflicts with local truth
- this creates the minimum review surface needed before any automatic resolution can be allowed

## 3. Current Position In The Function Tree

The primary functional home of this line is:

- `05-投资组合与交易 {#domain-05}`
- especially `5.3 交易决策 {#domain-05-node-03}`
- most directly `执行跟踪`

See:

- `docs/FUNCTION_TREE.md`

Current function-tree truth already says:

- this domain is a safety-sensitive domain
- current execution-capable paths should still be read as `experimental` / `in-progress`
- execution tracking must be interpreted together with Phase D / Wave 3 evidence

This means the current line is not ornamental work. It is filling the exact backend truth gap
behind `5.3 执行跟踪`.

In practical terms:

- `决策中心` can exist without proving execution truth
- `信号生成` can exist without proving broker-state safety
- `执行跟踪` cannot be trusted unless:
  - local order identity is durable
  - broker lifecycle identity is durable
  - mismatch classes are durable
  - unsafe cases are retained for review instead of guessed away

So this line is best understood as:

- not a UI feature line
- not a broker integration completion line
- but the evidence and control foundation for `交易决策 -> 执行跟踪`

It also lays groundwork for:

- `5.2 交易记录 -> 对账单`

because reconciliation-grade statements cannot be made safely without durable identity and
divergence evidence.

## 4. Current State Of The Line

The current line has completed the “make truth visible” phase, but not the “allow stronger
automated decisions” phase.

Already completed:

- local submit intent is durable
- broker acknowledgement binding is durable
- broker lifecycle event identity is durable
- local-vs-broker divergence is durable

Not completed yet:

- replay suppression policy
- bounded automatic resolution policy
- verified real broker adapter truth
- production-grade reconciliation workflow
- promotion-to-production evidence

The current status is therefore:

- stronger than local-only runtime hardening
- still intentionally weaker than production reconciliation

## 5. Why The Next Task Matters

The next planned task is:

- `Batch 5: Bounded Auto-Resolution And Replay-Suppression Gate`

Its purpose is to move from:

- “the system can see and preserve mismatches”

to:

- “the system may take stronger action only when broker-side identity evidence is explicit
  enough”

This is the key decision boundary for the line.

Without Batch 5:

- the system can audit and classify, but not safely automate
- duplicate lifecycle events still cannot be suppressed with defensible evidence
- divergence incidents still cannot be auto-resolved under a declared policy

With Batch 5 done correctly:

- replay suppression will be allowed only when the broker-side identity or sequencing basis is
  named explicitly
- auto-resolution will be allowed only for explicitly authorized divergence classes
- quantity, price, or timing coincidence alone will remain insufficient
- unsupported cases will stay in `review_required` state

Business meaning:

- this is the transition point from “auditable execution tracking” to “bounded operational
  control”
- it is the prerequisite for later claiming safer execution automation
- it reduces the risk of the system silently reconciling the wrong order based on weak
  coincidence

## 6. Recommended Review Lens

When reviewing this line, the right questions are:

1. Has the canonical execution truth stayed anchored in the application trading path instead of
   drifting into demo or compatibility surfaces?
2. Are broker-facing identity and divergence facts now durable enough to support later policy
   work?
3. Has the implementation avoided over-claiming replay safety or production readiness?
4. Is `05-投资组合与交易 -> 5.3 执行跟踪` now better grounded in runtime evidence than before?
5. Is the next step correctly focused on explicit policy gating rather than heuristic
   suppression?

## 7. Bottom Line

This line has already completed the foundational work needed to make trading execution truth
inspectable and mismatch-aware on the canonical local path.

Its current position in the function tree is clear:

- it is primarily advancing `05-投资组合与交易`
- specifically `5.3 交易决策`
- most concretely the currently incomplete `执行跟踪` capability

The next task is meaningful because it is not “more logging” or “more local evidence”. It is
the first step that decides when the system may safely act on broker truth instead of only
recording it.
