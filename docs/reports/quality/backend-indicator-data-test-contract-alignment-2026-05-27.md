# Backend Indicator/Data Test-Contract Alignment

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-27

Status: Ready for review

Scope: G2.160 narrow test-contract alignment plus governance records.

Base HEAD: `b31a1c69a96fa83f250e7577c4b21d3b4febbaeb`

Parent: G2.159, PR `#312`, merged as `b31a1c69a96fa83f250e7577c4b21d3b4febbaeb`.

Boundary: this package changes only the focused v1 indicator regression test and governance records. It does not edit application source, route/API behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec state, GitHub issue labels, or service getter implementations. It does not authorize Indicator/Data source implementation.

## Decision

The v1 indicator test-contract blocker identified by G2.159 is aligned.

Do not start Indicator/Data source implementation from this package. The next gate should be G2.161: Indicator/Data source implementation authorization package.

## Pre-Edit Evidence

GitNexus pre-edit impact:

| Symbol | Risk | Impacted | Direct callers | Processes |
|---|---:|---:|---:|---:|
| `test_v1_indicators_rejects_unsupported_indicator` | LOW | 0 | 0 | 0 |

`get_technical_indicators` is an ambiguous symbol name in GitNexus. Context lookup pinned the intended function at `web/backend/app/api/v1/strategy/indicators.py::get_technical_indicators`. No application source was edited.

## Red-Green Evidence

Red command:

```bash
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_v1_indicators_regressions.py -q --no-cov --tb=short
```

Red result:

- `1 failed, 1 passed in 1.87s`
- failing test: `test_v1_indicators_rejects_unsupported_indicator`
- cause: test expected `module.HTTPException`, while current implementation raises canonical `BusinessException`.

Green command:

```bash
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_v1_indicators_regressions.py -q --no-cov --tb=short
```

Green result:

- `2 passed in 1.61s`

## Change

Changed file:

- `web/backend/tests/test_v1_indicators_regressions.py`

Patch summary:

- import `pytest`;
- import `BusinessException` from `app.core.exceptions`;
- replace the legacy `try/except module.HTTPException` block with `pytest.raises(BusinessException)`;
- preserve status/detail assertions:
  - `status_code == 400`;
  - detail contains `Unsupported indicators`.

## Verification

| Check | Result |
|---|---|
| `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_v1_indicators_regressions.py -q --no-cov --tb=short` | 2 passed in 1.61s |
| `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_indicator_registry_route_provider.py -q --no-cov --tb=short` | 2 passed in 2.06s |
| `ruff check web/backend/tests/test_v1_indicators_regressions.py` | All checks passed |

No route/OpenAPI drift check was required because no application route, dependency, response model, or OpenAPI exposure changed.

## Boundaries

No application source was edited.

This package does not:

- edit `web/backend/app/**`;
- delete or privatize `get_data_service()`;
- change route paths, response envelopes, or OpenAPI exposure;
- touch Strategy adapter, root facade compatibility, or route dependency/provider governance;
- modify frontend, PM2, OpenSpec, config, scripts, or issue labels.

## Next Gate

Review this package. If accepted, start G2.161 as an Indicator/Data source implementation authorization package. G2.161 should re-run current-head impact and decide whether a source implementation lane can safely convert the three direct `get_data_service()` body calls without changing route/API contracts.
