# G2.241 Mock Data Manager Ownership / Runtime Seam Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: ownership decision for review
- Prepared at: `2026-05-29T22:22:46+08:00`
- Base HEAD checked: `70d75e77fa28fa8b9931fcdc4e89688478f8f1fc`
- Parent: G2.240, PR `#393`
- Source edit authority: none

Boundary note: this report records an ownership decision only. It does not
authorize source edits, test edits, route or OpenAPI changes, PM2 commands,
issue label changes, OpenSpec proposal creation, or PR merges.

## Decision

`get_mock_data_manager` is a mock data runtime facade and compatibility accessor.
It is not a route dependency provider, deletion candidate, thin wrapper, or
single-consumer implementation pilot.

The next gate should be G2.242, a no-source mock data manager provider/reset seam
authorization package. G2.241 does not authorize implementation.

## Current-HEAD Evidence

| Item | Result |
|---|---:|
| Definition count | 1 |
| Primary file | `web/backend/app/mock/mock_data/factory.py` |
| Factory file lines | 156 |
| Import lines in active scan roots | 16 |
| Call expressions in active scan roots | 27 |
| Active route-body calls | 0 |
| GitNexus impact sample | `CRITICAL`, 63 impacted, 27 direct, 4 processes, 8 modules |

Factory behavior:

- Uses an `app.main.mock_data_manager` runtime cache when present.
- Falls back to `_FallbackMockDataManager`.
- Exposes compatibility helper functions such as `get_dashboard_data`,
  `get_stocks_data`, `get_technical_data`, `get_wencai_data`,
  `get_strategy_data`, `get_monitoring_data`, and `get_backtest_data`.

## Consumer Matrix

| Bucket | Calls | Files | Current handling |
|---|---:|---:|---|
| API/helper fallback consumers | 8 | 6 | Keep as consumers; do not batch-migrate in G2.241 |
| Mock factory / fixture helpers | 9 | 2 | Owner surface; future provider/reset seam likely starts here |
| Active service adapters | 3 | 3 | Do not rewrite from this decision packet |
| Legacy/facade adapters | 3 | 3 | Defer behind future authorization and adapter ownership evidence |
| Tests | 4 | 3 | Preserve as verification consumers |

Representative API/helper consumers:

- `web/backend/app/api/market/_market_heatmap_router.py`
- `web/backend/app/api/market/market_data_request.py`
- `web/backend/app/api/stock_search/stock_search_support.py`
- `web/backend/app/api/strategy_management/_helpers.py`
- `web/backend/app/api/tradingview.py`
- `web/backend/app/api/wencai.py`

## Future Authorization Shape

If this decision is accepted, G2.242 should remain no-source and authorize only a
future bounded implementation shape.

Recommended future source shape if G2.242 is later accepted:

- Add an explicit provider/reset/test-double seam around the mock data manager
  runtime facade.
- Preserve the existing `get_mock_data_manager` compatibility accessor.
- Keep the first implementation scope limited to
  `web/backend/app/mock/mock_data/factory.py` plus focused mock-data manager
  tests.

Non-goals for the future authorization:

- Do not migrate all API/helper consumers in one batch.
- Do not rewrite adapter classes.
- Do not remove `get_mock_data_manager`.
- Do not change mock response shapes.
- Do not change route paths, OpenAPI exposure, frontend, config, scripts, or
  OpenSpec.

## Next Gate

If G2.241 is accepted:

- start G2.242 as a no-source mock data manager provider/reset seam
  authorization package
- keep G2.242 focused on authorizing a future bounded source lane
- do not implement source changes from G2.241

## Verification Targets

- generated JSON parses
- `steward-index.json` parses
- Markdown governance gate has 0 errors
- app/OpenAPI smoke remains `routes=548`, `paths=500`
- `openspec validate migrate-backend-singletons-to-lifecycle-di --strict` passes
- mainline scope gate reports only governance/documentation files
- GitNexus detect changes reports docs-only low risk
