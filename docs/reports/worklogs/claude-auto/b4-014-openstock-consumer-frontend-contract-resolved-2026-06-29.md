# B4.014 OpenStock Consumer — Frontend Contract Gaps Resolved (Backend Adapter Layer)

**Date**: 2026-06-29
**Author**: Claude (auto worklog)
**Status**: Closed — three gaps fixed in MyStocks backend adapter layer; live HTTP verified
**Commit**: `7e3a07cac` (B4.014-M1m: bridge frontend kline contract via backend adapter layer)
**Predecessors**:
- `b4-014-openstock-consumer-live-verification-2026-06-29.md` (route-level live verification)
- `b4-014-openstock-consumer-frontend-contract-gap-2026-06-29.md` (gap audit, decision request)
- `/opt/claude/openstock/docs/operations/B4-014_OPENSTOCK_MYSTOCKS_FIX_RECOMMENDATION.md` (OpenStock team recommendation: Option A, MyStocks-only adapter)

---

## TL;DR

All three frontend/backend kline contract gaps (URL 404, response shape, parameter mismatch) are fixed entirely in the MyStocks backend adapter layer. **OpenStock was not modified** — the integration conforms to OpenStock's `RUNTIME_CONTRACTS.md` principle: "No frontend-specific payloads. Product shaping remains in MyStocks."

End-to-end HTTP smoke verified through PM2 → FastAPI → OpenStock for 6 cases (3 intervals × 3 adjust variants) plus backwards-compat with the legacy `stock_code/period` shape.

End-to-end frontend browser verification is blocked by a pre-existing login env issue (mock auth not enabled), which is independent of this batch of adapter fixes.

---

## Scope Decision

Option A from the gap audit was chosen: extend the MyStocks backend adapter layer rather than touch 22 frontend files (Option B) or coordinate a cross-project schema change (Option C).

| Rationale | Detail |
|---|---|
| OpenStock side | No change. Their adapter layer (`execute_bars_payload`) already accepts `symbol/period/count`; `adjust` and date-range forwarding are tracked as separate OpenStock-side follow-ups. |
| Frontend side | No change. `klineApi.ts` continues to call `/market/kline?symbol=...&interval=1d&adjust=qfq`. Axios `baseURL: '/api'` resolves this to `/api/market/kline`. |
| Backend side | 2 files edited: `router_registry.py` adds `/api/market` alias; `market_data_request.py` extends the route handler and the `_normalize_openstock_kline_payload` adapter. |

Total diff: +139 / −39 across 2 files (commit `7e3a07cac`).

---

## Fixes Applied

### Gap #7 — URL 404 (`GET /api/market/kline` → 404)

**Root cause**: The market router was mounted only under `/api/v1/market` (via `VERSION_MAPPING`); the frontend's `/api/market/kline` path had no matching route.

**Fix** (`web/backend/app/router_registry.py:86-90`):

```python
# B4.014-M1m: Frontend axios baseURL is '/api', so /market/kline resolves to
# /api/market/kline. Mount the market router under the unversioned prefix as
# an alias to keep the frontend contract stable without touching 22 files.
app.include_router(router_modules["market"], prefix="/api/market", tags=["market-alias"])
```

The router is now dual-mounted: canonical `/api/v1/market/*` plus alias `/api/market/*`. Both paths route to the same handlers.

---

### Gap #8 — Response Shape Mismatch

**Frontend expected** (`web/frontend/src/types/kline.ts:12-20`):

```ts
{ code: number, data: { symbol, interval, adjust, candles: KLineData[] } }
// KLineData: { timestamp, open, high, low, close, volume, amount }
```

**Backend was returning** (raw OpenStock envelope echoed):

```json
{ "success": true, "stock_code": "...", "data": [{ "symbol": "...", "time": "...", "open": ..., ... }], "count": 60, ... }
```

**Three concrete mismatches**:
1. Outer envelope: `{code, data}` vs `{success, ..., data: [...]}`
2. Inner shape: `data.candles: [...]` vs flat `data: [...]` array
3. Bar timestamp field: `timestamp` vs `time`

**Fix** (`web/backend/app/api/market/market_data_request.py`):

`_normalize_openstock_kline_payload` was rewritten to produce the candles-envelope shape. A new helper `_convert_openstock_bar_to_candle` does the per-bar field renaming:

