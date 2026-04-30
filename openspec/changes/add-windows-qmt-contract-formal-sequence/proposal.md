# Change: Add Windows qmt Contract Formal Sequence

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why

The repository already has the local building blocks for Windows `qmt` / `miniQMT` Phase A
contract verification:

- a repo-owned acceptance harness
- baseline freeze and drift comparison helpers
- read-only summary tooling
- `kernel-phase-a` contract-profile alignment for the external `/mnt/d/MyCode3/miniQMT` project

What it still lacks is a single formal sequence that operators can run from `WSL 上的 Ubuntu 24.04.4 LTS`
when the external Windows service is ready.

Without a canonical sequence, the first real cross-project acceptance remains too manual:

- operators must remember which local scripts to run and in what order
- `kernel-phase-a` defaults can drift between runs
- report, comparison, summary, and optional baseline-freeze artifacts do not yet have one
  canonical orchestration entry point
- a successful contract acceptance can be confused with production broker truth if the local flow
  is not explicitly framed as a Phase A acceptance sequence

## What Changes

- Add a repo-owned formal acceptance sequence entry point that orchestrates:
  - readiness preflight from `WSL 上的 Ubuntu 24.04.4 LTS`
  - Windows `qmt` / `miniQMT` contract verification
  - optional baseline drift comparison
  - read-only status summary
  - explicit, opt-in baseline freeze after a successful reviewed run
- Default the formal sequence to the external `miniQMT` v1 kernel posture:
  - `contract_profile=kernel-phase-a`
  - standard report directory under `docs/reports/quality/windows-qmt-contract-acceptance`
- Emit a machine-readable sequence manifest that records:
  - invoked steps
  - step outcomes
  - produced artifact paths
  - final recommended exit status
- Modify trading execution safety so first formal readiness claims for an external Windows
  broker-facing path must point to a local formal acceptance sequence artifact and must not be
  described as production broker truth by default

## Impact

- Affected specs:
  - `windows-qmt-contract-formal-sequence` (new)
  - `trading-execution-safety` (modified)
- Affected code:
  - `scripts/dev/verify_windows_qmt_agent_contract.py`
  - `scripts/dev/summarize_windows_qmt_acceptance_reports.py`
  - `scripts/dev/freeze_windows_qmt_acceptance_baseline.py`
  - new formal-sequence orchestration entry point under `scripts/dev/`
  - `tests/unit/scripts/`
  - `docs/guides/quant-trading/windows-qmt-agent-contract-acceptance-guide.md`
  - `docs/guides/quant-trading/INDEX.md`
  - `docs/FUNCTION_TREE.md`
