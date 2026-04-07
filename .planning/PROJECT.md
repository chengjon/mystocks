# MyStocks Codebase Consolidation

> **使用说明**:
> 本文件是项目入口、工作流快照、规划工件或使用说明，不是当前共享规则、当前代码实现或当前运行状态的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码、主线任务系统及验证结果一并核对。
>
> 文内步骤、范围、状态或说明如未重新复核，应按其所属上下文理解，不得直接当作跨场景通用事实。


## Current Milestone: v1.1 Final Polish

**Goal:** Resolve the remaining deferred structural items and substantially reduce F821 undefined-name errors.

**Target features:**
- STRU-03: Single frontend entry point
- STRU-04: Composables relocation
- STRU-05: Archive removal
- LINT-05: Reduce F821 ruff errors from 791 toward zero

## What This Is

A structured cleanup initiative for the MyStocks quantitative trading platform codebase. Phase 1 (v1.0) eliminated code/file redundancy, resolved feature divergence, and established a clear mainline with consistent naming and a single source of truth for each concern.

## Core Value

Every file in the codebase has exactly one canonical location, every import resolves cleanly, and `ruff check` / `stylelint` / `pytest` pass with zero errors.

## Requirements

### Validated

- ✓ Market data fetching via akshare/efinance/TDX adapters — existing
- ✓ TDengine + PostgreSQL dual-database data layer — existing
- ✓ FastAPI backend with 205 route files — existing
- ✓ Vue 3 + Pinia frontend with ArtDeco design system — existing
- ✓ Unified Manager entry point — existing
- ✓ Real data mode (USE_MOCK_DATA=False) — existing
- ✓ LINT-01: src/interfaces/adapters/ deleted (commit 9ac60b838) — v1.0
- ✓ LINT-02: Total ruff errors reduced to 877 (<900 target), then 863 after Phase 2 — v1.0
- ✓ LINT-03: W293/F841/W291 zeroed via --unsafe-fixes (206 fixes) — v1.0
- ✓ LINT-04: Frontend case-conflict directories merged (Charts→charts) — v1.0
- ✓ DEAD-01: src/routes/ (19 files) removed — v1.0
- ✓ DEAD-02: src/api/ (5 files) removed — v1.0
- ✓ DEAD-03: src/data_access_pkg/ merged into src/data_access/ — v1.0
- ✓ DEAD-04: src/db_manager/ removed — v1.0
- ✓ DEAD-05: src/database_optimization/ merged into src/data_access/ — v1.0
- ✓ DEAD-06: DELETION-CANDIDATES.md review-before-delete process — v1.0
- ✓ STRU-01: Single canonical data access layer verified — v1.0
- ✓ STRU-02: All import paths updated to canonical locations — v1.0
- ✓ NAME-01: src/calcu/ removed — v1.0
- ✓ NAME-02: 32 part-files renamed to semantic names — v1.0
- ✓ NAME-03: *_new.py files resolved — v1.0
- ✓ NAME-04: Root-level shims deleted (core.py, data_access.py, monitoring.py) — v1.0
- ✓ NAME-05: Pinia store domain boundaries documented — v1.0

### Active

- [ ] STRU-03: Single frontend entry point (2 files remain — verify-mount.js blocks main.js removal)
- [ ] STRU-04: views/composables/ → src/composables/ (COMPOSABLES-AUDIT.md shows 15+ imports would break)
- [ ] STRU-05: views/converted.archive/ removal (5 test files must be deleted first)
- [ ] LINT-05: Reduce F821 ruff errors from 791 (current, verified 2026-04-08)

### Out of Scope

- Mock data relocation or removal — keep as-is, useful for testing
- New feature development — this is cleanup only
- Performance optimization — out of scope unless caused by duplicate code
- Mobile/responsive adaptation — desktop-only per project constraints
- API versioning changes — routes consolidation is structural only

## Context

### Current State (post-v1.0)

Shipped v1.0 Codebase Consolidation (2026-04-08):
- **4 phases, 10 plans, ~54 commits** over 3 days
- **Python**: ~195K LOC in src/ (863 ruff errors remaining, down from 1,456)
- **Frontend**: ~192K LOC in web/frontend/src/
- **Deleted**: 34 dead files across 5 directories, 3 root shims, 1 empty directory
- **Renamed**: 32 part-files to semantic names
- **Merged**: 3 case-conflict directories, overlapping data access layers
- **Known gaps**: STRU-03/04/05 deferred with audit evidence

### Architecture

Layered architecture: Frontend (Vue 3) → Backend API (FastAPI) → Core Business (src/) → Data Layer (TDengine + PostgreSQL).

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Lint first, structure after | Fixing adapters eliminates 500+ F821 errors, giving clean baseline | ✓ Phase 1: 40% reduction |
| Zero-breakage per phase | User requires system fully working at every phase boundary | ✓ All phases verified |
| Dead code: review-before-delete | User wants deletion list as MD document for approval | ✓ DELETION-CANDIDATES.md approved |
| Mock files: keep as-is | 66 mock files not blocking anything, useful for dev/testing | ✓ Kept |
| Two-step git mv for WSL2 | Case-sensitivity requires temp path rename | ✓ Charts/ merge worked |
| Composables: no bulk move | 15+ active imports would break, per-file migration needed | ✓ Deferred with audit |
| Store domains: document, don't merge | Overlap is intentional (simple vs enhanced), document boundaries | ✓ NAME-05 complete |
| Skip domain research | Brownfield cleanup — no new domain to research | ✓ No research phase needed |

## Constraints

- **Zero-breakage**: Every phase must leave the system fully working.
- **Deletion approval**: All dead code deletion must be saved as MD document for user review.
- **Desktop-only**: No mobile/responsive changes.
- **STANDARDS.md compliance**: All changes must comply with `architecture/STANDARDS.md`.
- **Port discipline**: Backend 8020, Frontend 3020 (from .env).

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
*Last updated: 2026-04-08 after v1.1 milestone started*
