# Tasks: Migrate AkshareMarketDataAdapter non-fund-flow Mixins to OpenStock

> **Proposal**: `migrate-akshare-market-adapter-modules-to-openstock`
> **Sibling**: `migrate-akshare-fundflow-mixin-to-openstock` (P6 fund_flow, in-flight)
> **Playbook**: `docs/guides/AKSHARE_MARKET_ADAPTER_MIGRATION_PLAYBOOK.md`

## P0 — Pre-flight Verification

- [x] P0.1 Run OpenStock 13-category verification probe against `192.168.123.104:8040` (no mocks) — **PASSED 2026-07-03** (probe v5, 13/13 green)
  - [x] `STOCK_PROFILE` (eltdx adapter, 1 row)
  - [x] `REALTIME_QUOTES` (50 rows — replaces proposed MARKET_OVERVIEW)
  - [x] `STOCK_NEWS` (eltdx adapter, 100 rows)
  - [x] `ANNOUNCEMENTS` (requires `date` param)
  - [x] `RESEARCH_REPORTS` (100 rows)
  - [x] `FINANCIAL_STATEMENTS`
  - [x] `FORECAST_DATA` (requires `code` not `symbol`, 12 rows)
  - [x] `FUND_FLOW` (requires retry on 503)
  - [x] `SECTOR_FUND_FLOW` (requires `sector_type=concept`)
  - [x] `SECTOR_CONSTITUENTS` (requires `sector` + `sector_type=concept`)
  - [x] `SECTOR_KLINES` (requires `sector` + `sector_type` + `start_date` + `end_date`, 8 rows)
  - [x] `MARKET_SENTIMENT` (zzshare adapter, requires `trade_date`)
  - [x] `HOT_RANK` (zzshare adapter, requires `trade_date`, 20 rows)
  - **Probe script**: `/tmp/p0_openstock_probe_v5.py` (real urllib HTTP, no MagicMock)
- [x] P0.2 Audit `git log -- web/backend/app/api/akshare_market/fund_flow.py` confirms B4.014 first-batch residue fields resolved — **PASSED 2026-07-03**
  - Endpoint-layer `_build_openstock_client` / `_translate_northbound_*_row` helpers already lifted into `FundFlowMixin` by commit `614290989` (D1 Wave 0) on branch `feat/b4-014-fundflow-mixin-openspec-proposal`
  - `git log -S "_build_openstock_client" -- web/backend/app/api/akshare_market/fund_flow.py` shows the symbol was added by `a40f38a0d` and removed by `614290989`
  - Residue is **resolved inside the sibling branch**; this proposal's P1 sees no residue in main yet
- [x] P0.3 Sibling proposal Wave 1 merged (constructor injection pattern established) — **BLOCKED 2026-07-03**
  - Sibling proposal `migrate-akshare-fundflow-mixin-to-openstock` exists at `openspec/changes/migrate-akshare-fundflow-mixin-to-openstock/`
  - Sibling Wave 0/Wave 1 commit `614290989` exists on branch `feat/b4-014-fundflow-mixin-openspec-proposal` but **NOT merged to main nor to this worktree's branch `feat/b4-014-openstock-routes`**
  - Constructor injection pattern (AkshareMarketAdapter accepting `openstock_client` parameter) is **not yet visible** in current worktree — `src/adapters/akshare/market_adapter/adapter.py` still has parameterless `__init__`
  - **P1 start is BLOCKED** until sibling Wave 0/Wave 1 merges to main and is cherry-picked/merged into this worktree

## P1 — stock_profile.py (157 LOC, low risk)

- [ ] P1.1 Map `stock_individual_info_em` → `OpenStockClient.fetch_data(category=STOCK_PROFILE, ...)`, build `_transform_stock_profile_row` mapping unit
- [ ] P1.2 `stock_sector_detail` (industry classification) — **DEFERRED**: upstream OpenStock does not implement `INDUSTRY_LIST` / `STOCK_INDUSTRY`. Track as follow-up debt; retain akshare fallback in this Mixin until upstream adds support.
- [ ] P1.3 Add Mixin-level dual-run for verification (legacy akshare + new OpenStock, compare 5+ fields, ≥95% consistency)
- [ ] P1.4 Unit tests `tests/adapters/test_stock_profile_mixin_migration.py` ≥ 70% coverage (project baseline 30%, this 2×+)
- [ ] P1.5 Integration test `pytest -m integration tests/adapters/test_stock_profile_real.py` — real HTTP to `192.168.123.104:8040`
- [ ] P1.6 Browser smoke: `/data/stock-info` page 5-dimension mini-regression (route/functional/data-state/visual/a11y)
- [ ] P1.7 PR description includes field mapping table (akshare field → OpenStock field → frontend contract field)
- [ ] P1.8 Remove `import akshare as ak` from `stock_profile.py`
- [ ] P1.9 PR merged to `feat/b4-014-openstock-routes`

## P2 — market_overview.py (233 LOC, medium risk)

