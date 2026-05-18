# Change: Consolidate backend health/status endpoints

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why

The backend audit found many health-like and status-like routes across platform readiness, system service checks, metrics, domain smoke endpoints, SSE monitoring, and examples. Current readiness exists at `/health/ready` and `/api/health/ready`, while service checks are exposed through `/api/health/services`.

Deleting domain health endpoints without a route table, OpenAPI diff, and consumer matrix can break PM2 checks, monitoring, frontend pages, tests, or CI smoke scripts.

## What Changes

- Establish a canonical health/status endpoint taxonomy.
- Generate local-decorator and prefix-expanded full-path route tables before health/status endpoint changes.
- Require OpenAPI diff and consumer matrix before retiring health-like or status-like endpoints.
- Preserve readiness/liveness behavior and compatibility paths until probes are migrated.
- Define rollback criteria for any health/status endpoint retirement or prefix change.

## Impact

- Affected specs:
  - `api-integration`
  - `api-documentation`
  - `architecture-governance`
- Affected code, when implementation is later approved:
  - `web/backend/app/main.py`
  - `web/backend/app/api/health.py`
  - `web/backend/app/router_registry.py`
  - Domain routers with `/health`-like or `/status`-like endpoints
  - PM2, monitoring, CI, frontend, and tests that call health/status endpoints

## Source Evidence

- `docs/reports/quality/health-endpoint-consolidation-2026-05-14.md`
- `docs/reports/quality/backend-audit-documents-review-2026-05-15.md`
- `docs/reports/quality/backend-route-table-openapi-baseline-2026-05-18.md`
- `docs/reports/quality/backend-route-table-duplicate-routes-mattpocock-review-2026-05-18.md`
- `docs/reports/quality/generated/backend-fullpath-route-table.md`
- `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md`

## Approval Boundary

This change is a proposal and design package only. It does not approve code implementation. Implementation must not begin until this OpenSpec change is reviewed and approved.
