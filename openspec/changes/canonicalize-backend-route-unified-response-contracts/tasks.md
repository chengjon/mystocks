# Tasks: Canonicalize backend route UnifiedResponse contracts

> **历史任务说明**:
> 本文件是历史任务、历史计划或历史执行清单，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## 1. Preflight

- [x] 1.1 Confirm the working lane is isolated from the root dirty/staged worktree.
- [x] 1.2 Reproduce the current `UnifiedResponse Contract Guard` blocker and record exact file/route counts.
- [x] 1.3 Run GitNexus impact for each route file before editing.
- [x] 1.4 Record the current `app.main` import and `test_health_route_conflicts.py` status as the before-state.

## 2. Contract Migration

- [x] 2.1 Record a route-level inventory before editing: routes with no
  `response_model`, routes with direct typed `response_model`, and routes already
  using `UnifiedResponse[...]` or `UnifiedPaginatedResponse[...]`.
- [x] 2.2 Add canonical wrapper declarations for routes with no `response_model`;
  current known target is `web/backend/app/api/data_quality.py`, plus any
  route-level gaps confirmed in `web/backend/app/api/technical_analysis.py`.
- [x] 2.3 Wrap existing direct typed response models without changing payload
  shape; current known targets are
  `web/backend/app/api/indicators/indicator_cache.py`,
  `web/backend/app/api/signal_monitoring/signal_history_response.py`, and the
  direct-model routes in `web/backend/app/api/technical_analysis.py`.
- [x] 2.4 Preserve response payload shape or record any intentional
  endpoint-level contract change with tests and OpenAPI diff.
- [x] 2.5 Re-run the guard after each file-level migration and record the
  remaining per-file error count before moving to the next file.

## 3. Verification

- [x] 3.1 Run `python scripts/compliance/unified_response_contract_guard.py --root-dir . --format json` on the changed route files and record `errors=0`.
- [x] 3.2 Run targeted `ruff check` on the changed files.
- [x] 3.3 Run `PYTHONPATH=web/backend python -c "from app.main import app; print('routes', len(app.routes))"` with local smoke env and record the route count.
- [x] 3.4 Run `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short`.
- [x] 3.5 Run targeted `app.openapi()` smoke and record path count, operation count, duplicate operationId count, and warnings.

## 4. Closure

- [x] 4.1 Record the implementation report under `docs/reports/quality/`.
- [x] 4.2 Update `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` after the implementation is reviewed.
- [x] 4.3 Re-evaluate whether `sequence-backend-architecture-unblocks` source commit can proceed.
