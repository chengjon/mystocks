# B4.011-M2a-HOLD docs/reports archive drift no-source review

Date: 2026-06-10
Node: `b4-docs-reports-archive-retirement`
Mode: no-source review
Head: `61559d666b10`

## Scope

This review covers the `18` remaining deleted tracked `docs/reports/**` entries after `B4.011-M2a-A`.

No source, test, runtime, frontend, OpenSpec, archive, or report file was modified by this review. No deletion was staged.

## Current status

- `docs/reports/**` modified tracked: `5`
- `docs/reports/**` deleted tracked: `18`
- `docs/reports/**` untracked: `11`
- Unexpected deleted tracked paths outside the 18 HOLD list: `0`
- Archive path exists for all 18 HOLD entries: `18/18`
- Archive blob matches active `HEAD` blob: `0/18`

## Drift classification

### Low-delta metadata or index drift

These files differ by a small localized delta and are candidates for archive overwrite plus active retirement after explicit deletion-retirement authorization:

- `docs/reports/cleanup/FILE_CLEANUP_TASK.md`
- `docs/reports/cleanup/INDEX.md`
- `docs/reports/cleanup/directory-organization/legacy/PROJECT_DIRECTORY_MANAGEMENT_PLAN.md`
- `docs/reports/cleanup/index-artifacts/INDEX_root.md`
- `docs/reports/documentation-governance/2026-04-08-decision-register.md`
- `docs/reports/documentation-governance/2026-04-09-worklogs-source-investigation.md`
- `docs/reports/plans/compatibility-inventory.md`
- `docs/reports/reviews/PHASE1_GOVERNANCE_APPROVAL.md`

### Medium/high-delta archive drift

These files have larger content drift and should not be blindly overwritten without an explicit preserve-vs-overwrite decision:

- `docs/reports/documentation-governance/2026-04-09-ai-tools-family-wave1.md`
- `docs/reports/misc/PROJECT_STRUCTURE.md`
- `docs/reports/plans/code-simplification-notes.md`
- `docs/reports/quality/README.md`
- `docs/reports/quality/backend-audit-2026-05-14.md`
- `docs/reports/quality/backend-residual-files-inventory-2026-05-14.md`
- `docs/reports/quality/generated/backend-fullpath-route-table.json`
- `docs/reports/quality/generated/backend-fullpath-route-table.md`
- `docs/reports/quality/health-endpoint-consolidation-2026-05-14.md`
- `docs/reports/tasks/2026-03-27-local-dirty-worktree-batch-plan.md`

## Recommendation

Split the HOLD bucket into two implementation packages:

1. `B4.011-M2a-HOLD-A`: low-delta archive overwrite plus active retirement.
2. `B4.011-M2a-HOLD-B`: medium/high-delta drift decision package. For each file, choose one of:
   - preserve active variant into archive, then retire active path;
   - preserve archive variant and restore active path for later MOD review;
   - keep as HOLD with a file-specific reason.

Both packages require explicit deletion-retirement authorization before staging.

## Exclusions

Still excluded from this review:

- `B4.011-M2a-MOD`: 5 modified tracked `docs/reports/**` files.
- `B4.011-M2a-UNTRACKED`: 11 untracked `docs/reports/**` entries.
- `docs/guides/**`, `docs/superpowers/**`, source, tests, scripts, web, OpenSpec, ST-HOLD, `marketKlineData`, and all external dirty files.
