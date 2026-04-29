# Change: Add Windows qmt Contract Acceptance Harness

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why

The repository now has a repo-owned Windows `qmt` reference service, authenticated/versioned bridge
adapter behavior, and a normalized `miniQMT` primary-path live bridge contract. What it still
lacks is a local acceptance harness that can safely verify a separately deployed Windows `miniQMT`
service from `WSL 上的 Ubuntu 24.04.4 LTS`.

Without this harness, cross-project integration remains manual and drift-prone:

- there is no canonical local command that checks `/health`, auth/version disclosure, and the
  `qmt/submit_order -> task_id -> result` contract through the existing Ubuntu / WSL-side runtime
- there is no fail-closed guard that refuses to run a full order-path smoke against a service that
  is not explicitly advertising `provider_mode=mock`
- there is no repo-owned acceptance summary artifact that freezes what "Phase A contract ready for
  integration" means on the local side

## What Changes

- Add a repo-owned acceptance harness that runs from `WSL 上的 Ubuntu 24.04.4 LTS` against a
  Windows `qmt` agent URL and validates:
  - `/health` disclosure
  - bridge auth/version configuration
  - `miniQMT` primary-path submission receipt normalization
  - polling-first deferred result normalization
- Default the harness to fail closed unless the remote service advertises `provider_mode=mock`
- Emit a machine-readable summary that records the health payload, receipt payload, result payload,
  verified fields, and failure reasons
- Add unit tests and guide docs so this harness becomes the canonical local pre-integration entry
  point for the separate Windows `miniQMT` project

## Impact

- Affected specs:
  - `windows-qmt-agent-contract-acceptance` (new)
- Affected code:
  - `scripts/dev/verify_windows_qmt_agent_contract.py`
  - `tests/unit/scripts/test_verify_windows_qmt_agent_contract.py`
  - `docs/guides/quant-trading/windows-qmt-agent-contract-acceptance-guide.md`
  - `docs/guides/quant-trading/INDEX.md`
  - `docs/FUNCTION_TREE.md`
