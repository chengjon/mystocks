# Backend Data Quality DataSourceFactory Route Migration Authorization - 2026-05-24

> **历史总结说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: ready for review

Workline: G2.61b data-quality route migration authorization

Base branch: `wip/root-dirty-20260403`

Current HEAD: `ee2c74f3c8e1c4f690d2a1737db29c97c39a54d2`

## Scope Boundary

G2.61b is a governance and implementation-authorization packet only.

This packet does not modify backend source code, tests, route paths, response
contracts, OpenAPI exposure, generated clients, OpenSpec files, issue labels,
runtime processes, or PM2 state.

Its purpose is to authorize a future path-limited implementation branch for the
first DataSourceFactory route consumer migration after the G2.61a provider seam
was implemented and closed out.

## Upstream State

Accepted upstream facts:

- PR `#202` merged the provider seam at
  `0aadb27801c86e97e65ffdb4426276e1bd14c352`.
- PR `#203` merged the closeout/current-head refresh at
  `ee2c74f3c8e1c4f690d2a1737db29c97c39a54d2`.
- `DATA_SOURCE_FACTORY_STATE_KEY`, `install_data_source_factory(app,
  factory=None)`, and `get_data_source_factory_dependency(request)` exist in
  `web/backend/app/services/data_source_factory/data_source_factory.py`.
- `get_data_source_factory()` and `_global_factory` remain preserved as
  compatibility surfaces.
- No API route consumer has been migrated yet.

## Current Evidence

Static current-head scan reports:

- API files scanned: `219`
- Direct `get_data_source_factory()` API calls: `17`
- API files containing direct calls: `9`
- `get_data_source_factory_dependency` API refs: `0`

Consumer matrix:

| File | Calls | Lines | Disposition |
|---|---:|---|---|
| `web/backend/app/api/data_quality.py` | 2 | `58`, `369` | first route migration candidate |
| `web/backend/app/api/data/financial.py` | 1 | `69` | later domain route batch |
| `web/backend/app/api/data/futures.py` | 2 | `91`, `114` | later domain route batch |
| `web/backend/app/api/data/kline.py` | 2 | `145`, `245` | later domain route batch |
| `web/backend/app/api/data/lhb.py` | 2 | `90`, `115` | later domain route batch |
| `web/backend/app/api/data/margin.py` | 3 | `104`, `128`, `150` | later domain route batch |
| `web/backend/app/api/data/market.py` | 1 | `98` | later domain route batch |
| `web/backend/app/api/data/stocks.py` | 2 | `269`, `371` | later domain route batch |
| `web/backend/app/api/market/market_data_request.py` | 2 | `134`, `427` | later market route batch |

## Selected Candidate

The selected first route consumer is:

```text
web/backend/app/api/data_quality.py
```

It has exactly two direct calls:

| Function | Line | Current statement |
|---|---:|---|
| `get_sources_health` | `58` | `factory = await get_data_source_factory()` |
| `get_system_status_overview` | `369` | `factory = await get_data_source_factory()` |

Both routes already return `UnifiedResponse[Dict[str, Any]]`. The future
implementation must not change route paths, response models, OpenAPI exposure,
or response shape.

## Package Export Decision

Current package export state:

- `web/backend/app/services/data_source_factory/__init__.py` exports
  `get_data_source_factory`.
- It does not export `get_data_source_factory_dependency`.
- It does not export `install_data_source_factory`.

Recommended future disposition:

- Authorize a package-level re-export of `get_data_source_factory_dependency`
  in the same path-limited implementation branch as the `data_quality.py`
  migration.
- Keep existing route imports at the package boundary:
  `from app.services.data_source_factory import ...`.
- Do not force route modules to import from the implementation file unless a
  later reviewed packet explicitly chooses that style.

This keeps the provider seam discoverable at the same package boundary already
used by route consumers.

## Verification

Executed in the G2.61b worktree at current HEAD
`ee2c74f3c8e1c4f690d2a1737db29c97c39a54d2`:

| Check | Result |
|---|---|
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short` | `4 passed` |
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_source_factory.py -q --no-cov --tb=short` | `38 passed` |
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_quality_mock_configuration.py -q --no-cov --tb=short` | `2 passed` |
| `ruff check` on provider/data-quality touched candidate files | passed |
| app import / OpenAPI smoke with non-secret test env | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0` |

The first app smoke without the complete required environment failed before
import with missing environment variables. The successful smoke used non-secret
test defaults for `POSTGRESQL_*`, backend ports, TDengine, Redis, JWT, and app
secret settings, with both project root and `web/backend` on `sys.path`.

## Authorized Future G2.61c Scope

If this packet is accepted, a separate implementation branch may be created for
G2.61c with this exact purpose:

> Migrate the two `data_quality.py` DataSourceFactory consumers from direct
> compatibility getter calls to the app-state provider dependency while
> preserving route contracts and compatibility surfaces.

Allowed future source/test paths:

- `web/backend/app/services/data_source_factory/__init__.py`
- `web/backend/app/api/data_quality.py`
- `web/backend/tests/test_data_quality_mock_configuration.py`
- `web/backend/tests/test_data_source_factory_lifecycle_di.py`

Allowed future governance paths:

- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/data-quality-data-source-factory-route-migration-implementation-*.json`
- `docs/reports/quality/backend-data-quality-data-source-factory-route-migration-implementation-*.md`
- `governance/mainline/task-cards/pr-*.yaml`

## Future Acceptance Criteria

The future implementation must satisfy all of the following:

- `web/backend/app/api/data_quality.py` direct
  `get_data_source_factory()` calls reduce from `2` to `0`.
- Total API direct `get_data_source_factory()` calls reduce from `17` to `15`.
- `data_quality.py` uses `Depends(get_data_source_factory_dependency)` or an
  explicitly documented equivalent reviewed in the implementation packet.
- Package-level imports remain valid; if `data_quality.py` imports the
  dependency from `app.services.data_source_factory`, `__init__.py` must export
  it.
- `get_data_source_factory()` and `_global_factory` remain preserved.
- Route paths, response models, OpenAPI path count, duplicate operation ID count,
  and response shapes remain unchanged.
- The future branch must run GitNexus impact before source edits and
  `gitnexus detect-changes --scope staged` before commit.

## Non-Goals

G2.61b and the future G2.61c route migration do not authorize:

- migrating the remaining `15` route/API direct calls;
- changing data source factory construction semantics;
- deleting `_global_factory` or `get_data_source_factory()`;
- changing OpenAPI exposure, route paths, response models, or response shape;
- touching frontend, generated clients, PM2/runtime process state, OpenSpec
  files, issue labels, docs/API examples, or unrelated service seams.

## Decision

Approve `web/backend/app/api/data_quality.py` as the first route migration
candidate after the DataSourceFactory provider seam.

Do not edit route code under this G2.61b packet. If accepted, create a separate
G2.61c implementation branch with the path and acceptance boundaries above.

## Next Gate

Human review of this G2.61b authorization PR.

If accepted and merged, open G2.61c as a path-limited implementation branch for
`data_quality.py` only. The remaining route consumers stay locked for later
consumer-specific authorization packets.
