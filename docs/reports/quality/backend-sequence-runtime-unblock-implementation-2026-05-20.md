# Backend Sequence Runtime Unblock Implementation Evidence

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Summary

- Date: 2026-05-20
- HEAD at verification: `7b097fffd`
- OpenSpec change: `sequence-backend-architecture-unblocks`
- Scope: runtime import-chain unblock needed before route/OpenAPI evidence refresh
- Result: `app.main` import restored; health route conflict suite restored to passing

The original blocker was recorded as `web/backend/app/api/data_lineage.py` reaching
`web/backend/app/api/_data_lineage_responses.py`, where `@asynccontextmanager`
was used without importing it. During implementation, the smoke advanced through
additional import-time blockers caused by split route/helper modules with missing
imports, missing route exports, or stale package paths. Those blockers were fixed
as one runtime-unblock batch because each directly prevented `app.main` import or
`test_health_route_conflicts.py` collection.

## Changed Runtime Surfaces

Runtime import-chain repairs were limited to the following route/helper surfaces:

- `web/backend/app/api/_data_lineage_responses.py`
- `web/backend/app/api/data_lineage.py`
- `web/backend/app/api/_data_source_config_responses.py`
- `web/backend/app/api/data_source_config.py`
- `web/backend/app/api/_technical_analysis_models.py`
- `web/backend/app/api/_technical_analysis_responses.py`
- `web/backend/app/api/technical_analysis.py`
- `web/backend/app/api/_governance_dashboard_responses.py`
- `web/backend/app/api/_monitoring_watchlists_models.py`
- `web/backend/app/api/_monitoring_watchlists_responses.py`
- `web/backend/app/api/monitoring_watchlists.py`
- `web/backend/app/api/_watchlist_responses.py`
- `web/backend/app/api/signal_monitoring/signal_history_response.py`
- `web/backend/app/api/data_quality.py`
- `web/backend/app/api/indicators/__init__.py`
- `web/backend/app/api/indicators/indicator_cache.py`
- `web/backend/app/api/trade/routes.py`
- `web/backend/app/api/data_source_registry.py`

The work did not intentionally change endpoint business behavior. The only route
shape correction was restoring the data-quality router prefix so central
registration at `/api` exposes the contract-tested `/api/data-quality/...` paths
instead of colliding with `/api/health`.

## GitNexus Impact Gate

GitNexus impact checks were run before editing the source files/surfaces touched
by this batch. Each returned `LOW` risk, with no affected execution processes.
Direct importers were limited to the corresponding route package/module where
GitNexus reported any importer.

Notable checked targets:

- `_data_lineage_responses.py`
- `data_lineage.py`
- `_data_source_config_responses.py`
- `data_source_config.py`
- `_technical_analysis_responses.py`
- `technical_analysis.py`
- `_governance_dashboard_responses.py`
- `_monitoring_watchlists_models.py`
- `_monitoring_watchlists_responses.py`
- `monitoring_watchlists.py`
- `_watchlist_responses.py`
- `signal_monitoring/signal_history_response.py`
- `_technical_analysis_models.py`
- `data_quality.py`
- `indicators/indicator_cache.py`
- `indicators/__init__.py`
- `trade/routes.py`
- `data_source_registry.py`

## Verification

Commands run from repository root:

```bash
ruff check <intended runtime-unblock files>
```

Result:

```text
All checks passed!
```

```bash
env PYTHONPATH=web/backend python -c "from app.main import app; print('routes', len(app.routes))"
```

Result:

```text
routes 548
```

```bash
pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short
```

Result:

```text
112 passed in 63.69s (0:01:03)
```

Minimal OpenAPI runtime snapshot:

```text
routes=548
paths=500
operation_ids=536
duplicate_operation_ids=0
warnings=121
```

Runtime warnings observed during import/smoke:

- GPU backtest dependency warning: Numba requires NumPy 2.2 or less; current environment reports NumPy 2.4.
- Mock backtest data falls back after the real-data branch raises `NotImplementedError`.
- These warnings did not block `app.main`, OpenAPI generation, or the health route suite.

## Remaining F821 Snapshot

After the runtime unblock, `ruff check web/backend/app/api --select F821` still
reports 25 F821 findings in 4 files:

| File | Undefined names | Disposition |
|---|---|---|
| `web/backend/app/api/data/analysis_api.py` | `ma_5`, `math`, `r` | Existing non-import-chain debt; not part of this runtime unblock. |
| `web/backend/app/api/data/data_api_new.py` | `datetime` | Existing non-import-chain debt; not reached by this smoke path. |
| `web/backend/app/api/risk/_alerts_responses.py` | `_acknowledged_v31_alerts`, `get_alert_rule_engine`, `get_risk_alert_notification_manager`, `get_risk_management_core` | Deferred because it involves risk alert state/helper ownership rather than import-time route startup. |
| `web/backend/app/api/risk/alerts.py` | `_build_active_alerts_payload`, `_resolve_notification_manager`, `_resolve_rule_engine`, `_resolve_runtime_alert_service` | Deferred with the paired risk alert helper ownership issue. |

The deferred risk alert findings should be handled as a separate routing/state
ownership task, not folded into this runtime unblock batch.

## OpenSpec State Impact

This evidence closes the runtime import/collection blocker for
`sequence-backend-architecture-unblocks` Task 2.x and makes the later route table,
OpenAPI, and probe consumer evidence refresh meaningful again.

It does not authorize broad architecture refactors, schema directory retirement,
service lifecycle migration, or risk alert state ownership changes.
