# B4.013-M2-E2 OpenStock Market Route Migration Closeout

Date: 2026-06-16
Branch: `wip/root-dirty-20260403`
Implementation commits:

- `6b6207f07 B4.013-M2-E2: migrate market routes to OpenStock consumer`
- `3ce1103de B4.013-M2-E2b: reconcile market route import lint`

FUNCTION_TREE nodes:

- `b4-013-m2e2-openstock-market-route-migration-audit`
- `b4-013-m2e2a-openstock-existing-market-api-tests`
- `b4-013-m2e2b-openstock-route-import-lint-reconciliation`

## Summary

The MyStocks backend compatibility routes for realtime quotes and K-line data now consume OpenStock through the backend consumer client instead of invoking MyStocks local provider/data-source acquisition paths.

Migrated routes:

- `GET /api/v1/market/quotes`
- `GET /api/v1/market/kline`

Preserved public compatibility:

- Route paths remain unchanged.
- Frontend continues calling MyStocks routes, not OpenStock directly.
- `quotes` response keeps the existing `create_success_response(...)` envelope and `quotes/total/symbols/source/endpoint` payload shape.
- `kline` response keeps `success`, `stock_code`, `stock_name`, `period`, `adjust`, `data`, `count`, and `timestamp`.
- Existing date validation, kline minimum-row validation, and route-level error envelopes remain in MyStocks.

## Boundary

This package keeps the data-source provider split intact:

- OpenStock owns provider acquisition, provider routing, provider health, upstream timeout/fallback/circuit-breaker behavior, and provider error mapping.
- MyStocks owns compatibility routes, consumer integration, and response normalization.
- No provider adapters, `src/data_sources`, `data_source_factory`, frontend code, or `/opt/claude/openstock` files were modified.

## Implementation Notes

`web/backend/app/api/market/market_data_request.py` now has a route-local OpenStock client factory:

- `OPENSTOCK_BASE_URL`
- `OPENSTOCK_API_BASE_URL`
- default `http://localhost:8050`
- optional `OPENSTOCK_TIMEOUT_SECONDS`

Route calls:

- `quotes`: `OpenStockClient.fetch("REALTIME_QUOTES", params={"symbols": symbol_list})`
- `kline`: `OpenStockClient.fetch("KLINES", params={"symbol", "period", "adjust", "start_date", "end_date"})`

The route deliberately uses generic `fetch("KLINES", ...)` rather than `fetch_bars(...)` because the existing MyStocks route exposes `adjust`, `start_date`, and `end_date`.

## Tests

Added:

- `web/backend/tests/test_openstock_market_routes.py`

Updated:

- `web/backend/tests/test_market_api.py`

Focused tests cover:

- `quotes` no longer calls `data_source_factory`.
- `kline` no longer calls `stock_search_service`.
- OpenStock route response data is normalized into existing MyStocks public response shapes.
- Existing `TestStockQuotesAPI` tests mock the OpenStock consumer client instead of attempting a real OpenStock network call.
- Existing OpenStock client tests remain green.

## Import Lint Reconciliation

Before implementation, `web/backend/app/api/market/market_data_request.py` had a pre-existing worktree hunk deleting two unused imports:

- `_error_response_spec`
- `_success_response_spec`

The implementation commit intentionally did not mix that hunk into the route migration package. A separate child package, `B4.013-M2-E2b`, then removed only those two unused imports so clean HEAD ruff checks pass. No route behavior changed in that child package.

## Verification

Post-implementation verification:

- `python -m py_compile web/backend/app/api/market/market_data_request.py web/backend/tests/test_openstock_market_routes.py web/backend/tests/test_market_api.py tests/backend/test_openstock_client.py`: passed.
- `python -m ruff check --no-fix web/backend/app/api/market/market_data_request.py web/backend/tests/test_openstock_market_routes.py web/backend/tests/test_market_api.py tests/backend/test_openstock_client.py`: passed.
- `pytest web/backend/tests/test_openstock_market_routes.py web/backend/tests/test_market_api.py::TestStockQuotesAPI tests/backend/test_openstock_client.py -q --no-cov`: 10 passed.
- `openspec validate externalize-data-source-provider-to-openstock --strict`: valid.
- GitNexus `verify-staged`: low risk during both implementation and import-reconciliation commits.
- GitNexus `detect-changes --scope staged`: low risk during both implementation and import-reconciliation commits.
- GitNexus post-commit analyze after `3ce1103de`: repository indexed successfully, `222,497 nodes | 279,392 edges | 2928 clusters | 300 flows`.
- OPENDOG verification: blockers `0`.

## Residual State

Target source and test files are clean after `3ce1103de`.

Known unrelated untracked governance files remain outside this package and were not staged:

- `.governance/programs/artdeco-web-design-governance/cards/b4-012-m3a-c5-other-adapter-compatibility-tests-authorization.yaml`
- `.governance/programs/artdeco-web-design-governance/cards/b4-013-m1a-watchlist-runtime-import-reexport.yaml`

## Decision

B4.013-M2-E2 is complete from the MyStocks side for the first ready market compatibility routes. The next OpenStock consumer migration package should remain category-based and should not add provider behavior back into MyStocks.
