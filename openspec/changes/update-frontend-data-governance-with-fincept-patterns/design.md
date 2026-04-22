## Context

MyStocks frontend already contains several partially standardized layers:

- `apiClient` and `unifiedApiClient` as request infrastructure,
- `PiniaStoreFactory` for repeated store patterns,
- OpenAPI-driven frontend type generation,
- existing realtime entrypoints such as `useWebSocketEnhanced.ts`, `useRealtimeMarket.ts`, and `useSSE.js`,
- strong project-wide governance and CI gates.

The missing piece is not a new architecture primitive. The missing piece is governance and migration structure around existing primitives.

Fincept Terminal demonstrates that the durable architecture advantage comes from:

1. a registry-first model for data topics/policies,
2. phased migration with coexistence,
3. runtime visibility,
4. explicit cleanup gates after maturity,
5. consistent error semantics.

MyStocks should borrow those qualities while preserving current repository truth and avoiding a second source of truth for frontend runtime behavior.

## Goals / Non-Goals

### Goals

- Add an auditable registry for frontend data capabilities and realtime channels.
- Standardize safe error semantics for selected service paths with known silent-failure behavior.
- Introduce shared coalescing semantics for high-frequency realtime updates without replacing current realtime primitives.
- Centralize reusable cache/realtime policy values around `PiniaStoreFactory`.
- Define migration sequencing and late-stage discipline gates for cleanup.
- Add developer-visible runtime inspection for frontend data paths.

### Non-Goals

- Do not introduce a DataHub/TopicBus runtime into MyStocks.
- Do not rewrite all services to `Result<T>` in one batch.
- Do not replace current OpenAPI, `apiClient`, or Pinia store factory truth sources.
- Do not enable aggressive CI discipline gates before migration maturity.
- Do not commit to full repo-wide adoption in a single phase.

## Decisions

### 1. Registry-First Governance

**Decision**: Add two frontend governance registries:

- `frontend-data-capability-registry`
- `frontend-realtime-channel-registry`

These are documentation and review artifacts first, not runtime dispatch systems.

**Rationale**:

- gives architecture/governance a stable audit surface;
- makes source-of-truth ownership explicit;
- creates a migration ledger without inventing a new runtime abstraction.

**Alternatives considered**:

- Build a DataHub-like runtime topic registry: rejected as a second architecture.
- Keep ownership implicit in code only: rejected because current migration work already shows visibility gaps.

### 2. Scoped `ServiceResult<T>` Adoption

**Decision**: Add `ServiceResult<T>` as a safe-path pattern for service methods with known silent failure risk, starting with a narrow set of methods.

**Rationale**:

- fixes real error-semantics defects without breaking all callers;
- allows old `{ data }` return contracts to coexist during migration;
- better aligns with developer-visible error handling and request tracking.

**Alternatives considered**:

- convert every service at once: too disruptive;
- keep `try/catch` + empty objects everywhere: preserves ambiguity;
- throw exceptions only: does not solve typed consumer branching.

### 3. Shared Latest-Only Coalescing On Existing Realtime Entry Points

**Decision**: Add a reusable latest-only coalescing helper under frontend utilities and apply it selectively within current realtime composables/stores.

**Rationale**:

- preserves existing WebSocket/SSE topology;
- reduces render churn on high-frequency channels;
- respects current repo rules that non-composable logic should not be lifted into `src/composables/`.

**Alternatives considered**:

- new global stream manager: rejected as over-architecture;
- page-by-page ad hoc throttling: rejected due to duplication and drift.

### 4. Store Policy Registry, Not Second Cache Runtime

**Decision**: Create a reusable store-policy registry for `PiniaStoreFactory` consumers.

**Rationale**:

- centralizes TTL, interval, and channel metadata where a store already exists;
- avoids `src/api/policies.ts` becoming a second cache truth source;
- complements rather than replaces store declarations.

**Alternatives considered**:

- no registry: leaves duplicated policy numbers scattered;
- separate policy engine: creates parallel truth.

### 5. Delayed Discipline Gates And Early Runtime Inspector

**Decision**:

- ship runtime inspection earlier;
- enable hard discipline gates only after migration maturity.

**Rationale**:

- early visibility helps migration;
- premature lock-down would block legitimate coexistence work;
- mirrors Fincept's staged “coexist first, enforce later” strategy.

**Alternatives considered**:

- immediate CI lock-down: too early and too brittle;
- no discipline gates: migration debt never closes.

## Risks / Trade-offs

### Governance Drift

- **Risk**: registries become stale documents.
- **Mitigation**: require them in proposal/closeout evidence and bind them to later discipline checks.

### Partial Adoption Ambiguity

- **Risk**: mixed `{ data }` and `ServiceResult<T>` patterns confuse developers.
- **Mitigation**: scope adoption to named methods and record migration status in registries/tasks.

### Over-Enforcement Too Early

- **Risk**: CI blocks valid migration work.
- **Mitigation**: discipline checks are explicitly phase-gated and only become blocking after migration closure criteria are met.

### Inspector Becoming Unmaintained Debug UI

- **Risk**: runtime inspector exists but is not trusted.
- **Mitigation**: keep scope small and tie fields directly to real store/service/realtime state rather than duplicating business logic.

## Migration Plan

### Phase 0: Governance Setup

- create registries for frontend data capabilities and realtime channels;
- classify source-of-truth ownership for selected frontend chains.

### Phase 1: Silent Failure Removal

- add `ServiceResult<T>` support for a targeted service path;
- update one real consumer path and its tests.

### Phase 2: Realtime Coalescing Pilot

- add shared coalescing helper;
- adopt on one high-frequency channel;
- verify no UX regression.

### Phase 3: Store Policy Consolidation

- add store-policy registry;
- migrate a small set of `PiniaStoreFactory` stores to reference it.

### Phase 4: Developer Runtime Inspector

- add a developer-only frontend inspection surface for capability/channel state.

### Phase 5: Cleanup-Stage Discipline Gates

- enforce “no direct `apiClient` in routed views”, “no new silent catch”, and registry/ownership hygiene once coexistence period is complete.

## Open Questions

- Which existing system/developer page is the best host for the runtime inspector?
- Should `ServiceResult<T>` carry `request_id`/`traceId` directly or via a common error payload object?
- Which high-frequency channel is the safest first coalescing pilot for user-visible validation?
