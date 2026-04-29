> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## 1. Spec And Validation

- [ ] 1.1 Add the `windows-qmt-agent-live-contract` capability spec covering authenticated
      execute/result interfaces, contract-version expectations, provider/method whitelist,
      mandatory receipt/result fields, and explicit failure semantics.
- [ ] 1.2 Modify `trading-execution-safety` so remote Windows agent auth/version/whitelist
      failures remain experimental and cannot advance broker truth.
- [ ] 1.3 Run `openspec validate add-windows-qmt-agent-runtime-contract --strict`.

## 2. Transport Contract Implementation

- [ ] 2.1 Extend `web/backend/app/services/windows_bridge_adapter.py` so Windows `qmt` execute
      and result requests carry the approved auth/version contract.
- [ ] 2.2 Extend `web/backend/app/services/miniqmt_live_bridge.py` to normalize auth failure,
      unsupported version, unsupported method, and explicit reason-code surfaces.
- [ ] 2.3 Add runtime configuration for bridge token, poll timeout, poll interval, and contract
      version without logging secrets or exposing raw credentials.
- [ ] 2.4 Constrain the Windows bridge call surface to the approved `qmt` provider and method
      whitelist instead of a generic remote command path.

## 3. Runtime Safety And Evidence

- [ ] 3.1 Route authenticated execute/result failures back into
      `src/application/trading/miniqmt_live_bridge_followup.py` and `OrderManagementService` as
      review-required runtime evidence.
- [ ] 3.2 Preserve `task_id`, `bridge_contract_version`, `reason_code`, `reason_detail`, and
      failure class in submission-attempt and divergence surfaces.
- [ ] 3.3 Add targeted backend/service tests for authenticated receipt/result polling,
      unsupported version, unsupported method, invalid payload, and unavailable endpoint
      handling.
- [ ] 3.4 Extend `tests/ddd/test_phase_7_application.py` for auth failure, timeout, identity
      mismatch, and explicit Tongdaxin supplemental handoff evidence retention.

## 4. Documentation And Closeout

- [ ] 4.1 Update
      `docs/guides/quant-trading/windows-qmt-agent-live-contract-requirements-review.md` with the
      approved v1 contract decisions and any implementation-specific caveats.
- [ ] 4.2 Update `docs/guides/quant-trading/broker-execution-truth-registry.md` and
      `docs/FUNCTION_TREE.md` only after implementation evidence exists.
- [ ] 4.3 Re-run `openspec validate add-windows-qmt-agent-runtime-contract --strict`.
- [ ] 4.4 Re-run the targeted backend/service and DDD tests, then record repo-truth evidence
      before closeout.
