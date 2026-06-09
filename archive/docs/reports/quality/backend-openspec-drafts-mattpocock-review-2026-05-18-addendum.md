# Backend OpenSpec Drafts Matt Pocock Review Addendum

Date: 2026-05-18
Reviewer: Codex
Scope:
- `docs/reports/quality/backend-openspec-drafts-mattpocock-review-2026-05-18.md`
- `docs/reports/quality/backend-openspec-drafts-mattpocock-review-2026-05-18-review.md`
- Current OpenSpec drafts under `openspec/changes/`

## Conclusion

`backend-openspec-drafts-mattpocock-review-2026-05-18-review.md` is directionally correct.

The original Matt Pocock-style review should now be treated as a review of an earlier draft snapshot, not as the current approval blocker for the four OpenSpec changes. Several blockers in the original report describe issues that have since been addressed in the current draft files.

The original report should therefore be revised or superseded with this addendum before being used for approval decisions.

## Current-State Assessment

The current drafts now contain evidence for several items that the original review marked as missing:

| Original concern | Current status | Assessment |
|---|---|---|
| Missing cross-change orchestration artifact | `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md` exists and is referenced by all four draft task lists | Original blocker is stale; revise to an approval check for orchestration completeness |
| C does not address `trading` / `backup` route duplication | C now records `trading` and `backup` as high-risk route ownership follow-ups and explicitly defers implementation from this bounded change | Original blocker is stale; keep as follow-up visibility requirement |
| G does not address `GET /status` duplication | G now includes health/status taxonomy and status endpoint classification work | Original blocker is stale |
| C/G do not distinguish local decorator duplicates from final full-path runtime conflicts | Current C/G drafts require prefix-expanded full-path route table and OpenAPI diff evidence | Original blocker is stale; keep artifact review as a gate |
| E/F do not coordinate singleton lifecycle DI with Core module splitting | E references F's import compatibility and lifecycle-owned module work; F marks lifecycle-owned Core modules as requiring E coordination | Original blocker is stale; keep dependency sequencing as an implementation gate |

## Corrected Task Counts

The review-of-review correctly identifies that the original report's task counts are outdated, but its own E/G counts appear to be swapped or based on a different counting pass.

Using the current `- [ ] N.M` numbered checkbox tasks in each `tasks.md`, the counts are:

| Change | Path | Current task count |
|---|---|---:|
| C | `openspec/changes/consolidate-backend-api-domain-routers/tasks.md` | 31 |
| E | `openspec/changes/migrate-backend-singletons-to-lifecycle-di/tasks.md` | 24 |
| F | `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/tasks.md` | 24 |
| G | `openspec/changes/consolidate-backend-health-endpoints/tasks.md` | 29 |

Any future approval summary should use these current counts or include an explicit snapshot timestamp and counting rule.

## Revised Approval Position

The correct current position is not "implementation remains blocked because these sections are absent."

The more accurate position is:

1. The four OpenSpec drafts are materially improved and now address the main structural gaps called out in the earlier review.
2. The original review's blockers should be downgraded to either resolved/stale or converted into approval verification checks.
3. Implementation should still wait until the evidence artifacts are reviewed, especially the cross-change orchestration document, route baseline, OpenAPI diff, consumer matrix, compatibility matrices, and rollback criteria.
4. Approval should be conditional on confirming that these artifacts are not merely referenced, but contain enough operational detail to guide safe staged implementation.

## Remaining Approval Gates

Before approving implementation, reviewers should still confirm:

- The orchestration artifact defines execution order, dependency boundaries, rollback order, and ownership for C/E/F/G together.
- Route work uses prefix-expanded full-path evidence, not only local decorator strings.
- `trading` and `backup` duplicates remain visible as explicitly deferred follow-up work, with no accidental deletion or implicit migration in C/G.
- Health/status canonicalization preserves existing consumers or documents compatibility shims and deprecation timing.
- E/F sequencing prevents lifecycle-owned Core modules from being moved before DI ownership and teardown rules are clear.
- Each change has a consumer matrix, OpenAPI or import compatibility diff where applicable, smoke validation, and rollback criteria.

## Recommendation

Keep the original review for audit history, but do not use it alone as the current status report.

Use this addendum as the current review stance:

- The review-of-review is mostly valid.
- The original review is stale against the current draft files.
- The only correction to the review-of-review is the current task count table: C=31, E=24, F=24, G=29.
- The approval decision should now focus on artifact completeness and execution sequencing, not on the previously missing sections.
