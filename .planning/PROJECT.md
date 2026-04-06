# MyStocks Codebase Consolidation

## What This Is

A structured cleanup initiative for the MyStocks quantitative trading platform codebase. The goal is to eliminate code/file redundancy, resolve feature divergence, and establish a clear mainline with zero dead code, consistent naming, and a single source of truth for each concern. This is not a feature project — it is a technical debt remediation effort targeting 12 documented issues across Python backend and Vue 3 frontend.

## Core Value

Every file in the codebase has exactly one canonical location, every import resolves cleanly, and `ruff check` / `stylelint` / `pytest` pass with zero errors.

## Requirements

### Validated

<!-- Existing capabilities confirmed working by codebase map. -->

- ✓ Market data fetching via akshare/efinance/TDX adapters — existing
- ✓ TDengine + PostgreSQL dual-database data layer — existing
- ✓ FastAPI backend with 205 route files — existing
- ✓ Vue 3 + Pinia frontend with ArtDeco design system — existing
- ✓ Unified Manager entry point — existing
- ✓ Real data mode (USE_MOCK_DATA=False) — existing

### Active

- [ ] Eliminate duplicate adapter layer (src/interfaces/adapters/ → resolve vs src/adapters/)
- [ ] Fix frontend case-conflict directories (Charts/ vs charts/ etc.)
- [ ] Auto-fix all ruff errors (target: <50 from ~1,456)
- [ ] Merge overlapping data access layers into single canonical layer
- [ ] Consolidate routes (remove src/routes/ + src/api/ dead code)
- [ ] Clean frontend entry points (remove 7 extra main-*.js/ts variants)
- [ ] Fix frontend structural mess (artdeco-pages monolith, misplaced composables, dead views)
- [ ] Resolve root-level shim chains (core.py, data_access.py, monitoring.py)
- [ ] Fix naming conventions (calcu/, part1/part2/part3, *_new.py, *_backup files)
- [ ] Consolidate overlapping stores (market.ts vs marketData.ts, trading.ts vs tradingData.ts)

### Out of Scope

- Mock data relocation or removal — keep as-is, useful for testing
- New feature development — this is cleanup only
- Performance optimization — out of scope unless caused by duplicate code
- Mobile/responsive adaptation — desktop-only per project constraints
- API versioning changes — routes consolidation is structural only

## Context

### Brownfield Project

This is an existing codebase with:
- **Python**: 38 sub-directories in src/, 530 Python files in web/backend/app/
- **Vue 3**: 908 .vue+.ts files in web/frontend/src/
- **Tests**: 908 test files (quality issues documented)
- **Known Issues**: 12 issues documented in `.planning/codebase/CONCERNS.md` (P0: 2, P1: 3, P2: 5, Low: 2)
- **Current ruff errors**: ~1,456 (46% auto-fixable, 80%+ caused by duplicate adapters)

### Architecture

Layered architecture: Frontend (Vue 3) → Backend API (FastAPI) → Core Business (src/) → Data Layer (TDengine + PostgreSQL). See `.planning/codebase/ARCHITECTURE.md` for full details.

## Constraints

- **Zero-breakage**: Every phase must leave the system fully working. No temporary breakage allowed.
- **Deletion approval**: All dead code deletion must be saved as an MD document for user review before any files are removed.
- **Desktop-only**: No mobile/responsive changes.
- **STANDARDS.md compliance**: All changes must comply with `architecture/STANDARDS.md`.
- **Port discipline**: Backend 8020, Frontend 3020 (from .env).

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Lint first, structure after | Fixing adapters eliminates 500+ F821 errors, giving clean baseline for structural work | — Pending |
| Zero-breakage per phase | User requires system fully working at every phase boundary | — Pending |
| Dead code: review-before-delete | User wants deletion list as MD document for approval before any removal | — Pending |
| Mock files: keep as-is | 66 mock files not blocking anything, useful for dev/testing | — Pending |
| Skip domain research | Brownfield cleanup — no new domain to research, all issues already documented | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-06 after initialization*
