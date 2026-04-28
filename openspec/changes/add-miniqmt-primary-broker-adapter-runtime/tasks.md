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
- [x] 2.3 Define the first canonical deferred-result ingress path for `miniQMT` bridge evidence
  without bypassing the shared broker lifecycle envelope.
- [x] 2.4 Define the explicit Tongdaxin supplemental handoff record and the conditions that
  trigger operator review instead of silent primary-path retry.
  - Repo-truth note: `src/application/trading/primary_broker_followup.py` now defines the first
    canonical deferred miniQMT bridge-result ingress path by resolving `bridge_task_id` through
    `broker_submission_attempt.py`, backfilling `local_submission_id`, and routing the normalized
    payload through `OrderManagementService.record_broker_lifecycle_event()` instead of bypassing
    the shared lifecycle envelope.
  - Repo-truth note: the same helper module now defines explicit Tongdaxin supplemental handoff
    persistence. `OrderManagementService.record_tdx_supplemental_handoff()` only allows handoff
    from an active `miniQMT` primary correlation that is still awaiting acknowledgement; it does
    not silently retry or auto-promote the supplemental path.

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
- [x] 3.4 Route deferred `miniQMT` bridge result, callback, or polled lifecycle evidence through
  `BrokerLifecycleEvent` and channel-scoped correlation binding.
- [x] 3.5 Add explicit Tongdaxin supplemental handoff persistence and preserve review-first
  topology semantics.
- [x] 3.6 Update `docs/guides/quant-trading/broker-execution-truth-registry.md` and
  `docs/FUNCTION_TREE.md` once implementation evidence exists.
  - Repo-truth note: `OrderManagementService.ingest_miniqmt_bridge_result_payload()` now routes
    deferred bridge results through `BrokerLifecycleEvent`; unmatched late miniQMT bridge results
    after channel rotation are persisted as `unmatched_deferred_bridge_result` review incidents
    instead of being auto-matched by timing or quantity coincidence.
  - Repo-truth note: `OrderManagementService.record_tdx_supplemental_handoff()` now records
    explicit operator handoff into the submission-attempt ledger, rotates the active correlation
    surface to the `tdx_manual` channel, and preserves the prior miniQMT attempt evidence in the
    handoff payload.
  - Repo-truth note: `docs/guides/quant-trading/broker-execution-truth-registry.md` and
    `docs/FUNCTION_TREE.md` now reflect the current repo-facing runtime evidence: primary-path
    submission classification, deferred bridge-result re-entry, and explicit Tongdaxin handoff.

## 4. Validation

- [x] 4.1 Add targeted tests for:
  - local order submission into the `miniQMT` primary runtime path
  - transport receipt without broker acknowledgement
  - deferred broker acknowledgement or rejection
  - explicit Tongdaxin supplemental handoff
- [x] 4.2 Run targeted trading tests, including `tests/ddd/test_phase_7_application.py`, before
  closing each implementation batch.
- [x] 4.3 Re-run `openspec validate add-miniqmt-primary-broker-adapter-runtime --strict` before
  completion.
- [x] 4.4 Confirm the closeout language stays at repo-truth level and does not claim live
  broker production readiness without new runtime evidence.
  - Repo-truth note: `tests/ddd/test_phase_7_application.py` now covers queued primary-path
    submission, immediate acknowledgement, transport-stage failure, deferred bridge-result
    acknowledgement, explicit Tongdaxin supplemental handoff, and late miniQMT bridge-result
    review escalation. The focused batch was re-verified with
    `pytest tests/ddd/test_phase_7_application.py -q --cov-fail-under=0 -o log_cli=false`
    (`59 passed`).
  - Repo-truth note: `openspec validate add-miniqmt-primary-broker-adapter-runtime --strict`
    now passes after the runtime, docs, and task ledger updates.
  - Repo-truth note: closeout language in the spec, registry, and `FUNCTION_TREE.md` still
    stays at repo-facing runtime evidence level. It explicitly avoids claiming a verified live
    miniQMT adapter, production-ready broker execution, or production-ready Tongdaxin bridge.