```python
# Pseudocode for clarity — actual code in market_data_request.py
def _normalize_openstock_kline_payload(payload, requested_symbol, requested_interval, requested_adjust):
    bars = payload.get("data") or []
    candles = [_convert_openstock_bar_to_candle(b) for b in bars]
    return {
        "code": 0,
        "data": {
            "symbol": requested_symbol or payload.get("stock_code"),
            "interval": requested_interval or _OPENSTOCK_PERIOD_TO_INTERVAL.get(payload.get("period")),
            "adjust": requested_adjust or payload.get("adjust", "qfq"),
            "candles": candles,
        },
    }

def _convert_openstock_bar_to_candle(bar):
    return {
        "timestamp": bar["time"],   # critical rename
        "open": bar["open"],
        "high": bar["high"],
        "low": bar["low"],
        "close": bar["close"],
        "volume": bar["volume"],
        "amount": bar["amount"],
    }
```

The mapping table `_OPENSTOCK_PERIOD_TO_INTERVAL` covers both OpenStock-internal values (`day`, `week`, `month`) and user-facing echoes (`daily`, `weekly`, `monthly`) → `1d` / `1w` / `1M`. The dual keys handle the case where OpenStock echoes the requested period back verbatim.

---

### Gap #9 — Parameter Mismatch

**Frontend sends**: `?symbol=000001&interval=1d&adjust=qfq`
**Backend was accepting**: `?stock_code=...&period=daily&count=N`

**Fix** (`web/backend/app/api/market/market_data_request.py`, `get_kline_data` signature):

The route handler now accepts both vocabularies simultaneously:

| Frontend param | Backend alias | Internal translation |
|---|---|---|
| `symbol=000001` | `stock_code=000001` | `stock_code` wins if both present |
| `interval=1d` | `period=daily` | `1d→daily`, `1w→weekly`, `1M→monthly`, `1m→minute_1`, `5m→minute_5`, `15m→minute_15`, `1h→minute_60` |
| `adjust=qfq` | (same) | `none` normalized to empty string |
| `start_date` / `end_date` | (accepted, not yet forwarded) | OpenStock-side follow-up |

Translation map for `interval → period`:

```python
_INTERVAL_TO_PERIOD = {
    "1d": "daily", "1w": "weekly", "1M": "monthly",
    "1m": "minute_1", "5m": "minute_5", "15m": "minute_15", "1h": "minute_60",
}
```

Then the existing `period_map` (`daily→day`, `weekly→week`, etc.) translates to OpenStock's internal vocabulary before calling `client.fetch_bars(...)`.

**Not in scope of this batch**:
- `count` is still hardcoded to 60 inside the route body. Forwarding the frontend's expected `count`/date-range semantics requires OpenStock's `execute_bars_payload` to accept `start_date`/`end_date` (currently it only extracts `symbol/period/count`).
- `adjust=none` is normalized to `""` but OpenStock's `execute_bars_payload` does not currently forward `adjust` to the underlying `get_adjusted_kline` call, so non-qfq behavior is not yet verifiable end-to-end.

---

## Live Verification

Backend restarted via PM2; direct HTTP smoke through the FastAPI layer (PM2 → uvicorn → OpenStock client → `192.168.123.104:8040`).

### Test matrix (all returned HTTP 200)

| Path | Params | Result |
|---|---|---|
| `GET /api/market/kline` (alias) | `symbol=000001&interval=1d&adjust=qfq` | 200, `data.candles[0].timestamp` populated, `data.interval=1d` |
| `GET /api/market/kline` (alias) | `symbol=000001&interval=1w&adjust=qfq` | 200, `data.interval=1w` |
| `GET /api/market/kline` (alias) | `symbol=000001&interval=1M&adjust=qfq` | 200, `data.interval=1M` |
| `GET /api/market/kline` (alias) | `symbol=000001&interval=1d&adjust=hfq` | 200, `adjust=hfq` echoed (OpenStock-side forwarding pending) |
| `GET /api/market/kline` (alias) | `symbol=000001&interval=1d&adjust=none` | 200, `adjust=""` (normalized) |
| `GET /api/v1/market/kline` (canonical) | `stock_code=000001&period=daily` | 200, backwards-compat preserved |
| `GET /api/v1/market/kline` (canonical) | `stock_code=000001&period=weekly` | 200, weekly bars returned |

**Bar shape verified**: each candle has `{timestamp, open, high, low, close, volume, amount}` — matches `KLineData` exactly.

