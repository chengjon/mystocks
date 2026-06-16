# B4.013-M2-E1 OpenStock Backend Consumer Client Closeout

## Scope

- Node: `b4-013-m2e1-openstock-backend-consumer-client-authorization`
- Authorization status at implementation start: `approved-for-implementation`
- Implemented only the MyStocks-side OpenStock consumer HTTP boundary.
- No route migration was performed.
- No provider runtime, provider adapter, SDK call, cache warmer, registry mutation, or OpenStock repository change was performed.

## Files

Changed implementation files:

- `web/backend/app/services/openstock_client.py`
- `tests/backend/test_openstock_client.py`
- `docs/reports/worklogs/claude-auto/b4-013-m2e1-openstock-backend-consumer-client-closeout-2026-06-16.md`

Governance state files changed by FUNCTION_TREE transitions and evidence refresh:

- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`

Explicitly untouched:

- `web/backend/app/api/market/market_data_request.py`
- `web/backend/app/api/v1/strategy/indicators.py`
- `web/backend/app/services/data_service.py`
- `web/backend/app/services/data_source_factory/**`
- `web/backend/app/services/adapters_split/**`
- `src/adapters/**`
- `src/data_sources/**`
- `web/frontend/**`
- `/opt/claude/openstock/**`

## Implementation Summary

Added `OpenStockClient` as an isolated async HTTP consumer client with:

- `OpenStockClientConfig`
- `OpenStockFetchResult`
- typed errors for provider unavailable, unsupported category, timeout, and invalid response
- `fetch()` for `/data/fetch`
- `fetch_bars()` for `/data/bars`
- `ready()` and `aclose()` lifecycle helpers
- local category whitelist for `REALTIME_QUOTES` and `KLINES`
- response metadata preservation for source, endpoint name, data category, request ID, route decision ID, latency, and staleness

The client normalizes OpenStock runtime failures into MyStocks service errors and preserves request/correlation identifiers without exposing raw provider stack details.

## TDD Evidence

Red test:

```bash
pytest tests/backend/test_openstock_client.py -q
```

Result:

- exit code `2`
- expected collection failure before implementation:
  - `ModuleNotFoundError: No module named 'web.backend.app.services.openstock_client'`

Green focused test:

```bash
pytest tests/backend/test_openstock_client.py -q --no-cov
```

Result:

- `5 passed in 0.36s`

Coverage note:

- Running the focused command without `--no-cov` collects the 5 target tests and they pass, but `tests/pytest.ini` enforces repo-wide `--cov-fail-under=80`, producing exit code `2` for this single-file run because total repository coverage is intentionally not measured by this focused batch.
- This is a coverage configuration effect, not an OpenStock client test failure.

## Static Validation

```bash
python -m py_compile web/backend/app/services/openstock_client.py tests/backend/test_openstock_client.py
```

Result: passed with no output.

```bash
python -m ruff check web/backend/app/services/openstock_client.py tests/backend/test_openstock_client.py
```

Result: `All checks passed!`

## Boundary Result

- `LHB` and other non-whitelisted categories are rejected before any HTTP request is sent from MyStocks.
- `REALTIME_QUOTES` and `KLINES` are the only M2-E1 supported OpenStock consumer categories.
- Existing MyStocks public routes remain unchanged and are deferred to B4.013-M2-E2.
- Provider category gaps and provider implementation remain outside this repository and belong to the separate OpenStock track.
