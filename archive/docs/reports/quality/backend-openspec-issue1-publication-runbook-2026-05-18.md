# Backend OpenSpec Issue 1 Publication Runbook

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> Date: 2026-05-18
>
> Status: issue 1 publication completed from this runbook. GitHub issue #80 was
> created; no issue 14 / issue 15 publication was performed.

## Purpose

This runbook defines the exact safe steps to publish only issue 1 after human
approval. It intentionally does not publish issues, edit backend code, or unlock
implementation.

## Current Gate

Do not run any `gh issue create` command until a human explicitly approves
publishing issue 1.

Issue 1 remains the approval gate:

```text
docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/01-approve-orchestration.md
```

Approval mechanism:

- A maintainer must record the exact phrase `APPROVED: publish issue 1` in
  `docs/reports/quality/backend-openspec-human-approval-packet-2026-05-18.md`,
  in a GitHub/PR review comment that links that approval packet, or in an
  equivalent durable approval artifact.
- The command executor must be named in the approval artifact or in the
  publication follow-up note.
- If the approval wording is ambiguous, oral only, or does not identify issue 1
  specifically, stop and request clarification.

Required source documents:

```text
docs/reports/quality/backend-openspec-human-approval-packet-2026-05-18.md
docs/reports/quality/backend-openspec-g-line-integration-decision-2026-05-18.md
docs/reports/quality/backend-openspec-3issue-publication-readiness-check-2026-05-18.md
docs/reports/quality/backend-openspec-issue-publication-preflight-2026-05-18.md
docs/reports/quality/backend-openspec-issue-publication-review-response-2026-05-18.md
docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/manifest.md
```

## Candidate Command

Run only after explicit human approval:

```bash
gh issue create --repo chengjon/mystocks --title "[Backend OpenSpec] Approve orchestration and C/E/F/G proposal scope" --label ready-for-human --label enhancement --body-file docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/01-approve-orchestration.md
```

Do not run issue 14 or issue 15 publication commands in the same step.

Do not publish audit-only bodies:

```text
03-decide-announcement-router.md
04-decide-strategy-router.md
05-decide-risk-router.md
```

## Pre-Publish Checklist

Before publishing issue 1, verify:

| Check | Command | Expected result |
|---|---|---|
| GitHub auth | `gh auth status --hostname github.com` | Authenticated; if this fails, stop |
| Duplicate approval issue | `gh issue list --repo chengjon/mystocks --search "[Backend OpenSpec] Approve orchestration" --state open --limit 10` | No existing open approval issue |
| Manifest command count | `node -e "const fs=require('fs'); const m=fs.readFileSync('docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/manifest.md','utf8'); console.log((m.match(/gh issue create/g)||[]).length)"` | `3` |
| Issue 1 body file hash | `git hash-object docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/01-approve-orchestration.md` | `df8061b5ee51869f1f243f429b3cec1bfba1e856`, or stop for re-review |
| Issue 1 labels | Inspect the candidate command below | exactly one state label: `ready-for-human`; category label: `enhancement` |
| Audit-only bodies in manifest commands | `node -e "const fs=require('fs'); const m=fs.readFileSync('docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/manifest.md','utf8'); console.log([...m.matchAll(/--body-file\\s+(\\S+)/g)].map(x=>x[1]).filter(x=>/03-decide|04-decide|05-decide/.test(x)))"` | `[]` |
| Held G-line bodies in manifest commands | `node -e "const fs=require('fs'); const m=fs.readFileSync('docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/manifest.md','utf8'); console.log([...m.matchAll(/--body-file\\s+(\\S+)/g)].map(x=>x[1]).filter(x=>/08-build-health|09-decide-health/.test(x)))"` | `[]` |
| Superseded merged bodies in manifest commands | `node -e "const fs=require('fs'); const m=fs.readFileSync('docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/manifest.md','utf8'); console.log([...m.matchAll(/--body-file\\s+(\\S+)/g)].map(x=>x[1]).filter(x=>/02-refresh|06-create|07-create|10-build|11-build|12-select|13-draft/.test(x)))"` | `[]` |
| Scoped markdown governance gate | `python scripts/compliance/markdown_governance_gate.py --root-dir /opt/claude/mystocks_spec --format json docs/reports/quality/cross-line-alignment-P3-impl-openspec-response-2026-05-18.md docs/reports/quality/backend-openspec-line-summary-and-next-plan-2026-05-18.md docs/reports/quality/backend-openspec-human-approval-packet-2026-05-18.md docs/reports/quality/backend-openspec-g-line-integration-decision-2026-05-18.md docs/reports/quality/backend-openspec-issue-readiness-blueprint-compressed-2026-05-18.md docs/reports/quality/backend-openspec-issue14-triage-gate-2026-05-18.md docs/reports/quality/backend-openspec-3issue-publication-readiness-check-2026-05-18.md docs/reports/quality/backend-openspec-issue-publication-preflight-2026-05-18.md docs/reports/quality/backend-openspec-issue-publication-review-response-2026-05-18.md docs/reports/quality/backend-openspec-issue1-publication-runbook-2026-05-18.md` | 10 files, 0 errors |
| OpenSpec C validation | `openspec validate consolidate-backend-api-domain-routers --strict` | valid |
| OpenSpec G validation | `openspec validate consolidate-backend-health-endpoints --strict` | valid |
| OpenSpec E validation | `openspec validate migrate-backend-singletons-to-lifecycle-di --strict` | valid |
| OpenSpec F validation | `openspec validate split-backend-core-modules-with-compatibility-wrappers --strict` | valid |
| Existing backend OpenSpec issues | `gh issue list --repo chengjon/mystocks --search "[Backend OpenSpec] in:title" --json number,title,state --limit 100` | No unexpected existing issues |

