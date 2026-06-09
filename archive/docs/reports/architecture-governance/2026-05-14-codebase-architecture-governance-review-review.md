# Review: 2026-05-14-codebase-architecture-governance-review.md

**Type**: md / arch | **Perspective**: arch (auto-detected) | **Date**: 2026-05-14 | **Reviewer**: Claude

---

## Executive Summary

This architecture governance review is well-structured, evidence-grounded, and actionable. All 30+ referenced files, 8 referenced symbols, and 14+ factual claims were verified against the live codebase with high accuracy. Two quantitative claims have material discrepancies (views total file count off by ~15%, Vue files over 500 lines overcounted by ~79%). The document correctly identifies the Domain-to-Infrastructure reverse dependency and accurately maps the current OpenSpec change landscape. The "Closure-First" strategy and explicit non-goals demonstrate strong governance discipline.

## Document Metadata

| Field | Value |
|-------|-------|
| Source | `docs/reports/architecture-governance/2026-05-14-codebase-architecture-governance-review.md` |
| File Type | .md |
| Doc Type | arch (path: `architecture-governance`; content: component boundaries, data flow, coupling analysis, layered architecture) |
| Sections | 7 |
| Referenced Files | 30 found / 0 missing (4 correctly noted as non-existent) |
| Referenced Symbols | 8 found / 0 missing |

## Evidence Verification

### Files Referenced

| File | Exists? | Location |
|------|---------|----------|
| `architecture/STANDARDS.md` | yes | `architecture/STANDARDS.md` |
| `openspec/AGENTS.md` | yes | `openspec/AGENTS.md` |
| `openspec/specs/architecture-governance/spec.md` | yes | `openspec/specs/architecture-governance/spec.md` |
| `openspec/specs/directory-governance/spec.md` | yes | `openspec/specs/directory-governance/spec.md` |
| `openspec/specs/frontend-routing/spec.md` | yes | `openspec/specs/frontend-routing/spec.md` |
| `docs/guides/frontend-structure.md` | yes | `docs/guides/frontend-structure.md` |
| `.zread/wiki/versions/2026-05-14-013747/` | yes | 23 wiki markdown files present |
| `CONTEXT.md` | no (correctly stated) | N/A |
| `docs/CONTEXT.md` | no (correctly stated) | N/A |
| `docs/adr/` | no (correctly stated) | N/A |
| `docs/agents/` | no (correctly stated) | N/A |
| `web/backend/app/api/monitoring.py` | yes | verified |
| `web/backend/app/api/strategy_management/get_monitoring_db.py` | yes | verified |
| `web/backend/app/api/efinance.py` | yes | verified |
| `web/backend/app/api/tasks.py` | yes | verified |
| `web/backend/app/api/risk/alerts.py` | yes | verified |
| `scripts/generate_frontend_types.py` | yes | verified |
| `scripts/dev/generate-types/generate_ts_types.py` | yes | verified |
| `web/backend/app/api/contract/services/openapi_generator.py` | yes | verified |
| `src/domain/portfolio/service/portfolio_valuation_service.py` | yes | verified |
| `src/domain/portfolio/service/portfolio_valuation_service_optimized.py` | yes | verified |
| `src/core/data_manager.py` | yes | verified |
| `src/core/unified_manager.py` | yes | verified |
| `src/core/config_driven_table_manager.py` | yes | verified |
| `src/core/data_classification.py` | yes | verified |
| `src/core/data_source_manager_v2.py` | yes | verified (doc uses `src/core/data_source*` glob) |
| `src/core/data_source_handlers_v2.py` | yes | verified (doc uses `src/core/data_source*` glob) |

### Functions/Classes Referenced

| Symbol | Found? | Location |
|--------|--------|----------|
| `MyStocksUnifiedManager` | yes | `src/core/unified_manager.py:40` |
| `DataManager` | yes | `src/core/data_manager.py:38` |
| `DataRouter` | yes | `src/core/infrastructure/data_router.py:6` |
| `AdapterRegistry` | yes | `src/core/infrastructure/adapter_registry.py:7` (also `web/backend/app/core/adapter_factory.py:39`) |
| `TDengineDataAccess` | yes | `src/data_access/tdengine_access.py:57` |
| `PostgreSQLDataAccess` | yes | `src/data_access/postgresql_access.py:59` |
| `DataClassification` | yes | `src/core/data_classification.py` (module-level) |
| `ConfigDrivenTableManager` | yes | `src/core/config_driven_table_manager.py` (module-level) |

### Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| API dir has ~213 Python files | confirmed | `find` returns 213 |
| ~54 API files exceed 500 lines | confirmed | `wc -l` count matches |
| Services dir has ~145 Python files | confirmed | `find` returns 145 |
| ~28 service files exceed 500 lines | partially confirmed | actual count is 29 (off by 1, within "约" tolerance) |
| Views dir has ~469 related files | contradicted | actual count is 540 (off by ~71, ~15% undercount) |
| ~257 Vue files in views | confirmed | `find` returns 257 |
| ~25 Vue files exceed 500 lines | contradicted | actual count is 14 (off by 11, ~79% overcount) |
| Router `index.ts` ~414 lines | confirmed | actual is 413 |
| ~55 route paths | confirmed | actual is 57 (within "约" tolerance) |
| ~44 dynamic imports | confirmed | actual is 44 (exact match) |
| Domain imports `src.infrastructure.persistence.exceptions` | confirmed | grep found both `portfolio_valuation_service.py:17` and `portfolio_valuation_service_optimized.py:20` |
| `/dashboard` served by `ArtDecoDashboard.vue` | confirmed | router line 35 |
| `/trade/terminal` served by `TradingDashboard.vue` | confirmed | router line 219 |
| 7 active OpenSpec changes listed | confirmed | directory listing matches exactly |
| Data layer spread across 7+ directories | confirmed | all 7 directories verified with contents |

## Checklist Results

| # | Check | Result | Notes |
|---|-------|--------|-------|
| A1 | Component boundaries | PASS | Sections 3.2-3.7 clearly delineate backend API/services, frontend views/router, data layer, DDD layers, contract generation, and legacy zones |
| A2 | Data flow | PASS | Section 3.4 traces data from adapters through data_sources, data_access, storage to database; wiki symbols (MyStocksUnifiedManager -> DataManager -> DataRouter -> AdapterRegistry -> TDengineDataAccess/PostgreSQLDataAccess) all verified |
| A3 | Coupling | PASS | Section 3.5 identifies Domain -> Infrastructure reverse dependency with specific file names and line numbers verified in codebase |
| A4 | Interface contracts | PASS | Recommendations 3, 4 specify target interfaces (thin route + use-case service, Data Source Runtime, Storage Routing Runtime) |
| A5 | Scalability | N/A | Document scope is governance and cleanup, not scaling architecture |
| A6 | Terminology consistency | PASS | Terms like "深模块", "收口", "真相源", "薄路由" used consistently throughout; all terms match codebase naming |
| A7 | Backward compatibility | PASS | Section 7 explicitly lists non-goals; Section 4 recommendations all include "should create or attach to existing OpenSpec proposal" safeguards |
| A8 | Implementation surface precision | PASS | Recommendations name specific files (`monitoring.py`, `efinance.py`), specific symbols (`MyStocksUnifiedManager`, `DataClassification`), and specific directories |
| A9 | Named entities verified | PASS | All 30+ files and 8 symbols verified against live codebase; zero false references |

## Findings

### Critical Issues

None.

### Medium Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 1 | Section 3.3 | Views total file count stated as "~469" but actual count is 540 (~15% undercount) | Understates frontend complexity; could lead to underestimated governance scope | `find web/frontend/src/views -type f` returns 540, not 469. Checked by running exact command. | Update to "~540" or re-verify with specific inclusion/exclusion criteria documented |
| 2 | Section 3.3 | Vue files over 500 lines stated as "~25" but actual count is 14 | Overstates the severity of the large-view problem; could misdirect governance priority | `find ... -name "*.vue" -exec wc -l {} +` shows 14 files above 500 lines, not 25. Largest is `ArtDecoStrategyManagement.vue` at 1033 lines. | Update to "~14" or document the inclusion criteria (e.g., whether `.ts` companion files were counted) |

