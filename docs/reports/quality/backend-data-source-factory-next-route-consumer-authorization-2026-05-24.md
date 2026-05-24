# Backend DataSourceFactory Next Route Consumer Authorization - 2026-05-24

> **历史总结说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: ready for review

Workline: G2.62 next DataSourceFactory route consumer authorization

Base branch: `wip/root-dirty-20260403`

Current HEAD: `fcc438de0965f80af7d485525fb494511976595b`

## Scope Boundary

G2.62 is a governance and implementation-authorization packet only.

This packet does not modify backend source code, tests, route paths, response
contracts, OpenAPI exposure, generated clients, OpenSpec files, issue labels,
runtime processes, or PM2 state.

## Upstream State

G2.61c closeout was merged by PR `#206` at
`fcc438de0965f80af7d485525fb494511976595b`.

Accepted current-head facts:

- `data_quality.py` direct DataSourceFactory calls remain `0`.
- Total API direct `get_data_source_factory()` calls remain `15`.
- Remaining direct consumers are locked until individually authorized.

## Candidate Comparison

The next search is intentionally limited to one-call consumers.

| Candidate | Direct calls | Handler | Route functions in file | Disposition |
|---|---:|---|---:|---|
| `web/backend/app/api/data/financial.py` | 1 | `get_financial_data` | 1 | selected for future G2.63 |
| `web/backend/app/api/data/market.py` | 1 | `get_market_overview` | 4 | locked for later packet |

`financial.py` is selected because it has the narrower route surface: one route
function and one direct factory call. `market.py` also has one direct call, but
the file carries a broader market route/test surface, so it should wait for a
separate route-specific packet.

## Selected Future Scope

If this packet is accepted, a future G2.63 implementation branch may migrate:

```text
web/backend/app/api/data/financial.py
```

Selected call site:

| Handler | Line | Current statement |
|---|---:|---|
| `get_financial_data` | `69` | `factory = await get_data_source_factory()` |

Allowed future source/test paths:

- `web/backend/app/api/data/financial.py`
- `web/backend/tests/test_data_source_factory_lifecycle_di.py`
- `web/backend/tests/test_health_route_conflicts.py`

Allowed future governance paths:

- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/data-source-factory-financial-route-migration-implementation-*.json`
- `docs/reports/quality/backend-data-source-factory-financial-route-migration-implementation-*.md`
- `governance/mainline/task-cards/pr-*.yaml`

## Future Acceptance Criteria

The future G2.63 implementation must satisfy all of the following:

- `web/backend/app/api/data/financial.py` direct
  `get_data_source_factory()` calls reduce from `1` to `0`.
- Total API direct `get_data_source_factory()` calls reduce from `15` to `14`.
- `get_financial_data` uses `Depends(get_data_source_factory_dependency)` or an
  explicitly documented equivalent reviewed in the implementation packet.
- Route path, query parameters, response shape, OpenAPI path count, and duplicate
  operation ID count remain unchanged.
- `get_data_source_factory()` and `_global_factory` remain preserved.
- The future branch must run GitNexus impact before source edits and
  `gitnexus detect-changes --scope staged` before commit.

## Non-Goals

G2.62 and the future G2.63 implementation do not authorize:

- migrating `web/backend/app/api/data/market.py`;
- migrating the other remaining `14` direct route/API consumers;
- deleting `get_data_source_factory()` or `_global_factory`;
- changing route paths, response models, response shape, OpenAPI exposure,
  frontend code, generated clients, PM2/runtime process state, OpenSpec files,
  issue labels, or docs/API examples.

## Decision

Authorize `web/backend/app/api/data/financial.py` as the next single-consumer
DataSourceFactory route migration candidate.

Do not edit route code under this G2.62 packet. If accepted, create a separate
G2.63 implementation branch with the path and acceptance boundaries above.

## Next Gate

Human review of this G2.62 authorization PR.

If accepted and merged, open G2.63 as a path-limited implementation branch for
`financial.py` only.
