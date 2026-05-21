# Backend OpenSpec Issue15 Publication Status

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-21

Status: published; decision/design-only; no backend implementation authorized.

Published issue:

- GitHub issue: `#92`
- URL: `https://github.com/chengjon/mystocks/issues/92`
- Title: `[Backend OpenSpec] Decide post-approval implementation plan`
- State: `OPEN`
- Labels: `enhancement`, `ready-for-human`

## Publication Preconditions

The issue15 publication gate was opened by:

- issue `#80` approval comment, with implementation still locked;
- issue `#83` accepted and closed with `evidence-accepted` and
  `ready-for-downstream`;
- PR `#89` merged Core split task `3.2` disposition;
- PR `#90` archived `split-backend-core-modules-with-compatibility-wrappers`;
- PR `#91` recorded the archived Core split branch in the steward tree.

## Verification

GitHub issue verification:

```text
number=92
state=OPEN
labels=enhancement, ready-for-human
has BLOCKED_BY_TODO=false
has UNBLOCKED_BY=true
has ready-for-agent label=false
has ready-for-human label=true
```

## Boundary

Issue `#92` is a human decision/design issue. It must not be moved to
`ready-for-agent` until a human decision record splits or approves concrete
implementation work.

It does not:

- authorize backend implementation;
- authorize Core Batch 2;
- publish a new OpenSpec proposal;
- retire compatibility wrappers;
- mutate routes, DI ownership, PM2 workflows, or runtime behavior.
