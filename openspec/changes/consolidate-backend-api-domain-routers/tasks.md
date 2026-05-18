## 1. Pre-Implementation Evidence

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **2026-05-18 跨线对齐**:
> P3 implementation 线已经完成 announcement、strategy、risk canonical router
> 决策与部分收口实现。不要重新实现这些已完成项；本 change 剩余工作是
> post-P3 route/OpenAPI reconciliation、consumer evidence、documentation
> closure、verification，以及 trading/backup follow-up proposal。

- [x] 1.1 Confirm orchestration artifact: `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md`.
- [x] 1.2 Confirm local route baseline: `docs/reports/quality/backend-route-table-openapi-baseline-2026-05-18.md`.
- [x] 1.3 Generate prefix-expanded full-path route table with `cd web/backend && python ../../scripts/dev/backend_audit_fullpath_routes.py ../../docs/reports/quality/generated`. Current post-P3-D artifact records 538 routes, 0 full-path duplicate groups, and 2 remaining orphan route files.
- [x] 1.4 Confirm full-path artifact: `docs/reports/quality/generated/backend-fullpath-route-table.md`.
- [x] 1.5 Generate current OpenAPI schema baseline with `python scripts/generate_openapi.py --output docs/reports/quality/generated/openapi-before.json`. Existing baseline is OpenAPI 3.1.0 with 501 paths.
- [x] 1.6 Build endpoint inventory for `announcement`, `strategy`, and `risk`.
- [x] 1.7 Build consumer matrix for backend imports, frontend calls, tests, scripts, and documentation references.
- [x] 1.8 Identify current shims, mock routers, and compatibility prefixes.
- [x] 1.9 Record `trading` and `backup` as deferred high-risk route ownership follow-ups, using route scan evidence.

> 2026-05-18 reconciliation evidence:
> `docs/reports/quality/backend-domain-router-reconciliation-2026-05-18.md`
> confirms the orchestration and route baseline artifacts, records runtime
> endpoint inventory, consumer matrix counts, shim/compatibility status, and
> keeps `trading` plus `backup` as separate high-risk follow-up ownership
> changes.

## 2. Domain Decisions

- [x] 2.1 Announcement decision: resolved by P3-A1; `announcement/` package canonical; implementation closure in `243d40a8a`.
- [x] 2.2 Strategy decision: resolved by P3-A2; `strategy_management/` package canonical; convergence in `1241c4b7e`.
- [x] 2.3 Risk decision: resolved by P3-A3; `risk/` package canonical; orphan cleanup in `243d40a8a`.
- [x] 2.4 Trading decision: deferred follow-up OpenSpec recorded by P3-A6; do not implement in this change.
- [x] 2.5 Backup decision: deferred follow-up OpenSpec recorded by P3-A7; do not implement in this change.
- [x] 2.6 Document endpoint parity gaps and unresolved consumers.
- [x] 2.7 Define rollback trigger per domain.

> 2026-05-18 reconciliation evidence:
> `backend-domain-router-reconciliation-2026-05-18.md` records the remaining
> `strategy-mgmt` compatibility surface, the runtime-only OpenAPI-hidden
> catch-all redirect, trading/backup deferrals, and per-domain rollback
> triggers.

## 3. Implementation Batches

- [x] 3.1 Announcement batch: already handled by P3 implementation closure in `243d40a8a`; remaining work is verification/reconciliation only.
- [x] 3.2 Strategy batch: already handled by P3-C1 convergence in `1241c4b7e`; remaining work is verification/reconciliation only.
- [x] 3.3 Risk batch: already handled by P3 safe closure in `243d40a8a`; remaining work is verification/reconciliation only.
- [x] 3.4 Keep compatibility shims unless exit criteria are explicitly met.
- [x] 3.5 Do not delete flat modules, packages, or shims in the same batch that introduces a canonical path unless rollback is proven.

> 2026-05-18 implementation boundary:
> No additional shim, flat module, package, or compatibility prefix is deleted in
> this reconciliation batch. `strategy_mgmt.py`,
> `_strategy_mgmt_compat.py`, and the split-module compatibility wrapper remain
> retained until their explicit exit criteria are met.

## 4. Verification

- [x] 4.1 Run import smoke for old and new router import paths.
- [x] 4.2 Run OpenAPI diff and attach summary to the implementation notes.
- [x] 4.3 Run targeted backend tests for announcement, strategy, and risk routes.
- [x] 4.4 Run frontend API smoke or relevant E2E subset for changed consumers.
- [x] 4.5 Confirm PM2 backend startup with `./scripts/run_pm2_integration_workflow.sh` or a named equivalent approved by the implementation issue.
- [x] 4.6 Confirm no new route exposure drift beyond approved OpenAPI diff.

> 2026-05-18 verification evidence:
> `backend-domain-router-reconciliation-2026-05-18.md` records 16/16 import
> smoke matches, OpenAPI `501 -> 500` with only the runtime-only
> `/api/strategy-mgmt/{path}` schema removal, `duplicate_operation_ids=0`, route
> governance `7 passed`, announcement route regression `1 passed`, strategy
> runtime fallback `7 passed`, and clean-HEAD risk runtime bootstrap `8 passed`.
> The current dirty worktree still has an unrelated `risk/stop_loss.py` change
> that can make risk verification fail locally; that parallel change is not
> reverted or included here.

## 5. Closure

- [x] 5.1 Update documentation with canonical router decisions and compatibility status.
- [x] 5.2 Record shim retirement candidates and exit criteria.
- [x] 5.3 Leave cleanup-only deletions for a later approved batch when consumers are clear.
- [x] 5.4 Update this checklist only after each item is actually complete.

> 2026-05-18 frontend smoke evidence:
> `npx vitest run src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts
> src/api/services/__tests__/strategyService.msw.spec.ts
> tests/unit/config/strategy-route-canonical-paths.spec.ts
> tests/unit/config/risk-route-canonical-paths.spec.ts
> src/views/risk/__tests__/Overview.spec.ts`
> passed with 5 files and 26 tests.

> 2026-05-19 PM2 named-equivalent evidence:
> `bash scripts/run_e2e_pm2.sh` started PM2 services, observed
> `mystocks-backend` and `mystocks-frontend` online during the run, and passed
> 14 Chromium navigation-consistency tests. The script intentionally deletes PM2
> processes after completion. A later manual restart attempt surfaced an
> unrelated dirty-worktree backend startup blocker in
> `web/backend/app/api/signal_monitoring/signal_history_response.py`; that
> parallel change is not included in this C-line.

> 2026-05-18 closure boundary:
> Documentation/evidence closure is updated, but the change remains unarchived
> until frontend API smoke/E2E and PM2 startup/named equivalent verification are
> executed for this C-line.
