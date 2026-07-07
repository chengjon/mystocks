# Spec Delta: data-source-runtime-service

## MODIFIED Requirements

### Requirement: Fund-flow acquisition via OpenStock

The backend SHALL acquire all fund-flow data (HSGT summary/detail, northbound/southbound daily, per-symbol holdings, big-deal ranking) through the `OpenStockClient` calling OpenStock's `/data/fetch` endpoint with the appropriate `data_category`. Direct `import akshare` in `src/adapters/akshare/market_adapter/fund_flow.py` is FORBIDDEN once Wave 3 completes.

#### Scenario: Mixin method returns translated DataFrame

```gherkin
Given the OpenStock middle-tier exposes category `NORTHBOUND_FLOW` returning rows with fields
  | trade_date | board_name | fund_direction | net_buy_amount | index_change_pct | up_count | down_count | flat_count | related_index | fund_net_inflow |
And the AkshareMarketAdapter is constructed with a default OpenStockClient
When `adapter.get_stock_hsgt_fund_flow_summary_em(start_date="2026-06-20", end_date="2026-06-29")` is called
Then the OpenStockClient.fetch is invoked with `data_category="NORTHBOUND_FLOW"` and `params={"start_date": "2026-06-20", "end_date": "2026-06-29"}`
And the returned DataFrame contains the akshare-era columns `板块`, `资金方向`, `成交净买额`, `指数涨跌幅`, `交易日` populated from the OpenStock normalized fields
And the row count equals the OpenStock result row count
```

#### Scenario: OpenStockClientError surfaces (no silent swallow)

```gherkin
Given OpenStockClient.fetch raises OpenStockClientError
When any FundFlowMixin method is called
Then the exception propagates to the caller (it is NOT swallowed and converted to an empty DataFrame)
So that the endpoint handler can map it to INTERNAL_SERVER_ERROR in the response envelope
```

#### Scenario: Empty upstream data

```gherkin
Given OpenStockClient.fetch returns OpenStockFetchResult with `data=[]`
When any FundFlowMixin method is called
Then the returned DataFrame is empty (zero rows)
And no exception is raised
So that the endpoint handler can shape the DATA_NOT_FOUND response
```

#### Scenario: Per-symbol holding lookup

```gherkin
Given the OpenStock middle-tier exposes category `NORTHBOUND_HOLDING` returning rows with fields
  | trade_date | close | change_pct | holding_shares | holding_market_cap | holding_shares_ratio | add_shares | add_amount | holding_market_cap_change |
When `adapter.get_stock_hsgt_north_acc_flow_in_em(symbol="600519")` is called
Then OpenStockClient.fetch is invoked with `data_category="NORTHBOUND_HOLDING"` and `params={"symbol": "600519"}`
And the returned DataFrame columns include `持股日期`, `持股数量`, `持股市值`, `持股比例`, `增持数量`, `增持金额`
```

## ADDED Requirements

### Requirement: AkshareMarketAdapter constructor accepts OpenStockClient

The `AkshareMarketAdapter` constructor SHALL accept an optional `openstock_client: OpenStockClient | None` keyword parameter. When omitted, the adapter SHALL construct a default client from environment variables (`OPENSTOCK_BASE_URL`, `OPENSTOCK_SECURITY_API_KEY`, `OPENSTOCK_TIMEOUT_SECONDS`). The env name `OPENSTOCK_SECURITY_API_KEY` aligns with OpenStock upstream `config.py` `_get_config_value` derivation (`OPENSTOCK_` + `key_path.upper().replace('.', '_')`). The client is stored on the instance and reused across all Mixin method invocations.

#### Scenario: Default client construction

```gherkin
Given environment variables `OPENSTOCK_BASE_URL=http://192.168.123.104:8040`, `OPENSTOCK_TIMEOUT_SECONDS=5.0`
When `AkshareMarketAdapter()` is constructed without an `openstock_client` argument
Then `adapter._openstock_client` is an OpenStockClient instance
And its `base_url` is `http://192.168.123.104:8040`
And its `timeout_seconds` is `5.0`
```

#### Scenario: Explicit client injection (for tests)

```gherkin
Given a stub OpenStockClient instance
When `AkshareMarketAdapter(openstock_client=stub_client)` is constructed
Then `adapter._openstock_client` IS the stub_client (no default construction occurs)
And no real HTTP client is initialized
```

### Requirement: Adapter lifecycle hook for OpenStockClient

The `AkshareMarketAdapter` SHALL expose an `aclose()` coroutine that closes the internal `OpenStockClient` if it was default-constructed by the adapter. If the client was injected by the caller, `aclose()` SHALL NOT close it (caller owns lifecycle).

#### Scenario: Default-constructed client closes on adapter close

```gherkin
Given an adapter constructed without an explicit openstock_client
When `await adapter.aclose()` is called
Then the internal OpenStockClient's underlying HTTP connection pool is closed
```

#### Scenario: Injected client is not closed by adapter

```gherkin
Given an adapter constructed with an explicit openstock_client
When `await adapter.aclose()` is called
Then the injected client's HTTP pool is NOT closed (caller manages its lifecycle)
```

## REMOVED Requirements

### Requirement: FundFlowMixin imports akshare

The previous implementation `import akshare as ak` at the top of `src/adapters/akshare/market_adapter/fund_flow.py` and the eight `ak.stock_hsgt_*` / `ak.stock_fund_flow_big_deal` calls inside `FundFlowMixin` are REMOVED. This requirement is superseded by the MODIFIED "Fund-flow acquisition via OpenStock" requirement above.

```gherkin
Given Wave 3 of this proposal has shipped
When `scripts/linting/forbidden_imports.py --path src/adapters/akshare/market_adapter/fund_flow.py` is run
Then the lint SHALL PASS (no `import akshare` present)
```
