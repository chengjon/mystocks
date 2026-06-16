# B4.013-M2-E2 OpenStock Market Route Migration No-Source Audit

Date: 2026-06-16
Branch: `wip/root-dirty-20260403`
Baseline HEAD: `c64f6b6cd B4.013-M2-E1: close OpenStock consumer client node`
FUNCTION_TREE node: `b4-013-m2e2-openstock-market-route-migration-audit`
Edit mode: no-source audit only

## Scope

This audit covers only the first ready market compatibility routes for the OpenStock consumer migration:

- `GET /api/v1/market/quotes`
- `GET /api/v1/market/kline`

The audit does not authorize source edits. It does not modify backend routes, services, provider adapters, frontend callers, OpenSpec files, or `/opt/claude/openstock`.

## Architecture Boundary

The active OpenSpec direction is that `/opt/claude/openstock` owns provider adapters, upstream acquisition, provider health, provider route decisions, runtime cache state, provider circuit-breaker state, REST pull data, and market-stream production.

`mystocks_spec` remains the business application and compatibility API owner. It should:

- keep existing frontend-facing MyStocks routes stable,
- call OpenStock through the backend consumer client for approved provider-backed categories,
- normalize OpenStock runtime envelopes into existing route response shapes,
- avoid adding or expanding local provider SDK calls, data-source factories, or provider adapters.

## Current Route Truth

Route registration is still stable:

| Public route | Registry source | Current route function | Current provider dependency | Frontend compatibility expectation |
| --- | --- | --- | --- | --- |
| `GET /api/v1/market/quotes` | `web/backend/app/router_registry.py` + `VERSION_MAPPING["market"]["prefix"] == "/api/v1/market"` | `get_market_quotes` in `web/backend/app/api/market/market_data_request.py` | `get_data_source_factory().get_data("market", "quotes", {"symbols": symbol_list})` | Frontend calls `/v1/market/quotes` and consumes `quotes`, `total`, `symbols`, `source`, `endpoint`. |
| `GET /api/v1/market/kline` | `web/backend/app/router_registry.py` + `VERSION_MAPPING["market"]["prefix"] == "/api/v1/market"` | `get_kline_data` in `web/backend/app/api/market/market_data_request.py` | `get_stock_search_service().get_a_stock_kline(...)` under the current `market_data` circuit-breaker wrapper | Frontend calls `/v1/market/kline` and consumes the current route payload, including `success`, `stock_code`, `stock_name`, `period`, `adjust`, `data`, `count`, and `timestamp`. |

The target route file currently has an unrelated external dirty state:

- `M web/backend/app/api/market/market_data_request.py`
- `git diff --numstat`: `0 insertions / 2 deletions`

The two audited functions still use the same provider-facing dependencies as `HEAD`. A future source phase must reconcile this pre-existing dirty file explicitly before editing and must not overwrite or stage unrelated changes.

## OpenStock Consumer Readiness

`web/backend/app/services/openstock_client.py` is now available from B4.013-M2-E1 and provides:

- `OpenStockClient.fetch(data_category, params=..., request_id=...)`
- `OpenStockClient.fetch_bars(symbol=..., period="day", count=100, request_id=...)`
- supported categories: `REALTIME_QUOTES`, `KLINES`
- typed failures: provider unavailable, unsupported category, timeout, invalid response
- metadata preservation: `source`, `endpoint_name`, `data_category`, `request_id`, `route_decision_id`, `latency_ms`, `staleness_ms`, `raw`

For this route migration, the generic `fetch(...)` method is the safest fit:

- `quotes` can call `fetch("REALTIME_QUOTES", params={"symbols": symbol_list})`.
- `kline` should call `fetch("KLINES", params={"symbol": stock_code, "period": period, "adjust": adjust, "start_date": start_date, "end_date": end_date})`.

`fetch_bars(...)` is not the recommended route migration primitive for `GET /api/v1/market/kline` because it currently does not accept `adjust`, `start_date`, or `end_date`. Using generic `fetch("KLINES", ...)` preserves the public MyStocks route parameters without reopening the client in this batch.

## Migration Matrix

