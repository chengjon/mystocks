# Backend OpenSpec Drafts Post-Review Fix Summary

> Historical planning artifact. Use current code, `architecture/STANDARDS.md`,
> root `AGENTS.md`, OpenSpec validation results, and the latest actual route /
> OpenAPI evidence as the execution source of truth before implementation.

## Verdict

The review findings in
`docs/reports/quality/backend-openspec-drafts-mattpocock-review-2026-05-18.md`
were valid for the earlier draft snapshot. The four OpenSpec drafts were
structurally sound, but they needed approval-level orchestration and several
scope clarifications before they could support implementation planning.

Those blockers have now been addressed in documentation and OpenSpec deltas.
The result is suitable for human approval review. It still does not approve
backend code implementation.

The addendum
`docs/reports/quality/backend-openspec-drafts-mattpocock-review-2026-05-18-addendum.md`
is the current review stance: do not use the original Matt Pocock-style review
alone as the current approval status report. Treat its blockers as either
resolved/stale or approval verification checks against the current artifacts.

For approval intake, use
`docs/reports/quality/backend-openspec-human-approval-packet-2026-05-18.md`
as the one-page entry point.

## Updated Artifacts

| Artifact | Status | Purpose |
|---|---|---|
| `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md` | Added | Cross-change execution order, shared surfaces, blocking matrix, allowed parallel batches, ownership and rollback boundaries |
| `openspec/changes/consolidate-backend-api-domain-routers/` | Updated | C: API domain router governance with trading/backup explicitly deferred |
| `openspec/changes/consolidate-backend-health-endpoints/` | Updated | G: health/status taxonomy, `GET /status` included, full-path route gate added |
| `openspec/changes/migrate-backend-singletons-to-lifecycle-di/` | Updated | E: lifecycle DI now blocked by F import matrix for shared Core modules; first batch limited to one pilot |
| `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/` | Updated | F: lifecycle-owned Core modules and `app.core.logger` smoke now explicit |

## Current Task Counts

Counting current `- [ ] N.M` numbered checklist items in each `tasks.md`:

| Change | Path | Current task count |
|---|---|---:|
| C | `openspec/changes/consolidate-backend-api-domain-routers/tasks.md` | 31 |
| E | `openspec/changes/migrate-backend-singletons-to-lifecycle-di/tasks.md` | 24 |
| F | `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/tasks.md` | 24 |
| G | `openspec/changes/consolidate-backend-health-endpoints/tasks.md` | 29 |

Approval summaries should use these counts or include an explicit snapshot
timestamp and counting rule.

## Review Finding Disposition

| Review finding | Disposition | Evidence |
|---|---|---|
| Missing cross-proposal orchestration matrix | Fixed | Added `backend-openspec-change-orchestration-2026-05-18.md` with execution order, shared prerequisites, shared surfaces, blocking matrix, allowed parallel batches and not-ready gates |
| C omitted `trading` / `backup` high-risk domains | Fixed by explicit deferral | C now records `trading_runtime.py` vs `trading_monitor.py` and `backup_recovery.py` vs `backup_recovery_secure/` as high-risk deferred follow-ups, not hidden current scope |
| G did not cover `GET /status` | Fixed | G scope is now health/status endpoint taxonomy; tasks include status endpoint classification and status smoke for approved canonical paths |
| C/G did not fully absorb local decorator vs final URL distinction | Fixed | C/G now require prefix-expanded full-path route table and OpenAPI diff before runtime-conflict claims |
| E/F implementation order unclear | Fixed | Orchestration makes F import compatibility matrix and lifecycle-owned module list a blocker for E shared-Core lifecycle mutation |
| E could be interpreted as broad singleton migration | Fixed | E first implementation batch is limited to one low-risk representative pilot |
| F lacked concrete logger and PM2 smoke detail | Fixed | F tasks include `from app.core.logger import logger` import smoke and PM2 workflow command / named equivalent |
| Route/OpenAPI artifact paths were not stable enough | Fixed | C/G and orchestration name `docs/reports/quality/generated/backend-fullpath-route-table.md`, `.json`, and `openapi-before.json` |

## Current Approval Checklist

| Item | Status |
|---|---|
| Cross-change orchestration matrix exists | Done |
| C explicitly includes or defers trading / backup | Done; deferred as follow-up route ownership proposals |
| G explicitly includes `GET /status` taxonomy | Done |
| C/G require prefix-expanded final route table, not only local decorator duplicates | Done |
| E depends on F import compatibility matrix for shared Core modules | Done |
| F identifies lifecycle-owned modules that must coordinate with E | Done |
| Each `tasks.md` includes concrete verification commands or named scripts | Done |
| Route/OpenAPI artifact paths are named and stable | Done |
| Follow-up issues remain blocked until OpenSpec approval and `Blocked by` chain are resolved | Done in orchestration matrix |

## Revised Approval Position

The correct current position is no longer "implementation remains blocked
because sections are absent."

The current position is:

1. The four OpenSpec drafts now address the main structural gaps from the
   earlier review.
2. The original review's blockers should be downgraded to resolved/stale items
   or converted into approval verification checks.
3. Implementation should still wait until reviewers confirm artifact
   completeness: orchestration, route baseline, OpenAPI diff, consumer matrix,
   import compatibility matrix, lifecycle ownership matrix, smoke validation,
   and rollback criteria.
4. Approval should focus on whether the referenced artifacts contain enough
   operational detail to guide staged implementation, not on whether those
   sections exist at all.

## Validation Evidence

Strict OpenSpec validation passed for all four changes:

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

Markdown governance gate still exits `1` for unrelated historical repository
documents, but the changed files in this batch have no governance hits.

## Implementation Boundary

These documents can now move into human approval review.

Implementation remains blocked until:

- The orchestration artifact is accepted.
- The four OpenSpec changes are approved.
- Implementation issues are split with explicit `Blocked by` chains.
- C/G route-changing work uses current prefix-expanded full-path route and
  OpenAPI evidence.
- E/F shared-Core work uses the approved import compatibility and lifecycle
  ownership matrix.

No backend implementation files were changed by this review-fix pass.
