# Change: Add Windows qmt Agent Runtime Contract

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why
The repository has now completed the internal broker-truth foundation, channel-topology, primary
runtime, and repo-owned live-bridge normalization lines for `miniQMT`.

What still remains undefined is the next boundary outside the repo: the real Windows `qmt`
agent contract that the Linux trading runtime must call and trust.

Current repo truth still stops at a transport shell:

- `web/backend/app/services/windows_bridge_adapter.py` can post to `/api/v1/task/execute`
  and poll `/api/v1/task/result/{task_id}`
- `web/backend/app/services/miniqmt_live_bridge.py` can normalize receipts and polled results
- `OrderManagementService` can preserve timeout, unavailable, invalid-result, and mismatch
  evidence

But the project still does not have an approved, implementation-ready definition for:

- how Windows `qmt` agent authentication works
- how execute/result requests and responses are versioned
- what provider/method whitelist the agent must enforce
- which receipt/result fields are mandatory before broker truth may advance
- how auth failures, unsupported versions, unsupported methods, and agent unavailability must be
  surfaced without silent Tongdaxin fallback

The newly committed review draft
`docs/guides/quant-trading/windows-qmt-agent-live-contract-requirements-review.md` captured the
project-specific audit requirements. The next step is to turn that audit draft into an approved
OpenSpec implementation line.

## What Changes
- Add a new OpenSpec capability for the Windows `qmt` agent live contract.
- Define the first approved execute/result API contract between the Linux trading runtime and the
  Windows `qmt` agent for the `miniQMT` primary path.
- Freeze the v1 authentication, contract-version, provider/method whitelist, and result-envelope
  expectations the repository will trust.
- Define the minimum receipt and live-result identity fields required before broker-facing truth
  may advance.
- Define how auth failure, unsupported version, unsupported method, timeout, unavailable, and
  invalid-result states must become review-required runtime evidence.
- Modify `trading-execution-safety` so remote Windows agent auth/version/whitelist handling
  becomes part of the minimum safety contract for broker-facing paths.

## Impact
- Affected specs:
  - `windows-qmt-agent-live-contract`
  - `trading-execution-safety`
- Affected code:
  - `web/backend/app/services/windows_bridge_adapter.py`
  - `web/backend/app/services/miniqmt_live_bridge.py`
  - `src/application/trading/miniqmt_live_bridge_followup.py`
  - `src/application/trading/broker_submission_attempt.py`
  - `src/application/trading/order_mgmt_service.py`
  - `tests/ddd/test_phase_7_application.py`
  - future backend/service tests for authenticated execute/result polling
