# Cross-Line Alignment Response: P3 Implementation And OpenSpec Governance

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> Date: 2026-05-18
>
> Input reviewed:
> `docs/reports/quality/cross-line-alignment-P3-impl-openspec-2026-05-18.md`
>
> This document records the governance-line updates made after learning that the
> P3 implementation line had already completed part of the backend route
> consolidation work. It does not approve backend implementation and does not
> publish GitHub Issues.

## Decision

Accepted the cross-line alignment finding.

The original GitHub issue draft package retained 13 body files. After P3 and
G-line implementation alignment, and after human agreement to compress the
package, the current directory retains 15 body files but only 3 are publishable.
Drafts 03, 04, and 05 are audit-only because the P3 implementation line already
resolved the C announcement, strategy, and risk canonical-router decisions.
Drafts 08 and 09 are publication-hold because G-line evidence superseded their
original health/status taxonomy and canonical-path scopes. Drafts
02/06/07/10/11/12/13 are superseded source bodies merged into 14/15.

## Updated Artifacts

### Issue publication package

Updated:

```text
docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/manifest.md
```

New publication posture:

| Metric | Current value |
|---|---:|
| Retained body files | 15 |
| Publishable `gh issue create` commands | 3 |
| Audit-only / do-not-publish bodies | 3 |
| Publication-hold / reclassification bodies | 2 |
| Superseded / merged bodies | 7 |
| Existing GitHub Issues created by this line | 0 |

Manifest command order is the authoritative safe publication order:

```text
1 -> 14 -> 15
```

The manifest keeps superseded source body mapping for audit, but the three
commands above are the only publishable sequence.

```text
Compressed publication: 1 -> 14 -> 15
Held G residual-tail work: reclassify 08/09 before any publication.
```

Audit-only bodies:

| Body | Status | Evidence |
|---|---|---|
| `03-decide-announcement-router.md` | Do not publish | P3-A1; `announcement/` package canonical; `announcement.py` deleted in `243d40a8a` |
| `04-decide-strategy-router.md` | Do not publish | P3-A2; `strategy_management/` package canonical; convergence in `1241c4b7e` |
| `05-decide-risk-router.md` | Do not publish | P3-A3; `risk/` package canonical; orphan cleanup in `243d40a8a` |

### Issue body changes

Updated publishable bodies:

| Body | Change |
|---|---|
| `01-approve-orchestration.md` | Re-scoped approval to acknowledge P3-resolved C work and focus on remaining C reconciliation, E/F/G scope, and trading/backup follow-ups. |
| `02-refresh-route-openapi-evidence.md` | Added current evidence: post-P3-D route table has 538 routes, 0 full-path duplicate groups, and 2 remaining orphan route files; OpenAPI baseline is 3.1.0 with 501 paths. Remaining work is post-P3 regeneration/reconciliation and diffing. |
| `08-build-health-status-taxonomy.md` | Added requirement to reuse or supersede P3-A5 taxonomy and 52-route inventory; no duplicate health proposal. |
| `11-build-singleton-lifecycle-inventory.md` | Added requirement to reuse or supersede P3-A4 singleton lifecycle inventory and produce DI-specific classification. |

Updated audit-only bodies:

```text
03-decide-announcement-router.md
04-decide-strategy-router.md
05-decide-risk-router.md
```

Each now starts with an explicit already-resolved / do-not-publish note and no
longer carries live `BLOCKED_BY_TODO` dependencies.

### Governance summary documents

Updated:

```text
docs/reports/quality/backend-openspec-human-approval-packet-2026-05-18.md
docs/reports/quality/backend-openspec-issue-readiness-blueprint-compressed-2026-05-18.md
docs/reports/quality/backend-openspec-issue-publication-preflight-2026-05-18.md
docs/reports/quality/backend-openspec-issue-publication-review-response-2026-05-18.md
docs/reports/quality/backend-openspec-line-summary-and-next-plan-2026-05-18.md
docs/reports/quality/backend-openspec-issue1-publication-runbook-2026-05-18.md
docs/reports/quality/backend-openspec-g-line-integration-decision-2026-05-18.md
```

Main changes:

- Approval scope now says C announcement/strategy/risk are already resolved by
  P3 and must not be republished as new HITL decisions.
