## 1. Governance Foundation

- [x] 1.1 Create `frontend-data-capability-registry` with owner, source-of-truth, endpoint/channel, cache, refresh, and consumer-scope fields
- [x] 1.2 Create `frontend-realtime-channel-registry` with push/coalesce/force-refresh metadata
- [x] 1.3 Identify the first scoped migration targets and mark them as pilot capabilities

## 2. Safe Error Semantics Pilot

- [x] 2.1 Add `ServiceResult<T>` to the frontend type system without breaking existing `{ data }` contracts
- [x] 2.2 Convert one known silent-failure service path to expose a safe variant
- [x] 2.3 Update one real consumer flow to branch on explicit success/error semantics
- [x] 2.4 Add unit/integration evidence for the pilot path

## 3. Realtime Coalescing Pilot

- [x] 3.1 Add a shared latest-only coalescing helper under frontend utilities
- [x] 3.2 Wire the helper into one existing realtime entrypoint
- [x] 3.3 Validate that the pilot channel preserves user-visible freshness while reducing repeated updates

## 4. Store Policy Consolidation

- [x] 4.1 Add a store policy registry that complements `PiniaStoreFactory`
- [x] 4.2 Migrate a small set of factory-created stores to use shared policy values
- [x] 4.3 Document force-refresh semantics and stale/fresh expectations for those stores

## 5. Developer Visibility

- [x] 5.1 Add a developer-mode runtime inspector surface for frontend data paths
- [x] 5.2 Surface fetch recency, cache staleness, realtime connection status, and request/readiness metadata
- [x] 5.3 Document how the inspector is used during migration verification

## 6. Cleanup-Stage Discipline

- [x] 6.1 Define non-blocking checks for forbidden direct data-access patterns during coexistence
- [x] 6.2 Promote selected checks to blocking CI gates only after migration closure criteria are satisfied
- [x] 6.3 Record closeout evidence before deleting or forbidding legacy paths
