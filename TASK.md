# TASK

> Exported from Mongo control plane. Do not treat this file as the primary editable task source.

- Issue Identifier: `2026-04-03-root-task-artifact-mongo-cutover-main`
- Issue Title: `Cut root task artifacts over to Mongo-exported snapshots`
- Objective: `Backfill frontend mainline Phases 1-4 plus the overall closeout evidence into the Mongo control plane and replace root TASK.md/TASK-REPORT.md with exported snapshots so root artifacts stop acting as hand-maintained truth.`
- Branch: `wip/root-dirty-20260403`
- Assigned Worker CLI: `main`
- Tracker State: `verified`

## Allowed Paths
- `TASK.md`
- `TASK-REPORT.md`
- `docs/plans/2026-04-02-frontend-mainline-testing-overall-plan.md`
- `docs/plans/2026-04-02-frontend-mainline-phase-1-execution-matrix.md`
- `docs/plans/2026-04-03-frontend-mainline-phase-2-execution-matrix.md`
- `docs/plans/2026-04-03-frontend-mainline-phase-3-execution-matrix.md`
- `docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md`
- `reports/analysis/frontend-mainline-phase-1-matrix.md`
- `reports/analysis/frontend-mainline-phase-1-status.json`
- `reports/analysis/frontend-mainline-phase-2-matrix.md`
- `reports/analysis/frontend-mainline-phase-2-status.json`
- `reports/analysis/frontend-mainline-phase-3-matrix.md`
- `reports/analysis/frontend-mainline-phase-3-status.json`
- `reports/analysis/frontend-mainline-phase-4-matrix.md`
- `reports/analysis/frontend-mainline-phase-4-status.json`
- `reports/analysis/frontend-mainline-overall-closeout.md`
- `reports/analysis/frontend-mainline-overall-status.json`
- `reports/governance`

## Forbidden Paths
- (none)

## Acceptance Checks
- `python scripts/runtime/coordctl.py work export-task 2026-04-03-root-task-artifact-mongo-cutover-main --output-path TASK.md --output json`
- `python scripts/runtime/coordctl.py work export-task-report 2026-04-03-root-task-artifact-mongo-cutover-main --output-path TASK-REPORT.md --output json`
- `pytest tests/unit/runtime/test_maestro_coordination_cli.py tests/unit/runtime/test_collab_migration_scripts.py tests/unit/maestro_collab/test_mongo_store.py tests/unit/maestro_collab/test_coordination_service.py tests/unit/services/maestro/test_graphiti_preflight.py tests/unit/services/maestro/test_task_report_graphiti_projection.py -q --no-cov -o addopts=''`
- `rg -n 'Exported from Mongo control plane' TASK.md TASK-REPORT.md`
- `rg -n 'frontend-mainline-phase-4|frontend-mainline-overall' TASK.md TASK-REPORT.md`

## OpenSpec
- (none)

## Related Plans
- docs/plans/2026-04-02-frontend-mainline-testing-overall-plan.md
- docs/plans/2026-04-02-frontend-mainline-phase-1-execution-matrix.md
- docs/plans/2026-04-03-frontend-mainline-phase-2-execution-matrix.md
- docs/plans/2026-04-03-frontend-mainline-phase-3-execution-matrix.md
- docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md

## Owner Decision
- Suggested Owner: `main`
- Final Owner: `main`
- Worker CLI: `main`
- Decision Basis:
  - Root artifact cutover lives in the Maestro control-plane and export runtime owned by main.
  - Frontend mainline Phase 1-4 matrices plus the overall closeout under reports/analysis are the evidence source for the aligned snapshots.
  - Legacy root TASK.md and TASK-REPORT.md are retained only as archived pre-cutover references.

## Scope Paths
- TASK.md
- TASK-REPORT.md
- scripts/runtime/export_collab_snapshots.py
- scripts/runtime/maestro_collab.py
- src/services/maestro/collab/store/models.py
- tests/unit/runtime/test_maestro_coordination_cli.py
- tests/unit/runtime/test_collab_migration_scripts.py
- reports/analysis/frontend-mainline-overall-closeout.md
- reports/analysis/frontend-mainline-overall-status.json

## Validation Commands
- python scripts/runtime/coordctl.py work export-task 2026-04-03-root-task-artifact-mongo-cutover-main --output-path TASK.md --output json
- python scripts/runtime/coordctl.py work export-task-report 2026-04-03-root-task-artifact-mongo-cutover-main --output-path TASK-REPORT.md --output json
- pytest tests/unit/runtime/test_maestro_coordination_cli.py tests/unit/runtime/test_collab_migration_scripts.py tests/unit/maestro_collab/test_mongo_store.py tests/unit/maestro_collab/test_coordination_service.py tests/unit/services/maestro/test_graphiti_preflight.py tests/unit/services/maestro/test_task_report_graphiti_projection.py -q --no-cov -o addopts=''
- rg -n 'Exported from Mongo control plane' TASK.md TASK-REPORT.md
- rg -n 'frontend-mainline-phase-4|frontend-mainline-overall' TASK.md TASK-REPORT.md

