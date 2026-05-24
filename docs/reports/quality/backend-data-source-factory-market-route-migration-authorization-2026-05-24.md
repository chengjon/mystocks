# Backend DataSourceFactory Market Route Migration Authorization - 2026-05-24

> **历史总结说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: ready for review

Workline: G2.64 authorization-only packet

Base branch: `wip/root-dirty-20260403`

Current HEAD: `cfb98f079c488c7e33c270e44342408a0e10db44`

## Scope Boundary

This packet authorizes a future implementation branch only. It does not change
backend source code, tests, route paths, response contracts, OpenAPI exposure,
generated clients, OpenSpec files, issue labels, runtime process state, or PM2
state.

## Upstream State

G2.63 closeout is merged as PR `#209` at
`cfb98f079c488c7e33c270e44342408a0e10db44`.

Current-head route guard reports:

- API files scanned: `219`
- Direct `get_data_source_factory()` API calls: `14`
- `get_data_source_factory_dependency` API refs: `5`
- `market.py` direct refs: `1`
- `market.py` dependency refs: `0`

Remaining direct-call files:

| File | Calls |
|---|---:|
| `web/backend/app/api/data/futures.py` | 2 |
| `web/backend/app/api/data/kline.py` | 2 |
| `web/backend/app/api/data/lhb.py` | 2 |
| `web/backend/app/api/data/market.py` | 1 |
| `web/backend/app/api/data/margin.py` | 3 |
| `web/backend/app/api/data/stocks.py` | 2 |
| `web/backend/app/api/market/market_data_request.py` | 2 |

## Candidate Evidence

Selected future implementation candidate:

| Candidate | Direct calls | Handler | Route functions in file | Disposition |
|---|---:|---|---:|---|
| `web/backend/app/api/data/market.py` | 1 | `get_market_overview` | 4 | selected for future G2.65 |

The single direct call is:

| Line | Handler | Current call |
|---:|---|---|
| 98 | `get_market_overview` | `factory = await get_data_source_factory()` |

Route functions in `market.py`:

| Line | Function | Path |
|---:|---|---|
| 94 | `get_market_overview` | `/markets/overview` |
| 118 | `get_price_distribution` | `/markets/price-distribution` |
| 146 | `get_hot_industries` | `/markets/hot-industries` |
| 171 | `get_hot_concepts` | `/markets/hot-concepts` |

`market.py` is selected because it is now the remaining one-call
DataSourceFactory route consumer after the `financial.py` migration. It has a
broader route surface than `financial.py`, so the future implementation must
remain path-limited and test-gated.

## Candidate Style Baseline

Candidate file style checks currently expose existing debt:

| Check | Result |
|---|---|
| `ruff check web/backend/app/api/data/market.py web/backend/tests/test_health_route_conflicts.py web/backend/app/services/data_source_factory/__init__.py` | failed: `market.py` has three existing `E701` issues at lines `123`, `154`, `179` |
| `black --check web/backend/app/api/data/market.py web/backend/tests/test_health_route_conflicts.py web/backend/app/services/data_source_factory/__init__.py` | failed: `market.py` would be reformatted |

This G2.64 packet does not fix those lines. A future G2.65 implementation may
normalize formatting inside `web/backend/app/api/data/market.py` while migrating
the single factory call. No other file formatting cleanup is authorized by this
packet.

## Verification

Executed at current HEAD:

| Check | Result |
|---|---|
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov --tb=short` | `113 passed` |
| `PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov --tb=short` | `4 passed` |
| app import / OpenAPI smoke with non-secret test env | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0` |

The app/OpenAPI smoke still reports `warning_count=121`, including the existing
local GPU fallback warning for the NumPy/Numba mismatch.

## GitNexus Refresh

GitNexus was refreshed from a non-linked checkout:

- Repo: `g2-64-gitnexus-index-checkout`
- HEAD: `cfb98f079`
- `.git` kind: `directory`
- `gitnexus analyze` exit: `0`
- Nodes: `62656`
- Edges: `145824`
- Flows: `300`

Current-head upstream impact:

| Target | Risk | Impacted count | Direct | Processes affected |
|---|---|---:|---:|---:|
| `web/backend/app/api/data/market.py` | LOW | 1 | 1 | 0 |
| `get_data_source_factory_dependency` | LOW | 0 | 0 | 0 |

`get_market_overview` is an ambiguous symbol name in GitNexus because multiple
modules define a function with that name. For this packet, file-level
`market.py` impact is the authoritative risk signal.

## Future G2.65 Scope

If this packet is reviewed and merged, the future source branch may edit only:

- `web/backend/app/api/data/market.py`
- `web/backend/tests/test_health_route_conflicts.py`
- implementation evidence report and generated JSON
- the steward tree
- the future mainline task card

Expected future outcome:

- `market.py` direct factory refs: `1` -> `0`
- total direct API `get_data_source_factory()` calls: `14` -> `13`
- route paths unchanged
- response shape unchanged
- OpenAPI exposure unchanged
- `get_data_source_factory()` and `_global_factory` retained
- `market.py` formatting normalized enough for ruff/black touched-file gates

## Non-Goals

This packet and the future G2.65 implementation do not authorize:

- migrating any non-`market.py` route/API consumer;
- deleting `get_data_source_factory()` or `_global_factory`;
- changing route paths, response models, response shape, OpenAPI exposure,
  frontend code, generated clients, PM2/runtime process state, OpenSpec files,
  issue labels, or docs/API examples;
- broad formatting cleanup outside `web/backend/app/api/data/market.py`.

## Decision

Authorize `web/backend/app/api/data/market.py` as the next DataSourceFactory
route migration candidate.

Do not edit route code under this G2.64 packet. If accepted, create a separate
G2.65 implementation branch with the path, TDD, rollback, and style-debt
boundaries above.

## Next Gate

Human review of this G2.64 authorization PR.

If accepted and merged, open G2.65 as a path-limited implementation branch for
`market.py` only.