| Route | OpenStock category | Proposed source action | Compatibility adapter requirement | Test focus | Risk |
| --- | --- | --- | --- | --- | --- |
| `/api/v1/market/quotes` | `REALTIME_QUOTES` | Replace route-local `data_source_factory` call with `OpenStockClient.fetch(...)`. Preserve default symbol behavior and `@cache_response("real_time_quotes", ttl=10)`. | Convert `OpenStockFetchResult` into the existing `build_quotes_response_payload(...)` input shape. Map `endpoint_name` to existing `endpoint` if needed. Preserve fallback behavior for empty rows unless explicitly changed. | Route returns existing public keys; symbols default and explicit symbol list both work; OpenStock metadata is normalized without leaking raw provider errors. | Low to medium. GitNexus reports LOW blast radius, but runtime compatibility depends on response-shape adapter tests. |
| `/api/v1/market/kline` | `KLINES` | Replace route-local `stock_search_service.get_a_stock_kline(...)` acquisition with `OpenStockClient.fetch("KLINES", params=...)`. Preserve existing parameter validation and public error envelope. | Normalize OpenStock data into current route keys: `stock_code`, `stock_name`, `period`, `adjust`, `data`, `count`, then add current `success` and `timestamp`. Decide whether the current MyStocks `market_data` circuit-breaker wrapper remains as a route-level guard or is removed in a separately authorized behavior change. | Date validation remains local; invalid date still returns validation response; happy path preserves payload keys; OpenStock timeout/unavailable maps to existing BusinessException/route error behavior. | Medium. Public route shape and current local circuit-breaker behavior make this more sensitive than `quotes`. |

## Explicit Non-Goals

The next implementation batch must not:

- modify `src/adapters/**`, `src/data_sources/**`, or provider SDK integration,
- expand `web/backend/app/services/data_source_factory*` or split adapter services,
- move provider acquisition logic back into MyStocks,
- add direct frontend-to-OpenStock calls,
- touch `/opt/claude/openstock/**`,
- migrate unsupported categories such as sector fund-flow, LHB, block-trade, ETF refresh, or AkShare compatibility routes,
- change strategy, trade, risk, portfolio, or persisted read-model workflows,
- stage the existing unrelated dirty edits in `market_data_request.py` unless explicitly reconciled in the source batch.

## Source Authorization Recommendation

Recommended next node: `B4.013-M2-E2 OpenStock market compatibility route migration implementation`.

Recommended allowed paths:

- `web/backend/app/api/market/market_data_request.py`
- `web/backend/app/services/openstock_client.py` only if a minimal config/factory hook is required after implementation design review
- one focused backend route test file, preferably under `tests/backend/` or `web/backend/tests/`, selected after matching the existing FastAPI test fixture pattern
- closeout worklog under `docs/reports/worklogs/claude-auto/`
- FUNCTION_TREE governance files generated by helper commands

Recommended forbidden paths:

- `src/adapters/**`
- `src/data_sources/**`
- `web/backend/app/services/data_source_factory*`
- `web/backend/app/services/adapters_split/**`
- `web/backend/app/services/data_service.py`
- `web/frontend/**`
- `/opt/claude/openstock/**`
- OpenSpec provider-gap work outside the approved compatibility-route scope
- any external dirty files

Recommended gates:

- GitNexus impact for `get_market_quotes`, `get_kline_data`, and any edited OpenStock client/config symbol
- `python -m py_compile` for edited Python files
- `python -m ruff check` for edited Python files
- focused backend pytest for route compatibility and OpenStock error mapping
- existing OpenStock client unit test remains green
- `openspec validate externalize-data-source-provider-to-openstock --strict`
- GitNexus `verify-staged` and staged `detect-changes`
- OPENDOG verification shows no new blockers
- staged files exactly match the approved source batch

## Evidence

GitNexus impact checks:

- `get_market_quotes`: LOW risk, impacted count 0, no indexed processes affected.
- `get_kline_data` disambiguated to `web/backend/app/api/market/market_data_request.py`: LOW risk, impacted count 0, no indexed processes affected.
- `OpenStockClient`: LOW risk, impacted count 0, no indexed processes affected.

Existing tests and anchors found:

- `web/backend/tests/test_market_api.py` exercises `/api/v1/market/quotes`.
- `web/backend/tests/test_market_api_integration.py` references `/api/v1/market/kline` and factory monkeypatch patterns.
- `web/backend/tests/test_health_route_conflicts.py` records expected route parameters for both routes.
- `tests/e2e/backend-api-critical.spec.ts` includes `/api/v1/market/kline`.
- `tests/backend/test_openstock_client.py` covers the new consumer client.

## Decision

M2-E2 is ready for a narrow source authorization package, but implementation should not begin from this no-source audit alone.

The recommended implementation order is:

1. Reconcile the pre-existing dirty state of `web/backend/app/api/market/market_data_request.py` without overwriting external work.
2. Implement `quotes` migration first because the response adapter is already close to `build_quotes_response_payload(...)`.
3. Implement `kline` migration second with explicit response-shape tests and a clear decision on the existing route-level circuit-breaker wrapper.
4. Keep all provider ownership in OpenStock and keep MyStocks limited to consumer integration and public response compatibility.
