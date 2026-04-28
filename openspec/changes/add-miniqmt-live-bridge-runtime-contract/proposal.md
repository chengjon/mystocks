# Change: Add miniQMT Live Bridge Runtime Contract

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why
The repository has now completed three prerequisite lines:

- generic broker acknowledgement and reconciliation foundation
- project-specific `miniQMT primary / Tongdaxin supplemental` channel topology
- repo-facing `miniQMT` primary runtime classification, deferred lifecycle re-entry, and explicit
  supplemental handoff evidence

But the current implementation still stops at a repository-owned normalization boundary:

- `src/application/trading/miniqmt_primary_runtime.py` can classify immediate runtime outcomes
- `OrderManagementService.ingest_miniqmt_bridge_result_payload()` can re-enter deferred results
  into the shared lifecycle envelope
- `web/backend/app/services/windows_bridge_adapter.py` still only posts to a remote
  `/api/v1/task/execute` surface and returns a synthesized receipt with `task_id`

That means the project still lacks the next approved layer: a canonical live bridge contract
between the Linux trading runtime and the Windows `miniQMT` agent. Today there is still no
repository-owned definition for:

- the submission receipt shape returned by the Windows `qmt` bridge
- the first canonical result retrieval path keyed by `task_id`
- the minimum fields that a deferred live bridge result must echo back before broker identity may
  be bound
- the timeout, mismatch, and operator-escalation rules when the live bridge does not produce
  safe broker-facing evidence

Without this change, the repo can safely describe only an experimental repo-facing primary
runtime path, not a verified live bridge path.

## What Changes
- Add a new OpenSpec capability for the `miniQMT` live bridge runtime contract.
- Define the first repository-owned live bridge contract between the Linux trading runtime and
  the Windows `miniQMT` agent.
- Freeze the canonical live submission receipt shape for `qmt` primary submissions.
- Define the first canonical result retrieval path for live bridge results, including whether the
  first implementation is polling-first or callback-first.
- Define the identity echo requirements for live bridge result payloads before lifecycle
  binding may advance from transport receipt to broker truth.
- Define timeout, mismatch, bridge-unavailable, and explicit operator-escalation semantics so
  Tongdaxin never becomes a silent fallback path.
- Modify `trading-execution-safety` so live bridge result delivery, timeout, and mismatch
  handling become part of the minimum trading safety contract.

## Impact
- Affected specs:
  - `miniqmt-live-bridge-runtime`
  - `trading-execution-safety`
- Affected code:
  - `web/backend/app/services/windows_bridge_adapter.py`
  - future `miniQMT` live bridge polling / callback ingress under `web/backend/app/`
  - `src/application/trading/miniqmt_primary_runtime.py`
  - `src/application/trading/primary_broker_followup.py`
  - `src/application/trading/order_mgmt_service.py`
  - `tests/ddd/test_phase_7_application.py`
  - future integration tests covering Windows agent result retrieval and timeout handling
