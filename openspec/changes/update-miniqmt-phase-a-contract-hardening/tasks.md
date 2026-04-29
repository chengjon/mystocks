## 1. Implementation

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [x] 1.1 Update the repo-owned Windows `qmt` reference service so the Phase A result envelope
      consistently includes `event_id` alongside the already-frozen contract metadata
- [x] 1.2 Preserve canonical Phase A identity fields through live result normalization and deferred
      `miniQMT` follow-up re-entry, including `account_scope`, `event_id`, `occurred_at`,
      `source_name`, and `bridge_contract_version`
- [x] 1.3 Add or extend repository tests that freeze the Phase A field set for the Windows `qmt`
      reference service and the local follow-up re-entry path

## 2. Validation

- [x] 2.1 Run `pytest web/backend/tests/services/test_miniqmt_live_bridge.py -q --no-cov`
- [x] 2.2 Run `pytest tests/unit/windows_qmt_agent/test_reference_service.py -q --no-cov`
- [x] 2.3 Run `pytest tests/ddd/test_phase_7_application.py -q --no-cov`
- [x] 2.4 Run `openspec validate update-miniqmt-phase-a-contract-hardening --strict`
