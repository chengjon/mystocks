# Backend Route UnifiedResponse Contract Implementation - 2026-05-20

> **历史实施说明**:
> 本文件是历史实施记录，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: implemented in isolated worktree; ready for review

Worktree: `.worktrees/sequence-route-contract-unblock`
Change: `canonicalize-backend-route-unified-response-contracts`

## Scope

This implementation resolves the `UnifiedResponse Contract Guard` blocker that
prevented the runtime unblock source changes from becoming commit-ready.

Target route files:

| File | Baseline errors | Final errors |
|---|---:|---:|
| `web/backend/app/api/data_quality.py` | 9 | 0 |
| `web/backend/app/api/indicators/indicator_cache.py` | 6 | 0 |
| `web/backend/app/api/signal_monitoring/signal_history_response.py` | 4 | 0 |
| `web/backend/app/api/technical_analysis.py` | 8 | 0 |

Total: `27` route-contract errors reduced to `0`.

## Implementation

- Added `response_model=UnifiedResponse[...]` declarations for route handlers
  without canonical response contracts.
- Wrapped direct typed response payloads in success responses where FastAPI
  response validation would otherwise reject a `UnifiedResponse[...]` model.
- Preserved existing success-wrapper returns where endpoints already returned
  `create_success_response(...)`.
- Kept route-contract migration scoped to the four target files.
- Restored explicit compatibility re-exports in `indicator_cache.py` for
  `IndicatorCache`, `RateLimiter`, and `IndicatorOptimizationRequest` so
  `app.api.indicators.__init__` remains import-compatible.
- Restored `None`-initialized runtime fallback globals in
  `monitoring_watchlists.py` after rechecking the previous source commit gate.

## Contract Shape Notes

This change intentionally moves the target OpenAPI response contracts to the
canonical `UnifiedResponse[...]` envelope. Endpoints that previously returned a
direct list/model/dict now expose that payload under `data`.

No service-layer behavior, singleton lifecycle, schema directory retirement,
frontend behavior, or miniQMT evidence state was changed.

## Verification

Environment used for import and OpenAPI smoke:

```bash
PYTHONPATH=web/backend
POSTGRESQL_HOST=localhost
POSTGRESQL_USER=test
POSTGRESQL_PASSWORD=test
JWT_SECRET_KEY=test-secret-key-for-local-import-smoke-only
BACKEND_PORT=8020
BACKEND_BACKUP_PORT=8021
```

| Check | Result |
|---|---|
| GitNexus impact before edits | all four target files `LOW` |
| `UnifiedResponse Contract Guard` on four target files | `checked_files=4`, `checked_routes=27`, `errors=0` |
| `ruff check` on four target files | `issues=0` |
| `Backend Singleton None Guard` on changed backend API files | `checked_files=18`, `errors=0` |
| `from app.main import app; print("routes", len(app.routes))` | passed, `routes 548` |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | `112 passed in 63.42s` |
| targeted `app.openapi()` smoke | `paths=500`, `operations=536`, `duplicate_operation_ids=0`, `duplicate_operation_id_warnings=0`, `warnings=121` |

## Disposition

The dedicated route-contract blocker is cleared in the isolated worktree. The
previous singleton-none commit blocker was also rechecked and cleared for the
changed backend API files. The next gate is review of this implementation batch,
then a path-limited commit that includes the runtime unblock source changes plus
this route-contract implementation.