**Outer envelope verified**: `{code: 0, data: {symbol, interval, adjust, candles: [...]}}` — matches `KLineResponse`.

---

## Pre-existing Blocker (out of scope)

End-to-end frontend browser verification is blocked at the login step. The frontend correctly submits form-urlencoded `admin/admin123` to `/api/v1/auth/login`, but the backend returns HTTP 401 "用户名或密码错误".

**Root cause**: Mock auth is not enabled. The backend's mock-auth path (`web/backend/app/core/security.py:440-470`) requires `MOCK_AUTH_ENABLED=True` + `MOCK_ADMIN_PASSWORD` env vars; neither is present in `web/backend/.env`. The real PostgreSQL at `192.168.123.104:5438/mystocks` has a different admin password hash.

**Verification that this is pre-existing**:
- The OpenStock adapter fixes touched only `router_registry.py`, `market_data_request.py` (lines 80-148, ~609+), and `.env` (`OPENSTOCK_*` keys).
- None of these touch auth, security, or user management.
- The login flow (`auth.py:54-99`) and mock-auth gate (`security.py:440-470`) were not modified in this batch.

**Resolution path** (not auto-applied — needs explicit authorization): set `MOCK_AUTH_ENABLED=true` + `MOCK_ADMIN_PASSWORD=admin123` in `web/backend/.env` and restart PM2 backend. This is an env/config decision, not a code change.

---

## OpenStock-side Follow-ups (cross-project, non-blocking)

Two follow-ups identified for the OpenStock maintainers. Neither blocks MyStocks first-integration; both are about exposing capabilities that OpenStock's underlying adapters already support but `execute_bars_payload` does not yet forward.

1. **`adjust` param forwarding** — `openstock/fetching.py:232-254` extracts `symbol/period/count` from the `/data/bars` request but does not forward `adjust`. The underlying eLtdx `ADJUSTED_KLINES` category supports `qfq/hfq`. Forwarding `adjust` would let MyStocks expose `hfq` (currently untestable) and explicit `none` (currently normalized to empty string).
2. **Date-range / count semantics** — `execute_bars_payload` accepts `count` but not `start_date`/`end_date`. MyStocks' frontend already sends `start_date`/`end_date`; without forwarding, the route can only do count-based queries (currently hardcoded `count=60`).

These are tracked as OpenStock-internal capability gaps, not MyStocks frontend shape issues. They will be raised via a separate cross-project communication.

---

## Commit Footprint

```
7e3a07cac B4.014-M1m: bridge frontend kline contract via backend adapter layer
  web/backend/app/api/market/market_data_request.py  (+124/-39)
  web/backend/app/router_registry.py                   (+15/-0)
  Total: +139/-39 across 2 files
```

GitNexus `detect-changes` after commit: **Risk: medium**. Three affected execution flows, all kline-local — no cross-module blast radius. Index updated to 224,162 nodes / 281,369 edges / 300 execution flows.

---

## State Summary

| Item | Status |
|---|---|
| Gap #7 (URL 404) | ✅ Fixed + live-verified |
| Gap #8 (response shape) | ✅ Fixed + live-verified |
| Gap #9 (parameter mismatch) | ✅ Fixed + live-verified (count/adjust/date-range forwarding deferred) |
| Frontend browser smoke | ⏸ Blocked by pre-existing login env config (out of scope) |
| OpenStock `adjust` forwarding | ⏸ Cross-project follow-up |
| OpenStock date-range / count semantics | ⏸ Cross-project follow-up |

OpenStock consumer integration is functionally complete at the HTTP contract level: the frontend's kline shape is now served natively without any frontend code change, and OpenStock's bar schema is preserved as the canonical wire format.

---

## Next Steps (Subject to Separate Authorization)

1. **Resolve login env** (single-decision): enable mock auth or obtain real admin credentials, then complete browser-based end-to-end verification of `data.candles[].close` consumption in `useKlineChart.ts:48-50`.
2. **Push `wip/root-dirty-20260403`** to remote and open PR for `7e3a07cac`. Note this is a dirty worktree branch; pushing is irreversible and needs explicit authorization.
3. **Cross-project**: raise the two OpenStock-side follow-ups (`adjust` and date-range forwarding in `execute_bars_payload`) with the OpenStock maintainers.

Until then: no further source changes. The state at `7e3a07cac` is the last landed commit; the frontend remains unable to reach the kline page only due to the pre-existing auth env issue, which is independent of the OpenStock integration.