- Readiness blueprint now distinguishes 15 retained body files from 3
  publishable issue commands, 3 audit-only bodies, 2 held G-line bodies, and 7
  superseded source bodies.
- Preflight now checks 3 publishable commands, 3 audit-only bodies, 2 held
  G-line bodies, and 7 superseded source bodies.
- The line summary now records the P3 alignment and updates the next plan.
- The G-line integration decision records that health/status progress is absorbed
  as a factual update, not merged into the issue 1 approval gate.

### OpenSpec task checklists

Updated:

```text
openspec/changes/consolidate-backend-api-domain-routers/tasks.md
openspec/changes/consolidate-backend-health-endpoints/tasks.md
openspec/changes/migrate-backend-singletons-to-lifecycle-di/tasks.md
```

Key task status changes:

- C marks P3-resolved announcement, strategy, and risk decisions as complete
  with commit evidence.
- C marks the already-handled P3 implementation closure batches as complete and
  explicitly scopes remaining work to verification/reconciliation.
- G marks shared route/OpenAPI evidence as available and P3-A5 taxonomy as the
  current input to reuse or supersede.
- E marks the P3-A4 singleton lifecycle inventory as the existing input to reuse
  or supersede.

## Verification

Manifest alignment check:

```json
{
  "commandCount": 10,
  "bodyRefCount": 10,
  "retainedBodyCount": 13,
  "blockedRefs": [],
  "missing": [],
  "auditMarkers": [
    "03-decide-announcement-router.md: marked",
    "04-decide-strategy-router.md: marked",
    "05-decide-risk-router.md: marked"
  ]
}
```

OpenSpec validation:

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

Validation emitted a non-blocking PostHog telemetry flush network warning after
successful validation. The OpenSpec validation result itself was valid for all
four changes.

GitHub issue state:

```json
{
  "backendOpenSpecIssueCount": 0,
  "titles": []
}
```

No `gh issue create` command was executed.

Markdown governance gate for the seven changed summary/publication documents:

```text
checked_files: 7
errors: 0
exit code: 0
```

## Review Feedback Follow-Up

Applied follow-up fixes after human review:

| Finding | Fix |
|---|---|
| Function tree path was ambiguous/nonexistent at repo root | Updated relevant reports and issue bodies to use `docs/FUNCTION_TREE.md`. Verified `docs/FUNCTION_TREE.md` exists and there is no root-level function tree file. |
| Publication order could be read two ways | Declared manifest command order as the authoritative safe publication order. Track A/B is now documented as dependency analysis and parallel preparation only. |
| Markdown gate status mixed scoped and global results | Updated summary wording to separate issue 1 publication package scoped gate (`10 files, 0 errors`) from global historical repository debt; later codebase-map input alignment plus issue 14 dry-run / publication-runbook / post-publication status / issue 80 status comments adds a separate approval + issue 15 input scoped gate (`16 files, 0 errors`). |

Follow-up verification:

```json
{
  "bareFunctionTree": [],
  "manifestCommandCount": 10,
  "manifestBodyRefCount": 10,
  "blockedRefs": [],
  "scopedMarkdownGate": {
    "exitCode": 0,
    "checked_files": 7,
    "errors": 0
  }
}
```

## P3-D Metric Refresh

Applied the non-blocking metric refresh noted by review.

The previous approval materials referenced an earlier route-table snapshot
whose total route count was 588. After P3-D deleted true orphan API files and
the route scanner was fixed to trace `include_router` chains, the regenerated
artifact is:

```json
{
  "git_head": "4327ddf22 fix(audit): trace include_router chains in route scanner, regenerate baseline",
  "total_routes": 538,
  "registered_routes": 522,
  "orphan_routes": 16,
  "unique_files": 94,
  "full_path_duplicate_groups": 0,
  "orphan_files": [
    "app/api/algorithms/_naive_bayes_router.py",
    "app/api/algorithms/get_algorithms_module.py"
  ]
}
```

OpenSpec C currently has 11 of 31 checklist items marked complete. That is a
governance checklist alignment state, not evidence that this governance line
performed backend implementation.

## Issue 1 Runbook Review Follow-Up

Applied feedback from:

```text
docs/reports/quality/backend-openspec-issue1-publication-runbook-mattpocock-review-2026-05-18.md
```

Runbook changes:

