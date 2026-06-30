# Tasks: Migrate FundFlowMixin to OpenStock

> All checkboxes map to Wave 1 / Wave 2 / Wave 3 in `proposal.md`. Wave 1 is unblocked. Wave 2/3 are blocked on OpenStock categories and should not be started until those land in `/opt/claude/openstock`.

## 1. Pre-flight (audit + design)

- [ ] 1.1 Grep all callers of `FundFlowMixin.*` methods across `web/`, `src/`, `scripts/`, `tests/`. Output a list of call sites with their expected return type (DataFrame vs other). This determines whether the Mixin return type can shift to `OpenStockFetchResult` cleanly or needs a DataFrame shim at the boundary.
- [ ] 1.2 Grep all `AkshareMarketAdapter(...)` constructor calls. Confirm none pass positional args that the new `openstock_client` parameter would break.
- [ ] 1.3 Confirm `OpenStockClient` constructor is sync (no async init) — required for it to be instantiated inside the adapter's `__init__`. If async, decide on lazy-init pattern.
- [ ] 1.4 Define the OpenStock→DataFrame translation contract for each Mixin method: which OpenStock normalized fields map to which akshare-era columns. Reuse Phase 1.1's `_translate_northbound_flow_row` / `_translate_northbound_holding_row` as the template.
- [ ] 1.5 Decide Mixin return shape: (a) keep `pd.DataFrame` and have the Mixin build it from `OpenStockFetchResult.data`, or (b) change to `OpenStockFetchResult` and migrate callers. Default recommendation: (a) — preserves call-site compatibility.

## 2. Adapter constructor change (foundation)

