## 1. Proposal Review

- [ ] 1.1 Confirm OpenStock owns external provider adapters and provider runtime behavior.
- [ ] 1.2 Confirm MyStocks remains the backend compatibility and business consumer boundary.
- [ ] 1.3 Confirm frontend direct OpenStock calls are out of scope for first implementation.
- [ ] 1.4 Confirm fund-flow, sector-flow, LHB, block-trade, and ETF provider refresh require OpenStock-owned category/contract work before MyStocks migration.

## 2. MyStocks Consumer Client Implementation

- [ ] 2.1 Add a backend OpenStock consumer client with base URL/env configuration, timeout, request id propagation, and typed error mapping.
- [ ] 2.2 Add focused tests for successful fetch, provider unavailable, timeout, invalid payload, and degraded fallback behavior.
- [ ] 2.3 Preserve existing MyStocks route response shapes.

## 3. Ready Route Migration

- [ ] 3.1 Migrate `/api/v1/market/quotes` provider-backed acquisition to OpenStock `REALTIME_QUOTES`.
- [ ] 3.2 Migrate `/api/v1/market/kline` acquisition to OpenStock `/data/bars` or `KLINES`.
- [ ] 3.3 Keep technical-indicator calculation in MyStocks while sourcing OHLCV through the approved consumer/local-store boundary.
- [ ] 3.4 Run focused backend tests, frontend service tests, and business smoke for dashboard/market/strategy routes.

## 4. OpenStock Contract-Gap Follow-up

- [ ] 4.1 Define OpenStock contract/category for fund-flow.
- [ ] 4.2 Define OpenStock contract/category for sector fund-flow.
- [ ] 4.3 Define OpenStock contract/category for LHB.
- [ ] 4.4 Define OpenStock contract/category for block-trade.
- [ ] 4.5 Define OpenStock contract/category for ETF provider refresh if needed beyond local persisted reads.

## 5. Closeout

- [ ] 5.1 Validate OpenSpec with `openspec validate externalize-data-source-provider-to-openstock --strict`.
- [ ] 5.2 Run GitNexus staged verification and OPENDOG checks for each implementation package.
- [ ] 5.3 Record FUNCTION_TREE evidence and close the proposal/implementation nodes only after route smoke proves the mainline remains runnable.
