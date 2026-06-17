# B4.013-M3a-A OpenStock consumer category contract closeout

Date: 2026-06-18
Repository: `/opt/claude/mystocks_spec`
Commit: `42f31b8db B4.013-M3a-A: expand OpenStock consumer categories`

## Scope

This implementation expanded only the MyStocks backend OpenStock consumer contract. It did not add provider/data-source implementation to MyStocks.

Changed runtime/test files:

- `web/backend/app/services/openstock_client.py`
- `tests/backend/test_openstock_client.py`

Governance metadata was updated for the corresponding FUNCTION_TREE node and active gate.

## Behavior landed

`OpenStockClientConfig` now allows the OpenStock categories required for later MyStocks `market_v2` refresh migration:

- `FUND_FLOW`
- `SECTOR_FUND_FLOW`
- `DRAGON_TIGER`
- `BLOCK_TRADE`
- `ETF_SPOT`

The client still preserves the existing public behavior:

- `REALTIME_QUOTES` and `KLINES` remain supported.
- unsupported categories still raise `OpenStockUnsupportedCategory` before any HTTP request is sent.
- no route, frontend, provider adapter, SDK fallback, or direct OpenStock frontend call was introduced.

## Verification

TDD red evidence:

- `pytest tests/backend/test_openstock_client.py -q --no-cov` failed before implementation with 5 failures for the new P0 categories being rejected by `_validate_category`.

Green evidence:

- `python -m py_compile web/backend/app/services/openstock_client.py tests/backend/test_openstock_client.py` passed.
- `python -m ruff check web/backend/app/services/openstock_client.py tests/backend/test_openstock_client.py` passed.
- `pytest tests/backend/test_openstock_client.py -q --no-cov` passed: 10 tests.
- `GitNexus verify-staged --repo mystocks` passed: risk low, affected processes 0.
- `GitNexus detect-changes --scope staged --repo mystocks` passed: risk low, affected processes 0.
- OPENDOG verification was fresh with trusted build/lint/test runs.
- post-commit `node .gitnexus/run.cjs analyze` completed and indexed `222,555 nodes | 279,453 edges | 2928 clusters | 300 flows`.

## Boundary confirmation

MyStocks remains a consumer and compatibility application only. OpenStock remains the provider/data-source runtime owner.

External dirty files were not touched or staged:

- `web/backend/app/api/market_v2.py`
- `docs/reports/worklogs/claude-auto/b4-013-m1a-watchlist-runtime-import-reexport-closeout-2026-06-16.md`
- `docs/reports/worklogs/claude-auto/b4-013-runtime-mainline-bring-up-plan-2026-06-15.md`

## Next step

The next source batch should be `B4.013-M3a-B market_v2 refresh acquisition migration`, after a fresh no-source mapping check for existing DB model fields and OpenStock category payload shapes.
