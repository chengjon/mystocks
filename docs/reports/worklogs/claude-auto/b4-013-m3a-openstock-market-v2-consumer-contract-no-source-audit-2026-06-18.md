# B4.013-M3a OpenStock market_v2 consumer contract no-source audit

Date: 2026-06-18
Repository: `/opt/claude/mystocks_spec`
Mode: no-source audit
Source edits authorized: false

## Boundary

This audit resumes MyStocks-side development after the OpenStock handoff. The architecture boundary remains fixed:

- OpenStock owns provider/data-source runtime, provider adapters, category execution, retries, and provider-specific schema normalization.
- MyStocks owns business routes, compatibility responses, persistence/read models, and backend consumer integration with OpenStock.
- MyStocks must not add provider fallback, provider SDK calls, provider adapters, or frontend-to-OpenStock direct calls.

No source files were modified during this audit.

## Current repository state

- MyStocks branch: `wip/root-dirty-20260403`
- MyStocks HEAD: `c54a7660a B4.013-M2-E4: record OpenStock category vocabulary evidence`
- OpenStock HEAD observed for boundary context: `8cf55fc docs: align zzshare capability status`
- MyStocks target-domain external dirty file observed: `web/backend/app/api/market_v2.py`

The dirty `market_v2.py` changes are treated as external and are not part of this batch. This means the first safe MyStocks source package should avoid editing route definitions and should start at the clean consumer-client contract layer.

## OpenStock capability now available for MyStocks consumption

OpenStock now exposes P0 category vocabulary and AkShare-backed provider mapping for the categories MyStocks previously identified as contract gaps:

| Category | MyStocks use case | OpenStock provider responsibility |
| --- | --- | --- |
| `FUND_FLOW` | individual stock fund flow refresh | Provider call and raw/provider schema handling |
| `SECTOR_FUND_FLOW` | sector/concept fund flow refresh | Provider call and raw/provider schema handling |
| `DRAGON_TIGER` | LHB / dragon-tiger detail refresh | Provider call and raw/provider schema handling |
| `BLOCK_TRADE` | block trade refresh | Provider call and raw/provider schema handling |
| `ETF_SPOT` | ETF spot/list refresh | Provider call and raw/provider schema handling |

MyStocks should consume these only through the backend `OpenStockClient`.

## MyStocks consumer contract gap

`web/backend/app/services/openstock_client.py` currently allows only:

- `REALTIME_QUOTES`
- `KLINES`

Therefore MyStocks cannot yet consume the new OpenStock P0 categories through its backend client without a source-authorized contract expansion.

## market_v2 route and service truth

`web/backend/app/api/market_v2.py` still exposes the public compatibility routes. Because this file is externally dirty, this batch should not edit it.

| Route family | Public route shape | Current service call family | M3 implication |
| --- | --- | --- | --- |
| fund flow | `GET /fund-flow`, `POST /fund-flow/refresh` | `query_fund_flow`, `fetch_and_save_fund_flow` | Refresh path can migrate after client contract expansion |
| ETF spot/list | `GET /etf/list`, `POST /etf/refresh` | `query_etf_spot`, `fetch_and_save_etf_spot` | Refresh path can migrate after client contract expansion |
| LHB / dragon-tiger | `GET /lhb/detail`, `POST /lhb/refresh` | `query_lhb_detail`, `fetch_and_save_lhb_detail` | Refresh path can migrate after client contract expansion |
| sector fund flow | `GET /sector/fund-flow`, `POST /sector/fund-flow/refresh` | `query_sector_fund_flow`, `fetch_and_save_sector_fund_flow` | Refresh path can migrate after client contract expansion |
| block trade | `GET /blocktrade`, `POST /blocktrade/refresh` | `query_blocktrade`, `fetch_and_save_blocktrade` | Refresh path can migrate after client contract expansion |

`web/backend/app/services/market_data_service_v2.py` still initializes and uses the local EastMoney adapter for provider acquisition paths:

