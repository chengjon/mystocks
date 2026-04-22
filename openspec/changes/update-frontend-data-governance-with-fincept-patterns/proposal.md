# Change: Update Frontend Data Governance With Fincept Patterns

## Why

MyStocks already has important frontend foundations in place: a unified API client, a Pinia store factory, OpenAPI-driven type generation, and strong CI quality gates. However, current frontend data access still suffers from three operational gaps:

- error semantics are inconsistent and some service paths still silently swallow failures;
- realtime update paths exist in multiple forms but lack a shared coalescing policy and refresh contract;
- cache/realtime ownership is not documented in one auditable place, so migration and cleanup work rely too much on grep and tribal knowledge.

Fincept Terminal's advantage is not that it uses a desktop-only DataHub primitive, but that it combines:

- explicit result/error semantics,
- centralized policy/registry thinking,
- phased migration with coexistence and rollback,
- discipline gates added only after migration maturity,
- developer-visible runtime inspection.

This change adapts those advantages to MyStocks without introducing a second runtime architecture or replacing the existing `apiClient + service + PiniaStoreFactory + WebSocket/SSE` model.

## What Changes

- define a frontend data capability registry and realtime channel registry as governance artifacts;
- introduce a scoped `ServiceResult<T>` pattern for safe service paths where silent failure exists;
- define a shared latest-only coalescing pattern for high-frequency realtime channels on top of existing WebSocket/SSE entrypoints;
- define a store policy registry layered on top of `PiniaStoreFactory`, rather than adding a second cache system;
- define phased migration rules, developer-mode runtime inspection requirements, and delayed discipline gates for cleanup-stage enforcement.

## Impact

- Affected specs:
  - `architecture-governance`
  - `api-integration`
  - `code-quality`
- Affected code:
  - `web/frontend/src/api/`
  - `web/frontend/src/stores/`
  - `web/frontend/src/composables/`
  - `web/frontend/src/utils/`
  - `web/frontend/src/views/system/`
  - `docs/guides/frontend/`
- Expected outcomes:
  - fewer silent failures in service consumers,
  - lower repeated render pressure on high-frequency channels,
  - clearer ownership of cache/realtime behavior,
  - safer migration closure with explicit governance evidence before cleanup.
