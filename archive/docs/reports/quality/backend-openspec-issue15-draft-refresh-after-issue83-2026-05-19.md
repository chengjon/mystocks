# Backend OpenSpec Issue 15 Draft Refresh After Issue 83

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Recorded at: `2026-05-19`

## Scope

Refresh the unpublished issue15 draft after issue `#83` moved to
`ready-for-agent` and after another line reported the first validation messages
Core helper split.

Draft updated:

```text
docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/15-decide-post-approval-plan.md
```

## Reason

The original issue15 draft asked the reviewer to draft the first low-risk Core
split batch.

That wording became stale after another line reported:

```text
caa5a6bd6339d2dea6ed5d55a3be28dae40c64fe
refactor(core): split validation messages wrapper
```

Issue15 should now decide the next Core split batch or wrapper-retirement
decision boundary, not reopen the already-completed validation messages split as
new implementation work.

## Changes Made

The issue15 draft now:

- states that validation messages helper split evidence should be reconciled via
  issue `#83`;
- asks the reviewer to decide the next Core split batch or defer it until F
  runtime tasks 4.3 / 4.4 / 4.5 have evidence or a documented blocker owner;
- requires the decision record to cite commit
  `caa5a6bd6339d2dea6ed5d55a3be28dae40c64fe` when reachable;
- keeps the issue decision/design-only;
- keeps backend implementation locked.

## Boundaries

This refresh did not:

- publish issue15;
- replace issue15's shared evidence package placeholder;
- move issue15 to any GitHub state;
- create OpenSpec proposals;
- mutate backend code.

Issue15 remains unpublished and still contains:

```text
BLOCKED_BY_TODO: shared evidence package.
```
