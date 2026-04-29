# Tasks: Windows qmt Contract Acceptance Harness

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## 1. Implementation

- [x] 1.1 Add a repo-owned local acceptance harness that probes a Windows `qmt` service from
      `WSL 上的 Ubuntu 24.04.4 LTS`, validates `/health`, and runs the existing
      `qmt/submit_order -> task_id -> result` contract through the normalized local runtime path
- [x] 1.2 Fail closed by default unless the remote health payload explicitly advertises
      `provider_mode=mock`, while still allowing the operator to see why execution was blocked
- [x] 1.3 Emit a machine-readable summary containing the health payload, normalized receipt,
      normalized result, verified field list, and any gating or validation issues
- [x] 1.4 Add or extend tests that freeze the harness behavior for success, fail-closed provider
      mode mismatches, and missing canonical result fields
- [x] 1.5 Update the quant-trading guide family and `FUNCTION_TREE.md` so the new acceptance entry
      point is visible to future integration work

## 2. Validation

- [x] 2.1 Run `pytest tests/unit/scripts/test_verify_windows_qmt_agent_contract.py -q --no-cov`
- [x] 2.2 Run `openspec validate add-windows-qmt-contract-acceptance-harness --strict`
