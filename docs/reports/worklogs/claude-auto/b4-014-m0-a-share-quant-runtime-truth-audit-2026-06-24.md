# B4.014-M0 A-share Quant Runtime Truth Audit

Date: 2026-06-24
Program: artdeco-web-design-governance
Node: b4-014-m0-a-share-quant-runtime-truth-audit
Parent: b4-014-mainline-a-share-quant-runtime-usability-recovery
Mode: no-source runtime audit
Source edits authorized: false
Current HEAD: 092d8e156ec1

## Scope

This audit records the real runtime state of the A-share quant system mainline.

It is read-only. No source, tests, docs, OpenSpec, or governance implementation changes are included in this package.

## Runtime Facts

### Process / Service State

- `mystocks-backend` is online in PM2
- `mystocks-frontend` is online in PM2
- backend port is `8020`
- OpenStock PM2 runtime is not present in the current PM2 list

### Backend / Frontend Availability

Observed HTTP status:

- `http://localhost:8020/` -> 200
- `http://localhost:8020/health` -> 200
- `http://localhost:8020/api/health` -> 200
- `http://localhost:8020/api/v1/health` -> 404
- `http://localhost:8020/openapi.json` -> 200
- `http://localhost:3020/` -> 200
- `http://localhost:3020/dashboard` -> 200
- `http://localhost:3020/market` -> 200
- `http://localhost:3020/data` -> 200
- `http://localhost:3020/watchlist` -> 200
- `http://localhost:3020/strategy` -> 200
- `http://localhost:3020/trade` -> 200
- `http://localhost:3020/risk` -> 200
- `http://localhost:3020/system` -> 200

### Browser Rendering Truth

Playwright is available and routes load without console/page errors, but every audited business route renders the login surface instead of the business page:

- `/` -> title `Login - MyStocks`
- `/dashboard` -> title `Login - MyStocks`
- `/market` -> title `Login - MyStocks`
- `/data` -> title `Login - MyStocks`
- `/watchlist` -> title `Login - MyStocks`
- `/strategy` -> title `Login - MyStocks`
- `/trade` -> title `Login - MyStocks`
- `/risk` -> title `Login - MyStocks`
- `/system` -> title `Login - MyStocks`

This means route HTTP reachability exists, but business-page usability is not yet proven.

### OpenAPI / API Surface

Backend OpenAPI summary:

- total paths: 501
- core business-path candidates (matching dashboard / market / data / watchlist / strategy / trade / risk / system / indicators / technical / analysis / stocks): 55

Core GET endpoints without path parameters that were probed:

- 11 returned 200
- 8 returned 401
- 7 returned 422
- 1 returned 500

### High-Signal Failures

1. `GET /api/strategy-mgmt/health` returned 500 with:
   - `数据源初始化失败: TDengineTimeSeriesDataSource must implement ITimeSeriesDataSource`

   This is a P0 runtime blocker for strategy / runtime health and must be treated as a core mainline failure.

2. Several protected or validation-gated endpoints returned 401 / 422.
   These are not automatically defects, but they prove the runtime path is not yet a clean end-to-end business smoke.

### OpenStock Boundary Facts

Repository-side boundary state:

- `/opt/claude/openstock` exists
- OpenStock git HEAD: `fb7926147402`
- OpenStock worktree is clean
- Repo references show MyStocks expects `OPENSTOCK_BASE_URL=http://localhost:8031`
- `http://localhost:8031/`, `/health`, and `/openapi.json` were unreachable during this audit

This means the OpenStock consumption boundary is not runtime-proven from the MyStocks side yet.

## Decision

The project has runtime reachability, but it does not yet have runtime usability.

The main blockers are:

- business routes currently collapse to the login surface
- strategy health endpoint returns a TDengine interface mismatch 500
- the configured OpenStock runtime base URL is unreachable

## Recommended Next Mainline Node

Create and execute:

`B4.014-M1 core runtime blocker repair`

Priority order:

1. fix the TDengine / strategy health blocker
2. restore a valid OpenStock runtime consumption path
3. prove business routes can progress beyond the login-only surface
4. only then expand to broader data / page recovery

## Governance Outcome

M0 is ready to move to `decision-prepared`.

The new mainline should proceed from runtime truth audit into blocker repair, and all B4.012 governance work should remain frozen as backlog-hold until the mainline is stable.
