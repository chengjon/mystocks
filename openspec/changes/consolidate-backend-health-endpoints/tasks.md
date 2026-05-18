> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## 1. Pre-Implementation Evidence

> **2026-05-18 跨线对齐**:
> P3-A5 已提出 health/status taxonomy，并已有 52-route inventory。更新本
> change 时必须复用或明确 supersede 这些 evidence；不要创建重复的
> health endpoint proposal。

- [x] 1.1 Confirm orchestration artifact: `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md`.
- [x] 1.2 Confirm local route baseline: `docs/reports/quality/backend-route-table-openapi-baseline-2026-05-18.md`.
- [x] 1.3 Generate prefix-expanded full-path route table with `cd web/backend && python ../../scripts/dev/backend_audit_fullpath_routes.py ../../docs/reports/quality/generated`. Current post-P3-D artifact records 538 routes, 0 full-path duplicate groups, and 2 remaining orphan route files.
- [x] 1.4 Confirm full-path artifact: `docs/reports/quality/generated/backend-fullpath-route-table.md`.
- [x] 1.5 Generate current OpenAPI schema baseline with `python scripts/generate_openapi.py --output docs/reports/quality/generated/openapi-before.json`. Existing baseline is OpenAPI 3.1.0 with 501 paths.
- [x] 1.6 Classify all health-like and status-like endpoints. Initial classification exists in P3-A5 / 52-route inventory; remaining work is formal OpenSpec reconciliation.
- [x] 1.7 Build consumer matrix for PM2, monitoring, CI, frontend, tests, scripts, and docs.
- [x] 1.8 Confirm `/health/readiness` remains absent unless intentionally added.

> 2026-05-18 G line start evidence:
> `docs/reports/quality/backend-health-status-taxonomy-start-2026-05-18.md`
> confirms orchestration, route baseline, consumer matrix, `/health/readiness`
> absence in code roots, and the first implementation boundary.

## 2. Design Decisions

- [x] 2.1 Define canonical liveness endpoint.
- [x] 2.2 Define canonical readiness endpoint and compatibility readiness path.
- [x] 2.3 Define canonical system services health endpoint.
- [x] 2.4 Define status endpoint taxonomy: platform status, service status, domain status, metrics/observability, example/embedded app.
- [x] 2.5 Decide which domain smoke/status endpoints remain intentionally separate.
- [x] 2.6 Decide whether `backup_recovery_secure/cleanup_old_backups.py` belongs to health/status consolidation or deferred backup domain route ownership.
- [x] 2.7 Define rollback trigger per endpoint category.

> 2026-05-18 taxonomy decision:
> canonical liveness is `GET /health`; canonical readiness is
> `GET /health/ready`; compatibility readiness is `GET /api/health/ready`;
> canonical system services health is `GET /api/health/services`; domain
> smoke/status endpoints remain separate until consumer migration is proven;
> `backup_recovery_secure/cleanup_old_backups.py` remains deferred to backup
> route ownership.

## 3. Implementation

- [ ] 3.1 Update only approved probe paths or aliases.
- [ ] 3.2 Preserve existing readiness paths until consumers migrate.
- [ ] 3.3 Retire only endpoints with no active consumers and approved OpenAPI diff.
- [ ] 3.4 Do not treat 404 on old endpoints as success without approved retirement notes.

## 4. Verification

- [x] 4.1 Run `/health/ready` smoke.
- [x] 4.2 Run `/api/health/ready` smoke.
- [x] 4.3 Run `/api/health/services` smoke.
- [ ] 4.4 Run status endpoint smoke for approved canonical status paths.
- [x] 4.5 Run OpenAPI diff and classify changes.
- [ ] 4.6 Run affected backend tests and frontend/API smoke.
- [ ] 4.7 Confirm PM2 backend status and configured health checks with `pm2 list` and `./scripts/run_pm2_integration_workflow.sh` or a named equivalent approved by the implementation issue.

## 5. Closure

- [x] 5.1 Update health/status endpoint documentation with canonical and compatibility paths.
- [ ] 5.2 Record retained domain smoke/status endpoints and owners.
- [ ] 5.3 Record retired endpoints and rollback notes.

> 2026-05-18 smoke evidence:
> `docs/reports/quality/backend-health-status-smoke-2026-05-18.md`
> records TestClient smoke for `/health`, `/health/ready`,
> `/api/health/ready`, and `/api/health/services`; confirms
> `/health/readiness` remains absent; and records an OpenAPI diff with
> `baseline_path_count=501`, `current_path_count=501`, `added_paths=0`,
> `removed_paths=0`. Task 4.6 remains open because the broader historical
> `test_health_route_conflicts.py` suite currently has 5 unrelated OpenAPI
> documentation failures.
