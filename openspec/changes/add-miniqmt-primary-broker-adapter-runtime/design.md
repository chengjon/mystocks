## Context

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

The repository has already finished two prerequisite lines:

- generic broker acknowledgement and reconciliation foundation
- project-specific channel topology (`miniQMT` primary-candidate, Tongdaxin supplemental)

Current repo truth now looks like this:

- `OrderManagementService.place_order()` persists the local order and a channel-scoped
  correlation record, but only under the conservative `local_anchor` channel.
- `OrderManagementService.ingest_miniqmt_lifecycle_payload()` and
  `src/application/trading/miniqmt_lifecycle_ingestion.py` can normalize incoming `miniQMT`
  payloads into the shared `BrokerLifecycleEvent` envelope.
- `web/backend/app/services/windows_bridge_adapter.py` can trigger a remote `qmt/*` task, but
  it currently returns a transport/task receipt only. It does not yet define:
  - a canonical primary submission response shape
  - the meaning of transport acceptance versus broker acknowledgement
  - how deferred bridge results bind back to the local submission attempt

The next line therefore needs to be runtime-specific, not another generic broker-truth line.

## Goals / Non-Goals

- Goals:
  - Define the first canonical repo-facing runtime contract for outbound `miniQMT` primary-path
    submission.
  - Preserve the distinction between transport receipt and broker acknowledgement.
  - Define the canonical re-entry path for deferred bridge result, callback, or polled
    lifecycle evidence into the shared broker ledgers.
  - Define how the primary path degrades into operator review or explicit Tongdaxin
    supplemental handoff.
- Non-Goals:
  - Claim that a live `miniQMT` adapter already exists today.
  - Promote any path to production-eligible during proposal creation.
  - Upgrade Tongdaxin supplemental flow into an automation-equivalent path.
  - Introduce multi-broker smart routing or broker selection policy.

## Decisions

- Decision: Keep `OrderManagementService` as the canonical local order anchor, but do not
  re-expand it into a transport-heavy broker integration layer.
  - Rationale: the recent Wave 3 refactor reduced service size and split out generic safety
    logic. The next line should preserve that direction.

- Decision: Add a dedicated repo-facing `miniQMT` primary runtime surface adjacent to
  `src/application/trading/` instead of treating `windows_bridge_adapter.py` as the domain
  contract itself.
  - Rationale: the Windows bridge is a transport boundary. The project still needs a trading
    runtime contract that normalizes submission outcomes before local services depend on them.

- Decision: Distinguish at least three immediate submission outcomes:
  - `bridge_task_accepted`
  - `broker_acknowledged`
  - `submission_failed`
  - Rationale: transport acceptance alone is not broker truth, while some future adapters may
    still return immediate broker identity synchronously.

- Decision: Preserve outbound submission attempts separately from later broker lifecycle facts.
  - Preferred shape: a dedicated submission-attempt ledger or an equivalently explicit durable
    surface that can hold:
    - local `order_id`
    - `broker_channel`
    - `local_submission_id`
    - `adapter_path`
    - `account_scope`
    - `session_scope`
    - immediate submission outcome
    - remote `bridge_task_id` or equivalent transport receipt
    - failure reason when transport delivery fails before acknowledgement
  - Rationale: this avoids overloading the existing correlation record, whose primary job is
    local-to-external identity binding.

- Decision: Keep the inbound broker lifecycle envelope canonical.
  - Rationale: whether the primary path uses callback, polling, or task-result retrieval at the
    bridge edge, repo-facing lifecycle evidence should still converge into
    `BrokerLifecycleEvent` and the existing reconciliation surfaces.

- Decision: Any Tongdaxin fallback must be recorded as an explicit supplemental handoff, not a
  silent retry of the `miniQMT` primary path.
  - Rationale: topology and authority rules are already channel-specific. Silent fallback would
    collapse that distinction and corrupt broker-truth auditability.

## Risks / Trade-offs

- Remote Windows bridge capabilities may not yet expose a stable task-result or callback
  contract.
  - Mitigation: keep the repo-facing contract explicit and allow the outer transport mechanism
    to vary as long as it normalizes into the same submission and lifecycle surfaces.

- Deferred lifecycle evidence may arrive from multiple sources and create duplicate facts.
  - Mitigation: keep the current channel-aware replay-suppression gates and require explicit
    identity or sequencing evidence before claiming suppression.

- Operator handoff could be implemented informally and bypass the channel topology contract.
  - Mitigation: require an explicit handoff record and keep Tongdaxin supplemental automation
    boundaries unchanged.

## Migration Plan

1. Add the runtime capability spec and update trading execution safety.
2. Introduce a repo-facing `miniQMT` primary submission contract plus durable submission-attempt
   evidence.
3. Wire `OrderManagementService` to the primary runtime path without collapsing transport logic
   back into the application service.
4. Normalize deferred bridge results into the existing lifecycle and correlation ledgers.
5. Add explicit Tongdaxin supplemental handoff recording.
6. Update the broker truth registry and `FUNCTION_TREE.md` only after implementation evidence
   exists.

## Open Questions

- Should the first live bridge integration use callback push, task-result polling, or a hybrid
  retrieval path?
- Does the remote Windows `qmt` provider already have a stable result schema that can be
  normalized, or does this repository need to define and enforce it first?
- Should submission-attempt evidence be a new ledger or an extension of an existing trading
  audit store?
