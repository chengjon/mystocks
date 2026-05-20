# Tasks: Canonicalize backend route UnifiedResponse contracts

> **历史任务说明**:
> 本文件是历史任务、历史计划或历史执行清单，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## 1. Preflight

- [ ] 1.1 Confirm the working lane is isolated from the root dirty/staged worktree.
- [ ] 1.2 Reproduce the current `UnifiedResponse Contract Guard` blocker and record exact file/route counts.
- [ ] 1.3 Run GitNexus impact for each route file before editing.
- [ ] 1.4 Record the current `app.main` import and `test_health_route_conflicts.py` status as the before-state.

## 2. Contract Migration

- [ ] 2.1 Migrate `web/backend/app/api/data_quality.py` response models.
- [ ] 2.2 Migrate `web/backend/app/api/indicators/indicator_cache.py` response models.
- [ ] 2.3 Migrate `web/backend/app/api/signal_monitoring/signal_history_response.py` response models.
- [ ] 2.4 Migrate `web/backend/app/api/technical_analysis.py` response models.
- [ ] 2.5 Preserve response payload shape or record any intentional endpoint-level contract change with tests and OpenAPI diff.

## 3. Verification

- [ ] 3.1 Run `python scripts/compliance/unified_response_contract_guard.py --root-dir . --format json` on the changed route files and record `errors=0`.
- [ ] 3.2 Run targeted `ruff check` on the changed files.
- [ ] 3.3 Run `PYTHONPATH=web/backend python -c "from app.main import app; print('routes', len(app.routes))"` with local smoke env and record the route count.
- [ ] 3.4 Run `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short`.
- [ ] 3.5 Run targeted `app.openapi()` smoke and record path count, operation count, duplicate operationId count, and warnings.

## 4. Closure

- [ ] 4.1 Record the implementation report under `docs/reports/quality/`.
- [ ] 4.2 Update `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` after the implementation is reviewed.
- [ ] 4.3 Re-evaluate whether `sequence-backend-architecture-unblocks` source commit can proceed.
