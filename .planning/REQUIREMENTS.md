# Requirements: MyStocks Codebase Consolidation

**Defined:** 2026-04-09
**Core Value:** Every file has exactly one canonical location, every import resolves cleanly, and `ruff check` / `stylelint` / `pytest` pass with zero errors.

## v1.2 Requirements

Requirements for Lint & Test Zero milestone. Each maps to roadmap phases.

### F821 Resolution

- [x] **LINT-05**: All F821 errors in src/adapters/ resolved
  - **Baseline:** 468 errors in 15 files (2026-04-09)
  - **Verification:** `ruff check src/adapters/ --select F821`
  - **Pass condition:** Zero output (F821 count = 0)

- [x] **LINT-06**: All F821 errors in src/advanced_analysis/ resolved
  - **Baseline:** 91 errors in 10 files (2026-04-09)
  - **Verification:** `ruff check src/advanced_analysis/ --select F821`
  - **Pass condition:** Zero output (F821 count = 0)
  - **Completed:** 2026-04-10 (Phase 09)

- [x] **LINT-07**: All F821 errors in src/monitoring/ resolved
  - **Baseline:** 83 errors in 8 files (2026-04-09)
  - **Verification:** `ruff check src/monitoring/ --select F821`
  - **Pass condition:** Zero output (F821 count = 0)
  - **Completed:** 2026-04-10 (Phase 09)

- [x] **LINT-08**: All F821 errors in src/gpu/ resolved
  - **Baseline:** 46 errors in 6 files (2026-04-09)
  - **Verification:** `ruff check src/gpu/ --select F821`
  - **Pass condition:** Zero output (F821 count = 0)
  - **Completed:** 2026-04-10 (Phase 09)

- [x] **LINT-09**: All F821 errors in remaining directories resolved
  - **Baseline:** 11 errors in 6 files (2026-04-09)
  - **Scope:** alternative_data (2), core (1), database (1), governance (1), storage (1)
  - **Specific files:**
    - src/alternative_data/_news_sentiment_service_helper.py
    - src/alternative_data/news_sentiment_analyzer.py
    - src/core/data_source/config_manager.py
    - src/database/service/adapter_queries.py
    - src/governance/risk_management/services/alert_rule_engine.py
    - src/storage/database/database_manager/database_table_manager_methods/close_all_connections.py
  - **Verification:** `ruff check src/alternative_data/ src/core/ src/database/ src/governance/ src/storage/ --select F821`
  - **Pass condition:** Zero output (F821 count = 0)
  - **Completed:** 2026-04-10 (Phase 10)

### Vitest Fixes

- [x] **VTEST-01**: Chart style and type cleanup tests pass
  - **Baseline:** 4 failing test files (2026-04-09)
  - **Scope:**
    - tests/unit/config/chart-component-style-normalization.spec.ts
    - tests/unit/config/chart-style-sources.spec.ts
    - tests/unit/config/charts-use-pro-kline-chart-types-cleanup.spec.ts
    - tests/unit/config/indicator-selector-types-cleanup.spec.ts
  - **Verification:** `cd web/frontend && npx vitest run tests/unit/config/chart-component-style-normalization.spec.ts tests/unit/config/chart-style-sources.spec.ts tests/unit/config/charts-use-pro-kline-chart-types-cleanup.spec.ts tests/unit/config/indicator-selector-types-cleanup.spec.ts`
  - **Pass condition:** All 4 test files pass with zero failures
  - **Completed:** 2026-04-10 (Phase 10)

- [x] **VTEST-02**: ArtDeco system settings tests pass
  - **Baseline:** 2 failing test files (2026-04-09)
  - **Scope:**
    - src/views/artdeco-pages/system-tabs/__tests__/ArtDecoDataManagement.spec.ts
    - src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts
  - **Verification:** `cd web/frontend && npx vitest run src/views/artdeco-pages/system-tabs/__tests__/`
  - **Pass condition:** Both test files pass with zero failures
  - **Completed:** 2026-04-10 (Phase 10)

- [x] **VTEST-03**: Unhandled error in vitest resolved
  - **Baseline:** 1 unhandled rejection (TypeError: monitoringApi.getSystemGeneralSettings is not a function) co-occurring with ArtDecoSystemSettings.spec.ts failure (2026-04-09)
  - **Verification:** `cd web/frontend && npx vitest run 2>&1 | grep -c "Unhandled"`
  - **Pass condition:** grep returns exit code 1 (zero matches)
  - **Completed:** 2026-04-10 (Phase 10)

### Milestone Gate

- [x] **GATE-01**: Full F821 zero achieved
  - **Verification:** `ruff check src/ --select F821 --statistics`
  - **Pass condition:** Zero F821 errors reported
  - **Completed:** 2026-04-10 (Phase 11)

- [x] **GATE-02**: Full vitest pass achieved
  - **Verification:** `cd web/frontend && npx vitest run`
  - **Pass condition:** All test files pass, zero failures, zero unhandled errors
  - **Completed:** 2026-04-10 (Phase 11) — 231 files, 840 tests, all passed

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

(None identified — this milestone targets full lint/test zero)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Non-F821 ruff errors | ~164 remaining (other codes); out of scope for this milestone |
| New feature development | Cleanup only — no new features |
| Performance optimization | Out of scope unless caused by missing imports |
| Backend test (pytest) fixes | Separate concern; not in scope |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| LINT-05 | Phase 8 | Complete |
| LINT-06 | Phase 9 | Complete |
| LINT-07 | Phase 9 | Complete |
| LINT-08 | Phase 9 | Complete |
| LINT-09 | Phase 10 | Complete |
| VTEST-01 | Phase 10 | Complete |
| VTEST-02 | Phase 10 | Complete |
| VTEST-03 | Phase 10 | Complete |
| GATE-01 | Phase 11 | Complete |
| GATE-02 | Phase 11 | Complete |

**Coverage:**
- v1.2 requirements: 10 total
- Mapped to phases: 10
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-09*
*Last updated: 2026-04-10 — All requirements marked complete; v1.2 shipped*
