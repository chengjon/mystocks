# Review: backend-audit-P3-progress-report.md

**Type**: progress report review  
**Source**: `docs/reports/quality/backend-audit-P3-progress-report.md`  
**Date**: 2026-05-18  
**Reviewer**: Codex  
**Verdict**: useful progress summary, but not yet strong enough as closure evidence

---

## Executive Summary

The report captures the broad direction correctly: route-table metrics now show `588` total routes, `0` full-path duplicate groups, and `12` remaining orphan files; the cited commits exist; the listed OpenSpec change currently validates with `openspec validate consolidate-backend-api-domain-routers --strict`.

However, several claims need tightening before this report should be used as final P3 closeout evidence. The biggest issues are deletion accounting gaps, incomplete OpenSpec governance evidence, an inaccurate description of the `strategy_mgmt.py` compatibility behavior, and an unreproducible `54` health/status route count. These are not cosmetic: they touch the repository's cleanup/deletion standard, OpenSpec approval gate, and future migration safety.

## Evidence Checked

| Item | Result |
|------|--------|
| Source report line count | `193` lines by `wc -l`; file split count observed as `194` including trailing split |
| Current branch | `wip/root-dirty-20260403` |
| Cited commits | all present: `0fbc72ad1`, `170d8553d`, `243d40a8a`, `cc0e33719`, `ba40aa211`, `1241c4b7e` |
| Generated route-table summary | `total_routes=588`, `full_path_duplicate_groups=0`, `orphan_files=12` |
| OpenSpec validation | `consolidate-backend-api-domain-routers` is valid under `--strict` |
| OpenSpec task checklist | `0` checked, `31` unchecked |
| `get_monitoring_db.py` size | current file count observed as `1584` lines, not `1582` |
| `strategy_mgmt.py` registration | still registered in `web/backend/app/router_registry.py` before `_strategy_mgmt_compat` |

## Findings

### F1 - High - Deletion inventory is incomplete and internally inconsistent

The report says P3-B deleted `14` orphan files and lists the main deletion groups. The actual P3-B commits delete more files than the report enumerates:

| Commit | Deleted files observed |
|--------|------------------------|
| `243d40a8a` | 9 deleted files, including `announcement.py`, `backup_recovery.py`, 6 risk files, and `trading_monitor.py` |
| `cc0e33719` | 2 deleted files under `monitoring_old/` |
| `ba40aa211` | 5 deleted files, including `technical/__init__.py` and `technical/routes.py` |

The report omits at least these deletion objects:

| Omitted object | Why it matters |
|----------------|----------------|
| `web/backend/app/api/announcement.py` | deletion occurred in the same commit as the announcement dual-registration fix |
| `web/backend/app/api/backup_recovery.py` | deletion occurred in the same commit as backup route registration |
| `web/backend/app/api/technical/__init__.py` | deleted with `technical/routes.py`, but only `routes.py` is named |

P3-C1/C6 also needs sharper wording. The report says `strategy.py` was deleted, but git records it as a rename to `strategy_management/_strategy_execution_router.py`. The same commit also deletes `strategy_management/get_backtest_result.py`, which the report does not mention.

This conflicts with the cleanup/deletion standard in `architecture/STANDARDS.md`: any task report containing cleanup or deletion must state the cleanup object, functional node, status judgement, deletion evidence, and retention reason where applicable. The current report is directionally useful, but its deletion ledger is not complete enough for audit closure.

Recommended correction:

- Add a complete deletion table covering every deleted file in `243d40a8a`, `cc0e33719`, `ba40aa211`, and `1241c4b7e`.
- Separate "deleted", "renamed/moved", "registered", and "retained for compatibility" actions.
- For each deleted file, include functional node, status judgement, evidence source, and rollback/compatibility note.

### F2 - High - OpenSpec governance evidence does not prove approved implementation flow

The report lists OpenSpec deliverables under `openspec/changes/consolidate-backend-api-domain-routers/`, and the change validates successfully now. That is good, but the governance evidence is incomplete:

| Evidence | Observation |
|----------|-------------|
| `1241c4b7e` file list | adds `proposal.md`, `design.md`, `tasks.md`, specs, and implementation files in the same commit |
| `tasks.md` | `31` checklist items, all unchecked |
| OpenSpec instructions | require proposal validation and approval before implementation, then checklist update after work is complete |
| Report quality gates | do not mention `openspec validate ... --strict`, approval status, or checklist closure |

This does not prove the implementation was approved before execution. It may only be an evidence gap, but the report should not present the OpenSpec folder as closure-grade evidence unless it also records approval and checklist status.

Recommended correction:

- State whether the OpenSpec change was approved before implementation.
- Add the exact validation command and result.
- Either mark completed `tasks.md` items truthfully or state that the OpenSpec change is a follow-up governance artifact rather than the implementation control record.
- Explain why implementation and proposal artifacts appear in the same commit if that is intentional.

### F3 - Medium - `strategy_mgmt.py` compatibility behavior is described inaccurately

The deferred item says the compatibility redirect sends `307` for legacy `/api/strategy-mgmt/*` paths. Current registration order says otherwise:

| File | Evidence |
|------|----------|
| `web/backend/app/router_registry.py` | includes `strategy_mgmt.router` before `_strategy_mgmt_compat.router` |
| `web/backend/app/api/strategy_mgmt.py` | defines concrete routes under `/api/strategy-mgmt` |
| `web/backend/app/api/_strategy_mgmt_compat.py` | catch-all `/{path:path}` redirect under the same prefix |

