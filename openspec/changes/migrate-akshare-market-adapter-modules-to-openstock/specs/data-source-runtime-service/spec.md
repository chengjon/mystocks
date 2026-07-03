# Spec Delta: data-source-runtime-service

## ADDED Requirements

### Requirement: Non-fund-flow Mixin acquisition via OpenStock

The backend SHALL acquire all non-fund-flow market data through the `OpenStockClient` calling OpenStock's `/data/fetch` endpoint with the appropriate `data_category`. This requirement covers five Mixin files in `src/adapters/akshare/market_adapter/`: `stock_profile.py`, `market_overview.py`, `board_sector.py`, `stock_sentiment.py`, `forecast_analysis.py`. Direct `import akshare as ak` in these five files is FORBIDDEN once the corresponding Phase (P1–P5) completes.

`FundFlowMixin` is governed by the sibling proposal `migrate-akshare-fundflow-mixin-to-openstock`.

#### Scenario: Stock profile acquisition

```gherkin
Given the OpenStock middle-tier exposes category `STOCK_PROFILE` returning rows with fields
  | code | name | industry | list_date | total_shares | float_shares |
When `adapter.get_stock_individual_info_em(symbol="600519")` is called
Then OpenStockClient.fetch is invoked with `data_category="STOCK_PROFILE"` and `params={"symbol": "600519"}`
And the returned DataFrame contains the akshare-era columns `股票代码`, `股票简称`, `行业`, `上市时间`, `总股本`, `流通股` populated from OpenStock normalized fields
```

#### Scenario: Industry classification

```gherkin
Given the OpenStock middle-tier exposes category `INDUSTRY_LIST`
When `adapter.get_stock_sector_detail()` is called
Then OpenStockClient.fetch is invoked with `data_category="INDUSTRY_LIST"`
And the returned DataFrame contains industry classification rows
```

#### Scenario: Market overview spot data

```gherkin
Given the OpenStock middle-tier exposes category `MARKET_OVERVIEW` returning rows with fields
  | code | name | latest_price | change_pct | volume | amount |
When `adapter.get_stock_zh_a_spot_em()` is called
Then OpenStockClient.fetch is invoked with `data_category="MARKET_OVERVIEW"`
And the returned DataFrame columns include `代码`, `名称`, `最新价`, `涨跌幅`, `成交量`, `成交额`
```

#### Scenario: Sector constituent with prefix reshape

```gherkin
Given the OpenStock middle-tier exposes category `SECTOR_CONSTITUENTS` returning rows with bare codes
  | code | name | weight |
  | 600519 | 贵州茅台 | 12.5 |
  | 000858 | 五粮液 | 8.3 |
When `adapter.get_stock_board_concept_cons_em(symbol="白酒")` is called
Then OpenStockClient.fetch is invoked with `data_category="SECTOR_CONSTITUENTS"` and `params={"symbol": "白酒"}`
And the returned DataFrame's `代码` column contains `sh600519` and `sz000858` (prefixed per exchange)
And no bare 6-digit code appears in the result
```

#### Scenario: Sector kline ISO8601 truncation

```gherkin
Given the OpenStock middle-tier exposes category `SECTOR_KLINES` returning ISO8601 timestamps
  | trade_date | open | close | high | low | volume |
  | 2026-06-01T00:00:00 | 1200.5 | 1210.3 | 1215.0 | 1198.0 | 1234567 |
When `adapter.get_stock_board_concept_hist_em(symbol="白酒", period="daily", start_date="20260601", end_date="20260610")` is called
Then OpenStockClient.fetch is invoked with `data_category="SECTOR_KLINES"` and `params` containing `period="day"`
And the returned DataFrame's `日期` column contains `"2026-06-01"` (10-char ISO truncation, not full ISO8601)
```

#### Scenario: News acquisition

```gherkin
Given the OpenStock middle-tier exposes category `STOCK_NEWS` returning rows with fields
  | title | content | publish_time | source | url |
When `adapter.get_stock_news_em(symbol="600519")` is called
Then OpenStockClient.fetch is invoked with `data_category="STOCK_NEWS"` and `params={"symbol": "600519"}`
And the returned DataFrame columns include `标题`, `内容`, `发布时间`, `来源`, `链接`
```

#### Scenario: Research report acquisition

```gherkin
Given the OpenStock middle-tier exposes category `RESEARCH_REPORTS`
When `adapter.get_stock_research_report_em(symbol="600519")` is called
Then OpenStockClient.fetch is invoked with `data_category="RESEARCH_REPORTS"` and `params={"symbol": "600519"}`
And the returned DataFrame columns include research-report fields mapped to the akshare-era Chinese column names
```

#### Scenario: OpenStockClientError surfaces (no silent swallow)

```gherkin
Given OpenStockClient.fetch raises OpenStockClientError
When any of the five governed Mixin methods is called
Then the exception propagates to the caller (it is NOT swallowed and converted to an empty DataFrame)
So that the endpoint handler can map it to INTERNAL_SERVER_ERROR in the response envelope
```

