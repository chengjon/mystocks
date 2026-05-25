# Backend DataSourceFactory Compatibility Getter Final Retirement Implementation - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.84 source implementation packet

Status: ready for review

Branch: `g2-84-data-source-factory-compat-getter-final-retirement-implementation`

Baseline HEAD: `5de71a8847a45efd0628b184baff985a9dd3b180`

Prepared at: `2026-05-25T13:45:00+08:00`

## Purpose

Implement the G2.83 authorization to retire the public
`get_data_source_factory()` compatibility getter and its package export.

This packet keeps `get_data_source_factory_dependency` and private
`_get_or_create_data_source_factory()` intact. It does not edit route/API
modules, OpenAPI exposure, frontend, runtime/PM2, OpenSpec, or issue labels.

## Scope

Changed source files:

- `web/backend/app/services/data_source_factory/data_source_factory.py`;
- `web/backend/app/services/data_source_factory/__init__.py`.

Changed test files:

- `web/backend/tests/test_data_source_factory_lifecycle_di.py`;
- `web/backend/tests/test_market_api_integration.py`;
- `web/backend/tests/test_data_stocks_runtime_fallback.py`;
- `tests/backend/test_data_api_regression.py`.

## Implementation Summary

- Removed public `get_data_source_factory()` from
  `data_source_factory.py`.
- Removed the package re-export and `__all__` entry from
  `web/backend/app/services/data_source_factory/__init__.py`.
- Kept `_get_or_create_data_source_factory()`.
- Kept `get_data_source_factory_dependency()`.
- Retargeted test monkeypatches from package-level public getter patches to the
  supported `get_data_source_factory_dependency` FastAPI override seam.
- Replaced the old compatibility getter initialization test with a retirement
  assertion proving the module and package no longer expose the public getter.

## TDD Evidence

RED:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short
1 failed, 4 passed
```

Expected failure:

- `test_package_no_longer_exports_public_compatibility_getter` failed because
  `data_source_factory_module.get_data_source_factory` still existed.

GREEN after implementation and formatting:

```text
PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short
5 passed in 1.97s
```

## Verification

| Check | Result |
|---|---|
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short` | 5 passed |
| `pytest -o addopts= web/backend/tests/test_data_stocks_runtime_fallback.py -q --no-cov --tb=short` | 1 passed |
| `pytest -o addopts= web/backend/tests/test_market_api_integration.py -q --no-cov --tb=short` | 18 passed |
| `pytest -o addopts= tests/backend/test_data_api_regression.py -q --no-cov --tb=short` | 3 failed; existing historical-route 404 failures remain |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | 120 passed |
| `ruff check` on all touched files | passed |
| `black --check` on all touched files | passed |
| OpenAPI smoke with root `.env` loaded | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0` |

`test_data_api_regression.py` still fails because its in-file app includes the
data router at a path that returns 404 for its historical expectations. This was
recorded in G2.83 and is not fixed by this packet.

## Public Getter Scan

Current exact scan excluding `get_data_source_factory_dependency`:

| Metric | Result |
|---|---:|
| Exact public getter hits | 3 |
| Production exact public getter hits | 0 |
| Package export lines | 0 |
| Public getter patch points | 0 |

Remaining exact hits are only negative assertions in
`web/backend/tests/test_data_source_factory_lifecycle_di.py`.

## GitNexus Evidence

Pre-edit GitNexus impact for `get_data_source_factory`:

| Metric | Result |
|---|---|
| Risk | CRITICAL |
| Impacted count | 22 |
| Direct dependents | 21 |
| Processes affected | 12 |

GitNexus still reports stale route/API and service helper callers. The precise
current-head scan before implementation showed no live route/API production
consumer; after implementation, production public getter hits are `0`.

GitNexus did not find `_get_or_create_data_source_factory` or
`get_data_source_factory_dependency`, even after `gitnexus analyze`. Those
symbols were checked by current source scans and focused tests instead.

Staged GitNexus `detect_changes(scope=staged)` was run before commit:

| Metric | Result |
|---|---|
| Changed files | 10 |
| Changed symbols | 0 |
| Affected processes | 0 |
| Risk | LOW |

## Boundary Confirmation

This packet did not:

- remove `get_data_source_factory_dependency`;
- remove `_get_or_create_data_source_factory`;
- edit route modules under `web/backend/app/api/**`;
- edit route paths, response models, response shapes, or OpenAPI exposure;
- edit frontend files;
- edit runtime or PM2 scripts;
- edit OpenSpec changes;
- change GitHub issue labels;
- change `DATA_SOURCE_FACTORY_STATE_KEY`;
- fix unrelated historical-route failures in `tests/backend/test_data_api_regression.py`.

## Next Gate

Human review / PR merge decision for G2.84.

If accepted, create a closeout/current-head refresh before selecting any further
DataSourceFactory compatibility-surface cleanup.
