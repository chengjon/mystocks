# Change: update-miniqmt-phase-a-contract-hardening

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why

The separate Windows `miniQMT` project has now absorbed the cross-project contract decisions for
Phase A, but the repository-owned `mystocks_spec` side still has a narrow local gap:

- the Windows `qmt` reference service does not yet treat `event_id` as a first-class v1 field
- normalized live bridge results do not fully preserve the newly frozen identity fields through the
  deferred follow-up re-entry path
- the repo-owned contract tests do not yet lock these fields as a stable v1 boundary

Without this hardening batch, the cross-project contract is documented but not fully enforced by
the local reference implementation and test suite.

## What Changes

- Tighten the repo-owned Windows `qmt` reference service to emit the canonical Phase A fields needed
  by `mystocks_spec`, especially `event_id`, `account_scope`, `occurred_at`, `source_name`, and
  `bridge_contract_version`
- Preserve the same canonical fields across live result normalization and deferred
  `miniQMT` follow-up re-entry into the shared lifecycle ledger
- Add or extend contract tests so the local reference service and `WSL 上的 Ubuntu 24.04.4 LTS`
  runtime fail if these fields drift
- Keep the scope limited to Phase A contract hardening; do not introduce real Windows
  `miniQMT` SDK adapter logic, callback ingestion, multi-account routing, or Tongdaxin automation

## Impact

- Affected specs:
  - `trading-execution-safety`
- Affected code:
  - `scripts/windows_qmt_agent/service.py`
  - `web/backend/app/services/miniqmt_live_bridge.py`
  - `src/application/trading/miniqmt_live_bridge_followup.py`
  - `web/backend/tests/services/test_miniqmt_live_bridge.py`
  - `tests/unit/windows_qmt_agent/test_reference_service.py`
  - `tests/ddd/test_phase_7_application.py`
