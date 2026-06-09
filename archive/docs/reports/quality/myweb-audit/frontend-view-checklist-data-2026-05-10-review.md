# Review: frontend-view-checklist-data-2026-05-10.md

**Type**: md / general (audit checklist) | **Perspective**: completeness + consistency (auto) | **Date**: 2026-05-10 | **Reviewer**: Claude

---

## Executive Summary

The document is a well-structured audit checklist for `views/data/*` that correctly classifies 4 active Vue pages and 3 support helpers. All 16 referenced files exist, all 4 route-to-component mappings match the live router exactly, and all cross-domain wrapper references are verified. One minor gap: the document claims `FundFlow.vue` is wrapped by `CapitalFlow.vue` but does not mention the parallel `IndicatorLibrary.vue` wrapper for `Advanced.vue` in the "compatible wrapper" section (line 54 only names Concepts and FundFlow wrappers, though line 41 names IndicatorLibrary in the table). No factual errors found.

## Document Metadata

| Field | Value |
|-------|-------|
| Source | `docs/reports/quality/myweb-audit/frontend-view-checklist-data-2026-05-10.md` |
| File Type | .md |
| Doc Type | general (audit checklist) |
| Sections | 4 |
| Referenced Files | 16 found / 0 missing |
| Referenced Symbols | 0 explicitly named functions |

## Evidence Verification

### Files Referenced

| File | Exists? | Location |
|------|---------|----------|
| `web/frontend/src/layouts/MenuConfig.ts` | yes | `web/frontend/src/layouts/MenuConfig.ts` |
| `web/frontend/src/router/index.ts` | yes | `web/frontend/src/router/index.ts` |
| `web/frontend/src/views/data/Industry.vue` | yes | `web/frontend/src/views/data/Industry.vue` |
| `web/frontend/src/views/data/Concepts.vue` | yes | `web/frontend/src/views/data/Concepts.vue` |
| `web/frontend/src/views/data/FundFlow.vue` | yes | `web/frontend/src/views/data/FundFlow.vue` |
| `web/frontend/src/views/data/Advanced.vue` | yes | `web/frontend/src/views/data/Advanced.vue` |
| `web/frontend/src/config/pageConfig.ts` | yes | `web/frontend/src/config/pageConfig.ts` |
| `openspec/changes/restructure-frontend-directory/tasks.md` | yes | `openspec/changes/restructure-frontend-directory/tasks.md` |
| `docs/FUNCTION_TREE.md` | yes | `docs/FUNCTION_TREE.md` |
| `views/data/__tests__/Industry.spec.ts` | yes | `web/frontend/src/views/data/__tests__/Industry.spec.ts` |
| `views/data/__tests__/Concepts.spec.ts` | yes | `web/frontend/src/views/data/__tests__/Concepts.spec.ts` |
| `views/data/__tests__/FundFlow.spec.ts` | yes | `web/frontend/src/views/data/__tests__/FundFlow.spec.ts` |
| `views/data/__tests__/Advanced.spec.ts` | yes | `web/frontend/src/views/data/__tests__/Advanced.spec.ts` |
| `views/data/industryAnalysisData.ts` | yes | `web/frontend/src/views/data/industryAnalysisData.ts` |
| `views/data/marketConceptData.ts` | yes | `web/frontend/src/views/data/marketConceptData.ts` |
| `views/data/fundFlowPageData.ts` | yes | `web/frontend/src/views/data/fundFlowPageData.ts` |

### Route Mappings Verified

| Document Claim | Codebase Evidence | Status |
|----------------|-------------------|--------|
| `/data/industry` -> `Industry.vue` | `router/index.ts:72`: `import('@/views/data/Industry.vue')` | confirmed |
| `/data/concept` -> `Concepts.vue` | `router/index.ts:78`: `import('@/views/data/Concepts.vue')` | confirmed |
| `/data/fund-flow` -> `FundFlow.vue` | `router/index.ts:84`: `import('@/views/data/FundFlow.vue')` | confirmed |
| `/data/indicator` -> `Advanced.vue` | `router/index.ts:90`: `import('@/views/data/Advanced.vue')` | confirmed |

### Cross-Domain Wrapper References Verified

| Document Claim | Codebase Evidence | Status |
|----------------|-------------------|--------|
| `views/market/Concepts.vue` wraps `data/Concepts.vue` | `views/market/Concepts.vue:6`: `import ConceptsPage from '@/views/data/Concepts.vue'` | confirmed |
| `views/market/CapitalFlow.vue` wraps `data/FundFlow.vue` | `views/market/CapitalFlow.vue:6`: `import FundFlowPage from '@/views/data/FundFlow.vue'` | confirmed |
| `IndicatorLibrary.vue` wraps `data/Advanced.vue` | `views/IndicatorLibrary.vue:6`: `import DataIndicatorCanonicalPage from '@/views/data/Advanced.vue'` | confirmed |

### Helper Import References Verified

