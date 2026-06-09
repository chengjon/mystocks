# Backend OpenSpec 3-Issue Publication Readiness Check

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> Historical planning artifact. This check records the reviewed 3-issue
> publication package state for the backend OpenSpec drafts. It is not a
> GitHub issue publication approval, and it does not authorize implementation.

## Scope

This document records the post-review readiness state for the compressed
backend OpenSpec publication package:

- Publish issue 1 first as the human approval gate.
- Publish issue 14 only after issue 1 approval, placeholder replacement, and
  issue 14 triage confirmation.
- Publish issue 15 only after issue 14 exists, with issue 15 remaining a
  human-reviewed planning / decision issue.
- Keep audit-only, held, and superseded source bodies unpublished.

No backend code change is part of this check.

## Current Package Shape

| Category | Current count | Files / notes |
|---|---:|---|
| Retained body files | 15 | `01` through `15`, including merged and held source bodies |
| Publishable commands | 3 | `01-approve-orchestration.md`, `14-build-shared-evidence-package.md`, `15-decide-post-approval-plan.md` |
| Audit-only / do-not-publish | 3 | `03`, `04`, `05` |
| Publication hold / reclassification | 2 | `08`, `09` |
| Superseded / merged source bodies | 7 | `02`, `06`, `07`, `10`, `11`, `12`, `13` |

The manifest command order is:

```text
1 -> 14 -> 15
```

The dependency order is:

```text
issue 1 approval gate -> issue 14 shared C/E/F evidence package -> issue 15 post-approval plan and follow-up boundaries
```

## Review Disposition

The package structure is accepted for the approval path:

- The 3-issue compression is the current publication shape.
- Issue 1 remains the approval gate.
- Issue 14 is the only AFK-after-approval candidate, and only after its
  triage gate confirms the body is still evidence-only.
- Issue 15 stays `ready-for-human` because it combines DI pilot selection,
  Core split planning, trading/backup follow-up proposal strategy, and G-line
  residual-tail disposition.
- Original issue bodies `08` and `09` remain on publication hold until G
  residual-tail reclassification is complete.

This review disposition does not replace the explicit publication authorization
record. The current approval packet still requires the exact phrase
`APPROVED: publish issue 1` and a named command executor before any
`gh issue create` command can run.

## Verification Snapshot

The following checks were re-run on 2026-05-18 from
`/opt/claude/mystocks_spec`.

| Check | Result |
|---|---|
| Manifest publishable command count | pass: 3 |
| Manifest publishable body files | pass: `01`, `14`, `15` only |
| Forbidden bodies in manifest commands | pass: none |
| Issue 14 triage-gate reference | pass |
| Issue 15 split-decision point | pass |
| Issue 1 body hash with `git hash-object` | `df8061b5ee51869f1f243f429b3cec1bfba1e856` |
| Runbook hash expectation | pass: matches current issue 1 body |
| Issue 1 publication package scoped markdown governance gate | pass: 10 files, 0 errors |
| Pre-publication duplicate search for `[Backend OpenSpec] in:title` | pass before publication: 0 issues returned; issue `#80` was created later by the approved runbook |
| `openspec validate consolidate-backend-api-domain-routers --strict` | pass |
| `openspec validate consolidate-backend-health-endpoints --strict` | pass |
| `openspec validate migrate-backend-singletons-to-lifecycle-di --strict` | pass |
| `openspec validate split-backend-core-modules-with-compatibility-wrappers --strict` | pass |

## Publication Gate

Current status: issue 1 published as GitHub issue #80.

Later alignment note: `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md`
has been approved only as an issue 15 / future proposal input baseline. It is
not part of the issue 1 publication package gate and does not authorize
publication or implementation.

The approval packet records:

- Approval phrase recorded? yes: `APPROVED: publish issue 1`
- Named command executor: Codex in the current execution thread
- Publication authorization: exercised for issue 1 only
- Published issue: `https://github.com/chengjon/mystocks/issues/80`

No further `gh issue create` command is authorized by this check.

## Next Step

Issue 1 has been published as GitHub issue `#80`. Keep issue 14 and issue 15
blocked until their own gates pass. If the placeholder updates are not yet
applied in your local branch, replace the issue 14 and issue 15
`BLOCKED_BY_TODO: issue 1 approval.` placeholders with the real issue 1 number
before considering any later publication.
