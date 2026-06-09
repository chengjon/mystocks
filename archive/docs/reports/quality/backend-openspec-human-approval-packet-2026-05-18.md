# Backend OpenSpec Human Approval Packet

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> Historical planning artifact. This packet summarizes the current approval
> state for the backend OpenSpec drafts. It does not approve implementation.
> Before implementation, use current code, `architecture/STANDARDS.md`,
> `openspec/AGENTS.md`, current OpenSpec validation, and fresh route / OpenAPI
> evidence as the execution source of truth.

## Purpose

This packet is the human approval entry point for four backend OpenSpec changes:

| Change | Current scope | Current task count | Approval request |
|---|---|---:|---|
| `consolidate-backend-api-domain-routers` | Post-P3 route/OpenAPI reconciliation; announcement/strategy/risk already resolved by P3; trading/backup explicitly deferred | 31 | Approve remaining proposal scope and reconciliation boundary |
| `consolidate-backend-health-endpoints` | Health/status endpoint taxonomy and probe compatibility | 29 total / 27 checked | Approve proposal and taxonomy boundary |
| `migrate-backend-singletons-to-lifecycle-di` | Singleton/getter lifecycle classification and one low-risk DI pilot | 24 | Approve proposal and pilot-first constraint |
| `split-backend-core-modules-with-compatibility-wrappers` | Core import compatibility matrix and wrapper-safe split batches | 24 | Approve proposal and import-compatibility constraints |

## Current Source Documents

| Document | Role |
|---|---|
| `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md` | Cross-change execution order, dependencies, shared surfaces, allowed parallel work |
| `docs/reports/quality/backend-openspec-drafts-mattpocock-review-2026-05-18.md` | Earlier snapshot review; kept for audit history, not current approval status alone |
| `docs/reports/quality/backend-openspec-drafts-mattpocock-review-2026-05-18-review.md` | Review-of-review; useful for identifying stale blocker language |
| `docs/reports/quality/backend-openspec-drafts-mattpocock-review-2026-05-18-addendum.md` | Current stance correcting stale blocker and task-count interpretation |
| `docs/reports/quality/backend-openspec-drafts-post-mattpocock-review-2026-05-18.md` | Post-review fix summary and resolved/stale blocker disposition |
| `docs/reports/quality/cross-line-alignment-P3-impl-openspec-2026-05-18.md` | Cross-line state sync showing which issue drafts are already resolved by P3 implementation work |
| `docs/reports/quality/backend-openspec-g-line-integration-decision-2026-05-18.md` | G-line progress sync and decision not to merge G residual verification into issue 1 approval |
| `docs/reports/quality/backend-openspec-issue-readiness-blueprint-compressed-2026-05-18.md` | Current compressed 3-issue breakdown for approval, evidence, and post-approval planning |
| `docs/reports/quality/backend-openspec-issue14-triage-gate-2026-05-18.md` | Gate for moving issue 14 from `needs-triage` to `ready-for-agent` |
| `docs/reports/quality/backend-openspec-issue14-triage-dry-run-2026-05-18.md` | Dry-run issue 14 triage result; currently blocked by issue `#80` remaining open |
| `docs/reports/quality/backend-openspec-issue14-publication-runbook-2026-05-18.md` | Dry-run publication runbook for issue 14 after issue `#80` receives a durable approval decision |
| `docs/reports/quality/backend-openspec-3issue-publication-readiness-check-2026-05-18.md` | Post-review 3-issue package readiness check; records verification and remaining publication gate |
| `docs/reports/quality/backend-openspec-issue1-post-publication-status-2026-05-18.md` | Post-publication status for GitHub issue `#80`; records that issue 14/15 remain unpublished |
| `docs/reports/quality/backend-openspec-issue80-status-comment-2026-05-18.md` | Status comment body posted to GitHub issue `#80`; not an approval |
| `docs/reports/quality/backend-openspec-issue80-issue14-triage-dry-run-comment-2026-05-18.md` | Follow-up status comment body posted to GitHub issue `#80`; records issue 14 dry-run blocker |
| `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md` | Approved input baseline for issue 15 / future proposal planning; not part of the issue 1 publication gate |
| `docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/manifest.md` | Draft `gh issue create` commands and body-file publication order |
| `docs/reports/quality/backend-openspec-issue1-publication-runbook-2026-05-18.md` | Dry-run publication checklist for issue 1 only |

## Approval Decisions Required

| Decision | Required answer | Notes |
|---|---|---|
| Orchestration accepted? | Approve / revise | Must be accepted before implementation issues are marked `ready-for-agent` |
| C remaining scope accepted? | Approve / revise | Announcement/strategy/risk canonical router decisions are already resolved by P3 and should not be republished; C now covers reconciliation and deferred trading/backup follow-up scope |
| G health/status boundary accepted? | Approve / revise | G-line evidence superseded original issue drafts 08/09; remaining G work is residual verification, not taxonomy rebuild |
| E pilot-first rule accepted? | Approve / revise | First implementation batch may contain only one low-risk representative DI pilot |
| F import matrix rule accepted? | Approve / revise | Lifecycle-owned Core modules cannot move before E/F coordination |
| Follow-up proposal strategy accepted? | Approve / revise | Trading and backup should become explicit follow-up OpenSpec work before implementation |

## Not Yet Approved For Implementation

Implementation remains blocked until all of the following are true:

