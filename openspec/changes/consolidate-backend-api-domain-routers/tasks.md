## 1. Pre-Implementation Evidence

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [ ] 1.1 Confirm orchestration artifact: `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md`.
- [ ] 1.2 Confirm local route baseline: `docs/reports/quality/backend-route-table-openapi-baseline-2026-05-18.md`.
- [ ] 1.3 Generate prefix-expanded full-path route table with `cd web/backend && python ../../scripts/dev/backend_audit_fullpath_routes.py ../../docs/reports/quality/generated`.
- [ ] 1.4 Confirm full-path artifact: `docs/reports/quality/generated/backend-fullpath-route-table.md`.
- [ ] 1.5 Generate current OpenAPI schema baseline with `python scripts/generate_openapi.py --output docs/reports/quality/generated/openapi-before.json`.
- [ ] 1.6 Build endpoint inventory for `announcement`, `strategy`, and `risk`.
- [ ] 1.7 Build consumer matrix for backend imports, frontend calls, tests, scripts, and documentation references.
- [ ] 1.8 Identify current shims, mock routers, and compatibility prefixes.
- [ ] 1.9 Record `trading` and `backup` as deferred high-risk route ownership follow-ups, using route scan evidence.

## 2. Domain Decisions

- [ ] 2.1 Announcement decision: blocked by 1.2, 1.3, 1.5, endpoint parity, and consumer matrix.
- [ ] 2.2 Strategy decision: blocked by 1.2, 1.3, 1.5, frontend/test consumer matrix, and mock router classification.
- [ ] 2.3 Risk decision: blocked by 1.2, 1.3, 1.5, risk v31 compatibility matrix, and service consumer evidence.
- [ ] 2.4 Trading decision: mark as deferred follow-up OpenSpec; do not implement in this change.
- [ ] 2.5 Backup decision: mark as deferred follow-up OpenSpec; do not implement in this change.
- [ ] 2.6 Document endpoint parity gaps and unresolved consumers.
- [ ] 2.7 Define rollback trigger per domain.

## 3. Implementation Batches

- [ ] 3.1 Announcement batch: implement only after parity, OpenAPI diff, and consumer evidence are complete.
- [ ] 3.2 Strategy batch: implement only after strategy frontend/test consumers and mock router behavior are classified.
- [ ] 3.3 Risk batch: implement only after risk v31, shim, legacy API, and service consumer evidence are complete.
- [ ] 3.4 Keep compatibility shims unless exit criteria are explicitly met.
- [ ] 3.5 Do not delete flat modules, packages, or shims in the same batch that introduces a canonical path unless rollback is proven.

## 4. Verification

- [ ] 4.1 Run import smoke for old and new router import paths.
- [ ] 4.2 Run OpenAPI diff and attach summary to the implementation notes.
- [ ] 4.3 Run targeted backend tests for announcement, strategy, and risk routes.
- [ ] 4.4 Run frontend API smoke or relevant E2E subset for changed consumers.
- [ ] 4.5 Confirm PM2 backend startup with `./scripts/run_pm2_integration_workflow.sh` or a named equivalent approved by the implementation issue.
- [ ] 4.6 Confirm no new route exposure drift beyond approved OpenAPI diff.

## 5. Closure

- [ ] 5.1 Update documentation with canonical router decisions and compatibility status.
- [ ] 5.2 Record shim retirement candidates and exit criteria.
- [ ] 5.3 Leave cleanup-only deletions for a later approved batch when consumers are clear.
- [ ] 5.4 Update this checklist only after each item is actually complete.