## After Issue 1 Is Created

The named command executor records the returned issue number:

```text
ISSUE_1=80
ISSUE_1_URL=https://github.com/chengjon/mystocks/issues/80
```

Then the same executor, or a named docs follow-up owner, updates only the
dependent body placeholders that reference issue 1:

| Body | Placeholder to replace after issue 1 exists |
|---|---|
| `14-build-shared-evidence-package.md` | `BLOCKED_BY_TODO: issue 1 approval.` |
| `15-decide-post-approval-plan.md` | `BLOCKED_BY_TODO: issue 1 approval.` |

Place those placeholder edits in a normal docs commit or PR together with a
short note naming the created issue number. Do not mix backend implementation
changes into that commit or PR.

Status after publication: both issue bodies 14 and 15 have been updated to
reference GitHub issue `#80` instead of the placeholder approval text. Issue 14
and issue 15 remain unpublished.

After issue 14 is later published, replace
`BLOCKED_BY_TODO: shared evidence package.` in
`15-decide-post-approval-plan.md` with the real issue 14 number.

Do not update or publish held body files `08-build-health-status-taxonomy.md`
and `09-decide-health-status-canonical-paths.md` until a human explicitly
reclassifies them. Do not publish superseded body files 02, 06, 07, 10, 11, 12,
or 13 directly.

Do not mark any issue `ready-for-agent` just because issue 1 exists. Issue 1
approval is necessary but not sufficient for agent readiness.

## Out Of Scope

This runbook intentionally omits later placeholder maps, later publication
order, and evidence snapshots. For those, use:

```text
docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/manifest.md
docs/reports/quality/backend-openspec-issue-readiness-blueprint-compressed-2026-05-18.md
docs/reports/quality/backend-openspec-issue14-triage-gate-2026-05-18.md
docs/reports/quality/cross-line-alignment-P3-impl-openspec-response-2026-05-18.md
```

## Stop Conditions

Stop and return for human review if any of the following occurs:

- Approval is missing, ambiguous, oral-only, or does not contain the exact
  issue-1 approval phrase.
- `gh auth status --hostname github.com` fails or reports an expired token.
- `gh issue list` returns a network or authentication error.
- The issue 1 command would create a duplicate `[Backend OpenSpec]` approval
  issue.
- Required labels are missing.
- The issue 1 body hash differs from the hash listed in the pre-publish
  checklist.
- The manifest command count is no longer 3.
- Audit-only bodies 03/04/05 appear in `gh issue create` commands.
- Held bodies 08/09 or superseded bodies 02/06/07/10/11/12/13 appear in
  `gh issue create` commands.
- OpenSpec validation fails for C/G/E/F.
- Any step would require backend code mutation.
