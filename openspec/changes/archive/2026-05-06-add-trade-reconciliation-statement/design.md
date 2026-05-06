# Trade Reconciliation Statement Design

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Context
The approved design for this batch defines a new trade reconciliation statement capability for `5.2 对账单`. The current repository truth supports trade history and execution tracking, but it does not yet provide a dedicated reconciliation statement surface, account-aware internal statement projection, or CSV-based import/export flow for reconciliation.

The intended scope is intentionally narrower than live broker reconciliation. This batch is read-only, deterministic, and statement-focused. It reuses the existing trade domain and the current persisted trade history as the internal truth source, but it does not collapse into `History.vue` and does not claim live broker closure.

## Goals / Non-Goals
- Goals:
  - Provide a dedicated reconciliation page under `/trade/reconciliation`.
  - Support account switching through explicit account descriptors.
  - Project internal statement rows from persisted trade history into a reconciliation-specific surface.
  - Support normalized-template CSV import and `miniQMT` raw CSV import.
  - Perform deterministic one-to-one matching and export filtered results as CSV.
- Non-Goals:
  - Implement manual review, manual override, or online correction.
  - Implement PDF export or print layouts.
  - Implement cross-account aggregate statements.
  - Merge reconciliation into the trade history workbench.
  - Claim production-ready broker reconciliation closure.

## Decisions
### Decision: Keep reconciliation as its own trade-domain surface
The capability should live under the existing trade domain, but it should not be added as a variant of the current history workbench.

Rationale:
- the history page already serves a different user workflow
- reconciliation needs its own import, matching, and export contract
- keeping the surface separate reduces regression risk and preserves route clarity

### Decision: Use explicit account descriptors
The first batch should expose account switching through explicit reconciliation account descriptors, including a stable `account_id` and display metadata.

Rationale:
- account filtering must be explicit rather than inferred from the history endpoint
- the statement surface needs a stable selector for reconciliation batches
- this keeps the contract aligned with the reviewed design and implementation plan

### Decision: Project internal statements from persisted trade history
The internal statement surface should be derived from persisted trade-domain records, with account-aware projection logic.

Rationale:
- this keeps the feature grounded in existing repository truth
- the internal statement contract remains distinct from the history workbench contract
- it allows reconciliation to evolve without rewriting the current history API

### Decision: Restrict matching to deterministic read-only outcomes
The first batch should only expose `matched`, `mismatched`, and `missing_broker_record`.

Rationale:
- the approved scope is statement reconciliation, not operator-driven repair
- deterministic matching is easier to test and reason about
- narrower status semantics reduce ambiguity in the UI and export flow

### Decision: Keep import formats explicit
The first batch should support two import modes only:
- normalized project template CSV
- `miniQMT` raw CSV

Rationale:
- this matches the approved design
- it avoids widening the parser surface before the core statement flow is stable

## Risks / Trade-offs
- Risk: the internal statement projection may need to evolve when more trade-domain truth becomes available.
  - Mitigation: keep the projection logic isolated behind a dedicated reconciliation source layer.
- Risk: adding a new route and page increases frontend routing surface area.
  - Mitigation: keep the route additive and preserve the existing history route label as `交易历史`.
- Risk: the feature could be mistaken for broker-lifecycle reconciliation.
  - Mitigation: keep terminology consistently statement-focused and read-only.
