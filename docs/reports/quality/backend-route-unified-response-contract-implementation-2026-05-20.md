# Backend Route UnifiedResponse Contract Implementation - 2026-05-20

> **历史实施说明**:
> 本文件是历史实施记录，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: approved with notes

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

## Review Result

Review verdict: `APPROVE_WITH_NOTES`.

Verified by review:

- Runtime blocker is fixed: `_data_lineage_responses.py` imports
  `asynccontextmanager`, and `app.main` imports with `548` routes.
- New exports import successfully, including `EdgeInfo`, `NodeInfo`,
  `_AsyncpgLineageConnectionAdapter`, and
  `ContractDriftIncidentResponse`.
- Ruff reports zero errors across the `18` changed backend API files.
- `response_model=UnifiedResponse[...]` is applied consistently for the reviewed
  route-contract targets.

Non-blocking notes:

1. `data_source_config.py` imports runtime dependencies from
   `._data_source_config_responses`, including `get_config_manager`,
   `get_current_user`, and `router`. This works but mixes route runtime
   composition with response artifact exports; track as a future split candidate.
2. `monitoring_watchlists.py` keeps module-level mutable runtime fallback state.
   The state is now initialized to `None` for the singleton guard, but the
   concurrency/lifecycle design should be handled by a separate future proposal.
3. The implementation commit scope is wider than the title alone suggests: it
   includes runtime import repair, compatibility exports, schema additions, and
   route-contract canonicalization. This was accepted for this unblock batch but
   should be treated as an exception, not a micro-commit precedent.

## Disposition

The dedicated route-contract blocker is cleared in the isolated worktree. The
previous singleton-none commit blocker was also rechecked and cleared for the
changed backend API files. The implementation batch is approved with notes. The
next gate is deciding whether to push or merge commit `00101699b` through the
normal branch integration flow.
