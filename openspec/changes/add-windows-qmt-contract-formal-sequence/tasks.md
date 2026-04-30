> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## 1. Specification

- [x] 1.1 Add the `windows-qmt-contract-formal-sequence` capability spec covering the canonical
      `preflight -> verify -> compare -> summarize -> optional freeze` sequence from
      `WSL 上的 Ubuntu 24.04.4 LTS`.
- [x] 1.2 Modify `trading-execution-safety` so first formal readiness claims for an external
      Windows broker-facing path require a local sequence artifact and remain distinct from
      production broker truth.
- [x] 1.3 Run `openspec validate add-windows-qmt-contract-formal-sequence --strict`.

## 2. Implementation

- [x] 2.1 Add a repo-owned formal sequence entry point under `scripts/dev/` that orchestrates the
      existing acceptance harness, optional baseline comparison, read-only summary, and explicit
      baseline freeze.
- [x] 2.2 Default the sequence to `contract_profile=kernel-phase-a` plus the standard Windows qmt
      report directory, while still allowing explicit operator override where needed.
- [x] 2.3 Emit a machine-readable sequence manifest that records step order, step outcomes,
      artifact paths, and the final recommended exit code.
- [x] 2.4 Ensure the sequence treats acceptance success as contract-level evidence only and does
      not synthesize production broker-truth claims.

## 3. Verification

- [x] 3.1 Add unit tests for:
      - no-baseline formal sequence
      - baseline-compare formal sequence
      - explicit baseline-freeze success path
      - refusal to freeze when the source acceptance summary is not successful
- [x] 3.2 Run targeted tests for the formal sequence entry point and the touched helper scripts.
- [x] 3.3 Re-run `openspec validate add-windows-qmt-contract-formal-sequence --strict` before
      closeout.

## 4. Documentation

- [x] 4.1 Update the Windows qmt acceptance guide with the canonical formal-sequence command,
      expected artifacts, and operator review flow.
- [x] 4.2 Update `docs/guides/quant-trading/INDEX.md` and `docs/FUNCTION_TREE.md` so the new
      sequence is the canonical local Phase A acceptance path.
