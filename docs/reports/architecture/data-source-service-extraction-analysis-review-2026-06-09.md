# Data Source Service Extraction Analysis Review

Date: 2026-06-09
Reviewed document: `docs/reports/architecture/data-source-service-extraction-analysis-2026-06-09.md`
Review lens: mattpocock architecture skills vocabulary (`Module`, `Interface`, `Seam`, `Adapter`, `Depth`) plus repository OpenSpec and runtime governance rules.

## Verdict

The proposal is directionally sound: introducing a separate data-source runtime module is a plausible way to make provider-specific failures, credentials, routing, and realtime ingestion less coupled to the MyStocks functional core.

However, it is not yet ready to become an OpenSpec implementation proposal. The main weakness is not protocol selection; the protocol recommendations are mostly reasonable. The main weakness is that the proposal postpones several interface-defining decisions until later phases. Those decisions define the seam itself, so they need to be settled before extraction starts.

## Findings

### High: Registry ownership is acknowledged but scheduled too late

The proposal correctly identifies mixed configuration truth sources in the summary and current facts, including `config/data_sources.json`, `config/data_sources_registry.yaml`, `config/adapter_priority_config.yaml`, and DB/YAML registry behavior. It also says the registry truth source must be single and explicit in Phase 0.

But the concrete migration plan postpones “Registry Ownership and Config Cleanup” to Phase 4. That is too late. The registry interface is the seam between the functional core and the data-source runtime module. If ownership is unresolved when Phase 2 adds `mystocks-data-source`, the project will almost certainly create another parallel truth source.

Evidence:

- Source document line 52: `get_data_with_failover()` reads `config/adapter_priority_config.yaml`, another routing truth source.
- Source document line 63: the current backend config API owns create/update/delete/version/rollback/reload behavior.
- Source document line 226: proposed data-source runtime owns registry runtime, routing, credentials, handlers, rate limits, cache, circuit breakers, health, and outbound calls.
- Source document line 326: Phase 0 says registry truth source must be single and explicit.
- Source document lines 363-368: actual convergence is deferred to Phase 4.
- Current implementation: `src/core/data_source/config_manager.py` writes YAML for create/update/delete/rollback and keeps in-memory version cache; `src/core/data_source/registry.py` loads from DB and YAML.

Required correction:

- Move registry ownership into Phase 0/Phase 1.
- Decide whether the data-source runtime module owns registry writes or only registry reads.
- Specify whether the main backend remains the writer and the data-source runtime is a read-through runtime, or whether the data-source runtime becomes the writer and backend config APIs proxy to it.
- Specify how version history, rollback, reload callbacks, and DB/YAML merge precedence survive the move.

### High: Public write-contract parity is under-specified

The proposal preserves the backend facade, which is the right instinct. But it does not define parity for the current write-heavy config interface. Keeping `/api/v1/data-sources*` stable is not enough; the interface includes auth behavior, write semantics, versioning semantics, rollback behavior, reload semantics, OpenAPI shape, and `UnifiedResponse` wrapping.

Evidence:

- Source document line 13: keep the main backend as functional core and API facade.
- Source document line 410: keep existing backend `/api/v1/data-sources*`.
- Source document line 63: current config API supports create, update, delete, detail, list, batch operations, version history, rollback, and reload.
- `web/backend/app/api/data_source_config.py` exposes create/update/delete/list/batch/version/rollback/reload.
- `web/backend/app/api/_data_source_config_responses.py` defines prefix `/api/v1/data-sources/config`.
- `web/backend/app/api/data_source_registry.py` defines prefix `/api/v1/data-sources`.

Required correction:

- Add an explicit “public data-source management interface parity” requirement.
- State that all existing backend endpoints must preserve request bodies, response envelopes, auth failures, status codes, OpenAPI examples, and version/rollback behavior during the first extraction.
- Add contract tests for every existing write path before implementing the remote adapter.

### High: Storage and observability ownership conflicts with “do not move storage ownership”

The proposal says the data-source runtime owns health, cache, circuit breakers, route selection, credentials, handlers, rate limits, and outbound provider calls. It also says not to move storage ownership in the first extraction. That sounds safe, but it conflicts with current runtime behavior: registry, metrics, health, call history, and config versioning already have persistence or observability concerns.

Evidence:

- Source document line 226 assigns health, cache, circuit breakers, and route selection to `mystocks-data-source`.
- Source document line 234 says not to move storage ownership in the first extraction.
- `src/core/data_source/metrics.py` records endpoint latency, success/failure, cache hits/misses, circuit breaker state, and estimated API cost.
- `src/core/data_source/config_manager.py` writes YAML and records versions.
- `src/core/data_source/registry.py` loads from DB and YAML.

