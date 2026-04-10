# Adjudication: implement-pinia-api-standardization

> **治理裁定说明**:
> 本文件用于记录 2026-04-10 对 `implement-pinia-api-standardization` 的当前治理判断。
> 共享规则仍以 `architecture/STANDARDS.md` 为准；本文件只回答该 active change 是否应继续保留，以及应如何理解其边界。

## Decision

Keep `implement-pinia-api-standardization` active, but treat it as a partially executed standardization line rather than a completed migration.

## Why It Should Stay

- The change is structurally valid: `openspec validate implement-pinia-api-standardization --strict` passes.
- Current repo evidence shows real foundational implementation already exists:
  - `web/frontend/src/stores/storeFactory.ts`
  - `web/frontend/src/api/unifiedApiClient.ts`
  - `web/frontend/src/stores/apiStores.ts`
  - `web/frontend/src/stores/__tests__/store-factory.spec.ts`
- Its scope is still meaningful: it governs the frontend pattern for API-oriented Pinia stores, not a stale historical roadmap.

## Why It Must Not Be Read As Complete

Current repo truth shows Phase 1 style infrastructure exists, but the broader migration remains incomplete:

- `auth.ts` still uses a hybrid pattern rather than a clean fully standardized store flow.
- The change promised broader store migration, cleanup, E2E/integration verification, and performance closure that are not evidenced as complete.
- `unifiedApiClient.ts` now acts as a legacy wrapper to `apiClient.ts`, which means the original proposal text no longer matches the current layering exactly.
- Proposal/tasks/spec files also contain tool-residue fragments, so they should not be treated as exact implementation truth.

## Relationship To Current Frontend Trunks

- This change complements the current frontend API / state management line.
- It should not be interpreted as a mandate to rewrite every store immediately.
- It remains useful as the canonical active line for standardizing factory-based API stores where that pattern still brings convergence.

## Execution Rule For Future Sessions

- Do not retire this change as stale.
- Do not mark it completed from the existence of factory utilities alone.
- Do not continue the original checklist mechanically.
- If execution resumes, first restate remaining current-truth scope:
  - identify which stores are canonical candidates for factory migration
  - decide where hybrid stores like `auth.ts` should stay custom
  - verify whether realtime, cache, and wrapper abstractions still match current frontend architecture
  - add modern verification only for the remaining migration slice, not for the already-landed base infrastructure
