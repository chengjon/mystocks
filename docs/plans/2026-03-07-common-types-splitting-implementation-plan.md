# Frontend Common Types Splitting Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Split `web/frontend/src/api/types/common/all.ts` into domain-based type modules and reduce `all.ts` to a compatibility re-export layer.

**Architecture:** Keep all existing consumer import paths working while moving inline types into domain modules. Reuse the current domain layout, add only the minimum extra modules needed, and make both `common.ts` and `common/all.ts` thin re-export files.

**Tech Stack:** TypeScript, Vue 3, Vitest, vue-tsc

---

### Task 1: Add a failing structure test for `all.ts`

**Files:**
- Create: `web/frontend/tests/unit/common-types-structure.spec.ts`
- Modify: none
- Test: `web/frontend/tests/unit/common-types-structure.spec.ts`

**Step 1: Write the failing test**
- Assert `web/frontend/src/api/types/common/all.ts` does not contain inline `export interface` or `export type` definitions.
- Assert it contains re-export statements pointing at domain files.

**Step 2: Run test to verify it fails**
- Run: `npm --prefix web/frontend run test -- tests/unit/common-types-structure.spec.ts`
- Expected: FAIL because `all.ts` still contains inline definitions.

### Task 2: Move remaining type definitions into domain files

**Files:**
- Modify: `web/frontend/src/api/types/domains/system-base.ts`
- Modify: `web/frontend/src/api/types/domains/market-data.ts`
- Modify: `web/frontend/src/api/types/domains/trading-ops.ts`
- Modify: `web/frontend/src/api/types/domains/strategy-types.ts`
- Create: `web/frontend/src/api/types/domains/monitoring-alerts.ts`

**Step 1: Add missing types to each domain**
- Copy remaining inline contracts out of `all.ts` into the correct domain file.
- Add cross-domain imports where one type references another.

**Step 2: Keep dependencies explicit**
- Replace accidental implicit ordering with explicit `import type` between domain files.

### Task 3: Convert `all.ts` into a compatibility layer

**Files:**
- Modify: `web/frontend/src/api/types/common/all.ts`
- Modify: `web/frontend/src/api/types/common.ts`

**Step 1: Rewrite `all.ts`**
- Remove inline definitions.
- Replace them with domain re-exports only.

**Step 2: Finalize `common.ts`**
- Re-export full domain surface from thin entrypoint.
- Keep comments warning new code away from `all.ts`.

### Task 4: Verify compile and compatibility

**Files:**
- Test: `web/frontend/tests/unit/common-types-structure.spec.ts`
- Test: `web/frontend/tests/unit/use-strategy.spec.ts` (spot-check only if impacted)

**Step 1: Run focused structure test**
- Run: `npm --prefix web/frontend run test -- tests/unit/common-types-structure.spec.ts`

**Step 2: Run frontend type-check**
- Run: `npm --prefix web/frontend run type-check`
- Expected: no structural syntax errors; error count does not exceed baseline `reports/analysis/tech-debt-baseline.json`.

**Step 3: Spot-check known consumers if needed**
- Run a small subset of unit tests only if the refactor touches their imported types.