| Method | Current role | Provider-coupled today | Recommended action |
| --- | --- | --- | --- |
| `fetch_and_save_fund_flow` | write-model refresh | yes | later migrate to OpenStock `FUND_FLOW` |
| `fetch_and_save_etf_spot` | write-model refresh | yes | later migrate to OpenStock `ETF_SPOT` |
| `fetch_and_save_lhb_detail` | write-model refresh | yes | later migrate to OpenStock `DRAGON_TIGER` |
| `fetch_and_save_sector_fund_flow` | write-model refresh | yes | later migrate to OpenStock `SECTOR_FUND_FLOW` |
| `fetch_and_save_blocktrade` | write-model refresh | yes | later migrate to OpenStock `BLOCK_TRADE` |
| `query_fund_flow` | DB/read-model query | no | preserve response compatibility |
| `query_etf_spot` | DB/read-model query | no | preserve response compatibility |
| `query_lhb_detail` | DB/read-model query | no | preserve response compatibility |
| `query_blocktrade` | DB/read-model query | no | preserve response compatibility |
| `query_sector_fund_flow` | DB/read-model query with runtime fallback | partially | isolate fallback cleanup as a later batch |

## Risk assessment

| Area | Risk | Reason |
| --- | --- | --- |
| Consumer client category expansion | Low | Adds allowed category vocabulary only; no provider logic, no route behavior change |
| market_v2 route edits | High for this batch | File is already externally modified; editing would mix work and risk conflict |
| service refresh migration | Medium | Requires mapping OpenStock normalized records into existing DB model fields |
| sector query runtime fallback cleanup | Medium | Current fallback still reaches provider-shaped logic; should be handled only after refresh migration |
| frontend/API compatibility | Medium | Public MyStocks routes must remain stable while backend acquisition source changes |

## Recommended implementation batches

### B4.013-M3a-A consumer client category contract expansion

Purpose: allow MyStocks backend to request OpenStock P0 categories without changing any route or provider logic.

Allowed paths for source authorization:

- `web/backend/app/services/openstock_client.py`
- `web/backend/tests/test_openstock_client.py`

Allowed actions:

- Add `FUND_FLOW`, `SECTOR_FUND_FLOW`, `DRAGON_TIGER`, `BLOCK_TRADE`, and `ETF_SPOT` to the backend consumer client's supported category vocabulary.
- Add/adjust focused tests proving these categories pass the client boundary and unsupported categories still fail.

Non-goals:

- No provider SDK calls in MyStocks.
- No route edits.
- No `market_v2.py` edits while it remains externally dirty.
- No `MarketDataServiceV2` refresh migration yet.
- No frontend changes.

Focused gates:

- GitNexus impact before editing `OpenStockClient` / category contract.
- `python -m py_compile web/backend/app/services/openstock_client.py web/backend/tests/test_openstock_client.py`
- `python -m pytest web/backend/tests/test_openstock_client.py -q`
- GitNexus staged verification and change detection.
- OPENDOG verification fresh.
- Exact staging of only authorized files.

### B4.013-M3a-B market_v2 refresh acquisition migration

Purpose: migrate write-model provider acquisition from local provider adapter to OpenStock consumer calls while preserving public MyStocks routes and DB/read-model shapes.

Candidate paths:

- `web/backend/app/services/market_data_service_v2.py`
- focused service tests / route tests directly covering refresh methods

Non-goals:

- No provider implementation in MyStocks.
- No frontend direct OpenStock call.
- No public route shape change.

### B4.013-M3a-C route contract tests

Purpose: prove `/api/v2/market/**` compatibility routes still return MyStocks-shaped responses with fake OpenStock client/service dependencies.

Candidate scope:

- backend route tests only, using fake client/service responses

### B4.013-M3a-D sector runtime fallback cleanup

Purpose: remove or replace the remaining provider-shaped runtime fallback in `query_sector_fund_flow` only after refresh migration is stable.

This should remain separate because it can alter read-time behavior.

## Decision

The next source-authorized MyStocks batch should be `B4.013-M3a-A consumer client category contract expansion`.

This is the smallest safe step that moves MyStocks toward OpenStock consumption without mixing route edits, provider implementation, or externally dirty files.
