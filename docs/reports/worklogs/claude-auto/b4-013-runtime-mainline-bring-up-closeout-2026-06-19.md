# B4.013 Runtime Mainline Bring-Up Closeout

Date: 2026-06-19
Program: `.governance/programs/artdeco-web-design-governance`
FUNCTION_TREE node: `b4-013-runtime-mainline-bring-up`
Status: closeout-prepared
Edit class: governance closeout only, no source edits

## Scope

B4.013 was the runtime-mainline recovery and OpenStock consumer-integration line for MyStocks.

The governing direction is fixed:

- OpenStock owns provider runtime, data-source adapters, provider retries, category execution, and provider-specific normalization.
- MyStocks owns business routes, compatibility response shapes, persistence/read models, and backend consumer integration with OpenStock.
- MyStocks must not add provider fallback, provider SDK calls, provider adapters, frontend-to-OpenStock direct calls, or OpenStock repository edits from this line.

## Mainline Results

The line moved from cleanup-oriented drift management back to P0 runtime continuity and visible data-flow repair.

Completed runtime/governance results:

- Local methodology was aligned with the mainline-alignment standard: P0 runtime continuity outranks cleanup, archive work, formatting-only fixes, and future-feature polishing.
- FUNCTION_TREE execution was locked to the active P0 runtime node, with B4.007-B4.012 residual cleanup lines treated as backlog until the mainline cycle closes.
- OpenStock consumer boundary was documented and enforced: MyStocks only consumes OpenStock through backend integration.
- MyStocks-side OpenStock backend consumer contracts were expanded and tested for the market data categories needed by the current runtime path.
- Market runtime refresh paths were migrated where OpenStock had provider-backed contracts:
  - `ETF_SPOT`
  - `BLOCK_TRADE`
  - `DRAGON_TIGER`
  - `FUND_FLOW` for symbol-scoped `今日`
  - `SECTOR_FUND_FLOW` for `行业` / `概念` / `地域` with `今日` / `5日` / `10日`
- Query runtime fallback for sector fund flow was standardized:
  - persisted read-model data remains first priority;
  - OpenStock is used only for supported sector slices when runtime fallback is enabled and local data is unavailable;
  - unsupported `3日` remains on the existing legacy path.

Compatibility preserved:

- Existing MyStocks API routes and frontend-facing response contracts remain the compatibility boundary.
- Chinese `sector_type` and `timeframe` values are preserved for sector fund-flow read models and query responses.
- Local current-date `trade_date` compatibility is preserved for OpenStock-derived refresh/query fallback rows where required by the existing MyStocks shape.
- `sector_code` uses OpenStock data when present and falls back to `sector_name` for compatibility.
- Unsupported stock-level all-market/multi-day `FUND_FLOW` slices were not synthesized in MyStocks.

## Verification Evidence

Latest focused pre-closeout verification:

```text
python -m py_compile web/backend/app/services/openstock_client.py \
  web/backend/app/services/market_data_service_v2.py \
  tests/backend/test_openstock_client.py \
  web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py \
  web/backend/tests/services/test_market_data_service_v2_runtime_fallback.py

python -m ruff check web/backend/app/services/openstock_client.py \
  web/backend/app/services/market_data_service_v2.py \
  tests/backend/test_openstock_client.py \
  web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py \
  web/backend/tests/services/test_market_data_service_v2_runtime_fallback.py

python -m pytest web/backend/tests/services/test_market_data_service_v2_runtime_fallback.py \
  web/backend/tests/services/test_market_data_service_v2_openstock_refresh.py \
  tests/backend/test_openstock_client.py -q --no-cov
```

Result:

- `py_compile`: passed.
- `ruff`: passed.
- Focused pytest: `19 passed`.

Prior slice evidence recorded during B4.013:

- `B4.013-M3a-A`: OpenStock consumer category expansion closeout.
- `B4.013-M3a-B1`: ETF refresh migration closeout.
- `B4.013-M3a-B2`: block trade and dragon tiger refresh migration closeout.
- `B4.013-M3a-B3a`: symbol-scoped `FUND_FLOW` today refresh migration closeout.
- `B4.013-M3a-B3b`: all-market/multi-day `FUND_FLOW` contract-boundary decision.
- `B4.013-M3a-B4a`: `SECTOR_FUND_FLOW` supported refresh migration closeout.
- `B4.013-M3a-B5a`: sector query runtime fallback cleanup closeout.

## Remaining Backlog / Next-Cycle Inputs

The following nodes remain open as historical evidence or future-cycle inputs. They are not part of this parent closeout implementation package:

- `b4-013-m1c-mainline-route-runtime-blockers-audit`: decision-prepared; next step is a separate authorization package if route runtime blockers are promoted into the next P0 cycle.
- `b4-013-m1e-backend-api-residual-slow-endpoint-attribution-audit`: blocked; keep as attribution backlog until the blocking condition is explicitly removed.
- `b4-013-m1e-openstock-data-source-boundary-audit`: decision-prepared; preserved as OpenStock/MyStocks boundary evidence.
- `b4-013-m1e2-openstock-consumer-boundary-audit`: decision-prepared; preserved as consumer-boundary evidence.
- `b4-013-m1e3-openstock-consumer-openspec-proposal`: decision-prepared; preserved as proposal evidence.
- `b4-013-m2e3-openstock-category-coverage-audit`: decision-prepared; preserved as category-coverage evidence.
- `b4-013-m2e4-openstock-contract-gap-handoff`: decision-prepared; preserved as OpenStock handoff/backlog evidence.
- `b4-013-m3a-b3-fund-flow-refresh-openstock-audit`: decision-prepared; superseded operationally by B3a plus B3b, retained as audit evidence.
- `b4-013-m3a-b3b-fund-flow-all-market-multi-day-decision`: decision-prepared; remains the active boundary decision for unsupported stock-level all-market/multi-day `FUND_FLOW`.

Critical retained decision:

MyStocks must not migrate or synthesize `symbol=None`, `3日` / `5日` / `10日` stock-level `FUND_FLOW` all-market/multi-day slices until OpenStock exposes and validates a provider-backed contract such as a dedicated stock fund-flow ranking category. This is an OpenStock provider-contract gap, not a MyStocks-side data-generation task.

## Closeout Decision

B4.013 can close as a completed mainline runtime cycle because:

- The MyStocks/OpenStock responsibility boundary is explicit and enforced.
- MyStocks-side consumer integration has landed for the currently supported OpenStock market categories.
- Refresh and runtime fallback behavior now use OpenStock where contracts exist and retain legacy behavior where contracts do not.
- The remaining open decision nodes are documented as future-cycle inputs or provider-contract backlog and do not require additional B4.013 source changes.

Recommended next queue after closure:

1. Start a new no-source P0 mainline cycle from the highest-impact visible runtime gap, likely route/runtime blockers or residual slow endpoint attribution.
2. Keep OpenStock provider-contract gaps out of MyStocks implementation until OpenStock exposes tested provider contracts.
3. Continue using the fixed cycle: no-source truth audit -> scoped authorization -> TDD implementation -> focused/full gates -> FUNCTION_TREE closeout.