| Helper | Imported By | Status |
|--------|-------------|--------|
| `industryAnalysisData.ts` | `Industry.vue:111` | confirmed |
| `marketConceptData.ts` | `Concepts.vue:6` | confirmed |
| `fundFlowPageData.ts` | `FundFlow.vue:159` | confirmed |

### Additional Verified Claims

| Claim | Status | Evidence |
|-------|--------|----------|
| MenuConfig contains 4 data routes | confirmed | `MenuConfig.ts:70-73`: industry, indicator, concept, fund-flow |
| pageConfig contains 4 data entries | confirmed | `pageConfig.ts:57,67,76,85` |
| ArtDeco migration shims exist | confirmed | `artdeco-pages/market-data-tabs/industryAnalysisData.ts:1` re-exports from `@/views/data/` |

## Checklist Results

### Completeness

| # | Check | Result | Notes |
|---|-------|--------|-------|
| C1 | Required sections | PASS | 4 sections: Truth Inputs, Page Classification, Redundant-Page Checklist, Batch Conclusion |
| C2 | Edge cases | PASS | Covers naming mismatch (Advanced.vue vs /data/indicator), cross-domain wrappers, ArtDeco migration source |
| C3 | Implicit assumptions | PASS | Explicitly states "禁止误判项" covering ArtDeco history and naming mismatch |
| C4 | Acceptance criteria | PASS | Each page has clear classification and conclusion (排除归档审核) |
| C5 | Missing roles/stakeholders | PASS | Not applicable for this audit type |

### Consistency

| # | Check | Result | Notes |
|---|-------|--------|-------|
| N1 | Terminology | PASS | "canonical-active", "canonical-support-asset" used consistently |
| N2 | Naming conventions | PASS | File names match codebase exactly |
| N3 | Formatting | PASS | Uniform table format, consistent heading hierarchy |
| N4 | Cross-references | MED | Line 54 omits IndicatorLibrary.vue wrapper (see Finding #1) |
| N5 | Style consistency | PASS | Consistent Chinese professional documentation style |

## Findings

### Medium Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 1 | Section 3, line 54 | Wrapper list incomplete: mentions only `Concepts.vue` and `CapitalFlow.vue` wrappers, but omits `IndicatorLibrary.vue` wrapper for `Advanced.vue` which is already noted in the table on line 41 | Minor inconsistency between table (line 41) and prose (line 54); readers relying only on prose may miss the third wrapper dependency | Codebase: `views/IndicatorLibrary.vue:6` imports `Advanced.vue`. Document line 41 correctly lists "top-level `IndicatorLibrary.vue` wrapper 引用" but line 54 only names two wrappers. Internal: table covers all 3, prose misses 1. | Add `IndicatorLibrary.vue` to the wrapper list on line 54 for parity with line 41 |

### Low Issues

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | Section 2, line 42-44 | "page import + historical tests" cited as evidence for support-asset status but no specific import line numbers given | `Industry.vue:111`, `Concepts.vue:6`, `FundFlow.vue:159` are the actual import locations. Document says "page import" without citing lines. Internal: claim is true, just not precisely cited. | Consider adding import line numbers for parity with the route truth section (which cites router lines) |

## Strengths

- Every file, route, and wrapper reference verified against the live codebase with zero misses
- Clear two-tier classification (canonical-active vs canonical-support-asset) that maps directly to archive-flow decisions
- "禁止误判项" section proactively prevents common misclassification pitfalls
- Truth Inputs section provides verifiable anchors (MenuConfig, router, pageConfig, FUNCTION_TREE, tests) that any reviewer can independently confirm

## Detailed Recommendations

1. **Line 54 — add IndicatorLibrary.vue wrapper**: The prose says "Concepts.vue、FundFlow.vue 同时被 views/market/Concepts.vue、views/market/CapitalFlow.vue 兼容 wrapper 引用". Add that `Advanced.vue` is similarly wrapped by `views/IndicatorLibrary.vue` (confirmed at `IndicatorLibrary.vue:6`). This makes the prose consistent with the table on line 41.

2. **Optional — cite helper import lines**: Section 2 claims "page import" as evidence for support assets but doesn't cite line numbers. Adding `Industry.vue:111`, `Concepts.vue:6`, `FundFlow.vue:159` would match the precision of the Truth Inputs section.

## Scoring

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Technical Accuracy | 5 | All 16 files, 4 routes, 3 wrappers, 3 helper imports verified correct |
| Completeness | 4 | Minor gap: prose wrapper list on line 54 omits IndicatorLibrary.vue |
| Codebase Alignment | 5 | Every claim matches live code; ArtDeco shim layer confirmed |
| Actionability | 5 | Clear classifications with explicit archive-flow decisions |
| Terminology Consistency | 5 | canonical-active/support-asset used uniformly |
| **Overall** | **4.8** | |

## Verdict

**APPROVE_WITH_NOTES** — Document is factually accurate and well-structured. All codebase references verified correct. One minor consistency gap: line 54 should include `IndicatorLibrary.vue` wrapper to match the table on line 41.