Required correction:

- Split “business storage ownership” from “runtime state ownership.”
- State whether endpoint health, route metrics, circuit breaker state, cache state, call history, and config version history are owned by the data-source runtime module or by the main backend.
- If the data-source runtime owns them, it needs explicit DB/Redis access and Docker env keys.
- If the backend owns them, the runtime module must report state through an interface rather than persist it directly.

### Medium: The proposed `mystocks-data-source` module risks becoming shallow

The proposal lists many endpoints: registry CRUD, route lookup, fetch, batch fetch, WebSocket stream, and optional MCP tools. This could become a broad pass-through module unless the interface hides real complexity behind a small surface.

Using the mattpocock vocabulary: the proposed seam is promising, but the interface is not yet deep. It exposes many operational verbs before defining the core invariant that callers can rely on.

Evidence:

- Source document lines 236-260 list separate control and pull data endpoints.
- Source document lines 265-291 list stream message fields.
- Source document lines 293-304 list MCP tools.

Required correction:

- Define the core data-source runtime interface around a smaller set of caller capabilities:
  - resolve route
  - fetch snapshot/batch
  - subscribe stream
  - inspect health
  - manage registry
- Put provider-specific handler details, rate limit decisions, cache decisions, route scoring, and circuit breaker behavior behind the module implementation.
- Avoid exposing one external endpoint per internal concern unless a caller genuinely needs it.

### Medium: Pilot scope is still ambiguous

The recommendation says the first pilot should be `REALTIME_QUOTES` or one AkShare market-data category. Those are materially different pilots. One stresses streaming, freshness, and backpressure. The other stresses registry routing, request/response normalization, payload shape, and provider handler correctness.

Evidence:

- Source document line 353: add service WebSocket stream for `REALTIME_QUOTES`.
- Source document line 408: scope is `REALTIME_QUOTES` or one AkShare market-data category.

Required correction:

- Pick one first pilot in the proposal.
- Recommended first pilot: AkShare request/response category first, then realtime.
- Reason: current registry is mostly AkShare (`api_library`) and current `DataSourceManagerV2` is already registry/handler-oriented. This proves the service seam without adding stream lifecycle risk at the same time.
- Make realtime the second pilot once REST contract parity and registry ownership are stable.

### Medium: Rate limiting is described as owned by the new runtime, but current V2 docs say it is not default on the main outbound chain

The proposal assigns rate limits to `mystocks-data-source`, which is probably correct for the target design. But the current project documentation explicitly warns that `AdaptiveRateLimiter` is not default-enabled on the `DataSourceManagerV2` outbound path.

Evidence:

- Source document line 226 includes rate limits in the proposed runtime ownership.
- Source document line 383 notes provider-specific rate limits.
- `docs/guides/data-source/DATA_SOURCE_DEVELOPER_GUIDE.md` states `AdaptiveRateLimiter` exists but is not default-connected to the main `DataSourceManagerV2` outbound chain.
- The same guide warns not to describe `AdaptiveRateLimiter` as default main-chain behavior.

Required correction:

- Reword rate limiting as a target capability, not current inherited behavior.
- Add a task to connect or implement per-source rate limiting before any real provider traffic moves into the container.
- Add tests for rate-limit behavior using a mock provider before real AkShare/TuShare/BYAPI traffic is enabled.

### Medium: Realtime stream contract needs stronger failure and replay semantics

The WebSocket recommendation is directionally right. The proposal names staleness, sequence, heartbeat, subscribe/unsubscribe, and smoke tests, but it does not specify acceptance behavior for reconnects, missed messages, duplicate messages, out-of-order sequence, slow consumers, or market close/open state.

Evidence:

- Source document lines 141-160 recommend WebSocket for realtime.
- Source document lines 265-291 propose `/ws/market` fields including `sequence` and `staleness_ms`.
- Source document line 420 proposes a realtime WebSocket smoke with subscribe/update/unsubscribe.
- Existing WebSocket docs target batching, pooling, >500 RPS, and sub-50ms message latency.

Required correction:

- Add stream invariants:
  - message ordering is per symbol and per source
  - every update carries source timestamp and receive timestamp
  - reconnect either sends latest snapshot or resumes from a known sequence
  - slow consumers are dropped or degraded predictably
  - stale quotes are marked, not silently treated as fresh
- Add acceptance tests beyond smoke: subscribe, unsubscribe, reconnect, stale mark, duplicate suppression, and slow-client behavior.

### Medium: OpenSpec affected specs need sharper mapping

