# Backend Health/Status Implementation Boundary

日期: 2026-05-18  
OpenSpec change: `consolidate-backend-health-endpoints`  
范围: G 线健康 / 状态端点 implementation guardrail 收口

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## 结论

本批次不需要运行时代码迁移。

原因:

- `GET /health` 已作为 platform liveness 存在。
- `GET /health/ready` 已作为 canonical readiness 存在。
- `GET /api/health/ready` 已作为 compatibility readiness 存在。
- `GET /api/health/services` 已作为 system services health 存在。
- 本批未批准新增 `/health/services`、`/health/readiness` 或其他 alias。
- 本批未批准退役 domain smoke/status endpoints。

因此 `3.1-3.4` 按 no-op implementation verified 收口，而不是按代码改造收口。

## Probe Path Inventory

扫描范围:

- `.github/workflows/`
- `config/`
- `scripts/`
- root `ecosystem*.config.js`
- root `docker-compose*.yml`

扫描结果:

- checked files: `5825`
- matched files for canonical health/status probe paths: `15`
- disallowed `/health/readiness` consumer hits: `0`
- project-wide `/health/readiness` hits: only in `openspec/changes/consolidate-backend-health-endpoints/` explanatory text

代表性 active consumer paths:

- `.github/workflows/data-sync-testing.yml`: `/health/ready`
- `.github/workflows/ci-cd-with-type-checking.yml`: `/health/ready`
- `.github/workflows/e2e-testing.yml`: `/health/ready`
- `scripts/run_pm2_integration_workflow.sh`: `/api/health/ready`
- PM2 / live smoke evidence uses `http://localhost:8020/api/health/ready`

## Task 3.1

Task:

- Update only approved probe paths or aliases.

Disposition:

- Closed as verified no-op.
- No unapproved probe path update was made.
- Existing approved paths remain the active paths.

## Task 3.2

Task:

- Preserve existing readiness paths until consumers migrate.

Disposition:

- Closed.
- `/health/ready` and `/api/health/ready` remain present in OpenAPI and passed TestClient smoke.
- No consumer migration was forced in this batch.

## Task 3.3

Task:

- Retire only endpoints with no active consumers and approved OpenAPI diff.

Disposition:

- Closed as guardrail satisfied.
- No endpoint was retired in this batch.
- OpenAPI diff recorded `added_paths=0` and `removed_paths=0`.

## Task 3.4

Task:

- Do not treat 404 on old endpoints as success without approved retirement notes.

Disposition:

- Closed as guardrail satisfied.
- `/health/readiness` remains absent and was not introduced.
- Its absence is documented as an intentional non-addition, not as a successful migration of an active endpoint.

## Boundary

This report does not close:

- cross-domain OpenAPI documentation failures in `web/backend/tests/test_health_route_conflicts.py`
- full PM2 integration workflow
- OpenSpec archive
- any future domain smoke/status endpoint retirement
