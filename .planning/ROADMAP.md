# Roadmap

## Milestones

- ✅ **v1.0 Codebase Consolidation** — Phases 1-4 (shipped 2026-04-08)
- ✅ **v1.1 Final Polish** — Phases 5-7 (shipped 2026-04-09)
- ◆ **v1.2 Lint & Test Zero** — Phases 8-11 (in progress)

## Current: v1.2 Lint & Test Zero

**Created:** 2026-04-09
**Starting Phase:** 8 (continues from v1.1 Phase 7)

### Overview

4 phases covering 10 requirements. Resolve all 699 F821 ruff errors in 45 files, fix 7 vitest failures (1 with unhandled error), and verify full zero-lint zero-failure state.

**Build order rationale:** Adapters first (heaviest at 468 errors, patterns established there apply to rest), then analysis/monitoring/gpu (mid-weight, similar missing-import patterns), then remaining F821 + vitest (lightest Python + independent frontend work), then gate verification (final proof).

---

### Phase 8: Adapters F821 Resolution

**Goal:** Resolve all 468 F821 errors in src/adapters/ (15 files) by adding missing imports.

#### Requirements

LINT-05

#### Success Criteria

1. `ruff check src/adapters/ --select F821 --statistics` reports 0 F821 errors
2. `python -c "import src.adapters.akshare.index_daily; import src.adapters.financial.stock_daily"` (and 13 other adapter modules) — no ImportError
3. `ruff check src/adapters/ --statistics | grep -v F821` — no new error categories introduced vs pre-phase baseline
4. `git diff --stat src/adapters/` — only import lines changed (no logic changes)

#### Approach

- Analyze each adapter file to identify missing imports (common: `pd`, `logger`, `ak`, `normalize_date`, `format_index_code_for_source`)
- Group files by adapter (akshare vs financial) — likely share the same missing import patterns
- Add correct imports at module top, respecting import order conventions (stdlib → third-party → local)
- Verify per-file after changes

---

### Phase 9: Analysis + Monitoring + GPU F821

**Goal:** Resolve all F821 errors in src/advanced_analysis/ (91 errors, 10 files), src/monitoring/ (83 errors, 8 files), and src/gpu/ (46 errors, 6 files).

#### Requirements

LINT-06, LINT-07, LINT-08

#### Success Criteria

1. `ruff check src/advanced_analysis/ --select F821 --statistics` reports 0 errors
2. `ruff check src/monitoring/ --select F821 --statistics` reports 0 errors
3. `ruff check src/gpu/ --select F821 --statistics` reports 0 errors
4. `ruff check src/ --select F821 --statistics` reports ≤131 errors (699 − 468 − 91 − 83 − 46 = remaining only)
5. `git diff --stat src/advanced_analysis/ src/monitoring/ src/gpu/` — only import lines and function signature changes (no logic changes)

#### Approach

- Apply same import-resolution patterns from Phase 8 to these directories
- Some files have non-mechanical F821 errors (variables used outside scope) — fix by adding missing parameters to function signatures
- Conditional dependencies (SNOWNLP, jieba) use try/except ImportError + AVAILABLE flag pattern
- Cross-module types imported from canonical locations only (no local stubs)
- Process by directory: advanced_analysis first (most complex, has non-mechanical errors), then monitoring, then gpu
- Verify per-directory after changes

---

### Phase 10: Remaining F821 + Vitest Fixes

**Goal:** Resolve final 11 F821 errors in remaining directories (6 files), fix 7 vitest test failures (1 with unhandled error).

#### Requirements

LINT-09, VTEST-01, VTEST-02, VTEST-03

#### Success Criteria

1. `ruff check src/ --select F821 --statistics` reports 0 F821 errors (all 45 files clean)
2. `cd web/frontend && npx vitest run tests/unit/config/chart-component-style-normalization.spec.ts tests/unit/config/chart-style-sources.spec.ts tests/unit/config/charts-use-pro-k-line-chart-types-cleanup.spec.ts tests/unit/config/indicator-selector-types-cleanup.spec.ts --reporter=verbose 2>&1 | tail -5` — shows "X passed", 0 failed
3. `cd web/frontend && npx vitest run src/views/artdeco-pages/system-tabs/__tests__/ --reporter=verbose 2>&1 | tail -5` — shows "X passed", 0 failed
4. `cd web/frontend && npx vitest run 2>&1 | grep -c "Unhandled"` returns exit code 1 (no matches)

#### Approach

**F821 (6 files):** Apply same pattern — identify missing imports, add correct ones.

**Vitest (4 chart tests):** Investigate what changed in chart styles/type cleanup. Tests assert ArtDeco token namespace / ts-nocheck absence — likely source files regressed or tests need updating to match current state.

**Vitest (2 system tests):** Fix `monitoringApi.getSystemGeneralSettings is not a function` — likely missing mock or API method. Fix batch status update test similarly.

**Unhandled error:** Resolve the TypeError by ensuring proper mock setup in ArtDecoSystemSettings.spec.ts.

---

### Phase 11: Gate Verification

**Goal:** Prove full F821 zero and full vitest pass with clean verification.

#### Requirements

GATE-01, GATE-02

#### Success Criteria

1. `ruff check src/ --select F821 --statistics` reports 0 F821 errors (GATE-01)
2. `cd web/frontend && npx vitest run --reporter=verbose 2>&1 | tail -10` — zero failures, zero unhandled errors (GATE-02)
3. `ruff check src/ --statistics` — total error count not higher than pre-milestone baseline (excluding F821)
4. `git diff --stat src/` — changes limited to import blocks only (no logic regressions)

#### Approach

- Run full verification suite
- Document final error counts for all quality gates
- If any failures found, triage and fix before declaring complete

---

### Phase Summary

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 8 | Adapters F821 | Resolve 468 errors in 15 adapter files | LINT-05 | 5 |
| 9 | Analysis + Monitoring + GPU | Resolve 220 errors in 24 files | LINT-06, LINT-07, LINT-08 | 5 |
| 10 | Remaining + Vitest | Resolve 11 errors + fix 7 test failures | Complete    | 2026-04-10 |
| 11 | Gate Verification | Prove full zero state | GATE-01, GATE-02 | 4 |

**Coverage:** 10/10 requirements mapped ✓

---

## Completed

<details>
<summary>✅ v1.0 Codebase Consolidation (Phases 1-4) — SHIPPED 2026-04-08</summary>

- [x] Phase 1: Python Lint Baseline (1 plan)
- [x] Phase 2: Dead Code Inventory & Removal (4 plans)
- [x] Phase 3: Structural Consolidation (2 plans)
- [x] Phase 4: Naming Polish (3 plans)

See [v1.0-ROADMAP.md](milestones/v1.0-ROADMAP.md) for details.

</details>

<details>
<summary>✅ v1.1 Final Polish (Phases 5-7) — SHIPPED 2026-04-09</summary>

- [x] Phase 5: Composables Disposition (1 plan)
- [x] Phase 6: Archive Cleanup (2 plans)
- [x] Phase 7: Entry Consolidation (2 plans)

See [v1.1-ROADMAP.md](milestones/v1.1-ROADMAP.md) for details.

</details>

---
*Last updated: 2026-04-09*