The proposal lists likely affected specs, but `03-adapter-pattern` currently describes frontend adapter classes and UI ViewModel transformations, not backend data-source provider adapters. Treating it as the main backend provider adapter spec would conflate two different meanings of “adapter.”

Evidence:

- Source document lines 308-326 list affected specs.
- `openspec/specs/03-adapter-pattern/spec.md` is about API-to-UI data transformation adapters.
- `openspec/specs/data-sources/spec.md` is thin and still has a `TBD` purpose.
- `openspec/specs/containerized-runtime-deployment/spec.md` currently requires backend, frontend, postgresql, and redis services only.

Required correction:

- Prefer a new or renamed capability such as `data-source-runtime-service` for backend/provider runtime behavior.
- Modify `containerized-runtime-deployment` for Docker topology and smoke evidence.
- Modify `data-sources` for provider coverage and data semantics.
- Avoid overloading `03-adapter-pattern` unless the delta is explicitly about frontend/UI data adapters.

### Low: Active OpenSpec work is not explicitly reconciled

The repository has an active `optimize-data-source-v2` change at 108/120 tasks. The proposal refers to current V2 implementation but does not state whether the new extraction proposal depends on, supersedes, or must wait for the unfinished V2 change.

Evidence:

- `openspec list` shows `optimize-data-source-v2` at 108/120 tasks.
- `docs/guides/data-source/DATA_SOURCE_DEVELOPER_GUIDE.md` says it describes the current implemented state of `optimize-data-source-v2`.

Required correction:

- Add an OpenSpec conflict section:
  - Does `extract-data-source-runtime-service` depend on completing `optimize-data-source-v2`?
  - Which unfinished V2 tasks are prerequisites?
  - Which V2 tasks become obsolete after extraction?

### Low: Terminology should be tightened before turning this into a mattpocock-style architecture proposal

The reviewed document uses reasonable engineering language, but for mattpocock architecture review it should use sharper terms:

- `Module`: main backend functional core, data-source runtime module.
- `Interface`: REST/OpenAPI, WebSocket message contract, optional MCP tools, and every invariant a caller must know.
- `Seam`: the `DataSourceClient` seam between main backend and data-source runtime module.
- `Adapter`: `LocalDataSourceClient`, `RemoteDataSourceClient`, provider handlers.

Required correction:

- Replace vague “service boundary” language with seam/interface/module wording in the eventual OpenSpec design.
- Define the `DataSourceClient` interface in terms of invariants, error modes, config requirements, and performance characteristics, not only method names.

## Recommended Rewrite Structure

Before creating the OpenSpec change, rewrite the proposal around these sections:

1. Current state and constraints
   - mixed config truth sources
   - existing V2 runtime chain
   - active `optimize-data-source-v2` status
   - current public backend API paths

2. Chosen seam
   - `DataSourceClient` interface in main backend
   - `LocalDataSourceClient` adapter
   - `RemoteDataSourceClient` adapter
   - `mystocks-data-source` runtime module implementation

3. Registry ownership decision
   - writer, reader, merge precedence, versioning, rollback, reload

4. Runtime state ownership decision
   - health, metrics, cache, rate limiter, circuit breaker, call history

5. Protocol contracts
   - REST/OpenAPI for control and pull fetch
   - WebSocket for realtime after first pilot
   - SSE only for browser one-way operational updates
   - MCP Streamable HTTP only for diagnostics/admin

6. Pilot
   - choose one: recommended AkShare REST/pull category first
   - define exact endpoint/category and test fixture

7. Verification matrix
   - backend public API parity tests
   - local-vs-remote client contract tests
   - config write/version/rollback tests
   - container readiness smoke
   - provider mock tests
   - later realtime stream tests

## Suggested OpenSpec Change Shape

Suggested change id:

`extract-data-source-runtime-service`

Suggested affected specs:

- `data-source-runtime-service` (new)
- `containerized-runtime-deployment` (modified)
- `data-sources` (modified)
- `market-data` (modified if the pilot changes market-data behavior)

Avoid using `03-adapter-pattern` as the main provider-runtime spec unless the delta is explicitly about frontend ViewModel adapters.

## Conclusion

Approve the direction, but do not approve implementation from the current document as-is.

Required pre-approval edits:

1. Move registry ownership to Phase 0/Phase 1.
2. Define public write-contract parity for `/api/v1/data-sources/config`.
3. Separate runtime state ownership from business storage ownership.
4. Pick one pilot, preferably AkShare REST/pull first.
5. Treat rate limiting as a target capability, not current inherited behavior.
6. Add realtime stream failure/replay semantics before the WebSocket pilot.
7. Reconcile the active `optimize-data-source-v2` OpenSpec change.
