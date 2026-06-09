# Backend OpenSpec Issue 83 Core Split Cross-Line Impact

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Recorded at: `2026-05-19`

## Input

Another line reports that it completed the first low-risk Core helper split for:

```text
commit: caa5a6bd6339d2dea6ed5d55a3be28dae40c64fe
title: refactor(core): split validation messages wrapper
reported remote: wip/root-dirty-20260403
```

Local checkout status at review time:

```text
current HEAD: 02ac506cec8ef926e09090208cb584be65621749
current branch: wip/root-dirty-20260403
remote wip/root-dirty-20260403: e7c0cbdd1724f949f555e409dfe67efecf008be6
local branch containing caa5a6bd6: contract-startup-unblock
```

Therefore commit `caa5a6bd6339d2dea6ed5d55a3be28dae40c64fe` is visible locally
as a Git object and is contained in the remote branch history, but it is not an
ancestor of the current checkout `HEAD` yet.

Changed paths confirmed from the commit object:

```text
docs/reports/quality/backend-core-split-helper-batch1-2026-05-19.md
openspec/changes/split-backend-core-modules-with-compatibility-wrappers/design.md
openspec/changes/split-backend-core-modules-with-compatibility-wrappers/proposal.md
openspec/changes/split-backend-core-modules-with-compatibility-wrappers/specs/architecture-governance/spec.md
openspec/changes/split-backend-core-modules-with-compatibility-wrappers/specs/directory-governance/spec.md
openspec/changes/split-backend-core-modules-with-compatibility-wrappers/tasks.md
tests/unit/core/test_validation_messages_compat.py
web/backend/app/core/validation/__init__.py
web/backend/app/core/validation/messages.py
web/backend/app/core/validation_messages.py
```

## Local Scope Interpretation

This line currently owns the GitHub publication / governance flow:

```text
#80 approval gate
#83 issue 14: [Backend OpenSpec] Build shared C/E/F evidence package
```

Issue `#83` was published with initial labels:

```text
enhancement, needs-triage
```

It was not moved to `ready-for-agent`.

## Impact On This Line

The other line affects this line, but only as cross-line evidence and remote
state unless / until the current checkout is fast-forwarded or otherwise merged:

- F-line first helper split is no longer a purely future candidate.
- `app.core.validation.messages` is now the canonical implementation path.
- `app.core.validation_messages` is now an intentional compatibility wrapper.
- `app.core.validation` now provides package re-exports.
- The F OpenSpec tasks now show first-batch implementation progress.
- Runtime gates 4.3 / 4.4 / 4.5 remain open due a startup/import blocker outside
  the validation messages split.

It does not invalidate issue `#83`. Instead, it changes what `#83` should do:

- collect and reconcile the new F evidence;
- avoid re-running the same implementation as agent work;
- keep remaining C/E/F evidence boundaries explicit;
- keep runtime/OpenAPI blockers separate from the validation helper split.

## Merge Recommendation

Do not merge implementation progress into this publication line as a new code
batch.

Reason:

- issue `#83` is an evidence package issue, not an implementation issue;
- issue `#83` explicitly has no `ready-for-agent` label;
- the implementation already landed in the other line and is represented by
  commit `caa5a6bd6339d2dea6ed5d55a3be28dae40c64fe`;
- the current checkout has untracked governance artifacts from this publication
  line, so updating the local branch should be handled as a separate git hygiene
  step rather than mixed into issue `#83` triage;
- duplicating it here would blur the governance boundary between publication,
  evidence collection, and backend implementation.

Recommended handling:

1. Treat commit `caa5a6bd6339d2dea6ed5d55a3be28dae40c64fe` as external evidence
   for issue `#83`.
2. Do not pull, merge, or fast-forward this checkout as part of issue `#83`
   triage while the publication-line documents remain untracked.
3. Keep issue `#83` in `needs-triage`.
4. Do not move issue `#83` to `ready-for-agent` until the triage gate is rerun
   against the updated F-line state.
5. Before publishing issue 15, revise its draft because the "select / draft the
   first low-risk Core split batch" decision is now partially superseded by the
   completed validation messages batch.

## PM2 / Health / OpenAPI Blockers

The reported blocker is:

```text
ImportError: cannot import name 'ContractDriftIncidentListResponse' from 'app.api.contract.schemas'
```

This blocker should not be merged into this line as an implementation task.

Current interpretation:

- It blocks full PM2 startup verification.
- It blocks health endpoint smoke verification for this batch.
- It blocks route/OpenAPI drift confirmation for this batch.
- It appears outside the validation messages split because the batch did not
  modify `app.api.contract`, `router_registry`, or route registration files.

Recommended handling:

- keep F tasks 4.3 / 4.4 / 4.5 open;
- record the blocker in issue `#83` evidence if a GitHub comment is later
  approved;
- route the contract import failure to the appropriate contract/OpenAPI
  stabilization lane, not to the Core helper split line.

## Issue 15 Impact

Issue 15 remains unpublished.

Its current draft still has:

```text
BLOCKED_BY_TODO: shared evidence package.
```

That placeholder should remain until issue `#83` has a completed or explicitly
accepted evidence status.

However, before issue 15 is published, its decision language should be reviewed:

- replace "select the first low-risk Core split batch" with a decision about the
  next Core split batch or wrapper retirement criteria;
- cite commit `caa5a6bd6339d2dea6ed5d55a3be28dae40c64fe` and
  `docs/reports/quality/backend-core-split-helper-batch1-2026-05-19.md`;
- preserve the implementation lock for any future batches until the appropriate
  OpenSpec / issue approval exists.

## Current Decision

Do not merge the other line into this line as implementation work.

Do integrate it as evidence for issue `#83` and as a required input to the next
issue15 draft review.

If the local checkout must be updated to remote `wip/root-dirty-20260403`, do it
as a separate git hygiene action after deciding how to preserve or commit this
line's untracked governance artifacts.
