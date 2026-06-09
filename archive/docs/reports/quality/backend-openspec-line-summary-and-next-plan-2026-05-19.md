# Backend OpenSpec Line Summary And Next Plan

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Recorded at: `2026-05-19`

## Scope

This document summarizes the current backend OpenSpec publication / triage line
and proposes the next work plan for human review.

This line covers:

- issue `#80` approval gate;
- issue `#83` shared C/E/F evidence package publication and triage;
- issue15 draft readiness;
- cross-line boundary with the F Core split implementation line;
- git hygiene needed before pulling or merging remote work.

This line does not cover:

- backend implementation;
- PM2 workflow execution;
- contract/OpenAPI startup fixes;
- publishing issue15 without a separate approval decision.

## Current Verified State

GitHub issue state checked during this line:

| Issue | Title | State | Labels | Notes |
|---|---|---|---|---|
| `#80` | `[Backend OpenSpec] Approve orchestration and C/E/F/G proposal scope` | `OPEN` | `enhancement`, `ready-for-human` | approval record comment posted |
| `#83` | `[Backend OpenSpec] Build shared C/E/F evidence package` | `OPEN` | `enhancement`, `ready-for-agent` | agent brief comment posted |

Current checkout state observed before writing this document:

```text
current branch: wip/root-dirty-20260403
current HEAD: 7996d8848
remote wip/root-dirty-20260403: bbb399071df53c2ae6a1001f0b65ebf3e8baddea
caa5a6bd6 ancestor of current HEAD: false
local branch containing caa5a6bd6: contract-startup-unblock
```

Issue15 draft state:

```text
docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/15-decide-post-approval-plan.md
```

- still unpublished;
- still contains `BLOCKED_BY_TODO: shared evidence package.`;
- now references `caa5a6bd6339d2dea6ed5d55a3be28dae40c64fe`;
- now asks for the next Core split batch / wrapper-retirement decision boundary,
  not for reopening the already-reported validation messages split.

## Completed Work

### 1. Compressed Publication Package

The earlier 15 draft bodies were compressed into the current 3-issue publication
shape:

| Order | Body | GitHub status |
|---:|---|---|
| 1 | `01-approve-orchestration.md` | published as `#80` |
| 2 | `14-build-shared-evidence-package.md` | published as `#83` |
| 3 | `15-decide-post-approval-plan.md` | not published |

The non-published audit / merged-source bodies remain evidence records rather
than new GitHub issues.

### 2. Issue 80 Approval Gate

The maintainer provided approval:

```text
APPROVED: issue #80 scope accepted. Implementation remains locked. Issue 14 may proceed to publication with initial needs-triage only.
```

The approval was recorded locally:

```text
docs/reports/quality/backend-openspec-issue80-approval-record-2026-05-19.md
```

The approval was also recorded on GitHub:

```text
https://github.com/chengjon/mystocks/issues/80#issuecomment-4484052256
```

Boundary preserved:

- approval accepted `#80` scope;
- implementation remained locked;
- only issue14 publication with initial `needs-triage` was authorized.

### 3. Issue 14 Publication As Issue 83

Issue 14 was published as GitHub issue `#83`:

```text
https://github.com/chengjon/mystocks/issues/83
```

Initial publication status:

```text
ISSUE_83_STATE=OPEN
ISSUE_83_LABELS=enhancement, needs-triage
```

Post-publication record:

```text
docs/reports/quality/backend-openspec-issue14-post-publication-status-2026-05-19.md
```

Boundaries preserved:

- no `ready-for-agent` label at initial publication;
- no issue15 publication;
- no backend implementation;
- no OpenSpec proposal creation;
- no PM2 workflow execution.

### 4. Issue 83 Triage Gate

Issue `#83` was evaluated against:

```text
docs/reports/quality/backend-openspec-issue14-triage-gate-2026-05-18.md
```

Gate result:

```text
Move issue #83 from needs-triage to ready-for-agent.
Keep category label enhancement.
```

Local gate record:

```text
docs/reports/quality/backend-openspec-issue83-triage-gate-2026-05-19.md
```

GitHub transition completed:

```text
ISSUE_83_STATE=OPEN
ISSUE_83_LABELS=enhancement, ready-for-agent
```

Agent brief comment:

```text
https://github.com/chengjon/mystocks/issues/83#issuecomment-4488769140
```

Status record:

```text
docs/reports/quality/backend-openspec-issue83-ready-for-agent-status-2026-05-19.md
```

The ready-for-agent scope is limited to evidence-package work. It does not
authorize backend implementation.

### 5. Cross-Line F Core Split Boundary

Another line reported:

```text
caa5a6bd6339d2dea6ed5d55a3be28dae40c64fe
refactor(core): split validation messages wrapper
```

This line treated that commit as external evidence input for issue `#83`, not as
work authorized by issue `#83`.

Cross-line impact record:

```text
docs/reports/quality/backend-openspec-issue83-core-split-cross-line-impact-2026-05-19.md
```

Other-line next-work boundary:

```text
docs/reports/quality/backend-core-split-other-line-next-work-boundary-2026-05-19.md
```

Current interpretation:

- the validation messages split is relevant evidence for F;
- current checkout has not incorporated `caa5a6bd6` as an ancestor;
- the other implementation line should continue in a clean worktree or clean
  branch state;
- contract/OpenAPI startup failures should not be mixed into the Core helper
  split batch unless direct causality is proven.

