# B4.013-M1-E OpenStock Data-Source Boundary Reset

Date: 2026-06-16
Mode: no-source boundary correction
Program: `artdeco-web-design-governance`

## User Direction

The current line is corrected to the previously intended architecture:

- `/opt/claude/openstock` owns data-source provider functionality.
- `mystocks_spec` must not keep expanding or repairing data-source provider behavior as if it were the provider system.
- `mystocks_spec` is responsible for integrating with the data-source system, requesting data, adapting response contracts, and supporting business workflows that consume the data.

## Immediate Governance Impact

The just-started M1-E backend slow-endpoint attribution work must not continue as a mystocks-internal provider repair track.

The endpoint evidence collected during M1-E remains useful only as boundary evidence:

- Some Dashboard calls still hit provider-like endpoints inside `mystocks_spec`.
- Direct AkShare/TDX/provider paths remain in `web/backend/app` and `src/adapters`.
- Those paths should be classified as compatibility or migration candidates, not as places to deepen data-provider behavior.

## OpenStock Evidence

`/opt/claude/openstock` exists as a separate Python project:

- HEAD observed: `c9b8ffb docs: add minimal docker fault guide`
- It has `pyproject.toml`.
- It contains runtime/provider-facing modules such as:
  - `openstock/app.py`
  - `openstock/runtime.py`
  - `openstock/fetching.py`
  - `openstock/market_stream.py`
  - `openstock/adapters/*`
- It has provider/runtime tests including:
  - `tests/test_akshare_runtime_pilot.py`
  - `tests/test_baostock_adapter.py`
  - `tests/test_eltdx_adapter.py`
  - `tests/test_market_stream_contract.py`
  - `tests/test_runtime_contract.py`

## Mystocks Boundary Evidence

`mystocks_spec` still contains provider-like implementation surfaces:

- `src/adapters/*`
- `src/data_sources/*`
- `web/backend/app/api/akshare_market/*`
- `web/backend/app/api/market/market_data_request.py`
- `web/backend/app/api/market_v2.py`

Examples observed during no-source evidence collection:

- `web/backend/app/api/akshare_market/fund_flow.py` directly exposes `/api/akshare/market/fund-flow/*`.
- `src/adapters/akshare/market_adapter/fund_flow.py` calls `ak.stock_fund_flow_big_deal()`.
- `web/backend/app/api/market/market_data_request.py` exposes `/api/v1/market/kline` and delegates to local stock-search data access.
- `web/backend/app/api/v1/strategy/indicators.py` computes indicators locally from local OHLCV loading.

These are not necessarily deleted immediately. They must be treated as migration inventory and compatibility boundaries.

## Correct Development Direction

Allowed future direction for `mystocks_spec`:

- Add or standardize an OpenStock consumer client.
- Define request/response contracts between mystocks and OpenStock.
- Adapt OpenStock responses into existing mystocks UI/business DTOs.
- Add consumer-side timeout, retry, cache-read, and degradation behavior.
- Keep Dashboard, strategy, trading, risk, and system views focused on consuming normalized data.
- Preserve temporary compatibility wrappers only when required for mainline continuity.

Forbidden direction for `mystocks_spec`:

- Add new AkShare/Tushare/Baostock/TDX provider integrations.
- Deepen provider retry/failover/crawl/cache ownership inside mystocks.
- Treat endpoint slowness by expanding mystocks provider logic.
- Introduce new data acquisition workflows that should live in OpenStock.
- Mix data-source provider repairs into frontend runtime governance batches.

Correct ownership for OpenStock:

- Provider adapters and provider credentials.
- External data acquisition.
- Provider retry/failover/rate-limit/circuit-breaker semantics.
- Provider-side caching/freshness.
- Runtime REST/WebSocket data contracts.
- Market stream production.

## Revised M1-E Decision

M1-E should be reframed from:

> backend/API residual slow endpoint attribution and repair

to:

> OpenStock data-source boundary audit and mystocks consumer integration planning

No mystocks source implementation should be authorized until an OpenSpec-backed migration proposal or FUNCTION_TREE authorization explicitly scopes the consumer-side work.

## Recommended Next Package

Start a no-source package:

`B4.013-M1-E2 openstock consumer boundary audit`

Outputs:

- Mystocks provider-like endpoint inventory.
- OpenStock exposed contract inventory.
- Mapping table: current mystocks endpoint -> target OpenStock contract -> compatibility status.
- Consumer-only implementation candidates in mystocks.
- Provider-side implementation candidates in OpenStock.
- Explicit “do not implement in mystocks” list.

Then create an OpenSpec proposal, tentatively:

`externalize-data-source-provider-to-openstock`

The proposal should authorize only consumer-side integration changes in `mystocks_spec`; provider-side changes must be separately planned in `/opt/claude/openstock`.
