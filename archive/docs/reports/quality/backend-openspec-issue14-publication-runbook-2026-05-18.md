# Backend OpenSpec Issue 14 Publication Runbook

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> Dry-run publication runbook only. This document does not publish issue 14,
> move issue 14 to `ready-for-agent`, create additional GitHub issues, create
> OpenSpec proposals, or authorize backend implementation.

## Current Gate

Issue 14 is not authorized for publication while GitHub issue `#80` is still
`OPEN` without a human reviewer approval / close decision.

Current state:

```text
ISSUE_1=80
ISSUE_1_URL=https://github.com/chengjon/mystocks/issues/80
ISSUE_1_STATE=OPEN
ISSUE_1_COMMENTS=2
```

## Publication Semantics

Publishing issue 14 and moving issue 14 to `ready-for-agent` are separate
actions:

- Issue 14 publication uses the manifest's initial `needs-triage` state label.
- Issue 14 must not move to `ready-for-agent` until after publication and a
  passing decision under
  `docs/reports/quality/backend-openspec-issue14-triage-gate-2026-05-18.md`.
- This runbook prepares the publication step only.

## Candidate Command

Run only after issue `#80` has a durable human approval / close decision:

```bash
gh issue create --repo chengjon/mystocks --title "[Backend OpenSpec] Build shared C/E/F evidence package" --label needs-triage --label enhancement --body-file docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/14-build-shared-evidence-package.md
```

Do not run the issue 15 publication command in the same step.

## Pre-Publish Checklist

Before publishing issue 14, verify:

| Check | Command | Expected result |
|---|---|---|
| Issue 1 approval decision | `gh issue view 80 --repo chengjon/mystocks --json number,state,comments,labels,url` | Human approval / close decision exists; implementation remains locked |
| Duplicate issue 14 | `gh issue list --repo chengjon/mystocks --search "[Backend OpenSpec] Build shared C/E/F evidence package" --state open --limit 10` | No existing open issue 14 equivalent |
| Manifest command count | `node -e "const fs=require('fs'); const m=fs.readFileSync('docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/manifest.md','utf8'); console.log((m.match(/gh issue create/g)||[]).length)"` | `3` |
| Issue 14 body file hash | `git hash-object docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/14-build-shared-evidence-package.md` | `6397dff35b8a44a5987d9f5da420dd3347a73d1a`, or stop for re-review |
| Issue 14 labels | Inspect candidate command | exactly one state label: `needs-triage`; category label: `enhancement` |
| Issue 14 issue-1 placeholder | `rg "BLOCKED_BY_TODO: issue 1 approval" docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/14-build-shared-evidence-package.md` | no match |
| Issue 14 references issue 1 | `rg "github.com/chengjon/mystocks/issues/80|GitHub issue #80" docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/14-build-shared-evidence-package.md` | match |
| Issue 14 remains evidence-only | Inspect the body | route/OpenAPI evidence, Core import matrix, and singleton/getter inventory only |
| No backend mutation | Inspect the body | no route mutation, Core movement, DI lifecycle mutation, endpoint retirement, or PM2 execution |
| Issue 15 remains blocked | `rg "BLOCKED_BY_TODO: shared evidence package" docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/15-decide-post-approval-plan.md` | match |
| Issue 1 publication package markdown gate | Run the issue 1 package scoped markdown gate from `backend-openspec-issue1-publication-runbook-2026-05-18.md` | 10 files, 0 errors |
| Approval / issue 14 dry-run / issue 15 input markdown gate | Run the scoped markdown gate including this runbook | 16 files, 0 errors |
| OpenSpec C validation | `openspec validate consolidate-backend-api-domain-routers --strict` | valid |
| OpenSpec E validation | `openspec validate migrate-backend-singletons-to-lifecycle-di --strict` | valid |
| OpenSpec F validation | `openspec validate split-backend-core-modules-with-compatibility-wrappers --strict` | valid |

## After Issue 14 Is Created

Record the returned issue number:

```text
ISSUE_14=<real issue number>
ISSUE_14_URL=<real issue URL>
```

Then update only this placeholder in issue 15:

```text
BLOCKED_BY_TODO: shared evidence package.
```

Do not publish issue 15 until issue 14 exists and issue 15 has been updated with
the real issue 14 number.

Do not move issue 14 to `ready-for-agent` until the published issue passes
`docs/reports/quality/backend-openspec-issue14-triage-gate-2026-05-18.md`.

## Stop Conditions

Stop before publication if any of the following is true:

- Issue `#80` is still open without explicit approval.
- Issue `#80` requests revisions or rejects the scope.
- Issue 14 body hash differs from the hash above.
- Issue 14 no longer remains evidence-only.
- Issue 14 would require backend mutation, PM2 execution, route mutation, Core
  movement, or DI lifecycle mutation.
- Duplicate issue 14 already exists.
- Any scoped markdown or OpenSpec validation fails.