- [ ] P2.1 Map `stock_zh_a_spot_em` → `REALTIME_QUOTES` (P0 corrected: `MARKET_OVERVIEW` not implemented upstream), build `_transform_realtime_quotes_row`
- [ ] P2.2 Map `stock_market_activity_legu` → `MARKET_SENTIMENT` / `HOT_RANK` (P0 corrected: `MARKET_ACTIVITY` not implemented upstream; zzshare adapter requires `trade_date` param)
- [ ] P2.3 Mixin-level dual-run (statistical fields, ≥95% consistency)
- [ ] P2.4 Unit tests ≥ 70% coverage
- [ ] P2.5 Integration test (real HTTP)
- [ ] P2.6 Browser smoke: market analysis pages
- [ ] P2.7 PR description with mapping table
- [ ] P2.8 Remove `import akshare as ak` from `market_overview.py`
- [ ] P2.9 PR merged

## P3 — board_sector.py (332 LOC, medium risk, hotspot)

- [ ] P3.1 Map `stock_board_concept_name_em` → `SECTOR_QUOTES` with `sector_type=concept` (P0 corrected: `SECTOR_LIST` not implemented upstream), `_transform_sector_quotes_row`
- [ ] P3.2 Map `stock_board_concept_cons_em` → `SECTOR_CONSTITUENTS` with `sector_type=concept`, `_transform_sector_constituent_row` (add `sh`/`sz` prefix reshape)
- [ ] P3.3 Map `stock_board_concept_hist_em` → `SECTOR_KLINES` with `sector_type=concept` + `start_date`/`end_date` (required by upstream), `_transform_sector_kline_row` (ISO8601 truncation, period mapping per B4.014-M1h pattern)
- [ ] P3.4 **Dual-run retained** (per playbook §2.3 — sector constituent reshape is a field-drift hotspot)
- [ ] P3.5 Unit tests ≥ 70% coverage
- [ ] P3.6 Integration test (real HTTP, multi-sector scenarios)
- [ ] P3.7 Browser smoke: `/market/boards*` pages
- [ ] P3.8 PR description with explicit constituent-reshape mapping table
- [ ] P3.9 Remove `import akshare as ak` from `board_sector.py`
- [ ] P3.10 PR merged

## P4 — stock_sentiment.py (196 LOC, low risk)

- [ ] P4.1 Map `stock_news_em` → `STOCK_NEWS`, `_transform_news_row`
- [ ] P4.2 Map `stock_notice_report` → `ANNOUNCEMENTS`, `_transform_announcement_row`
- [ ] P4.3 (No dual-run required per playbook §2.3, low risk)
- [ ] P4.4 Unit tests ≥ 70% coverage
- [ ] P4.5 Integration test (real HTTP)
- [ ] P4.6 Browser smoke: news / announcement pages
- [ ] P4.7 PR description with mapping table
- [ ] P4.8 Remove `import akshare as ak` from `stock_sentiment.py`
- [ ] P4.9 PR merged

## P5 — forecast_analysis.py (186 LOC, medium risk)

- [ ] P5.1 Map `stock_research_report_em` → `RESEARCH_REPORTS`, `_transform_research_report_row`
- [ ] P5.2 Map `stock_em_pleasure_summary` → `FINANCIAL_STATEMENTS`, `_transform_financial_statement_row`
- [ ] P5.3 Map performance-forecast methods → `FORECAST_DATA`, `_transform_forecast_row`
- [ ] P5.4 (No dual-run required per playbook §2.3)
- [ ] P5.5 Unit tests ≥ 70% coverage
- [ ] P5.6 Integration test (real HTTP)
- [ ] P5.7 Browser smoke: forecast / analysis pages
- [ ] P5.8 PR description with mapping table
- [ ] P5.9 Remove `import akshare as ak` from `forecast_analysis.py`
- [ ] P5.10 PR merged

## P6 — Closeout (after sibling proposal P6 fund_flow also merged)

- [ ] P6.1 Confirm all 6 Mixin files in `src/adapters/akshare/market_adapter/` have `import akshare as ak` removed
- [ ] P6.2 Mark `src/adapters/akshare/market_adapter/` as `@deprecated` in module docstrings
- [ ] P6.3 Update `docs/guides/AKSHARE_MARKET_ADAPTER_MIGRATION_PLAYBOOK.md` with completion status
- [ ] P6.4 myweb-audit closeout-checklist for all affected pages green
- [ ] P6.5 Trigger separate proposal for `market_data_service_v2.py` retirement

## Notes

- **Coverage threshold**: 70% baseline (not 90%) — see playbook §4 rationale
- **Dual-run**: P1/P2/P3 retain dual-run; P4/P5 can skip per playbook §2.3 risk-tiered policy
- **Frontend**: zero change — all field mapping is adapter-layer responsibility
- **Sibling dependency**: P0.3 requires sibling fund_flow proposal Wave 1 merged for `OpenStockClient` injection pattern
