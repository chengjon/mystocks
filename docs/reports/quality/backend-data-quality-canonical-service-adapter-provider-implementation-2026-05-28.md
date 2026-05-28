# Backend Data-Quality Canonical Service Adapter Provider Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Node: G2.200 data-quality canonical service adapter provider implementation
- Status: implementation evidence
- Prepared at: `2026-05-28T10:53:34+08:00`
- Base HEAD checked: `41bef3787160ec3bf7b9b31220df9d99a3437474`
- Parent authorization: G2.199, PR `#352`, merge commit `41bef3787160ec3bf7b9b31220df9d99a3437474`
- Branch: `g2-200-data-quality-canonical-service-adapter-provider`

Boundary note: this implementation uses the source authority granted by G2.199
only. It does not authorize legacy data adapter migration, `market_data_adapter.py`
edits, monitor internals, wrapper deletion, routes, OpenAPI contracts, frontend,
config, scripts, or OpenSpec change edits.

## Implementation

| Path | Change |
|---|---|
| `web/backend/app/services/adapters/dashboard_adapter.py` | Adds keyword-only `quality_monitor` constructor injection and stores it on `self._quality_monitor` |
| `web/backend/app/services/adapters/data_adapter.py` | Adds keyword-only `quality_monitor` constructor injection and stores it on `self._quality_monitor` |
| `web/backend/tests/test_data_quality_canonical_service_adapter_provider.py` | Adds focused async tests proving injected monitors bypass the global getter |
| `governance/function-tree/catalog.yaml` | Registers the two canonical service adapter paths and focused test under `domain-01-node-03` so the mainline scope gate can map this implementation |
| `docs/FUNCTION_TREE.md` | Mirrors the `domain-01-node-03` service adapter mapping required by mainline governance |

Constructor compatibility is preserved:

```python
DashboardDataSourceAdapter(config)
DataDataSourceAdapter(config)
```

New test-only / DI-capable construction is now available:

```python
DashboardDataSourceAdapter(config, quality_monitor=fake_monitor)
DataDataSourceAdapter(config, quality_monitor=fake_monitor)
```

Runtime fallback is preserved: if `quality_monitor is None`, both adapters still
call `get_data_quality_monitor()` at monitoring time.

## GitNexus Impact

| Target | Risk | Impact |
|---|---|---|
| `web/backend/app/services/adapters/dashboard_adapter.py` | LOW | `impacted_count=5`, `direct=2`, `processes_affected=0` |
| `web/backend/app/services/adapters/data_adapter.py` | LOW | `impacted_count=4`, `direct=1`, `processes_affected=0` |

Direct graph consumers remain limited to adapter package exports, the dashboard
logging regression test, the compatibility facade, the data source factory, and
the existing data adapter regression test.

## TDD Evidence

| Step | Result |
|---|---|
| Red | `2 failed` because both constructors rejected `quality_monitor` |
| Green | `2 passed` after adding the keyword-only injection seam |

The focused tests patch each module-level `get_data_quality_monitor` with a
raising sentinel and assert the injected async monitor receives the exact
`evaluate_data_quality(...)` call.

## Verification

| Check | Result |
|---|---|
| Focused pytest | `21 passed` for the new provider test plus `test_data_adapter_regression.py` and `test_logging_noise_regressions.py` |
| Ruff | `ruff check` passed for the two source files and new test |
| Import smoke without env | Blocked by existing required env validation for `POSTGRESQL_HOST`, `POSTGRESQL_USER`, `POSTGRESQL_PASSWORD`, `JWT_SECRET_KEY`, `BACKEND_PORT`, `BACKEND_BACKUP_PORT` |
| Import smoke with minimal dummy env | Passed through `app.services.data_adapter` and `data_source_factory` imports |
| OpenSpec validation | `openspec validate migrate-backend-singletons-to-lifecycle-di --strict` passed; PostHog network flush warning is telemetry noise |
| JSON/YAML parse | Passed for generated implementation JSON, `steward-index.json`, and `pr-353.yaml` |
| Markdown governance | Passed, `checked_files=6`, `errors=0` |
| Diff whitespace | `git diff --check` passed |
| GitNexus staged scope | Low risk, `changed_files=14`, `changed_symbols=0`, `affected_processes=0` |
| Function-tree mapping | `domain-01-node-03` now covers the two canonical service adapter paths and focused test path; `docs/FUNCTION_TREE.md` mirror updated |
| Mainline scope gate | Passed, `changed_files=14`, `violations=0`, report `/tmp/pr353-mainline-governance-report.json` |

## Preserved Boundaries

This lane did not touch:

- `web/backend/app/services/data_adapters/**`
- `web/backend/app/services/market_data_adapter.py`
- `web/backend/app/services/_data_quality_monitor_singleton.py`
- `web/backend/app/services/data_quality_monitor.py`
- `web/backend/app/api/**`
- `web/frontend/**`
- `src/**`
- `docs/api/**`
- `config/**`
- `scripts/**`
- `openspec/changes/**`
- `openspec/specs/**`

## Next Gate

If G2.200 is accepted, run G2.201 closeout / residual refresh before selecting
another data-quality monitor surface. Do not batch legacy adapters, wrapper
retirement, `market_data_adapter.py`, route/provider cleanup, or monitor internals
into this implementation lane.
