# Change: Add miniQMT Primary Broker Adapter Runtime

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why
The broker-truth foundation line and the channel-topology line are both complete, but the
current repository still stops at a repo-facing boundary:

- `miniQMT` is only classified as the first `primary-candidate` broker-truth channel
- `OrderManagementService` persists local submissions and lifecycle evidence
- `src/application/trading/miniqmt_lifecycle_ingestion.py` normalizes inbound payloads
- `web/backend/app/services/windows_bridge_adapter.py` still returns a remote task receipt,
  not a canonical broker-facing submission or acknowledgement contract

That means the project now has channel-scoped correlation and lifecycle ingestion semantics,
but it still lacks the next approved layer: a canonical runtime contract for sending a local
order to the `miniQMT` primary path, distinguishing bridge transport receipt from broker
acknowledgement, and preserving explicit fallback or handoff boundaries when the primary path
cannot confirm external truth.

Without this change, the repository cannot safely move from "repo-facing lifecycle capture"
to "verified primary broker runtime path", and future live-trading claims would overstate the
actual bridge/runtime evidence.

## What Changes
- Add a new OpenSpec capability for the `miniQMT` primary broker adapter runtime.
- Define the canonical submission contract from the local trading application path into the
  `miniQMT` primary channel.
- Define the boundary between:
  - local order persistence
  - remote bridge or transport receipt
  - explicit broker acknowledgement and external order identity
- Define how deferred `miniQMT` bridge results or callbacks re-enter the shared broker
  lifecycle and correlation surfaces.
- Define the degradation and operator-handoff contract when the primary path cannot prove
  broker acknowledgement and Tongdaxin supplemental handling is invoked.
- Modify `trading-execution-safety` so asynchronous bridge receipt is never conflated with
  broker acknowledgement and audit records preserve transport-stage evidence.

## Impact
- Affected specs:
  - `miniqmt-primary-broker-adapter-runtime`
  - `trading-execution-safety`
- Affected code:
  - `src/application/trading/order_mgmt_service.py`
  - `src/application/trading/`
  - `web/backend/app/services/windows_bridge_adapter.py`
  - future bridge callback / polling ingress under `web/backend/app/`
  - `tests/ddd/test_phase_7_application.py`
  - future runtime or integration tests covering `miniQMT` bridge delivery
