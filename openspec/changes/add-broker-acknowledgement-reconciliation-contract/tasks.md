## 1. Specification

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [x] 1.1 Add the `broker-acknowledgement-reconciliation` capability spec with requirements for local-to-external identity binding, broker lifecycle event identity, divergence classification, and reconciliation resolution boundaries.
- [x] 1.2 Modify `trading-execution-safety` so production-eligible claims and broker-facing replay suppression require an explicit broker truth contract.
- [x] 1.3 Modify `architecture-governance` so broker-facing execution paths must publish a canonical truth registry entry with lifecycle source and reconciliation ownership.

## 2. Planning Follow-Up
- [x] 2.1 Inventory the current repository's broker-facing execution candidates and identify the canonical path to target first.
- [x] 2.2 Define the minimum implementation slices for identity persistence, lifecycle ingestion, and divergence evidence without widening into full broker integration.
- [x] 2.3 Define the acceptance evidence required before any later implementation may claim replay-safe execution-report handling or production-eligible lifecycle truth.

## 3. Validation
- [x] 3.1 Run `openspec validate add-broker-acknowledgement-reconciliation-contract --strict`.
- [x] 3.2 Review the draft against Wave 3 runtime hardening reports to confirm the proposal closes the correct next-layer gap instead of reopening local-only runtime work.

## 4. Implementation Micro-Batches
- [x] 4.1 Seed the canonical broker execution truth registry and supporting broker-truth path classification docs.
- [x] 4.2 Implement a local broker-order correlation ledger with explicit `awaiting broker acknowledgement` persistence and later external-id binding on the canonical application path.
- [x] 4.3 Define the broker lifecycle event envelope and persist minimum external identity plus sequencing metadata.
- [x] 4.4 Add durable divergence classification and review-required evidence for local-versus-broker mismatches.
- [x] 4.5 Gate replay suppression and bounded auto-resolution on explicit broker identity evidence.
  - Repo-truth note: current closure is the generic foundation gate in `src/application/trading/order_mgmt_service.py`, verified by `tests/ddd/test_phase_7_application.py`. Replay suppression is now blocked unless matched broker identity and explicit `event_id` / `sequence_id` evidence exist, duplicate lifecycle events are auditable as `suppressed_duplicate`, and auto-resolution remains narrowly bounded to `externally_terminal_locally_open` reject/cancel cases with matched `external_order_id` plus explicit `sequence_id`. Channel-specific authority for `miniQMT` primary vs Tongdaxin supplemental paths remains intentionally deferred to `add-broker-channel-topology-for-miniqmt-and-tdx`.
