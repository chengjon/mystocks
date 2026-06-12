# B4.011-M2a Residual-U11-C P3-C5 Historical Evidence Review

Date: 2026-06-12

Mode: no-source decision review

## Scope

This review covers the final two untracked `docs/reports` residual files after U11-A and U11-B closed.

Baseline:

- `HEAD`: `4bf8fccad B4.011-M2a-Residual-U11-B: close active evidence node`
- Staged changes: empty at review start.
- Remaining `docs/reports` dirty entries: 2 untracked files.
- Existing U11-C node before this review: none.

Target files:

- `docs/reports/P3-C5-HANDOFF.md`
- `docs/reports/P3-C5-exception-consolidation-progress.md`

This review is no-source only. It does not add, move, archive, delete, or rewrite the target files.

## Evidence Matrix

| File | Git status | Shape | Title / declared state | Archive counterpart | Reference signal | Decision class |
|---|---:|---:|---|---|---|---|
| `docs/reports/P3-C5-HANDOFF.md` | `??` | 182 lines / 7,915 bytes | `P3-C5 异常整合 & 大文件拆分：交接文档`; declares core work completed and handoff-ready. | none | Filename reference exists outside `docs/reports`; broader `P3-C5` references exist in archive evidence and governance records. | Historical handoff evidence; useful completion-context candidate. |
| `docs/reports/P3-C5-exception-consolidation-progress.md` | `??` | 97 lines / 5,449 bytes | `P3-C5: 核心异常统一迁移 — 阶段性进度报告`; explicitly marked in-progress on 2026-05-18 with remaining work. | none | No direct filename references outside `docs/reports`; broader `P3-C5` references exist. | Superseded progress evidence; active-path preservation would risk stale truth. |

Related tracked truth:

- `docs/reports/P3-C5-exception-consolidation-completion-report.md` exists in `HEAD` and is tracked.
- `archive/docs/reports/quality/backend-error-contract-completion-verification-2026-05-19.md` exists in `HEAD` and states that the completion report supersedes older live-count / migration wording.
- Archived planning evidence also says not to treat `app/api` HTTPException migration as an open primary task for P3-C5.

## Decision

Recommended disposition:

- Preserve `docs/reports/P3-C5-HANDOFF.md` at the active report path because it is a completion/handoff index, not an obsolete work-in-progress status.
- Do not preserve `docs/reports/P3-C5-exception-consolidation-progress.md` at the active report path. It is useful historical evidence, but it is explicitly stale relative to the tracked completion report.
- Archive the progress report under `archive/docs/reports/` only if the user wants to retain the historical phase snapshot. Otherwise mark it as local-retire candidate after explicit cleanup authorization.

Practical implementation shape if approved:

- Option A, balanced preservation:
  - Track `docs/reports/P3-C5-HANDOFF.md`.
  - Move `docs/reports/P3-C5-exception-consolidation-progress.md` to `archive/docs/reports/P3-C5-exception-consolidation-progress.md` and track the archive path.
  - Remove the untracked active progress path from the worktree as part of the move.
- Option B, strict active-only preservation:
  - Track only `docs/reports/P3-C5-HANDOFF.md`.
  - Leave the progress report untracked for a later archive/retire decision.
- Option C, preserve both active paths:
  - Not recommended because the progress report says the task is still in progress and could contradict current tracked completion evidence.

Recommended next authorization:

`B4.011-M2a-Residual-U11-C balanced historical preservation implementation`

Recommended allowed actions:

- Add/track `docs/reports/P3-C5-HANDOFF.md`.
- Move `docs/reports/P3-C5-exception-consolidation-progress.md` to `archive/docs/reports/P3-C5-exception-consolidation-progress.md` and track the archive copy.
- Do not modify report text except for whitespace required by `git diff --cached --check`.

## Explicit Non-Goals

- Do not modify source, tests, routes, API paths, runtime code, OpenSpec, ST-HOLD, `marketKlineData`, `docs/guides/**`, or `docs/superpowers/**`.
- Do not reopen P3-C5 implementation or change any P3-C5 completion truth.
- Do not touch the tracked completion report.
- Do not touch historical untracked governance card files.
- Do not use broad staging or root cleanup commands.

## Gates For Any Future Implementation

- Exact staging must contain only the approved U11-C target paths.
- `git diff --cached --check` must pass.
- GitNexus `verify-staged` and direct `detect-changes --scope staged` must pass with risk `low` or record a docs-only caveat.
- OPENDOG verification must show no new blocker.
- Final `docs/reports` residual state must be reported.