- [ ] 2.1 Modify `AkshareMarketAdapter.__init__` to accept an optional `openstock_client: OpenStockClient | None` parameter. If `None`, build a default client from env (reuse `_build_openstock_client()` logic from Phase 1.1's `fund_flow.py` endpoint file).
- [ ] 2.2 Store `self._openstock_client` on the adapter instance.
- [ ] 2.3 Update all `AkshareMarketAdapter(...)` instantiation sites to either pass an existing client or accept the default.
- [ ] 2.4 Add a unit test verifying the adapter can be constructed with and without an explicit client, and that the client is reachable from `FundFlowMixin` methods via `self._openstock_client`.

## 3. Wave 1 — switch 2 ready methods (categories NORTHBOUND_FLOW + NORTHBOUND_HOLDING)

- [ ] 3.1 Move `_translate_northbound_flow_row` and `_translate_northbound_holding_row` from `web/backend/app/api/akshare_market/fund_flow.py` into `FundFlowMixin` as private methods.
- [ ] 3.2 Rewrite `FundFlowMixin.get_stock_hsgt_fund_flow_summary_em(self, start_date, end_date)` to: call `self._openstock_client.fetch("NORTHBOUND_FLOW", params={start_date, end_date})`, translate each row, return a DataFrame matching the akshare-era column shape.
- [ ] 3.3 Rewrite `FundFlowMixin.get_stock_hsgt_north_acc_flow_in_em(self, symbol)` similarly against `NORTHBOUND_HOLDING`.
- [ ] 3.4 Revert the endpoint-layer switch in `web/backend/app/api/akshare_market/fund_flow.py` — handlers call the adapter mixin instead of `_build_openstock_client()`. Remove the now-unused `_build_openstock_client` / `_translate_*_row` endpoint helpers (they've been moved to the Mixin).
- [x] 3.5 Add Mixin-level unit tests in `tests/adapters/test_fund_flow_mixin.py` with stubbed `OpenStockClient` covering: success, empty data, `OpenStockClientError`. Reuse fixtures from `tests/api/test_fund_flow_openstock.py.
  - Done in Wave 0 commit `614290989`: 9 unit tests (3 constructor injection + 3 × success/empty/error for `get_stock_hsgt_fund_flow_summary_em` + 3 × success/empty/error for `get_stock_hsgt_north_acc_flow_in_em`).
- [x] 3.6 Extend `tests/api/test_fund_flow_openstock.py` (or rename it) — verify the endpoint still produces the same envelope after the Wave-1 refactor (no behavioral regression).
  - Done in Wave 0 commit `614290989`: 6 API e2e tests cover success/empty/error × (`hsgt-summary` + `north-stock/{symbol}`), monkeypatch target updated to `akshare_market_adapter._openstock_client`.
- [x] 3.7 Browser verification per `docs/guides/openstock-migration/DOMAIN_MIGRATION_PLAYBOOK.md` §4.2 for `hsgt-summary` and `north-stock/{symbol}` endpoints.
  - Verified 2026-06-30 against live OpenStock middle-tier at `http://192.168.123.104:8040` (akshare provider, API key auth). Drived Mixin directly in async context (bypassing TestClient's ephemeral-loop issue). Results: Test 1 `hsgt-summary` returned 4 real rows (沪股通/深股通/沪港通/深港通, 2026-06-30), all 5 truth-source columns present (`板块/资金方向/成交净买额/指数涨跌幅/交易日`); Test 2 `north-stock/600519` returned 50 real holding rows from 2017-03-16 onward, all 6 truth-source columns present (`持股日期/持股数量/持股市值/持股比例/增持数量/增持金额`); Test 3 unknown symbol correctly surfaced OpenStock middle-tier error as `INTERNAL_SERVER_ERROR` per Wave 1 contract.
- [x] 3.8 Confirm `import akshare as ak` is no longer needed by these two methods (other methods in the file may still need it — full removal waits for Wave 3).
  - Verified 2026-06-30: Wave 1 methods (lines 71–109) contain zero `ak.*` calls. `import akshare as ak` (line 12) is still required by Wave 2/3 methods at lines 124, 162, 199, 236, 274, 314, 348 (7 methods total). Full removal deferred to Wave 3 task 5.5.

## 4. Wave 2 — switch 4 daily/detail methods (blocked on OpenStock categories)

> **Blocked**: requires OpenStock to expose `NORTHBOUND_DAILY_HISTORY`, `SOUTHBOUND_DAILY_HISTORY`, `SOUTHBOUND_HOLDING`, `NORTHBOUND_FLOW_DETAIL`.

- [ ] 4.1 Confirm OpenStock category `NORTHBOUND_FLOW_DETAIL` is live and returns expected fields.
- [ ] 4.2 Confirm `NORTHBOUND_DAILY_HISTORY` is live.
- [ ] 4.3 Confirm `SOUTHBOUND_DAILY_HISTORY` is live.
- [ ] 4.4 Confirm `SOUTHBOUND_HOLDING` is live.
- [ ] 4.5 Rewrite `get_stock_hsgt_fund_flow_detail_em` against `NORTHBOUND_FLOW_DETAIL` + tests + browser verify.
- [ ] 4.6 Rewrite `get_stock_hsgt_north_net_flow_in_em` against `NORTHBOUND_DAILY_HISTORY` + tests + browser verify.
- [ ] 4.7 Rewrite `get_stock_hsgt_south_net_flow_in_em` against `SOUTHBOUND_DAILY_HISTORY` + tests + browser verify.
- [ ] 4.8 Rewrite `get_stock_hsgt_south_acc_flow_in_em` against `SOUTHBOUND_HOLDING` + tests + browser verify.

## 5. Wave 3 — switch final 2 methods + remove akshare import

> **Blocked**: requires OpenStock categories `HSGT_INDIVIDUAL_HOLDING`, `MARKET_BIG_DEAL_RANK`.

- [ ] 5.1 Confirm `HSGT_INDIVIDUAL_HOLDING` is live.
- [ ] 5.2 Confirm `MARKET_BIG_DEAL_RANK` is live.
- [ ] 5.3 Rewrite `get_stock_hsgt_hold_stock_em` against `HSGT_INDIVIDUAL_HOLDING` + tests + browser verify.
- [ ] 5.4 Rewrite `get_stock_fund_flow_big_deal` against `MARKET_BIG_DEAL_RANK` + tests + browser verify.
- [ ] 5.5 Remove `import akshare as ak` from `src/adapters/akshare/market_adapter/fund_flow.py`. Confirm `forbidden_imports.py` lint passes.
- [ ] 5.6 Confirm `FundFlowMixin` no longer references `ak.*` anywhere. Grep-verify.

## 6. Verification + closeout

- [ ] 6.1 Run `pytest tests/adapters/test_fund_flow_mixin.py tests/api/test_fund_flow_openstock.py` — all green.
- [ ] 6.2 Run `scripts/linting/forbidden_imports.py --path src/adapters/akshare/market_adapter/fund_flow.py` — PASS (akshare no longer imported).
- [ ] 6.3 Browser verify all 8 fund-flow endpoints render real data per Playbook §4.2.
- [ ] 6.4 Run `gitnexus_impact({target: "FundFlowMixin", direction: "upstream"})` — confirm no unexpected callers.
- [ ] 6.5 Run `gitnexus_detect_changes({scope: "staged"})` before each wave's commit.
- [ ] 6.6 Update `docs/guides/openstock-migration/DOMAIN_MIGRATION_PLAYBOOK.md` §3 to mark `FundFlowMixin` migrated.
- [ ] 6.7 Write completion worklog under `docs/reports/worklogs/claude-auto/`.
- [ ] 6.8 Mark Task #11 (`AkshareMarketDataAdapter 大型迁移单独立项`) completed in task tracker.
- [ ] 6.9 Run `openspec validate migrate-akshare-fundflow-mixin-to-openstock --strict` and resolve any findings.

## 7. Out-of-scope follow-ups (NOT in this proposal)

- Other Mixins (`KlineMixin`, `QuoteMixin`, `MarketOverviewMixin`, `StockProfileMixin`, `ForecastAnalysisMixin`, `BoardSectorMixin`, `StockSentimentMixin`) — each gets its own proposal
- `get_stock_cyq_em` (chip distribution) — different OpenStock category family
- Retiring the `/api/akshare/market/**` route prefix — parent proposal's closeout
- Removing `akshare` from `pyproject.toml` — only after **all** Mixins migrated