Because the active `strategy_mgmt.router` is still registered before the catch-all, existing concrete legacy endpoints are served by `strategy_mgmt.py`, not redirected. The redirect only covers unmatched legacy paths after the active routes fail to match.

The retirement criteria also need a wider consumer matrix. A repository scan found `155` references to `/api/strategy-mgmt`, including:

| Area | Count |
|------|-------|
| `web/frontend` | 2 |
| `web/backend` | 18 |
| tests | 33 |
| docs/OpenSpec and generated API docs | 60+ |

One frontend reference in `dashboardService.ts` is a stale comment while the implementation already calls `/v1/strategy/strategies`. Another is in archived menu config. These may not block runtime migration, but they still need classification before deleting the legacy router or compatibility redirect.

Recommended correction:

- Change the wording from "compat redirect sends 307 for any legacy paths" to "compat redirect catches unmatched legacy paths while `strategy_mgmt.py` remains registered".
- Add a consumer matrix split by runtime frontend, archived frontend, backend callers, tests, generated API docs, and historical docs.
- Define explicit exit criteria for removing `strategy_mgmt.py` and `_strategy_mgmt_compat.py`.

### F4 - Medium - P3-C7 health/status count is not reproducible from the report

The report says P3-C7 has `54` health/status routes across `40+` files. I could not tie that number to a checked-in generated artifact:

| Evidence source | Observed result |
|-----------------|-----------------|
| `backend-fullpath-route-table.json` | has route totals and orphan files, but no per-route health/status inventory |
| `health-endpoint-consolidation-2026-05-14.md` | records a later decorator scan of `46` health-like routes, with caveats |
| independent local decorator scan | found `74` decorator matches containing `health` or `status` across `49` files |

These numbers can all be valid under different scopes, but the report does not define which scope `54` uses: registered full paths only, local decorators, orphan-inclusive decorators, status-only plus health-only routes, or deduplicated functional endpoints.

Recommended correction:

- Add the exact scanner command or script used to produce `54`.
- Attach a generated inventory artifact with file, line, method, local path, router prefix, full path, registration status, and orphan status.
- Explicitly state whether the count includes orphan files, generated docs, WebSocket routes, and test-only route definitions.

### F5 - Medium - Quality gate record is too coarse for commits that changed frontend behavior

The report says all commits passed 8 guardrails, but it does not include command output, per-commit evidence, or the mandatory frontend status confirmation required by the repository instructions when frontend fixes are involved.

P3-B includes frontend 404 fixes in:

- `RiskOverviewTab.vue`
- `useStopLossMonitoringTab.ts`

For this kind of change, the completion report should include at least:

| Required status | Current report status |
|-----------------|-----------------------|
| structural syntax errors | not reported |
| frontend type baseline comparison | not reported |
| PM2 backend/frontend service status and URLs | marked N/A for PM2 because no orchestration changed |
| E2E suite/project/case count/pass/fail/skip | not reported |

Recommended correction:

- Add the exact commands run for frontend lint/type/E2E or explicitly state they were not run.
- Include actual E2E project and pass/fail/skip counts if any E2E was executed.
- If PM2 was intentionally not checked, explain why that is acceptable for a report that includes frontend runtime path fixes.

### F6 - Low - Several numeric and wording details need precision cleanup

| Report claim | Review note |
|--------------|-------------|
| `get_monitoring_db.py` is `1582` lines | current observed count is `1584`; use one counting method and cite it |
| P3-B deleted `14` orphan files | commit-level deletion count is higher unless some files are intentionally excluded; define the counting rule |
| `strategy.py` deleted | git records it as a rename into `strategy_management/_strategy_execution_router.py` |
| `PM2 First-Class Gate: N/A` | acceptable only if the report is strictly backend/docs; less clear because P3-B includes frontend fixes |

## Positive Notes

- The route-table baseline in the report matches the generated artifact for `588` total routes, `0` full-path duplicate groups, and `12` orphan files.
- The remaining 12 orphan files listed in the report match the generated route-table artifact.
- The P3-C7 recommendation to use OpenSpec first is sound because health endpoint URLs can affect load balancers, monitoring dashboards, and runbooks.
- Keeping `strategy_mgmt.py` temporarily is a reasonable safety choice, but the report should describe the actual dual-registration behavior precisely.
- `openspec validate consolidate-backend-api-domain-routers --strict` passes as of this review.

## Recommended Disposition

Do not treat `backend-audit-P3-progress-report.md` as final closure evidence yet. Treat it as a progress report that needs a follow-up evidence pass.

Minimum changes before closure:

1. Add a complete deletion ledger for all deleted/renamed files.
2. Clarify OpenSpec approval, validation, and checklist status.
3. Correct the `strategy_mgmt.py` compatibility behavior and add a consumer matrix.
4. Make the P3-C7 `54` count reproducible with an attached route inventory.
5. Expand quality gate evidence for the frontend fixes and any runtime-sensitive API route changes.

## Commands / Checks Run

| Check | Result |
|-------|--------|
| `git branch --show-current` | `wip/root-dirty-20260403` |
| `wc -l` on source report | `193` |
| commit existence and subjects | all cited commits present |
| commit name-status inspection | found deletion inventory gaps listed above |
| generated route-table JSON inspection | `588` routes, `0` full-path duplicate groups, `12` orphan files |
| `openspec validate consolidate-backend-api-domain-routers --strict` | valid |
| OpenSpec `tasks.md` checkbox scan | `0/31` checked |
| legacy `/api/strategy-mgmt` reference scan | `155` total references across code, tests, docs, and OpenSpec |