### Low Issues

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | Section 2.2 | `docs/agents/architecture-map.md` listed as a candidate location but `docs/agents/` directory does not exist | `Glob docs/agents/**` returns no files. The doc itself notes this directory doesn't exist but then recommends creating a file there. | If recommending `docs/agents/` as the target, note that the directory itself must be created, or prefer `CONTEXT.md` at project root as the alternative |
| 2 | Section 3.2 | Service files over 500 lines stated as "约 28" but actual count is 29 | `find web/backend/app/services -name "*.py" -exec wc -l {} +` with >500 filter returns 29 | Minor; within "约" tolerance. Update to 29 for precision |
| 3 | Section 3.4 | `AdapterRegistry` exists in two locations (`src/core/infrastructure/adapter_registry.py` and `web/backend/app/core/adapter_factory.py`) but this duality is not discussed | grep found `class AdapterRegistry` at both locations, suggesting the concept the doc highlights (scattered data-layer concepts) applies to more than just directory layout | Worth noting this specific duplicate in the data layer diagnosis to strengthen the "same concept, multiple homes" argument |
| 4 | Section 3.6 | Document lists 3 contract/type generation entries but does not mention their relative sizes or which is canonical | `scripts/generate_frontend_types.py` and `scripts/dev/generate-types/generate_ts_types.py` both exist; their relationship (wrapper vs. canonical) is unknown from the document | In Recommendation 6, consider specifying which script to audit first to determine canonicity |

## Strengths

- **Exceptional evidence grounding**: Every structural claim references specific file paths, line counts, or symbol names. All verified files exist; all verified symbols resolve. Zero phantom references.
- **Strong governance discipline**: Section 7 (Non-Goals) and the "execution constraint" header (lines 5-6) explicitly prevent scope creep. The document does not authorize code changes.
- **Closure-First strategy is well-justified**: The mapping of all 7 active OpenSpec changes (Section 2.3) directly supports the recommendation against opening parallel governance tracks.
- **Accurate DDD violation detection**: The Domain -> Infrastructure reverse dependency claim is verified at both `portfolio_valuation_service.py:17` and `portfolio_valuation_service_optimized.py:20`.
- **Pragmatic prioritization**: P0/P1/P2 tiering is clear and grounded in current state (dirty workspace with ~1020 uncommitted changes).
- **Route-level repo truth**: The `/dashboard` and `/trade/terminal` path-to-component mappings (Section 3.7, 建议 7) are verified correct, preventing stale-migration-snapshot errors.

## Detailed Recommendations

1. **Correct the Vue files >500 lines count** (Section 3.3). The actual count is 14, not ~25. The largest files are `ArtDecoStrategyManagement.vue` (1033 lines) and `Screener.vue` (908 lines). This correction may lower the perceived urgency of view-scope治理 but makes the diagnosis more trustworthy.

2. **Correct the views total file count** (Section 3.3). The actual count is 540, not ~469. If the ~469 figure was produced by excluding certain subdirectories (e.g., `composables/`, `styles/`), document the exclusion criteria so future reviews can reproduce the number.

3. **Note the `AdapterRegistry` duality** (Section 3.4). Adding a sentence like "AdapterRegistry exists in both `src/core/infrastructure/` and `web/backend/app/core/`, further illustrating the concept-scatter problem" would strengthen the diagnosis.

4. **Specify directory creation for `docs/agents/`** (Recommendation 2). If this is the preferred location for the architecture index, note that the directory must be created. Alternatively, lean toward `CONTEXT.md` at project root since it requires no directory setup.

5. **Consider adding a verification command appendix**. The document relies heavily on file counts and line counts. Including the exact commands used (e.g., `find web/backend/app/api -name "*.py" | wc -l`) would enable reproducibility and allow readers to detect drift.

## Scoring

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Technical Accuracy | 4 | 2 quantitative claims materially off (views count, Vue >500 count); all qualitative claims and symbol references verified correct |
| Completeness | 5 | Covers backend API, services, frontend, data layer, DDD, contracts, legacy, with governance recommendations and non-goals |
| Codebase Alignment | 5 | All 30+ files and 8 symbols verified; zero phantom references; route mappings confirmed |
| Actionability | 5 | Each recommendation has priority, scope, acceptance criteria, and explicit OpenSpec attachment guidance |
| Terminology Consistency | 5 | Consistent use of terms throughout; all technical terms match codebase naming conventions |
| **Overall** | **4.8** | Strong, evidence-grounded governance review with minor quantitative inaccuracies |

## Verdict

APPROVE_WITH_NOTES

The document is a high-quality, evidence-grounded architecture governance review. All structural claims are directionally correct and all referenced entities exist in the codebase. The two medium-severity findings (Vue file count discrepancies) should be corrected before this document is used as the basis for governance decisions, as the inflated "Vue files over 500 lines" count could misdirect frontend治理 priority. No critical issues found.
