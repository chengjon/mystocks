# Backend Data-Quality Monitor Singleton Implementation - 2026-05-28

> **历史文档说明**: 本文件是 G2.212 执行证据快照，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Lane: G2.212 data-quality monitor singleton/backing API compatibility implementation
- Parent approval: G2.211, PR `#364`, merge commit `535a6d9c1565b4ced7942cb4082104f2fb0506fd`
- OpenSpec change: `migrate-backend-singletons-to-lifecycle-di`
- Source authority: approved, path-limited
- Result: ready for PR review

## Scope

Authorized source paths:

- `web/backend/app/services/_data_quality_monitor_singleton.py`
- `web/backend/app/services/data_quality_monitor.py`

Authorized test path:

- `web/backend/tests/test_data_quality_monitor_singleton_provider.py`

Explicitly excluded:

- routes
- canonical adapters
- `adapter_split`
- legacy `data_adapters`
- `market_data_adapter.py`
- OpenAPI, frontend, config, scripts, and OpenSpec files

## Implementation

G2.212 keeps the existing public singleton API stable:

- `get_data_quality_monitor()`
- `monitor_data_quality(...)`

It adds two compatibility hooks exported through `app.services.data_quality_monitor`:

- `set_data_quality_monitor_provider(provider)`
- `reset_data_quality_monitor_provider()`

The default global `DataQualityMonitor()` fallback is still preserved when no provider override is registered.

## GitNexus Pre-Edit Evidence

`get_data_quality_monitor` was checked before editing:

- risk: `CRITICAL`
- impacted count: `24`
- direct dependents: `20`
- affected processes: `7`
- affected modules: `4`

Disposition: this high-risk root seam was known from G2.210 and explicitly authorized by G2.211 for a compatibility-first, two-source-file implementation only.

`monitor_data_quality` was also checked before editing:

- risk: `LOW`
- impacted count: `1`
- direct dependents: `1`

## TDD Evidence

RED:

```bash
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_quality_monitor_singleton_provider.py -q --no-cov --tb=short
```

Observed failure before implementation:

- `ImportError: cannot import name 'reset_data_quality_monitor_provider' from 'app.services.data_quality_monitor'`

GREEN:

```bash
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_quality_monitor_singleton_provider.py -q --no-cov --tb=short
```

Result:

- `3 passed`

## Verification

Focused provider seam regression:

```bash
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_quality_monitor_singleton_provider.py -q --no-cov --tb=short
```

Result:

- `3 passed`

Authorized non-large regression set:

```bash
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_quality_monitor_singleton_provider.py web/backend/tests/test_data_quality_route_provider_regressions.py web/backend/tests/test_data_quality_canonical_service_adapter_provider.py web/backend/tests/test_adapter_split_data_quality_monitor_provider.py web/backend/tests/test_market_data_adapter_quality_monitor_provider.py web/backend/tests/test_logging_noise_regressions.py -q --no-cov --tb=short
```

Result:

- `20 passed`

Large-file split regression record:

```bash
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_large_file_split_regressions.py -q --no-cov --tb=short || true
```

Observed result:

- `35 passed`
- `4 failed`

The four failures are existing unrelated baseline issues outside G2.212 scope:

- missing `src/interfaces/adapters/efinance_adapter/efinance_data_source.py`
- missing `src/routes/stocks_routes/check_use_mock_data.py`
- missing `get_stock_search_service` export
- missing `app.core.exceptions`

Ruff:

```bash
ruff check web/backend/app/services/_data_quality_monitor_singleton.py web/backend/app/services/data_quality_monitor.py web/backend/tests/test_data_quality_monitor_singleton_provider.py
```

Result:

- `All checks passed`

OpenSpec:

```bash
openspec validate migrate-backend-singletons-to-lifecycle-di --strict
```

Result:

- `Change 'migrate-backend-singletons-to-lifecycle-di' is valid`
- PostHog connection refusal is telemetry noise only.

## Function Tree

G2.212 updates `domain-01-node-03` / `1.3 多数据源集成` with the data-quality monitor singleton/backing API seam:

- `docs/FUNCTION_TREE.md`
- `governance/function-tree/catalog.yaml`

## Next Gate

If PR `#365` is accepted, start G2.213 as a no-source closeout / residual refresh package.

G2.213 should:

- record acceptance of the provider hook
- rescan remaining `get_data_quality_monitor` residuals
- classify retained residuals
- decide whether any later source lane is warranted

No new source lane should start before G2.213 classifies the residuals.
