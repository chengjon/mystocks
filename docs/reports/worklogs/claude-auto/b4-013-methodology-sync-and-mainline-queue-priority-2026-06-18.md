# B4.013 Methodology Sync And Mainline Queue Priority

Date: 2026-06-18
Status: methodology-synced
Source reference: `/mnt/c/Users/John Cheng/Documents/Obsidian Vault/软件开发/项目开发方法/项目主线对齐标准化开发方法论.md`
Local rule source updated: `architecture/STANDARDS.md`

## Methodology Delta

The local execution method now aligns with the external mainline-alignment methodology:

- Every task must be classified as `P0/P2/P3` before authorization.
- P0 runtime continuity and visible business capability outrank cleanup, documentation drift, test-shape cleanup, lint-only fixes, archive work, and cosmetic polish.
- A task is complete only when a user-visible service/page/API/data-flow path is demonstrably healthier; commits, worklogs, and green isolated tests are not sufficient by themselves.
- Every authorization package must state the P0 blocker or visible capability gap it resolves, and must also state which P2/P3 work is explicitly excluded.
- Verification follows a two-track order: usability gates first, engineering/governance gates second.
- FUNCTION_TREE execution is locked to one active P0 mainline node; historical cleanup tracks stay in Backlog until the current mainline closes.
- If consecutive commits only reduce local noise without improving runtime continuity, the queue must return to no-source mainline truth audit.

## Current Mainline Boundary

Current MyStocks responsibility:

- Consume OpenStock through backend consumer integration.
- Preserve MyStocks public API and route compatibility.
- Normalize OpenStock payloads into existing MyStocks response and database shapes.

Non-goals for this line:

- No provider/data-source implementation in MyStocks.
- No AkShare, TDX, Baostock, or provider SDK fallback inside MyStocks.
- No frontend-to-OpenStock direct calls.
- No OpenStock repository changes from this MyStocks queue.
- No edits to externally dirty `web/backend/app/api/market_v2.py` unless separately authorized and isolated.

## Completed P0 Work

- `B4.013-M2-E1`: OpenStock backend consumer client.
- `B4.013-M2-E2`: quotes and kline public route migration through OpenStock consumer.
- `B4.013-M2-E3`: OpenStock category coverage no-source audit.
- `B4.013-M2-E4`: OpenStock contract-gap handoff.
- `B4.013-M3a`: market_v2 consumer contract no-source audit.
- `B4.013-M3a-A`: MyStocks consumer category expansion for `FUND_FLOW`, `SECTOR_FUND_FLOW`, `DRAGON_TIGER`, `BLOCK_TRADE`, and `ETF_SPOT`.
- `B4.013-M3a-B`: market_v2 refresh mapping audit.
- `B4.013-M3a-B1`: `ETF_SPOT` refresh migration.
- `B4.013-M3a-B2`: `BLOCK_TRADE` and `DRAGON_TIGER` date refresh migration.

## Priority Queue

### P0-1: B4.013-M3a-B3 FUND_FLOW Symbol Refresh Migration

Priority: highest next action.

Reason:

- `FUND_FLOW` is already available from OpenStock provider work.
- It directly advances the market_v2 mainline refresh chain.
- It remains service-only and can avoid the externally dirty route file.

Required first step:

- No-source boundary check against the current `MarketDataServiceV2` fund-flow refresh/query methods and bound tests.

Implementation boundary:

- Allowed target family should remain `web/backend/app/services/market_data_service_v2.py` plus focused service tests.
- MyStocks maps OpenStock consumer payloads into existing MyStocks storage/response shapes.
- No local provider fallback or provider adapter work.

### P0-2: B4.013-M3a-B4 SECTOR_FUND_FLOW Readiness And Refresh Migration

Priority: second, but must begin with readiness audit.

Reason:

- Sector/concept fund flow is still part of the market_v2 mainline, but provider readiness and board/category parameter semantics are higher risk than `FUND_FLOW`.

Required first step:

- No-source readiness audit before any source edit.
- Confirm OpenStock category, params, provider readiness, and payload field names.

Decision rule:

- If OpenStock provider support is not live, keep this as consumer-contract pending and do not implement provider behavior in MyStocks.
- If OpenStock support is live, proceed with a service-only migration and focused tests.

### P0-3: B4.013-M3a-B5 Query Runtime Fallback Cleanup

Priority: third.

Reason:

- Query fallback cleanup should not run before acquisition paths are aligned.
- It can affect degraded runtime behavior and must not be mixed with B3/B4 refresh migrations.

Required first step:

- No-source audit of query fallback behavior, cached/read-model behavior, and current public API compatibility.

Implementation boundary:

- Only remove or narrow fallback behavior that is proven to bypass the OpenStock consumer boundary or mask runtime failures.
- Preserve public MyStocks API compatibility.

### P0-4: B4.013-M3b Full Consumer Validation And Mainline Closeout

Priority: after B3/B4/B5 decisions are complete.

Required evidence:

- Service-level focused pytest for migrated refresh paths.
- Public route/API compatibility smoke without editing externally dirty route files unless separately authorized.
- GitNexus impact/detect risk low or explicitly reviewed.
- OPENDOG fresh verification with no failing latest runs.
- Worklog comparing cycle start vs cycle end visible runtime capability.
- FUNCTION_TREE closeout of the active B4.013 mainline node or a clear carry-forward blocker list.

## External Dependency Queue

OpenStock-owned work must remain outside MyStocks:

- Provider adapter implementation for any category not yet live in OpenStock.
- Provider payload schema decisions.
- Provider retries, circuit breakers, fallback policy, and `/data/fetch` runtime behavior.

MyStocks may only record consumer evidence or update category compatibility once OpenStock publishes the contract/runtime behavior.

## Backlog

These remain blocked behind P0 closeout:

- B4.007/B4.008/B4.009/B4.010/B4.011/B4.012 cleanup or drift-retirement leftovers.
- Dirty worktree cleanup.
- Worklog/archive disposal.
- Lint-only or formatting-only improvements.
- Frontend polish unrelated to runtime continuity.
- Any route, UI, or test cleanup that does not unlock the current OpenStock consumer data flow.

## Next Authorization Recommendation

Request `B4.013-M3a-B3 FUND_FLOW symbol refresh no-source boundary check` first.

Do not request source authorization until the no-source check confirms:

- exact service methods and tests,
- current local provider calls to remove,
- OpenStock `FUND_FLOW` request params and payload field mapping,
- public compatibility expectations,
- external dirty files to isolate.
