# Design: Migrate FundFlowMixin to OpenStock

## Context

Phase 1.1 batch 2 of B4.014 shipped the OpenStock switch at the **endpoint layer** for two endpoints. The switch pattern looks like this today:

```python
# web/backend/app/api/akshare_market/fund_flow.py
async def get_hsgt_fund_flow_summary(...):
    client = _build_openstock_client()
    try:
        result = await client.fetch("NORTHBOUND_FLOW", params={...})
        if not result.data:
            return _error_response("DATA_NOT_FOUND", ...)
        translated = [_translate_northbound_flow_row(r) for r in result.data]
        return _success_response(translated, source="openstock", provider="akshare")
    except OpenStockClientError as e:
        return _error_response("INTERNAL_SERVER_ERROR", str(e))
    finally:
        await client.aclose()
```

This works for one endpoint. Replicating it across all 8 fund-flow endpoints would produce 8× the boilerplate with no shared abstraction — exactly the failure mode that `AkshareMarketDataAdapter` was built to prevent.

The Mixin pattern exists so that **every data acquisition method in a domain shares lifecycle, error handling, and translation**. This proposal restores that invariant by moving the OpenStock switch into `FundFlowMixin`.

## Goals

- One place per domain owns OpenStock translation: the Mixin.
- Endpoint handlers shrink back to "call the adapter, shape the response".
- `akshare` import removed from `fund_flow.py` once all methods switched.
- Phase 1.1's endpoint-layer bypass is **lifted into** the Mixin (not discarded — the translation logic moves, the bypass goes away).

## Non-Goals

- Do not change the public API surface (`/api/akshare/market/fund-flow/*` paths and response envelopes stay).
- Do not migrate other Mixins (KlineMixin, QuoteMixin, etc.) — separate proposals.
- Do not remove `akshare` from `pyproject.toml` — only this file's import goes.
- Do not introduce feature flags / akshare fallback. Cutover is clean.

## Architecture

### Current (post-Phase-1.1) — bypass pattern

```
endpoint handler (fund_flow.py)
    ├── _build_openstock_client()         ← endpoint-local
    ├── client.fetch("NORTHBOUND_FLOW")
    ├── _translate_northbound_flow_row()  ← endpoint-local
    └── response shaping

FundFlowMixin.get_stock_hsgt_*             ← still calls ak.stock_hsgt_*
                                            (unused by switched endpoints,
                                             still used by other endpoints)
```

### Target — Mixin-owns-translation pattern

```
endpoint handler (fund_flow.py)
    └── adapter.get_stock_hsgt_summary_em(start, end)
            │
            ▼
FundFlowMixin.get_stock_hsgt_summary_em(self, start, end)
    ├── self._openstock_client.fetch("NORTHBOUND_FLOW", ...)
    ├── self._translate_northbound_flow_row(...)
    └── return DataFrame (akshare-era shape)
```

### Constructor injection

```python
# src/adapters/akshare/market_adapter/adapter.py
class AkshareMarketAdapter(
    FundFlowMixin,
    KlineMixin,
    QuoteMixin,
    # ...
):
    def __init__(
        self,
        # ... existing params ...
        openstock_client: OpenStockClient | None = None,
    ):
        # ... existing init ...
        self._openstock_client = openstock_client or _build_default_openstock_client()
```

Where `_build_default_openstock_client()` is the env-driven factory currently living as `_build_openstock_client()` in `web/backend/app/api/akshare_market/fund_flow.py`. It moves to a shared location (either `src/adapters/akshare/market_adapter/_openstock.py` or directly on the adapter module).

### Return-type decision

Two options for what `FundFlowMixin` methods return:

**Option A (recommended): keep `pd.DataFrame`**
- Mixin method builds a DataFrame from `OpenStockFetchResult.data` rows after translation.
- Pros: zero caller-side changes (callers in endpoints still get a DataFrame).
- Cons: builds a DataFrame even when the caller will immediately re-iterate rows.

**Option B: change to `OpenStockFetchResult`**
- Mixin returns the raw result; callers iterate `result.data`.
- Pros: no DataFrame overhead, preserves `request_id` / `latency_ms` / provenance for the response envelope.
- Cons: every caller must change.

