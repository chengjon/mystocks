# Frontend Directory Restructure – Phase 1 Governance & Approval

**Status**: READY FOR ARCHITECTURE BOARD REVIEW
**Date**: 2026-03-02
**Change ID**: `restructure-frontend-directory`

---

## Executive Summary

The MyStocks frontend codebase contains **>250 Vue pages** scattered across a fragmented directory structure, causing:
- **Duplication** – 13 groups of same-named pages with different implementations
- **Routing friction** – Only 35 of 252 pages connected to the main router
- **Boundary blur** – Shared components/composables mixed with page-level code
- **Maintenance burden** – No clear domain boundaries

This OpenSpec change proposes a **domain-driven directory restructure** that:
1. Organizes pages into 8 business-capability domains (market, data, strategy, trade, risk, watchlist, system, errors)
2. Extracts shared assets to `src/shared/` (outside of `views/`)
3. Moves 58 legacy pages to `deprecated/` (read-only archive)
4. Updates ~100+ import statements and router configuration
5. Runs full smoke & E2E test suite to verify migration

**Effort**: 26 person-days (≈ 3.5 weeks)
**Risk**: Medium (coordinated file moves, import rewrites, routing changes)
**Approval Required**: Architecture Lead, Front-end Lead, Security Reviewer

---

## OpenSpec Change Package

All change artifacts are located in `openspec/changes/restructure-frontend-directory/`:

### 1. Proposal (`proposal.md`)
- **Why**: Addresses fragmentation, duplication, and boundary-blur issues
- **What**: Domain-driven layout + shared asset extraction
- **Impact**: All routing URLs change; breaking change until migration completes
- **Approval**: Requires Architecture Board sign-off

### 2. Tasks (`tasks.md`)
- **19 phases** with 100+ ordered sub-tasks
- **Phase 0** (Freeze & Planning) – ✅ COMPLETE
- **Phase 1** (Governance & Approval) – 🔄 IN PROGRESS
- **Phases 2–9** (Implementation, testing, deployment, archive) – ⏳ Pending

### 3. Design (`design.md`)
- **Context**: Current state, problems, goals
- **Decisions**: Use `git mv`, keep template, move shared assets to `src/shared/`, use absolute imports
- **Risks & Mitigations**: Import staleness, route table sync, duplicate merges, test coverage
- **Migration Plan**: 8-phase roadmap with timelines

### 4. Spec Deltas (`specs/frontend-structure/spec.md`)
- **MODIFIED**: Front-end directory layout requirement
- **ADDED**: Shared asset location requirement, deprecation process requirement, template retention requirement
- **REMOVED**: Orphaned pages in root views, shared assets under views/shared/

### Validation
✅ `openspec validate restructure-frontend-directory --strict` – **PASSED**

---

## New Directory Structure

### Before (Current State)
```
src/views/
├── artdeco-pages/           (86 pages – main business logic)
├── root level               (44 orphaned pages)
├── demo/                    (25 demo pages)
├── advanced-analysis/       (13 analysis pages)
├── converted.archive/       (9 archived pages)
├── market/                  (8 pages)
├── strategy/                (6 pages)
├── risk/                    (5 pages)
├── trading/                 (5 pages)
├── system/                  (4 pages)
├── settings/                (4 pages)
├── monitoring/              (3 pages)
├── stock-analysis/          (6 pages)
├── trade-management/        (5 pages)
├── trading-decision/        (3 pages)
├── stocks/                  (6 pages)
├── technical/               (2 pages)
├── errors/                  (3 pages)
├── examples/                (3 pages)
├── freqtrade-demo/          (6 pages)
├── tdxpy-demo/              (5 pages)
└── shared/                  (components + composables mixed with pages)
```

### After (Proposed State)
```
src/views/
├── market/                  (7 pages: Overview, Realtime, Technical, Concepts, CapitalFlow, ETF, Auction)
├── data/                    (6 pages: Overview, Advanced, Industry, Concepts, FundFlow, Indicator)
├── strategy/                (7 pages: List, Workbench, Backtest, Optimization, Parameters, Results, Stats)
├── trade/                   (4 pages: Center, Signals, Portfolio, History)
├── risk/                    (5 pages: Center, Overview, Alerts, StopLoss, News)
├── watchlist/               (3 pages: Manage, Screener, Signals)
├── system/                  (6 pages: Settings, Health, API, DataSource, Performance, Database)
├── errors/                  (3 pages: 404, 403, 500)
└── deprecated/              (58 legacy pages – read-only archive)
    ├── demo/                (25 demo pages)
    ├── archive/             (9 archived pages)
    ├── examples/            (3 example pages)
    ├── freqtrade-demo/      (6 freqtrade pages)
    └── tdxpy-demo/          (5 tdxpy pages)

src/shared/
├── components/              (reusable UI components)
├── composables/             (reusable Vue composables)
└── styles/                  (shared SCSS files)
```

---

## Key Metrics

| Metric | Value |
|--------|-------|
| **Total Vue pages** | 252 |
| **Pages to move** | 27 (main) + 58 (deprecated) = 85 |
| **Shared assets to extract** | ~20 components + ~10 composables |
| **Import statements to update** | ~100+ |
| **Domain folders** | 8 (market, data, strategy, trade, risk, watchlist, system, errors) |
| **Effort estimate** | 26 person-days (≈ 3.5 weeks) |
| **Critical path** | Phases 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 |
| **Parallel opportunities** | Phases 3a–3g (7 domain migrations) |

---

## Phase Breakdown