| Review finding | Fix |
|---|---|
| Approval mechanism was undefined | Added exact approval phrase, durable approval artifact requirement, and named executor requirement. |
| Pre-publish facts lacked executable commands | Added concrete commands for `gh auth status`, duplicate issue search, manifest count, issue 1 body hash, audit-only command scan, markdown governance, and OpenSpec validation. |
| Missing publication reference docs | Added approval packet, preflight, publication review response, and manifest as required source documents. |
| Authentication/network failure stop condition missing | Added `gh auth status` and `gh issue list` failure stop conditions. |
| Post-issue edit flow lacked owner/commit guidance | Added executor/follow-up owner wording and docs-only commit/PR guidance. |
| Runbook mixed issue 1 with later publication layers | Removed later placeholder map, full publication order, and evidence snapshot from the runbook; replaced them with references to manifest, readiness blueprint, and this response. |

## G-Line Implementation Progress Follow-Up

Applied the latest G-line status from the health/status implementation line:

```text
docs/reports/quality/backend-health-status-implementation-boundary-2026-05-18.md
docs/reports/quality/backend-health-status-residual-blockers-2026-05-18.md
docs/reports/quality/backend-openspec-g-line-integration-decision-2026-05-18.md
```

Decision:

- Do not merge G-line execution into this issue publication / approval line.
- Absorb the G-line status as a factual update: `27 done / 2 open`.
- Keep issue 1 as the approval gate.
- Keep issue 1 first; update later manifest publication to hold original 08/09
  drafts pending reclassification.
- Do not treat `eecfd5796 refactor(strategy): split get_monitoring_db.py into sub-modules`
  as G-line closure evidence.

Residual G-line boundaries:

| Item | Status | Boundary |
|---|---|---|
| `3.1-3.4` | Closed | Verified no-op implementation; no unapproved alias, no readiness compatibility removal, no endpoint retirement. |
| `4.6` | Open | Cross-domain OpenAPI documentation/schema debt; should be handled as a separate OpenAPI documentation stabilization batch. |
| `4.7` | Open | Full PM2 integration workflow is stateful and needs explicit approval, or an approved no-stop/delete named equivalent. |

## Remaining Work Plan

### P0. Human review

Please review this response together with:

```text
docs/reports/quality/backend-openspec-line-summary-and-next-plan-2026-05-18.md
docs/reports/quality/backend-openspec-human-approval-packet-2026-05-18.md
docs/reports/quality/github-issue-drafts/backend-openspec-2026-05-18/manifest.md
```

Decision needed:

1. Accept or revise the compressed 3-issue publication package.
2. Confirm that bodies 03, 04, and 05 should remain audit-only, 08/09 should
   remain held, and 02/06/07/10/11/12/13 should remain superseded source bodies.
3. Decide whether issue 1 may be published.

### P1. If issue publication is approved

Publish only issue 1 first:

```text
01-approve-orchestration.md
```

Use the dry-run checklist:

```text
docs/reports/quality/backend-openspec-issue1-publication-runbook-2026-05-18.md
```

Then replace `BLOCKED_BY_TODO: issue 1` placeholders in remaining publishable
bodies 14 and 15 with the real issue number.

Do not publish bodies 03, 04, 05, 08, 09, or superseded bodies
02/06/07/10/11/12/13.

### P2. After approval issue is accepted

Proceed with compressed evidence/design issues before implementation:

1. Issue 14: build the shared C/E/F evidence package.
2. Issue 15: decide post-approval implementation plan and follow-up boundaries.

### P3. Remaining HITL decisions

Inside issue 15, after evidence is attached:

1. Select the first low-risk DI pilot.
2. Decide trading and backup route ownership follow-up OpenSpec strategy.
3. Decide whether held G-line drafts 08/09 should be replaced by new
   residual-tail issues for OpenAPI documentation stabilization and PM2
   workflow approval.

### P4. Still blocked

Do not start these without explicit approval and issue-level evidence:

- Backend implementation in this governance line.
- New publication of issues 03, 04, or 05.
- New publication of issues 08 or 09 without reclassification.
- Folding G-line residual verification or strategy refactor into issue 1.
- Running stateful PM2 integration workflow without explicit approval.
- Route deletion or router registry mutation.
- Core file movement.
- DI migration.
- OpenSpec archive.
