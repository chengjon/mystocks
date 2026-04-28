## 1. Specification

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [x] 1.1 Add the `miniqmt-primary-broker-adapter-runtime` capability spec covering outbound
  primary-path submission, bridge-receipt versus broker-acknowledgement boundaries, deferred
  lifecycle re-entry, and explicit supplemental handoff semantics.
- [x] 1.2 Modify `trading-execution-safety` so asynchronous bridge acceptance is not conflated
  with broker acknowledgement and transport-stage evidence becomes part of the minimum runtime
  audit contract.
- [x] 1.3 Run `openspec validate add-miniqmt-primary-broker-adapter-runtime --strict`.

## 2. Runtime Contract Design

- [x] 2.1 Freeze the canonical repo-facing submission outcomes for the `miniQMT` primary path.
  - Repo-truth note: `src/application/trading/miniqmt_primary_runtime.py` now freezes
    `bridge_task_accepted`, `broker_acknowledged`, and `submission_failed` as the canonical
    immediate repo-facing outcomes for the `miniQMT` primary runtime path.
- [x] 2.2 Decide whether to add a dedicated submission-attempt ledger or extend an existing
  durable surface, and document the rationale in the implementation batch.
  - Repo-truth note: the repository now uses the dedicated ledger
    `src/application/trading/broker_submission_attempt.py` plus
    `TRADING_BROKER_SUBMISSION_ATTEMPT_SQLITE_PATH`, rather than extending the existing
    correlation or lifecycle ledgers.
- [ ] 2.3 Define the first canonical deferred-result ingress path for `miniQMT` bridge evidence
  without bypassing the shared broker lifecycle envelope.
- [ ] 2.4 Define the explicit Tongdaxin supplemental handoff record and the conditions that
  trigger operator review instead of silent primary-path retry.

## 3. Implementation Micro-Batches

- [x] 3.1 Introduce a repo-facing `miniQMT` primary runtime interface or adapter layer adjacent
  to `src/application/trading/`.
  - Repo-truth note: `src/application/trading/miniqmt_primary_runtime.py` now provides the
    canonical `MiniQMTPrimaryBrokerRuntime`, `WindowsBridgeMiniQMTTransport`, and normalized
    outbound submission payload builder adjacent to the local trading application layer.
- [x] 3.2 Wire `OrderManagementService.place_order()` to the primary runtime path while keeping
  local-order persistence, safety gates, and broker transport concerns separated.
  - Repo-truth note: `src/application/trading/order_mgmt_service.py` now accepts
    `primary_broker_runtime` and `broker_submission_attempt_store`, persists channel-scoped
    correlation for the `miniQMT` primary path, records submission attempts, and emits distinct
    audit outcomes for queued, immediate-acknowledged, and failed primary submissions.
- [x] 3.3 Normalize the Windows `qmt` transport response into canonical immediate submission
  outcomes and durable submission-attempt evidence.
  - Repo-truth note: `src/application/trading/miniqmt_primary_runtime.py` now normalizes
    Windows-bridge-style results such as `status`, `task_id`, and `external_order_id` into the
    canonical submission outcomes, while
    `tests/ddd/test_phase_7_application.py` verifies `bridge_task_accepted`,
    `broker_acknowledged`, and `submission_failed` through the new durable submission-attempt
    ledger.
- [ ] 3.4 Route deferred `miniQMT` bridge result, callback, or polled lifecycle evidence through
  `BrokerLifecycleEvent` and channel-scoped correlation binding.
- [ ] 3.5 Add explicit Tongdaxin supplemental handoff persistence and preserve review-first
  topology semantics.
- [ ] 3.6 Update `docs/guides/quant-trading/broker-execution-truth-registry.md` and
  `docs/FUNCTION_TREE.md` once implementation evidence exists.

## 4. Validation

- [ ] 4.1 Add targeted tests for:
  - local order submission into the `miniQMT` primary runtime path
  - transport receipt without broker acknowledgement
  - deferred broker acknowledgement or rejection
  - explicit Tongdaxin supplemental handoff
- [ ] 4.2 Run targeted trading tests, including `tests/ddd/test_phase_7_application.py`, before
  closing each implementation batch.
- [ ] 4.3 Re-run `openspec validate add-miniqmt-primary-broker-adapter-runtime --strict` before
  completion.
- [ ] 4.4 Confirm the closeout language stays at repo-truth level and does not claim live
  broker production readiness without new runtime evidence.
