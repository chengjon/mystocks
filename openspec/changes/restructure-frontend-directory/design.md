## Context

> **设计方案说明**:
> 本文件用于记录某项变更的设计思路、结构拆分、实现取舍或技术路径，属于方案设计层材料。
> 它不是共享规则正文，也不直接代表当前仓库已落地状态；落地判断应结合 `architecture/STANDARDS.md`、对应 proposal/tasks、审批结果与实际代码验证。


The existing `web/frontend/src/views` directory contains over 250 Vue page components spread across many loosely-organized sub-folders (artdeco-pages, demo, advanced-analysis, market, strategy, risk, etc.). This creates several problems:

1. **Duplication** – 13 groups of same-named pages with different implementations (e.g., `BacktestAnalysis.vue` in two locations).
2. **Routing friction** – Only 35 of 252 pages are connected to the main router; 217 are orphaned.
3. **Boundary blur** – Reusable UI components and composables are mixed with page-level code under `views/shared/`, making it unclear what is a "page" vs a "utility".
4. **Maintenance burden** – Adding new features requires navigating a fragmented structure; no clear domain boundaries.

This change implements a **domain-driven directory layout** and extracts shared assets to a true `src/shared/` layer, aligning with the project's "boundary clarification" goal (STANDARDS.md §71).

## Goals

- **Domain-driven layout** – Each top-level folder under `src/views/` corresponds to a business capability (market, data, strategy, trade, risk, watchlist, system).
- **True shared layer** – All reusable components and composables live under `src/shared/`, outside of `views/`.
- **Zero-duplicate routing** – Each URL maps to exactly one Vue component; no orphaned pages.
- **Dependency clarity** – Every file move includes its local dependencies (composables, styles); no broken imports.
- **Gate-process compliance** – The migration respects the project's approval and smoke-test requirements (STANDARDS.md §10, §11, §56).

## Non-Goals

- Refactoring component internals (e.g., splitting large components into smaller ones) – that is a separate effort.
- Changing the API contract or data flow – only file organization changes.
- Removing deprecated pages immediately – they are moved to `src/views/deprecated/` and archived for one release cycle before deletion.

## Decisions

### 1. Use `git mv` for all file moves
**Why**: Preserves commit history and makes it easier to track changes and blame.
**Alternative**: Copy + delete (loses history).

### 2. Keep `src/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue`
**Why**: It is still required by `ArtDecoRiskManagement.vue` (now `risk/Center.vue`).
**Alternative**: Refactor the dependent page to remove the import (higher risk, out of scope).

### 3. Move shared assets to `src/shared/` (not `src/views/shared/`)
**Why**: Eliminates the "page vs component" ambiguity; makes it clear that shared assets are utilities, not pages.
**Alternative**: Keep them under `views/shared/` (perpetuates the boundary blur).

### 4. Use absolute imports (`@/shared/...`) for all shared assets
**Why**: Prevents relative-path breakage if pages are moved again in the future.
**Alternative**: Relative imports (brittle; breaks if directory depth changes).

### 5. Deprecate (not delete) old pages immediately
**Why**: Allows one release cycle for users to migrate; reduces risk of breaking external scripts.
**Alternative**: Delete immediately (higher risk; may break undocumented integrations).

## Risks & Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| Import paths become stale after a move | Build failure, broken routing | Run `npm run lint && npm run type-check` after each file move; use IDE refactoring tools. |
| Route table out-of-sync with file structure | Navigation 404s | After migration, run a script that verifies every file under `src/views/` appears in the router config. |
| Human error in merge-duplicate cases | Lost functionality | Create a small checklist for each duplicate: compare exported names, run visual diff, run component unit test. |
| Smoke test suite incomplete | Regressions slip through | Expand smoke test coverage to include all domain pages; run E2E suite as well. |
| Staging deployment fails | Rollback required | Test the migration locally first; run full CI pipeline before merging. |

## Migration Plan

### Phase 0 – Freeze & Planning (1 day)
- Add git pre-commit hook to block new `.vue` files under `src/views/` not in the migration table.
- Validate the OpenSpec change package.
- Create a tracking document to log completed moves.

### Phase 1 – Governance & Approval (1–2 days)
- Submit PR with OpenSpec change to Architecture Board.
- Obtain explicit sign-off from Architecture Lead and Front-end Lead.
- Verify no conflicting changes in `openspec/changes/`.

### Phase 2 – Shared Asset Extraction (3 days)
- Create target directories: `src/shared/components/` and `src/shared/composables/`.
- Move all files from `src/views/shared/*` to `src/shared/*` (use `git mv`).
- Update all imports from `@/views/shared/...` to `@/shared/...`.
- Run lint & type-check; commit.

### Phase 3 – Page Migration by Domain (7 days)
- **3a – Market** (1 day): Move 6 pages + dependencies.
- **3b – Data** (1 day): Move 1 page + dependencies.
- **3c – Watchlist** (1 day): Move 3 pages + dependencies.
- **3d – Strategy** (1 day): Move 4 pages + dependencies.
- **3e – Trade** (1 day): Move 5 pages + dependencies.
- **3f – Risk** (1 day): Move 5 pages + dependencies.
- **3g – System** (1 day): Move 4 pages + dependencies.

Each sub-phase follows the same pattern:
1. Move source file to target location (use `git mv`).
2. Move any local dependencies (composables, styles) to `src/shared/`.
3. Update all imports in the moved file.
4. Run `npm run lint && npm run type-check`.
5. Commit with a domain-specific message (e.g., "refactor: migrate market domain pages").

### Phase 4 – Routing & Layout (2 days)
- Update `src/router/index.ts` to reflect new paths.
- Remove stale route entries.
- Run `npm run dev` and manually test navigation.
- Commit.

### Phase 5 – Testing (2 days)
- Run `npm run test:smoke` and fix failures.
- Run `npm run test:e2e` and fix regressions.
- Generate test reports.

### Phase 6 – Code Review (1 day)
- Front-end Lead posts "Ready for Review".
- Run comprehensive review and security review using the currently available local tooling/runtime.
- Address feedback; obtain final approval.

### Phase 7 – Merge & Deploy (1 day)
- Merge PR to `main`.
- Trigger CI pipeline; verify staging deployment.

### Phase 8 – Post-Deployment & Archive (1 day)
- Run smoke suite against staging.
- Verify all URLs resolve.
- Run `openspec archive restructure-frontend-directory --yes`.
- Update documentation.

**Total**: ≈ 21 working days (≈ 3 calendar weeks).

## Open Questions

1. **Should we delete deprecated pages immediately or keep them for one release cycle?**
   → Recommendation: Keep for one release cycle (lower risk).

2. **Should we add new unit tests for moved components?**
   → Recommendation: Yes, if coverage drops below 80%.

3. **Should we update the main navigation menu to reflect the new domain structure?**
   → Recommendation: Yes, as part of Phase 4 (routing updates).

4. **How do we handle external scripts that reference old page paths?**
   → Recommendation: Add a deprecation notice in the changelog; provide a migration guide.