#### Scenario: Empty upstream data

```gherkin
Given OpenStockClient.fetch returns OpenStockFetchResult with `data=[]`
When any of the five governed Mixin methods is called
Then the returned DataFrame is empty (zero rows)
And no exception is raised
So that the endpoint handler can shape the DATA_NOT_FOUND response
```

### Requirement: Field-level mapping resides inside the adapter

Each Mixin method that calls `OpenStockClient.fetch` SHALL include a `_transform_*_row` mapping unit that converts OpenStock normalized fields to the existing frontend-facing Chinese wide-table column names. The route handlers in `web/backend/app/api/akshare_market/` MUST NOT contain field-mapping logic. This is the pattern proven by B4.014 first batch (commit `af29d15d6`, files `useArtDecoCapitalFlowViewModel.ts` + `marketRealtimeData.ts` for the frontend; sibling proposal for the backend Mixin).

#### Scenario: Route handler does not transform fields

```gherkin
Given Mixin `StockProfileMixin.get_stock_individual_info_em` has been migrated to OpenStock
When the route handler `GET /api/akshare/market/stock-info/{symbol}` invokes the adapter method
Then the route handler does NOT call any `_transform_*_row` helper
And it receives a DataFrame already shaped with frontend-facing Chinese column names
```

### Requirement: Dual-run verification for high-risk Mixins

The Mixins `stock_profile.py` (P1), `market_overview.py` (P2), `board_sector.py` (P3), and (per sibling proposal) `fund_flow.py` (P6) SHALL implement a dual-run verification mode during their migration Phase. Dual-run invokes both the legacy akshare path and the new OpenStock path on the same inputs, compares ≥ 5 critical fields per method, and logs any field mismatch as a debt entry in `docs/reports/quality/BUG_LESSONS_LEARNED.md`. Dual-run is removed once the field-consistency rate reaches ≥ 95% across at least 50 sample inputs.

`stock_sentiment.py` (P4) and `forecast_analysis.py` (P5) MAY skip dual-run per playbook §2.3 risk-tiered policy.

#### Scenario: Dual-run enabled for board_sector Mixin

```gherkin
Given Mixin `BoardSectorMixin` is in P3 migration Phase with dual-run enabled
And OpenStockClient is wired into the adapter
When `adapter.get_stock_board_concept_cons_em(symbol="白酒")` is called
Then the adapter invokes both the legacy akshare `stock_board_concept_cons_em` AND OpenStock `SECTOR_CONSTITUENTS`
And compares at least 5 fields (`code`, `name`, `weight`, etc.) across the result sets
And logs any mismatch with severity=WARN to the structured logger
And returns the OpenStock-derived result (the akshare result is only used for comparison)
```

#### Scenario: Dual-run disabled for low-risk Mixin

```gherkin
Given Mixin `StockSentimentMixin` is in P4 migration Phase with dual-run disabled per playbook §2.3
When `adapter.get_stock_news_em(symbol="600519")` is called
Then the adapter invokes only the OpenStock path (no legacy akshare call)
And the result is returned without comparison overhead
```

## MODIFIED Requirements

### Requirement: AkshareMarketAdapter `import akshare` boundary

CI lint SHALL fail any new `import akshare` or `from akshare import` line added to the following files after their corresponding Phase completes:
- `src/adapters/akshare/market_adapter/stock_profile.py` (after P1)
- `src/adapters/akshare/market_adapter/market_overview.py` (after P2)
- `src/adapters/akshare/market_adapter/board_sector.py` (after P3)
- `src/adapters/akshare/market_adapter/stock_sentiment.py` (after P4)
- `src/adapters/akshare/market_adapter/forecast_analysis.py` (after P5)
- `src/adapters/akshare/market_adapter/fund_flow.py` (per sibling proposal)

The CI lint MUST NOT check the following files (they retain `import akshare` until full retirement via separate proposal):
- `src/adapters/akshare/market_adapter/adapter.py` (top-level aggregator)
- `src/adapters/akshare/market_adapter/__init__.py`
- Other Mixins not covered by this or the sibling proposal (e.g., `cyq_em` chip distribution)
- `src/adapters/akshare.py` (the legacy shim kept for fallback)

#### Scenario: CI lint blocks new akshare imports in migrated files

```gherkin
Given Phase P1 has merged (stock_profile.py migrated)
When CI runs the `forbidden_imports.py` lint
Then `src/adapters/akshare/market_adapter/stock_profile.py` is checked
And any new `import akshare` or `from akshare import` line causes the lint to FAIL
And the existing legacy `import akshare as ak` line (if any remains during transition) is flagged but not blocking
```

#### Scenario: Legacy shim unaffected

```gherkin
Given P1–P5 have all merged
When CI runs the forbidden-imports lint
Then `src/adapters/akshare.py` is NOT checked (it remains the fallback shim)
And `src/adapters/akshare/market_adapter/adapter.py` is NOT checked (until full retirement proposal)
```