**Decision: Option A for Wave 1** — minimizes blast radius, lets us prove the pattern. The DataFrame is built from translated dicts; the translation preserves the akshare-era column names. If a later wave needs the request_id (e.g., for the `X-Request-Id` response header), the mixin can stash it on `self` or attach it as a DataFrame attribute.

### Error mapping

`OpenStockClientError` raised inside a Mixin method is caught and converted to:
1. An empty DataFrame (current akshare-era behavior for any exception — see `get_stock_hsgt_fund_flow_summary_em` `try/except Exception` pattern), **or**
2. Re-raised for the endpoint handler to map to `INTERNAL_SERVER_ERROR`.

**Decision: re-raise**. The akshare-era "swallow exception, return empty DataFrame" pattern is what caused the P0 silent-failure incident. Better to surface the error and let the endpoint shape the response envelope.

### Lifecycle

`OpenStockClient` is async — it holds an `httpx.AsyncClient`. Options:

1. **Adapter owns the client, lifecycle tied to adapter.** Adapter gets `aclose()` method. Caller (FastAPI startup/shutdown or per-request) manages it.
2. **Per-request client.** Mixin builds a fresh client per call, closes in `finally`.

**Decision: adapter owns the client.** FastAPI's lifespan adds the adapter to `app.state`, calls `await adapter.aclose()` on shutdown. Reuses HTTP connections across requests.

## Risks / Trade-offs

- **Constructor signature change** on `AkshareMarketAdapter` may break direct callers in scripts/tests. Mitigation: `openstock_client` is keyword-only with a default; existing callers don't need to change.
- **Return-type preservation (Option A)** means we build DataFrames we don't always need. Acceptable — DataFrame construction is cheap relative to the upstream HTTP call.
- **Error visibility improvement** (re-raise vs swallow) could surface previously-hidden failures as 5xx responses. This is the intended behavior — silent failures are worse.
- **3-wave phasing** means `import akshare as ak` survives in the file until Wave 3 completes. `forbidden_imports.py` will continue to allow akshare in this specific file until then; the lint rule is updated only at Wave 3 closeout.

## Open Questions

- Should `_build_default_openstock_client()` live in `src/adapters/akshare/market_adapter/_openstock.py` (shared across Mixins) or stay endpoint-local during Wave 1 and move later? **Recommendation**: move now — Wave 1 is the only wave that touches this code, no point deferring.
- For the `big_deal` method (Wave 3), the akshare-era return has a `大单性质` field that classifies the deal (买/卖). Does `MARKET_BIG_DEAL_RANK` from OpenStock preserve this signal, or is it aggregated away? Needs confirmation when the category lands.
- Adapter lifecycle: does anything today call `AkshareMarketAdapter()` per-request (which would defeat the client-sharing benefit)? Grep needed in pre-flight task 1.2.

## Migration Plan

Wave 1 (this proposal, unblocked):

1. Pre-flight audit (tasks §1)
2. Constructor change (tasks §2)
3. Move translation functions into Mixin; rewrite 2 methods; revert endpoint-layer switch (tasks §3)
4. Tests + browser verify (tasks §3.5–3.7)

Wave 2 (blocked — OpenStock categories):

5. Per-method: confirm category live → rewrite method → unit test → API test → browser verify
6. Each method is a separate commit so partial progress is preserved if OpenStock rollout staggers

Wave 3 (blocked — final 2 categories):

7. Final 2 methods + remove `import akshare` + update lint rule (tasks §5)

Closeout:

8. Full-suite verification + worklog + task tracker update (tasks §6)

## References

- Parent proposal: `openspec/changes/externalize-data-source-provider-to-openstock/proposal.md`
- Phase 1.1 completion: `docs/reports/worklogs/claude-auto/b4-014-phase1-1-batch2-fundflow-openstock-switch-2026-06-29.md`
- P0 drift incident (motivation for error-visibility change): `docs/reports/worklogs/claude-auto/b4-014-p0-fundflow-drift-fix-verification-2026-06-29.md`
- Playbook: `docs/guides/openstock-migration/DOMAIN_MIGRATION_PLAYBOOK.md`
- Truth source contract: `web/frontend/src/views/data/fundFlowPageData.ts:105-111, 169`