- Human approval accepts this approval packet or records requested revisions.
- The orchestration artifact is accepted.
- Each OpenSpec change is approved or explicitly revised.
- Implementation issues include `Blocked by` relationships to the approved
  OpenSpec changes and shared artifacts.
- C/G route-changing work uses current prefix-expanded full-path route evidence
  and OpenAPI diff evidence.
- E/F shared-Core work uses an approved import compatibility matrix and
  lifecycle-owned module list.
- Smoke, test, OpenAPI/import diff, consumer matrix, and rollback evidence are
  named on each implementation issue.

## Suggested Issue Readiness After Approval

| Issue candidate | Readiness after approval | Reason |
|---|---|---|
| Shared C/E/F evidence package | Can become ready after issue 14 triage gate | Aggregates route/OpenAPI evidence, Core import matrix, and singleton/getter lifecycle inventory; evidence-only if no code mutation |
| Issue 15 split decision | Must stay human-reviewed | Approval package accepts the aggregated issue shape, but issue 15 itself must decide whether to split before execution |
| C announcement/strategy/risk decision issues | Do not publish | Already resolved by P3-A1/A2/A3 and commits `243d40a8a` / `1241c4b7e`; retain 03/04/05 only as audit bodies |
| C announcement/strategy/risk reconciliation | Not ready until post-P3 route/OpenAPI diff and consumer evidence are attached | Do not re-implement completed P3 work |
| Post-approval plan and follow-up boundaries | Ready for human review after approval and shared evidence | Aggregates DI pilot selection, first Core split batch design, trading/backup follow-up strategy, and G residual-tail disposition |
| Codebase-map concern classification | Issue 15 input only | Approved as an input baseline; it does not authorize new implementation issues, GitHub issue creation, or OpenSpec proposal creation |
| G health/status taxonomy / canonical path drafts 08/09 | Do not publish as originally drafted | G-line evidence now covers their original taxonomy and canonical-path scope; reclassify before publication |
| G residual-tail work | Not ready until separately approved | `4.6` is OpenAPI documentation/schema stabilization; `4.7` requires PM2 workflow approval or named equivalent |
| Superseded source bodies 02/06/07/10/11/12/13 | Do not publish directly | Their scopes are merged into bodies 14 and 15 |

## Validation Snapshot

The four OpenSpec changes currently validate under strict mode:

```text
openspec validate consolidate-backend-api-domain-routers --strict
Change 'consolidate-backend-api-domain-routers' is valid

openspec validate consolidate-backend-health-endpoints --strict
Change 'consolidate-backend-health-endpoints' is valid

openspec validate migrate-backend-singletons-to-lifecycle-di --strict
Change 'migrate-backend-singletons-to-lifecycle-di' is valid

openspec validate split-backend-core-modules-with-compatibility-wrappers --strict
Change 'split-backend-core-modules-with-compatibility-wrappers' is valid
```

Scoped markdown governance gate for this approval plus issue 14 dry-run /
publication-runbook, issue 15 input, and issue 80 status-comment batch passes:
16 checked files, 0 errors.

The global markdown governance gate still exits `1` because of pre-existing
historical repository documents outside this batch.

## Recommended Approval Outcome

Recommended decision:

1. Approve the orchestration artifact for planning use.
2. Approve C/E/F/G as proposal-level governance changes, with C narrowed to
   post-P3 reconciliation and remaining deferred follow-up work.
3. Do not approve implementation yet.
4. Create only 3 publishable issues first; keep issue bodies 03/04/05
   audit-only unless a human explicitly asks for historical tracking issues,
   keep issue bodies 08/09 held until reclassified, and keep 02/06/07/10/11/12/13
   as superseded source bodies.
5. Create implementation issues only after the relevant evidence artifacts,
   consumer matrices, compatibility matrices, smoke commands, and rollback
   criteria are attached.

Use `docs/reports/quality/backend-openspec-issue-readiness-blueprint-compressed-2026-05-18.md`
as the issue publication blueprint after approval.

Use `docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/manifest.md`
as the draft GitHub issue command manifest. Do not run the commands until
approval is recorded and `BLOCKED_BY_TODO` placeholders are replaced with real
issue numbers.

Use `docs/reports/quality/backend-openspec-issue1-publication-runbook-2026-05-18.md`
for the exact no-op checklist around issue 1 publication.

Use `docs/reports/quality/backend-openspec-3issue-publication-readiness-check-2026-05-18.md`
as the latest package-readiness verification note. That document records the
reviewed 3-issue shape and verification snapshot, but it does not grant
publication authorization.

## Current Approval Record

Status: issue 1 published.

This approval authorizes publishing issue 1 only. It does not authorize
publishing issue 14, publishing issue 15, creating any additional GitHub issue,
creating any OpenSpec proposal, or starting implementation work.

| Field | Current value |
|---|---|
| Required approval phrase | `APPROVED: publish issue 1` |
| Approval phrase recorded? | yes: `APPROVED: publish issue 1` |
| Named command executor | Codex in the current execution thread |
| Approval recorder | Human maintainer in the current review thread |
| Approval timestamp | 2026-05-18 22:17:23 CST |
| Publication authorization | exercised for issue 1 only |
| Published GitHub issue | `#80` — `https://github.com/chengjon/mystocks/issues/80` |
| Publication execution result | succeeded |

The issue 1 placeholder has been replaced in issue bodies 14 and 15. Issue 14
and issue 15 remain unpublished and blocked by their own gates.
