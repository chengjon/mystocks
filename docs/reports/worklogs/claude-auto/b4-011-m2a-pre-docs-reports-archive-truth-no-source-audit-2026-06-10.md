# B4.011-M2a-pre docs/reports archive truth no-source audit

Date: 2026-06-10

## Scope

This no-source audit covers current `docs/reports/**` dirty state and archive
evidence under `archive/docs/reports/**`.

No deletion, archive staging, source, test, runtime, route, UI, `docs/guides`,
or `docs/superpowers` changes are authorized by this report.

## Current Status

Current HEAD: `ca89f8f28`

Path-scoped `docs/reports/**` status:

- Modified tracked files: 5
- Deleted tracked files: 699
- Untracked entries: 11
- Archive files under `archive/docs/reports/**`: 3795

The current evidence differs from the M1 aggregate. M1 observed 681 deleted
files with 681 exact archive matches. After later documentation archive commits,
the current tree has 699 deleted tracked files:

- 681 deleted files have exact relative archive matches.
- 18 deleted files have a same relative archive path but content hash mismatch.
- 0 deleted files are missing a relative archive path.
- 0 deleted files require hash-only matching.

Therefore M2a must split into an exact archive-retirement package and a drift
HOLD package. It must not accept all 699 deletions as a single exact batch.

## Exact Package Candidate

`B4.011-M2a-A` may accept only the 681 deleted tracked files whose relative
archive paths match by content hash.

Recommended handling:

- Stage only those 681 active deletions.
- `git add -f` only their matching `archive/docs/reports/**` copies.
- Exclude all 18 drift files.
- Exclude the 5 modified tracked files.
- Exclude the 11 untracked entries.
- Use path list files or scripted staging to avoid accidental broad `git add`.

## Drift HOLD Candidate

`B4.011-M2a-HOLD` must separately inspect the 18 same-path archive hash
mismatches:

- `docs/reports/cleanup/FILE_CLEANUP_TASK.md`
- `docs/reports/cleanup/INDEX.md`
- `docs/reports/cleanup/directory-organization/legacy/PROJECT_DIRECTORY_MANAGEMENT_PLAN.md`
- `docs/reports/cleanup/index-artifacts/INDEX_root.md`
- `docs/reports/documentation-governance/2026-04-08-decision-register.md`
- `docs/reports/documentation-governance/2026-04-09-ai-tools-family-wave1.md`
- `docs/reports/documentation-governance/2026-04-09-worklogs-source-investigation.md`
- `docs/reports/misc/PROJECT_STRUCTURE.md`
- `docs/reports/plans/code-simplification-notes.md`
- `docs/reports/plans/compatibility-inventory.md`
- `docs/reports/quality/README.md`
- `docs/reports/quality/backend-audit-2026-05-14.md`
- `docs/reports/quality/backend-residual-files-inventory-2026-05-14.md`
- `docs/reports/quality/generated/backend-fullpath-route-table.json`
- `docs/reports/quality/generated/backend-fullpath-route-table.md`
- `docs/reports/quality/health-endpoint-consolidation-2026-05-14.md`
- `docs/reports/reviews/PHASE1_GOVERNANCE_APPROVAL.md`
- `docs/reports/tasks/2026-03-27-local-dirty-worktree-batch-plan.md`

Recommended handling:

- Do not stage these deletions in M2a-A.
- Compare each active HEAD blob against the archive variant.
- Decide whether the archive variant is corrected truth, stale drift, or a
  sidecar requiring preserve/rename.

## Modified Tracked Files

The following modified tracked files are outside M2a-A deletion-retirement:

- `docs/reports/BACKTEST_API_DOCUMENTATION.md`
- `docs/reports/IMPLEMENT_WEB_FRONTEND_V2_NAVIGATION_STATUS_REPORT.md`
- `docs/reports/PHASE2_MENU_REFACTORING_COMPLETION_REPORT.md`
- `docs/reports/codebase-cleanup-2026-03-29.md`
- `docs/reports/frontend-optimization-implementation-status-2026-01-27.md`

Recommended handling: separate docs-authorized disposition package after the
deletion-retirement batches.

## Untracked Entries

The following untracked entries are outside M2a-A deletion-retirement:

- `docs/reports/ARTDECO_DOCS_CODE_ALIGNMENT_AUDIT_2026-05-28-review.md`
- `docs/reports/ARTDECO_DOCS_CODE_ALIGNMENT_AUDIT_2026-05-28.md`
- `docs/reports/DASHBOARD_CRITIQUE_AUDIT.md`
- `docs/reports/FRONTEND_DATA_SOURCE_DIAGNOSIS.md`
- `docs/reports/GPU_DOCUMENTATION_INVENTORY.md`
- `docs/reports/P3-C5-HANDOFF.md`
- `docs/reports/P3-C5-exception-consolidation-progress.md`
- `docs/reports/PRODUCT_DESIGN_AUDIT.md`
- `docs/reports/architecture/`
- `docs/reports/workspace-cleanup-plan-2026-05-14-review.md`
- `docs/reports/workspace-cleanup-plan-2026-05-14.md`

Recommended handling: separate untracked report disposition package. Do not
delete or archive as part of M2a-A.

## Largest Deleted Artifacts

Largest deleted files include generated/static report outputs such as:

- `docs/reports/code_quality/flake8_report.txt` (2330812 bytes)
- `docs/reports/screenshots/4-技术分析.png` (1196501 bytes)
- `docs/reports/code_quality/pylint_report.txt` (1057654 bytes)
- `docs/reports/screenshots/12-策略管理.png` (979615 bytes)
- `docs/reports/code_quality/pylint_report_current.txt` (930955 bytes)

These are still subject to the exact archive rule; size alone does not
authorize deletion.

## Recommendation

Proceed in this order:

1. `B4.011-M2a-A`: 681 exact `docs/reports` archive-retirement entries only.
2. `B4.011-M2a-HOLD`: 18 drift files, with per-file content comparison.
3. `B4.011-M2a-MOD`: 5 modified tracked report files.
4. `B4.011-M2a-UNTRACKED`: 11 untracked report entries.

Each package should have separate authorization, exact staging, GitNexus
staged verification, OPENDOG freshness, and post-commit GitNexus refresh.
