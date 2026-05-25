# Backend DataSourceFactory Compatibility Getter Final Retirement Authorization - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.83 source-capable authorization packet

Status: ready for review

Branch: `g2-83-data-source-factory-compat-getter-final-retirement-authorization`

Current HEAD: `075768a56ea78f11796387d25fe33eed04668c6f`

Prepared at: `2026-05-25T13:21:46+08:00`

## Purpose

Authorize a future G2.84 implementation to retire the public
`get_data_source_factory()` compatibility getter and its package export, if the
implementation stays inside the file and gate boundaries below.

This packet does not edit backend source or tests. It records the evidence and
scope required before any final retirement implementation can start.

## Current State

G2.81 removed service-internal helper dependency on the public getter. G2.82
closed out that implementation at current HEAD.

Current precise scan excluding `get_data_source_factory_dependency` shows:

| Metric | Count |
|---|---:|
| Exact public getter hits | 9 |
| Production exact public getter hits | 3 |
| Exact public getter imports | 1 |
| Exact public getter calls | 2 |
| Exact public getter definitions | 1 |
| Package export lines | 2 |

The 3 production hits are only:

| File | Line | Role |
|---|---:|---|
| `web/backend/app/services/data_source_factory/data_source_factory.py` | 308 | public getter definition |
| `web/backend/app/services/data_source_factory/__init__.py` | 12 | package re-export |
| `web/backend/app/services/data_source_factory/__init__.py` | 31 | package `__all__` entry |

No route/API production consumer remains.

## Remaining Test Consumers

The public getter still appears in test monkeypatch or compatibility coverage:

| File | Line | Role |
|---|---:|---|
| `web/backend/tests/test_data_source_factory_lifecycle_di.py` | 31 | monkeypatch public getter to prove dependency fallback bypasses it |
| `web/backend/tests/test_data_source_factory_lifecycle_di.py` | 72 | compatibility getter still initializes |
| `web/backend/tests/test_data_source_factory_lifecycle_di.py` | 101 | monkeypatch public getter to prove service helpers bypass it |
| `web/backend/tests/test_market_api_integration.py` | 85 | monkeypatch package public getter |
| `web/backend/tests/test_data_stocks_runtime_fallback.py` | 43 | monkeypatch package public getter |
| `tests/backend/test_data_api_regression.py` | 25 | patch package public getter |

Future G2.84 must migrate or remove these test assumptions as part of the
retirement implementation.

## Current Verification

| Check | Result |
|---|---|
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short` | 5 passed |
| `pytest -o addopts= web/backend/tests/test_data_stocks_runtime_fallback.py -q --no-cov --tb=short` | 1 passed |
| `pytest -o addopts= web/backend/tests/test_market_api_integration.py -q --no-cov --tb=short` | 3 failed, 15 passed; failures are existing DB-dependent market overview failures against localhost:5438 |
| `pytest -o addopts= tests/backend/test_data_api_regression.py -q --no-cov --tb=short` | 3 failed; existing route expectation failures return 404 |

The failing tests are not introduced by this authorization packet. They are
recorded because they contain public getter patch points that a future G2.84
implementation may need to edit. Future G2.84 must not claim those files become
fully green unless it separately fixes their pre-existing failures inside an
approved scope.

## GitNexus Evidence

GitNexus impact for `get_data_source_factory` at current source state:

| Metric | Result |
|---|---|
| Risk | CRITICAL |
| Impacted count | 22 |
| Direct dependents | 21 |
| Processes affected | 12 |
| Process families | `Get_sources_health`, `Get_system_status_overview` |

GitNexus context still lists route/API callers and service helper callers that
the precise current-head text scan shows have been migrated. Treat this as a
stale-index/high-risk warning, not as proof of live route/API consumers.

G2.84 must still run fresh GitNexus impact/context before source edits and
staged `detect_changes(scope=staged)` before commit.

## Authorization Decision

Authorize a future G2.84 final retirement implementation only under the scope
below.

Allowed future source and test files:

- `web/backend/app/services/data_source_factory/data_source_factory.py`;
- `web/backend/app/services/data_source_factory/__init__.py`;
- `web/backend/tests/test_data_source_factory_lifecycle_di.py`;
- `web/backend/tests/test_market_api_integration.py`;
- `web/backend/tests/test_data_stocks_runtime_fallback.py`;
- `tests/backend/test_data_api_regression.py`.

Allowed future intent:

1. Remove the public `get_data_source_factory()` compatibility getter.
2. Remove its package re-export and `__all__` entry.
3. Update or remove tests that assert the old public getter exists.
4. Retarget package-level test monkeypatches to supported dependency seams.
5. Keep `get_data_source_factory_dependency` and private
   `_get_or_create_data_source_factory()` intact.

## Required Future G2.84 Gates

1. Read `architecture/STANDARDS.md`.
2. Run GitNexus impact/context for `get_data_source_factory`,
   `_get_or_create_data_source_factory`, and
   `get_data_source_factory_dependency`.
3. TDD RED: add or update a focused test proving the package no longer exports
   public `get_data_source_factory`.
4. Implement only the authorized retirement.
5. Run:
   - lifecycle DI tests;
   - stocks runtime fallback test;
   - health route conflicts test;
   - ruff and black on touched files;
   - OpenAPI smoke with root `.env` loaded.
6. For `test_market_api_integration.py` and
   `tests/backend/test_data_api_regression.py`, record whether existing
   unrelated failures remain unchanged. Do not convert their current baseline
   failures into new G2.84 success claims.
7. Text scan must show:
   - production public getter hits `0`;
   - package export lines `0`;
   - route/API direct calls `0`;
   - no `get_data_source_factory` public getter patch points remain.
8. Run staged GitNexus `detect_changes(scope=staged)`.

## Forbidden Future G2.84 Scope

G2.84 must not:

- edit route modules under `web/backend/app/api/**`;
- edit route paths, response models, response shapes, or OpenAPI exposure;
- edit frontend files;
- edit runtime or PM2 scripts;
- edit OpenSpec changes;
- change GitHub issue labels;
- change `DATA_SOURCE_FACTORY_STATE_KEY`;
- remove `get_data_source_factory_dependency`;
- remove `_get_or_create_data_source_factory`;
- fix unrelated DB-dependent or historical-route test failures without a
  separate approved scope.

## Stop Conditions

Stop before implementation or commit if:

- any live production consumer outside the allowed source files is found;
- deleting the public getter requires route/API, OpenAPI, frontend, runtime, or
  OpenSpec changes;
- the future implementation needs to fix unrelated market integration or
  historical-route regression failures;
- GitNexus reports a new HIGH/CRITICAL impact outside the known stale-index
  route-handler set and DataSourceFactory initialization paths.

## Next Gate

Human review / PR merge decision for this G2.83 authorization.

If accepted, create a separate G2.84 source implementation branch for final
public getter and package export retirement. Do not implement G2.84 in this
authorization packet.
