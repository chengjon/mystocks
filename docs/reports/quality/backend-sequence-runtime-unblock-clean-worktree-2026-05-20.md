# Backend Sequence Runtime Unblock Clean Worktree Report - 2026-05-20

> **历史实施说明**:
> 本文件是历史实施记录，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: Runtime import chain restored in isolated worktree; commit still blocked
by route-contract gate

Worktree: `.worktrees/sequence-route-contract-unblock`
Base HEAD: `93c6f6a05 chore(docs): record sequence backend unblocks`
Current worktree HEAD at proposal handoff: `f96ff2dc5 chore(docs): record route contract proposal checkpoint`
Commits since base: `9addc2458 chore(docs): add route contract unblock proposal`; `f96ff2dc5 chore(docs): record route contract proposal checkpoint`

## Scope

This report records the isolated source implementation follow-up after the
governance-only commit.

It does not authorize broad route response-contract migration. The runtime
unblock repairs only import-time blockers needed to make `app.main` and the
health route governance suite collect and run.

## Runtime Fixes Applied

- Restored missing contract drift response schemas used by
  `web/backend/app/api/contract/routes.py`.
- Converted remaining local helper imports to package-relative imports:
  - `web/backend/app/api/data_lineage.py`
  - `web/backend/app/api/data_source_config.py`
  - `web/backend/app/api/technical_analysis.py`
  - `web/backend/app/api/indicators/indicator_cache.py`
- Restored missing helper imports for extracted response/model modules:
  - `_data_lineage_responses.py`
  - `_data_source_config_responses.py`
  - `_governance_dashboard_responses.py`
  - `_monitoring_watchlists_models.py`
  - `_monitoring_watchlists_responses.py`
  - `_technical_analysis_models.py`
  - `_technical_analysis_responses.py`
  - `_watchlist_responses.py`
- Restored route-local imports or definitions required by import-time execution:
  - `data_quality.py`
  - `monitoring_watchlists.py`
  - `signal_history_response.py`
  - `trade/routes.py`
- Expanded the `data_source_registry.py` search endpoint docstring to satisfy
  the health route documentation guard.

## Verification

Environment used for import/test smoke:

```bash
PYTHONPATH=web/backend
POSTGRESQL_HOST=localhost
POSTGRESQL_USER=test
POSTGRESQL_PASSWORD=test
JWT_SECRET_KEY=test-secret-key-for-local-import-smoke-only
BACKEND_PORT=8020
BACKEND_BACKUP_PORT=8021
```

Results:

| Check | Result |
|---|---|
| `from app.main import app; print("routes", len(app.routes))` | passed, `routes 548` |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py --collect-only -q --no-cov` | passed, `112 tests collected` |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | passed, `112 passed in 62.72s` |
| `ruff check web/backend/app/api --select F821 --output-format json` | improved from `113` to `25`; remaining `25` are in data/risk historical debt files outside the current runtime import chain |

## Commit Gate Status

The source change is not commit-ready yet because the staged route files would
still trip `UnifiedResponse Contract Guard`.

Current guard summary for changed backend API files:

| File | Route-contract errors |
|---|---:|
| `web/backend/app/api/data_quality.py` | 9 |
| `web/backend/app/api/indicators/indicator_cache.py` | 6 |
| `web/backend/app/api/signal_monitoring/signal_history_response.py` | 4 |
| `web/backend/app/api/technical_analysis.py` | 8 |

Total: `27` route-contract errors across `4` files.

Disposition: keep the runtime unblock source changes in the isolated worktree
and open a separate OpenSpec lane for route-contract migration. Do not hide this
with `--no-verify`, and do not expand `sequence-backend-architecture-unblocks`
into a broad route response-contract migration.
