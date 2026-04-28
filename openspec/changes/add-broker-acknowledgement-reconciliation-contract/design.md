## Context

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Wave 3 runtime hardening deliberately stayed inside local application truth. Batches 16 through
20 added denial audit evidence, missing-order audit evidence, and stable refusal-reason
taxonomy for `cancel`, `reject`, and `handle_execution_report(...)`.

That work improved reconstructability, but it did not answer the next harder question:
which external broker or counterparty facts justify mutating or trusting local order state?

The current execution-report path accepts only local `order_id`, `filled_qty`, and `price`.
That is enough for local state mutation and local denial evidence, but it is not enough for
safe replay suppression or reconciliation with external order truth. Two valid partial fills
can resemble a replayed event if the broker-facing identity contract is undefined.

## Goals / Non-Goals

- Goals:
  - Define the contract for binding local order submissions to broker-facing acknowledgement
    identity.
  - Define the minimum metadata required for broker lifecycle events before duplicate
    suppression or reconciliation is claimed.
  - Define stable divergence classes for local-vs-broker lifecycle mismatch.
  - Define when reconciliation may auto-resolve and when it must stop at audit plus operator
    review.
  - Define the governance hook that records the canonical broker-facing execution path.

- Non-Goals:
  - Implementing a real broker adapter.
  - Implementing distributed exactly-once delivery or queue semantics.
  - Declaring the current trading path production-ready.
  - Replacing the existing local runtime audit and reservation evidence layers.
  - Designing every broker-specific field for every future adapter vendor.

## Decisions

### Decision: Introduce a dedicated broker truth capability

Broker acknowledgement and reconciliation should be modeled as a dedicated OpenSpec
capability instead of being hidden inside incremental runtime hardening notes.

Rationale:
- the problem is no longer "missing audit evidence for a local branch"
- the problem is now "what external truth contract makes local state safe to trust"
- that deserves a first-class capability with explicit requirements and scenarios

### Decision: Treat broker truth as a prerequisite for stronger lifecycle claims

Production-eligible classification, replay-safe execution-report suppression, and
broker-aligned terminal-state claims must depend on an explicit broker truth contract.

Rationale:
- local request idempotency is not the same as broker lifecycle replay safety
- local quantity/price coincidence is not sufficient proof of duplicate external execution
- classification must remain `simulated` or `experimental` until external truth semantics are
  explicit

### Decision: Separate identity binding from reconciliation policy

The design separates:
- local-to-external order identity binding
- broker lifecycle event identity
- divergence classification
- resolution policy

Rationale:
- identity binding answers "which local and external records refer to the same order"
- event identity answers "which external lifecycle event is this"
- divergence classification answers "what kind of mismatch happened"
- resolution policy answers "who or what may resolve it"

Keeping these concerns separate avoids premature auto-repair logic.

### Decision: Keep auto-resolution bounded and explicit

The contract should permit auto-resolution only when the reconciliation policy explicitly says
so. Otherwise divergence remains an audited incident or review-required state.

Rationale:
- premature reconciliation is more dangerous than incomplete reconciliation
- operator review is a valid bounded state when broker truth is partial
- the project should prefer honest `experimental` classification over silent local mutation

### Decision: Add a governance-visible broker execution truth registry

Any broker-facing execution path should publish a governance-visible registry entry that
identifies:
- canonical adapter or ingestion path
- local-to-external identity source
- lifecycle source scope
- reconciliation owner
- fallback or manual-review boundary

Rationale:
- the repository already uses governance registries to stabilize cross-cutting truths
- broker truth is similarly cross-cutting and should not remain hidden in code comments or
  informal reports

## Alternatives Considered

### Alternative 1: Continue local runtime micro-batches only

Rejected because the remaining high-value uncertainty is no longer local observability. More
local denial-audit extensions would add evidence breadth but not solve broker truth.

### Alternative 2: Implement execution-report deduplication first

Rejected because true deduplication would need broker event identity or sequencing metadata
that is not yet contractually defined. Implementing it now would encourage unsafe heuristics.

### Alternative 3: Design broker contract first, implement later

Accepted because it keeps scope narrow while preventing future implementation drift.

## Risks / Trade-offs

- Risk: the capability may remain abstract if no broker adapter path is selected soon.
  - Mitigation: require a governance registry entry and implementation planning tasks as the
    first follow-up.

- Risk: multiple future broker adapters may expose different identity fields.
  - Mitigation: define the minimum abstract contract in terms of local correlation, external
    order identity, event identity, and sequencing metadata "when available".

- Risk: the proposal could be mistaken for a production-readiness claim.
  - Mitigation: explicitly keep classification gating in `trading-execution-safety` and state
    that this change is contract-only.

## Migration Plan

1. Approve the OpenSpec contract without changing runtime code.
2. Publish the canonical broker-facing execution path and current gap assessment.
3. Plan implementation micro-batches for:
   - local-to-external order identity persistence
   - broker lifecycle ingestion schema
   - divergence evidence and review surfaces
4. Revisit execution-report replay suppression only after those prerequisites exist.

## Open Questions

- Which concrete broker-facing adapter path should become canonical first in this repository?
- Should divergence incidents live in the existing trading audit sink, a separate ledger, or a
  combined model with distinct classification fields?
- What is the minimum external sequencing metadata the first supported broker path can expose?
