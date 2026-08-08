# Change: Migrate AkshareMarketDataAdapter non-fund-flow Mixins to OpenStock

> **Parent proposal**: `externalize-data-source-provider-to-openstock` (B4.014)
> **Sibling proposal**: `migrate-akshare-fundflow-mixin-to-openstock` (P6 fund_flow, in-flight)
> **Scope**: 5 of 6 Mixins in `src/adapters/akshare/market_adapter/` — fund_flow covered by sibling
> **Origin**: B4.014 task #11 (deferred from first-batch scope)
> **Reference playbook**: `docs/guides/AKSHARE_MARKET_ADAPTER_MIGRATION_PLAYBOOK.md`

## Why

B4.014 first batch only migrated the `get_timeseries_source` chain (kline/quotes routes) and a single Mixin (`FundFlowMixin` — sibling proposal). The remaining 5 Mixins in `AkshareMarketDataAdapter` still `import akshare as ak` directly:

| Mixin | LOC | akshare methods | Consumer routes |
|---|---:|---|---|
| `stock_profile.py` | 157 | `stock_individual_info_em`, `stock_sector_detail` etc. | `stock_info.py` |
| `market_overview.py` | 233 | `stock_zh_a_spot_em`, `stock_market_activity_legu` etc. | `analysis.py`, `boards.py` |
| `board_sector.py` | 332 | `stock_board_concept_name_em`, `stock_board_concept_cons_em` etc. | `boards.py` |
| `stock_sentiment.py` | 196 | `stock_news_em`, `stock_notice_report` etc. | `analysis.py` |
| `forecast_analysis.py` | 186 | `stock_em_pleasure_summary`, `stock_research_report_em` etc. | `analysis.py` |
| **subtotal** | **1104** | ~25 async methods | 7 consumer files |

Leaving these on akshare keeps the project exposed to akshare version drift (production incidents already seen: `stock_hsgt_north_acc_flow_in_em` removed in akshare 1.18.60) and blocks retirement of `market_data_service_v2.py`.

## What Changes

### Per-Mixin deltas

- **MODIFIED** `src/adapters/akshare/market_adapter/stock_profile.py` — replace `import akshare as ak` with `OpenStockClient` calls against `STOCK_PROFILE` category; add `_transform_*_row` mapping units.
- **MODIFIED** `src/adapters/akshare/market_adapter/market_overview.py` — switch to `REALTIME_QUOTES` (replaces `stock_zh_a_spot_em`) and `MARKET_SENTIMENT` / `HOT_RANK` (zzshare adapter, replaces `stock_market_activity_legu`). P0 verification proved `MARKET_OVERVIEW` / `MARKET_ACTIVITY` are not implemented upstream.
- **MODIFIED** `src/adapters/akshare/market_adapter/board_sector.py` — switch to `SECTOR_QUOTES` (sector_type=concept for `stock_board_concept_name_em`), `SECTOR_CONSTITUENTS` (sector_type=concept), `SECTOR_KLINES` (sector_type=concept + start_date/end_date) categories; sector constituent reshape (add `sh`/`sz` prefix) handled in adapter. P0 verification proved `SECTOR_LIST` is not implemented upstream; the canonical replacement is `SECTOR_QUOTES` with `sector_type` parameter.
- **MODIFIED** `src/adapters/akshare/market_adapter/stock_sentiment.py` — switch to `STOCK_NEWS` / `ANNOUNCEMENTS`.
- **MODIFIED** `src/adapters/akshare/market_adapter/forecast_analysis.py` — switch to `RESEARCH_REPORTS` / `FORECAST_DATA` / `FINANCIAL_STATEMENTS`.
- **MODIFIED** `src/adapters/akshare/market_adapter/adapter.py` — already accepts `OpenStockClient` per sibling proposal (Wave 1); this proposal reuses the injection.
- **REMOVED** `import akshare as ak` from the 5 modified Mixin files (this file only; `cyq_em` chip distribution stays on akshare for now).

### Contract preservation

- **UNCHANGED** — Route handler return shapes (Chinese wide-table) preserved. All field-level mismatch between OpenStock real returns and existing frontend expectations is resolved **inside the adapter** via `_transform_*_row` methods, following the pattern proven by B4.014 first batch (commit `af29d15d6`, files `useArtDecoCapitalFlowViewModel.ts` + `marketRealtimeData.ts`).
- **NO FRONTEND CHANGE** required as a consequence of this proposal. (Field mapping is an adapter-layer responsibility, not a frontend contract change.)

## Mapping: Mixin → OpenStock category