### Phase 0 – Freeze & Planning (1 day) ✅ COMPLETE
- [x] Add git pre-commit hook to block new `.vue` files not in migration table
- [x] Validate OpenSpec change package
- [x] Create tracking document

### Phase 1 – Governance & Approval (1–2 days) 🔄 IN PROGRESS
- [ ] Submit PR to Architecture Board for review
- [ ] Obtain explicit sign-off from Architecture Lead
- [ ] Obtain sign-off from Front-end Lead
- [ ] Verify no conflicting changes in `openspec/changes/`

### Phase 2 – Shared Asset Extraction (3 days) ⏳ Pending
- [ ] Create target directories: `src/shared/components/` and `src/shared/composables/`
- [ ] Move all files from `src/views/shared/*` to `src/shared/*`
- [ ] Update all imports from `@/views/shared/...` to `@/shared/...`
- [ ] Run lint & type-check; commit

### Phase 3 – Page Migration by Domain (7 days) ⏳ Pending
- [ ] **3a – Market** (1 day): Move 6 pages + dependencies
- [ ] **3b – Data** (1 day): Move 1 page + dependencies
- [ ] **3c – Watchlist** (1 day): Move 3 pages + dependencies
- [ ] **3d – Strategy** (1 day): Move 4 pages + dependencies
- [ ] **3e – Trade** (1 day): Move 5 pages + dependencies
- [ ] **3f – Risk** (1 day): Move 5 pages + dependencies
- [ ] **3g – System** (1 day): Move 4 pages + dependencies

### Phase 4 – Routing & Layout (2 days) ⏳ Pending
- [ ] Update `src/router/index.ts` to reflect new paths
- [ ] Remove stale route entries
- [ ] Run `npm run dev` and manually test navigation

### Phase 5 – Testing (2 days) ⏳ Pending
- [ ] Run `npm run test:smoke` and fix failures
- [ ] Run `npm run test:e2e` and fix regressions
- [ ] Generate test reports

### Phase 6 – Code Review (1 day) ⏳ Pending
- [ ] Front-end Lead posts "Ready for Review"
- [ ] Run `oh-my-claudecode:code-reviewer` and `security-reviewer` agents
- [ ] Address feedback; obtain final approval

### Phase 7 – Merge & Deploy (1 day) ⏳ Pending
- [ ] Merge PR to `main`
- [ ] Trigger CI pipeline; verify staging deployment

### Phase 8 – Post-Deployment & Archive (1 day) ⏳ Pending
- [ ] Run smoke suite against staging
- [ ] Verify all URLs resolve
- [ ] Run `openspec archive restructure-frontend-directory --yes`
- [ ] Update documentation

### Phase 9 – Cleanup & Verification (1 day) ⏳ Pending
- [ ] Final lint check
- [ ] Verify no orphaned pages
- [ ] Close related issues
- [ ] Post final summary

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| Import paths become stale after a move | Build failure | Medium | Run `npm run lint && npm run type-check` after each move; use IDE refactoring |
| Route table out-of-sync with file structure | Navigation 404s | Medium | Verify every file appears in router config; run smoke tests |
| Human error in merge-duplicate cases | Lost functionality | Low | Create checklist for each duplicate; run unit tests |
| Smoke test suite incomplete | Regressions slip through | Low | Expand coverage; run E2E suite |
| Staging deployment fails | Rollback required | Low | Test locally first; run full CI before merge |

---

## Approval Checklist

### Architecture Lead
- [ ] Review the domain-driven design
- [ ] Verify gate-process compliance (STANDARDS.md §10, §11, §56)
- [ ] Approve the effort estimate (26 person-days)
- [ ] Sign-off: "APPROVED"

### Front-end Lead
- [ ] Review the migration plan
- [ ] Verify feasibility and resource availability
- [ ] Confirm no conflicts with ongoing work
- [ ] Sign-off: "APPROVED"

### Security Reviewer
- [ ] Verify no security implications
- [ ] Check for sensitive data exposure
- [ ] Confirm no breaking changes to auth/permissions
- [ ] Sign-off: "APPROVED" (or "NO SECURITY CONCERNS")

---

## Next Steps

### Immediate (Today)
1. ✅ OpenSpec change created and validated
2. ✅ Phase 0 (Freeze & Planning) complete
3. 🔄 Submit PR to Architecture Board for review

### Upon Approval (1–2 days)
4. Start Phase 2 (Shared Asset Extraction)
5. Execute Phases 3–9 following the detailed roadmap

### Post-Deployment (3.5 weeks)
6. Archive the OpenSpec change
7. Update documentation
8. Close related issues

---

## References

- **OpenSpec Change**: `openspec/changes/restructure-frontend-directory/`
- **Detailed Plan**: `frontend-directory-restructure-plan-revised.md`
- **Project Standards**: `STANDARDS.md` (§10, §11, §56, §71)
- **Project Conventions**: `AGENTS.md`
- **Directory Structure**: `docs/standards/FILE_ORGANIZATION_RULES.md`

---

## Questions?

For questions or clarifications, refer to:
- **Proposal**: `openspec/changes/restructure-frontend-directory/proposal.md`
- **Design**: `openspec/changes/restructure-frontend-directory/design.md`
- **Tasks**: `openspec/changes/restructure-frontend-directory/tasks.md`
- **Spec Deltas**: `openspec/changes/restructure-frontend-directory/specs/frontend-structure/spec.md`

---

**Status**: ✅ READY FOR ARCHITECTURE BOARD REVIEW
**Prepared**: 2026-03-02
**Change ID**: `restructure-frontend-directory`