### 6. Issue15 Draft Refresh

The unpublished issue15 draft was updated to avoid stale F-line wording.

Refresh record:

```text
docs/reports/quality/backend-openspec-issue15-draft-refresh-after-issue83-2026-05-19.md
```

Current issue15 draft now:

- references `caa5a6bd6339d2dea6ed5d55a3be28dae40c64fe`;
- asks for the next Core split batch or wrapper-retirement boundary;
- keeps the decision/design-only boundary;
- keeps issue15 unpublished;
- keeps `BLOCKED_BY_TODO: shared evidence package.` unresolved.

## Current Open Items

| Item | Status | Owner / next decision |
|---|---|---|
| Issue `#83` evidence package execution | Ready for agent | Wait for assigned agent output |
| Issue15 publication | Blocked | Wait until `#83` evidence package is completed or explicitly accepted |
| Issue15 placeholder replacement | Blocked | Requires concrete `#83` evidence result / issue number reference decision |
| F runtime tasks 4.3 / 4.4 / 4.5 | Open | Need runtime evidence or separately owned blocker record |
| `ContractDriftIncidentListResponse` startup blocker | Separate lane | Contract/OpenAPI stabilization, not issue `#83` implementation |
| Current checkout vs remote branch | Needs git hygiene decision | Preserve untracked docs before any pull / merge / rebase |

## Git Hygiene Boundary

Selected publication-line files are currently untracked in this checkout. Before
pulling, merging, rebasing, or fast-forwarding to remote
`wip/root-dirty-20260403`, preserve these artifacts.

Do not mix in one commit:

- GitHub issue publication / triage records;
- backend Core implementation;
- contract/OpenAPI startup fixes;
- generated route/OpenAPI evidence;
- PM2 runtime gate changes.

Recommended safe options:

| Option | When to use | Action |
|---|---|---|
| Commit docs first | preferred if this line should be durable before branch movement | stage only publication-line docs and commit separately |
| Separate worktree | preferred for implementation continuation | continue backend implementation outside this dirty checkout |
| Stash with manifest | only if commit is not desired yet | record exact file list, stash intended docs, verify restoration |

## Next Work Plan

### Step 1. Wait For Issue 83 Agent Result

Do not publish issue15 yet.

Wait for issue `#83` to produce or report:

- C route/OpenAPI evidence or blocker;
- F Core import compatibility evidence, including validation messages split
  handling when reachable;
- E singleton/getter lifecycle inventory evidence;
- strict OpenSpec validation results for C, E, and F;
- explicit confirmation that no backend implementation files were modified.

### Step 2. Review Issue 83 Evidence Package

When `#83` returns results, review for:

- branch and HEAD recorded;
- generated artifact paths present;
- blockers clearly separated from evidence;
- no mutation of routes, Core files, DI lifecycle ownership, endpoint retirement,
  or PM2 workflow state;
- `ContractDriftIncidentListResponse` treated as blocker-only unless routed to a
  separate approved lane.

If evidence is incomplete, keep issue15 blocked and ask for a targeted evidence
follow-up under `#83`.

### Step 3. Decide Whether Issue 83 Is Accepted

After review, record one of:

```text
ACCEPTED: issue #83 evidence package is sufficient for issue15 planning.
```

or:

```text
NEEDS REVISION: issue #83 evidence package is missing ...
```

Do not infer acceptance from an agent completion message alone.

### Step 4. Prepare Issue15 Publication Packet

Only after issue `#83` is accepted:

- replace `BLOCKED_BY_TODO: shared evidence package.` with the final issue `#83`
  evidence reference;
- re-run scoped markdown governance gate;
- confirm issue15 body has exactly one state label planned: `ready-for-human`;
- confirm issue15 category label remains `enhancement`;
- ensure the issue15 body remains decision/design-only.

### Step 5. Request Human Approval Before Publishing Issue15

Issue15 publication should require explicit approval, for example:

```text
APPROVED: publish issue 15 as ready-for-human after issue #83 evidence acceptance.
Implementation remains locked.
```

Do not publish issue15 on a generic "continue" instruction.

### Step 6. Keep Implementation Lines Separate

Continue backend implementation, contract startup fixes, PM2 verification, and
OpenAPI stabilization in separate implementation or evidence lanes.

This publication line should only coordinate:

- issue publication;
- triage state changes;
- evidence acceptance;
- issue15 readiness.

## Stop Conditions

Stop and request review if:

- issue `#83` evidence includes backend implementation changes;
- issue `#83` attempts to fix `ContractDriftIncidentListResponse`;
- issue15 is about to be published before `#83` evidence is accepted;
- current checkout needs a pull / merge / rebase while untracked publication docs
  remain;
- F runtime tasks 4.3 / 4.4 / 4.5 are marked complete without runtime evidence;
- a new issue/proposal would create implementation work outside explicit
  approval.

## Review Questions

Please review and decide:

1. Should this line commit the publication / triage documents before any git
   branch update?
2. Should issue `#80` remain open while `#83` runs, or should it be closed after
   recording that the approval gate has been satisfied?
3. Should issue15 wait for full `#83` evidence acceptance, or is a partial
   evidence acceptance enough to publish it as `ready-for-human`?
4. Should the `ContractDriftIncidentListResponse` blocker become a separate
   GitHub issue / OpenSpec proposal candidate?
