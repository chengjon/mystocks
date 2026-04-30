# Change: Add Windows qmt Service Readiness Probe

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why

The repository now has:

- a Windows `qmt` / `miniQMT` service ready checklist document,
- a local contract acceptance harness,
- and a formal sequence that can run `verify -> compare -> summarize -> optional freeze`.

What it still does **not** have is a repo-owned, read-only command that an operator can run from
`WSL 上的 Ubuntu 24.04.4 LTS` to determine whether a separately deployed Windows `miniQMT`
service has actually reached the documented `L1 / L2 / L3` readiness thresholds **before**
attempting any `task/execute` smoke.

Without this capability, the project still has a gap between:

- narrative checklist guidance, and
- machine-readable runtime evidence that the Windows side is truly ready for first formal
  contract acceptance.

## What Changes

- Add a new OpenSpec capability for a Windows `qmt` service readiness probe.
- Introduce a repo-owned, read-only readiness entry point that:
  - runs from `WSL 上的 Ubuntu 24.04.4 LTS`,
  - probes the Windows-side `/health` contract,
  - validates the documented `L1 / L2 / L3` readiness criteria,
  - emits a machine-readable readiness verdict plus artifact paths,
  - and **does not** trigger `qmt/submit_order` or `task/result` smoke.
- Modify `trading-execution-safety` so a Windows `qmt` / `miniQMT` service cannot be described as
  `service ready` for first formal cross-project acceptance unless a dedicated readiness artifact
  exists.
- Update operator-facing docs so the expected sequence becomes:
  - checklist understanding,
  - readiness probe,
  - formal sequence,
  - optional baseline freeze.

## Impact

- Affected specs:
  - `windows-qmt-service-readiness-probe` (new)
  - `trading-execution-safety` (modified)
- Affected code:
  - `scripts/dev/` Windows `qmt` local tooling
  - `tests/unit/scripts/`
  - `docs/guides/quant-trading/`
  - `docs/FUNCTION_TREE.md`
