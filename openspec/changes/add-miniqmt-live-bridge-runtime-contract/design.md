## Context

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

The repository now has a complete repo-facing `miniQMT` primary runtime line:

- `OrderManagementService.place_order()` preserves local-order persistence, channel-scoped
  correlation, and durable submission-attempt evidence.
- `src/application/trading/miniqmt_primary_runtime.py` classifies immediate primary-path results
  as `bridge_task_accepted`, `broker_acknowledged`, or `submission_failed`.
- `src/application/trading/broker_submission_attempt.py` preserves `bridge_task_id` receipts.
- `OrderManagementService.ingest_miniqmt_bridge_result_payload()` can route deferred bridge
  results back through `BrokerLifecycleEvent`.

Current repo truth still stops short of a live bridge contract:

- `web/backend/app/services/windows_bridge_adapter.py` only calls a remote
  `/api/v1/task/execute` endpoint and returns a synthetic receipt.
- There is no repository-owned definition for a `qmt` task-result endpoint or callback payload.
- There is no explicit timeout, mismatch, or authentication contract for the Linux-to-Windows
  agent boundary.

The next line therefore needs to define the live bridge contract itself, not repeat generic
broker truth or repo-facing normalization.

## Goals / Non-Goals

- Goals:
  - Define the first repository-owned live bridge contract for `miniQMT` primary submissions.
  - Freeze the canonical submission receipt and result payload fields the repository will trust.
  - Choose the first canonical live result retrieval mode.
  - Define timeout, mismatch, and escalation semantics without collapsing Tongdaxin into a
    silent fallback.
  - Keep the live bridge contract converging into the existing submission-attempt, lifecycle,
    and divergence ledgers.
- Non-Goals:
  - Claim that the Windows `miniQMT` agent is already implemented or production-ready.
  - Promote the path to `production-eligible` in the proposal itself.
  - Upgrade Tongdaxin to an automation-equivalent path.
  - Introduce multi-broker routing, broker selection, or strategy orchestration changes.

## Decisions

- Decision: keep the repository-owned live bridge contract separate from the raw Windows agent
  payload.
  - Rationale: `windows_bridge_adapter.py` is a transport shell. The repository needs a stable
    contract it can validate and test even if the remote payload evolves.

- Decision: choose a polling-first live result retrieval contract keyed by `task_id` for the
  first implementation.
  - Rationale: the current bridge already returns `task_id`, while the repository has no
    approved inbound callback service, callback authentication story, or long-lived Windows push
    listener today. Polling-first is more observable and lower-risk for the first live bridge
    slice.

- Decision: define two explicit runtime stages for the live bridge:
  - `bridge_submission_receipt`
  - `bridge_result_payload`
  - Rationale: a task receipt is transport evidence only. Broker-facing lifecycle truth can
    advance only from the result payload.

- Decision: require the live bridge result payload to echo enough identity to bind safely.
  - Minimum expected fields:
    - `task_id`
    - `provider`
    - `method`
    - `client_order_id` or `local_submission_id`
    - `account_scope`
    - `result_status`
    - `occurred_at`
    - `broker_event_type` when broker-facing evidence exists
    - `external_order_id` when acknowledgement exists
    - `sequence_id` or equivalent when sequencing identity exists
  - Rationale: if the live result cannot echo the original submission identity, the system must
    not auto-bind broker truth.

- Decision: treat timeout, mismatch, or bridge unavailability as review-required runtime
  evidence, not as synthetic broker rejection and not as silent Tongdaxin fallback.
  - Rationale: the supplemental path is operator-assisted by design. The live bridge line must
    preserve that topology boundary.

- Decision: keep `OrderManagementService` as the canonical local anchor and continue to push
  transport-specific details into adjacent helpers or adapters.
  - Rationale: the recent refactor line already reduced service sprawl and should not be undone.

## Risks / Trade-offs

- The remote Windows bridge may not yet expose a stable `task_id -> result` endpoint.
  - Mitigation: define the contract first and keep the first implementation behind explicit
    runtime evidence and tests.

- Polling-first retrieval may be slower than a callback design.
  - Mitigation: keep callbacks as a future extension once authentication and ingress ownership
    are defined, but do not block the first safe live bridge slice on that work.

- Live bridge result payloads may diverge from repo expectations during early integration.
  - Mitigation: require versioned payload semantics and treat mismatches as review-required
    incidents rather than opportunistic coercion.

## Migration Plan

1. Add the live bridge capability spec and extend `trading-execution-safety`.
2. Freeze the repository-owned submission receipt and result payload contract.
3. Add the first canonical live result retrieval surface keyed by `task_id`.
4. Route polled live results back into the existing lifecycle and divergence ledgers.
5. Add timeout, mismatch, and explicit operator-escalation handling.
6. Update the broker truth registry and `FUNCTION_TREE.md` only after implementation evidence
   exists.

## Open Questions

- What exact remote result endpoint path should the repository standardize on for the Windows
  `qmt` agent?
- What polling cadence and timeout budget should be considered the first safe default?
- Should callback/webhook ingestion be specified now as an optional extension, or deferred until
  polling-first runtime evidence exists?