| Mixin method group | OpenStock category | Required params | Status |
|---|---|---|---|
| `stock_individual_info_em` | `STOCK_PROFILE` | `symbol` | ✅ P0 verified (eltdx adapter) |
| `stock_zh_a_spot_em` (market overview) | `REALTIME_QUOTES` | — | ✅ P0 verified (50 rows) |
| `stock_market_activity_legu` | `MARKET_SENTIMENT` / `HOT_RANK` | `trade_date` | ✅ P0 verified (zzshare adapter) |
| `stock_board_concept_name_em` | `SECTOR_QUOTES` | `sector_type=concept` | ✅ P0 verified (via SECTOR_FUND_FLOW path) |
| `stock_board_concept_cons_em` | `SECTOR_CONSTITUENTS` | `sector`, `sector_type=concept` | ✅ P0 verified |
| `stock_board_concept_hist_em` | `SECTOR_KLINES` | `sector`, `sector_type`, `period`, `start_date`, `end_date` | ✅ P0 verified (8 rows) |
| `stock_news_em` | `STOCK_NEWS` | `symbol` | ✅ P0 verified (100 rows, eltdx adapter) |
| `stock_notice_report` | `ANNOUNCEMENTS` | `symbol`, `date` | ✅ P0 verified |
| `stock_research_report_em` | `RESEARCH_REPORTS` | `symbol` | ✅ P0 verified (100 rows) |
| `stock_em_pleasure_summary` | `FINANCIAL_STATEMENTS` | `symbol` | ✅ P0 verified |
| forecast / performance预告 | `FORECAST_DATA` | `code` (NOT `symbol`) | ✅ P0 verified (12 rows) |
| (sector fund flow) | `SECTOR_FUND_FLOW` | `sector_type=concept` | ✅ P0 verified |

**Categories NOT supported upstream** (proposal originally guessed these names — corrected):
- ❌ `MARKET_OVERVIEW` → use `REALTIME_QUOTES`
- ❌ `MARKET_ACTIVITY` → use `MARKET_SENTIMENT` / `HOT_RANK`
- ❌ `SECTOR_LIST` → use `SECTOR_QUOTES` with `sector_type`
- ❌ `INDUSTRY_LIST` (for `stock_sector_detail`) → **no upstream equivalent**; P1.2 deferred to follow-up proposal or implemented via akshare fallback

P0 verification run: 13/13 categories returned non-empty real data via HTTP to `192.168.123.104:8040` on 2026-07-03 (probe script `/tmp/p0_openstock_probe_v5.py`). Anti-mock clause satisfied: real HTTP, no MagicMock stubs.

## Implementation Phasing

Per playbook §2.1, executed as 5 sequential PRs (P6 fund_flow tracked in sibling proposal):

- **P1** `stock_profile.py` (157 LOC, risk=low) — establish `_transform_*_row` pattern
- **P2** `market_overview.py` (233 LOC, risk=medium) — statistical-field drift potential
- **P3** `board_sector.py` (332 LOC, risk=medium) — sector constituent reshape is the field-drift hotspot; **dual-run retained**
- **P4** `stock_sentiment.py` (196 LOC, risk=low) — news/announcement field stability
- **P5** `forecast_analysis.py` (186 LOC, risk=medium) — performance-forecast field drift

Each PR is independently revertable via `config/data_sources.json` factory switch (`market_adapter_provider: "akshare" | "openstock"`).

## Impact

- **Affected specs**: `data-source-runtime-service` (delta)
- **Affected code**:
  - 5 Mixin files under `src/adapters/akshare/market_adapter/`
  - `src/adapters/akshare/market_adapter/adapter.py` (no constructor change — already done by sibling)
  - 7 consumer files under `web/backend/app/api/akshare_market/`
  - New test files `tests/adapters/test_<mixin>_mixin_migration.py` per Mixin
- **Affected routes** (under `/api/akshare/market/**`):
  - stock_info routes (P1)
  - market overview / activity routes (P2)
  - board sector routes (P3)
  - news / announcement routes (P4)
  - forecast / research-report routes (P5)
- **Frontend impact**: zero (field mapping stays inside adapter)
- **Out of scope**:
  - `FundFlowMixin` (sibling proposal `migrate-akshare-fundflow-mixin-to-openstock`)
  - `cyq_em` chip distribution (different category family, deferred)
  - `market_data_service_v2.py` retirement (depends on full Mixin migration completion — separate proposal)
  - OpenStock upstream category additions (if P0 gate surfaces a gap, file as separate upstream issue)
- **Non-Goals**:
  - No frontend contract changes
  - No new cache / queue layer
  - No performance optimization (unless mapping naturally yields ≥ 2× speedup)
  - No akshare upstream bug fixes (log debt, separate proposal)

## Risks

See playbook §3.1 for full risk matrix. Top 3:

1. **Sector constituent reshape** (P3) — akshare returns bare codes, frontend expects `sh`/`sz` prefixed. Mitigation: explicit mapping table in PR description; dual-run retained.
2. **Performance-forecast field drift** (P5) — akshare reshapes these fields across versions. Mitigation: dual-run retained; debt logged in `docs/reports/quality/BUG_LESSONS_LEARNED.md` for any unmappable field.
3. **Constructor signature change ripple** (already done by sibling proposal Wave 1) — this proposal depends on sibling landing first to reuse `OpenStockClient` injection.

## Approval Gates

Before P1 implementation starts:

1. ✅ This proposal approved via OpenSpec
2. ✅ Sibling proposal `migrate-akshare-fundflow-mixin-to-openstock` Wave 1 merged (provides `OpenStockClient` injection pattern)
3. ✅ P0 verification gate passed (§1.3 of playbook): all 9 OpenStock categories return non-empty real data via HTTP to `192.168.123.104:8040`, no MagicMock stubs
4. ✅ `git log -- web/backend/app/api/akshare_market/fund_flow.py` audit confirms no unresolved field drift from B4.014 first batch
