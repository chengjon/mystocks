# Backend Core Split Post-Acceptance OpenSpec Archive

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: review-ready
- Review date: 2026-05-21 Asia/Shanghai
- Worktree: `.worktrees/post-pr89-core-split-archive`
- Base branch: `origin/wip/root-dirty-20260403`
- Base HEAD: `63cf97e79f8fd05248b2704b5906defc7c932ddf`
- Base subject: `Merge pull request #89 from chengjon/post-issue83-acceptance-3-2`

## Closure Input

The following gates are complete before archive:

- issue `#83` shared C/E/F evidence package accepted and closed;
- OpenSpec task `3.2` marked complete by PR `#89`;
- `split-backend-core-modules-with-compatibility-wrappers` reports `✓ Complete`;
- pre-archive strict validation passed for the change.

## Archive Action

Command:

```text
openspec archive split-backend-core-modules-with-compatibility-wrappers --yes
```

Archive result:

```text
Task status: ✓ Complete

Specs to update:
  architecture-governance: update
  directory-governance: update
Applying changes to openspec/specs/architecture-governance/spec.md:
  + 2 added
Applying changes to openspec/specs/directory-governance/spec.md:
  + 3 added
Totals: + 5, ~ 0, - 0, -> 0
Specs updated successfully.
Change 'split-backend-core-modules-with-compatibility-wrappers' archived as '2026-05-21-split-backend-core-modules-with-compatibility-wrappers'.
```

Archived paths:

- `openspec/changes/archive/2026-05-21-split-backend-core-modules-with-compatibility-wrappers/design.md`
- `openspec/changes/archive/2026-05-21-split-backend-core-modules-with-compatibility-wrappers/proposal.md`
- `openspec/changes/archive/2026-05-21-split-backend-core-modules-with-compatibility-wrappers/tasks.md`
- `openspec/changes/archive/2026-05-21-split-backend-core-modules-with-compatibility-wrappers/specs/architecture-governance/spec.md`
- `openspec/changes/archive/2026-05-21-split-backend-core-modules-with-compatibility-wrappers/specs/directory-governance/spec.md`

Canonical specs updated:

- `openspec/specs/architecture-governance/spec.md`
- `openspec/specs/directory-governance/spec.md`

## Verification

Post-archive spec validation:

```text
openspec validate --specs --strict --concurrency 1
Totals: 32 passed, 0 failed (32 items)
```

PostHog telemetry emitted `ECONNREFUSED` after successful OpenSpec validation.
This is the same telemetry noise observed in earlier OpenSpec runs and is not a
validation failure.

## Boundary

This is an OpenSpec archive step only. It does not:

- modify backend, frontend, test, or runtime behavior files;
- authorize another Core helper implementation batch;
- delete compatibility wrappers;
- publish issue15;
- create a new OpenSpec proposal.

Any future Core split work must start from a new concrete plan with current
impact analysis, compatibility tests, and explicit approval.
