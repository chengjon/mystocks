# Design: OpenStock provider boundary and MyStocks consumer integration

## Context

B4.013-M1-E2 established the current boundary truth:

- OpenStock exposes runtime contracts such as `/health/live`, `/health/ready`, `/sources`, `/routing/best`, `/data/fetch`, `/data/batch`, `/data/bars`, `/metrics`, and `/ws/market`.
- OpenStock currently covers provider categories including `REALTIME_QUOTES`, `KLINES`, `HISTORICAL_KLINES`, `STOCK_BASIC`, `ALL_STOCKS`, and related categories through AkShare, Baostock, and Eltdx adapters.
- MyStocks currently has active frontend calls to `/api/v1/market/**`, `/api/v2/market/**`, and `/api/akshare/market/**`, plus backend provider-like surfaces under `web/backend/app/services/adapters_split/**`, `src/adapters/**`, and provider portions of `src/data_sources/**`.

The main design decision is to avoid moving frontend or business code directly onto OpenStock. MyStocks backend remains the compatibility and business boundary.

## Goals

- Keep provider ownership singular in OpenStock.
- Keep MyStocks public API compatibility stable while provider-backed acquisition moves behind a backend consumer client.
- Make ready mappings small and testable: quotes and K-line/OHLCV first.
- Treat fund-flow, sector-flow, LHB, block-trade, and ETF provider refresh as OpenStock contract gaps before MyStocks implementation.
- Preserve local persisted database read models in MyStocks where they are business/application data rather than external provider acquisition.

## Non-Goals

- Do not implement the OpenStock client in this proposal package.
- Do not modify `src/adapters/**`, provider portions of `src/data_sources/**`, or `web/backend/app/services/adapters_split/**` in this proposal package.
- Do not retire `/api/akshare/market/**` routes during the first implementation phase.
- Do not point frontend code directly to OpenStock.
- Do not modify `/opt/claude/openstock` from the MyStocks worktree.

## Architecture

The target path is:

1. Frontend calls existing MyStocks service APIs.
2. MyStocks backend compatibility routes validate auth, parameters, response shape, and business-specific normalization.
3. A MyStocks OpenStock consumer client sends provider-backed requests to OpenStock.
4. OpenStock performs provider selection, health checks, fetch execution, timeout, cache, fallback, circuit breaker, and provider error mapping.
5. MyStocks maps OpenStock runtime envelopes into existing public route response shapes.

## Migration Plan

1. Add a MyStocks backend OpenStock consumer client with configuration, timeout, request id propagation, typed error mapping, and tests.
2. Migrate `/api/v1/market/quotes` to `POST /data/fetch` with `data_category=REALTIME_QUOTES`.
3. Migrate `/api/v1/market/kline` and technical-indicator OHLCV loading to `POST /data/bars` or a `KLINES` pull contract while preserving MyStocks indicator calculation.
4. Create separate OpenStock work packages for unsupported categories:
   - fund flow
   - sector fund flow
   - LHB
   - block trade
   - ETF provider refresh
5. After compatibility smoke passes, plan retirement or proxy-hardening for provider-specific MyStocks facades.

## Risks / Trade-offs

- Keeping compatibility routes temporarily means some legacy provider-shaped route names remain visible. This is acceptable because it protects frontend and external clients during migration.
- Moving provider behavior behind OpenStock may surface missing OpenStock categories. Those gaps must be resolved in OpenStock rather than patched locally in MyStocks.
- Some `src/data_sources/**` files are local persisted read models, not provider acquisition. They require classification before any retirement.

## Open Questions

- Which OpenStock category names should represent fund-flow, LHB, block-trade, and ETF provider refresh?
- Should MyStocks use REST-only for first quotes/K-line migration, or also consume `/ws/market` after the REST path is stable?
- Which MyStocks compatibility route should become the canonical public route after `/api/akshare/market/**` is deprecated?
