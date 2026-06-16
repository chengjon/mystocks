# Change: Externalize data-source provider ownership to OpenStock

## Why

The B4.013 runtime mainline audits found that `mystocks_spec` still mixes business application responsibilities with data-source provider responsibilities. This creates two problems:

- Provider behavior is being repaired or expanded inside `mystocks_spec`, even though `/opt/claude/openstock` already exists as the dedicated data-source runtime.
- Frontend and backend compatibility routes in `mystocks_spec` depend on provider-specific facades such as `/api/akshare/market/**`, which makes runtime health, fallback, and contract ownership ambiguous.

The corrected architecture is that OpenStock owns provider adapters and runtime acquisition, while MyStocks owns business workflows and consumer integration.

## What Changes

- Define OpenStock as the only target owner for external provider adapters, upstream acquisition, provider health, route decisions, cache/circuit-breaker state, REST pull data, and market stream production.
- Define MyStocks as an OpenStock consumer that preserves existing backend compatibility routes while routing provider-backed acquisition through a backend OpenStock client.
- Preserve MyStocks ownership of business data, local persisted read models, strategy/risk/trade logic, frontend services, and response normalization.
- Forbid new provider SDK integrations in MyStocks unless a separate deprecation/compatibility exception is explicitly approved.
- Split migration into ready mappings and OpenStock contract-gap work:
  - Ready in MyStocks after approval: quotes and K-line/OHLCV consumer integration.
  - OpenStock-owned gaps first: fund flow, sector fund flow, LHB, block trade, ETF provider refresh.

## Impact

- Affected specs:
  - `data-source-runtime-service`
  - `data-sources`
- Affected repositories:
  - `mystocks_spec`: proposal, backend consumer integration, compatibility route preservation.
  - `openstock`: provider contract/category additions for unsupported market-data families.
- Implementation is not authorized by this proposal package.
- Frontend direct OpenStock integration is explicitly out of scope for the first implementation phase.
- Existing `mystocks_spec` compatibility routes must remain stable until replacement proxy behavior is verified.