## Next Steps
- Leave archived AUTO/MANUAL session transcripts in markdown unless a concrete consumer requires them in Mongo.
- Use the focused per-work-item snapshots under reports/governance for historical deep dives instead of rebuilding a monolithic root TASK-REPORT.md.
- Use reports/analysis/frontend-mainline-overall-closeout.md as the aggregate consumer entrypoint for the frontend mainline.

## Compatibility Notes
- Legacy manual root artifacts are archived under reports/governance/*.pre-mongo-cutover.md.
- The exporter supports richer metadata and structured update details for Mongo-backed snapshots.
- Frontend mainline Phases 1-4 plus the overall closeout are backfilled as separate Mongo work items with focused snapshots under reports/governance and reports/analysis.
- Legacy WORK blocks from the archived root TASK-REPORT are backfilled across dedicated Mongo workstreams beyond the frontend mainline slices.
- Only AUTO/MANUAL session logs remain archived-only; all archived WORK blocks now have Mongo-backed homes.

## Rollback Rule
- If a downstream consumer still depends on the legacy manual root format, restore the archived files temporarily, but keep Mongo as the active source of truth until the consumer is migrated.

## Artifact Links
- reports/governance/2026-04-03-root-TASK.pre-mongo-cutover.md
- reports/governance/2026-04-03-root-TASK-REPORT.pre-mongo-cutover.md
- reports/analysis/frontend-mainline-phase-1-matrix.md
- reports/analysis/frontend-mainline-phase-1-status.json
- reports/analysis/frontend-mainline-phase-2-matrix.md
- reports/analysis/frontend-mainline-phase-2-status.json
- reports/analysis/frontend-mainline-phase-3-matrix.md
- reports/analysis/frontend-mainline-phase-3-status.json
- reports/analysis/frontend-mainline-phase-4-matrix.md
- reports/analysis/frontend-mainline-phase-4-status.json
- reports/analysis/frontend-mainline-overall-closeout.md
- reports/analysis/frontend-mainline-overall-status.json
- reports/governance/2026-04-03-frontend-mainline-phase-1.TASK.md
- reports/governance/2026-04-03-frontend-mainline-phase-1.TASK-REPORT.md
- reports/governance/2026-04-03-frontend-mainline-phase-2.TASK.md
- reports/governance/2026-04-03-frontend-mainline-phase-2.TASK-REPORT.md
- reports/governance/2026-04-03-frontend-mainline-phase-3.TASK.md
- reports/governance/2026-04-03-frontend-mainline-phase-3.TASK-REPORT.md
- reports/governance/2026-04-03-frontend-mainline-phase-4.TASK.md
- reports/governance/2026-04-03-frontend-mainline-phase-4.TASK-REPORT.md
- reports/governance/2026-04-03-frontend-mainline-overall.TASK.md
- reports/governance/2026-04-03-frontend-mainline-overall.TASK-REPORT.md
- reports/governance/2026-03-13-artdeco-pages-mainline.TASK.md
- reports/governance/2026-03-13-artdeco-pages-mainline.TASK-REPORT.md
- reports/governance/2026-03-09-repository-hygiene-root-convergence.TASK.md
- reports/governance/2026-03-09-repository-hygiene-root-convergence.TASK-REPORT.md
- reports/governance/2026-03-09-openspec-root-cleanup.TASK.md
- reports/governance/2026-03-09-openspec-root-cleanup.TASK-REPORT.md
- reports/governance/2026-03-09-local-2-owner-suggestion.TASK.md
- reports/governance/2026-03-09-local-2-owner-suggestion.TASK-REPORT.md
- reports/governance/2026-03-05-mock-manager-fix.TASK.md
- reports/governance/2026-03-05-mock-manager-fix.TASK-REPORT.md
- reports/governance/2026-03-12-data-db-runtime-audit.TASK.md
- reports/governance/2026-03-12-data-db-runtime-audit.TASK-REPORT.md
- reports/governance/2026-03-14-active-tree-legacy-backup-cleanup.TASK.md
- reports/governance/2026-03-14-active-tree-legacy-backup-cleanup.TASK-REPORT.md
- reports/governance/2026-03-14-api-route-registration-governance.TASK.md
- reports/governance/2026-03-14-api-route-registration-governance.TASK-REPORT.md

<!-- AUTO_LAYER1_START -->
## Auto Layer 1 (Now/Next/Blocked)
- Last Sync: 2026-04-13 01:02:45
- Session: `d8317aa3-774e-4359-9342-e62b24e15d9d`
- Completion Detected: `false`
- Summary: (no assistant text)
- Changed Files (0): (none)
- Next: Review and update task ownership/DDL if needed
- Blocked: (manual fill if any)
<!-- AUTO_LAYER1_END -->
