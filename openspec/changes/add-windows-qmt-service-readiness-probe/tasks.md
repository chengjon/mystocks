# Tasks: Windows qmt Service Readiness Probe

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## 1. Spec

- [ ] 1.1 Add the `windows-qmt-service-readiness-probe` capability spec covering a repo-owned,
      read-only readiness entry point for Windows `qmt` / `miniQMT` services.
- [ ] 1.2 Modify `trading-execution-safety` so first Windows `qmt` service-ready claims require a
      dedicated readiness artifact rather than a contract acceptance run alone.
- [ ] 1.3 Run `openspec validate add-windows-qmt-service-readiness-probe --strict`.

## 2. Implementation

- [ ] 2.1 Add a repo-owned readiness probe command under `scripts/dev/` that can run from
      `WSL 上的 Ubuntu 24.04.4 LTS` against a separately deployed Windows `qmt` / `miniQMT`
      service without triggering `task/execute`.
- [ ] 2.2 Make the probe validate the documented `L1 / L2 / L3` readiness gates by combining:
  - local configuration preflight,
  - remote `/health` reachability,
  - required auth/version/source/provider disclosure fields,
  - and explicit readiness issues/missing fields.
- [ ] 2.3 Emit a machine-readable JSON summary plus standard report artifacts for the latest and
      timestamped readiness verdicts.
- [ ] 2.4 Ensure the probe makes it explicit that readiness is a pre-acceptance gate and not
      broker-truth proof or live trading approval.

## 3. Verification

- [ ] 3.1 Add or extend unit tests that freeze the `L1 / L2 / L3` verdict semantics and fail-closed
      behavior.
- [ ] 3.2 Run the targeted readiness-probe unit test file(s).
- [ ] 3.3 Run `python -m py_compile` for the new or updated readiness-probe script(s).
- [ ] 3.4 Re-run `openspec validate add-windows-qmt-service-readiness-probe --strict` before
      commit.

## 4. Documentation

- [ ] 4.1 Update the Windows `qmt` readiness checklist and acceptance guide so the recommended
      operator order becomes readiness probe first, formal sequence second.
- [ ] 4.2 Update `docs/guides/quant-trading/INDEX.md` and `docs/FUNCTION_TREE.md` if the local
      repo-owned tooling surface changes.
