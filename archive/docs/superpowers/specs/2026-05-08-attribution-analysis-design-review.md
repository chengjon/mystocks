# Review: 2026-05-08-attribution-analysis-design.md

**Type**: .md / arch (design) | **Perspective**: architecture + completeness | **Date**: 2026-05-08 | **Reviewer**: Claude

---

## Executive Summary

A well-structured attribution analysis design that clearly separates shared computation from domain shells and locks first-batch scope tightly. Three gaps weaken implementation readiness: the existing `BusinessDataSource` abstract interface is not addressed, factor/benchmark/industry data sourcing is unspecified, and the proposed API paths diverge from the current v1 routing structure. Resolving these three items would make this document implementation-ready.

## Document Metadata

| Field | Value |
|-------|-------|
| Source | `docs/superpowers/specs/2026-05-08-attribution-analysis-design.md` |
| File Type | .md |
| Doc Type | arch (design) |
| Sections | 12 |
| Referenced Files | 3 found / 0 missing |
| Referenced Symbols | 10 found / 2 not yet implemented (expected) |

## Evidence Verification

### Files Referenced

| File | Exists? | Location |
|------|---------|----------|
| `web/frontend/src/views/trade/Portfolio.vue` | yes | `web/frontend/src/views/trade/Portfolio.vue` |
| `src/data_sources/real/composite_business.py` | yes | `src/data_sources/real/composite_business.py` |
| `src/data_sources/mock/business_mock.py` | yes | `src/data_sources/mock/business_mock.py` |

### Functions/Classes Referenced

| Symbol | Found? | Location |
|--------|--------|----------|
| `perform_attribution_analysis(...)` | yes | `src/data_sources/real/composite_business.py:523`, `src/data_sources/mock/business_mock.py:424`, `src/interfaces/business_data_source.py:475` |
| `performanceAttribution` (computed) | yes | `web/frontend/src/views/trade/Portfolio.vue:56` |
| `FUNCTION_TREE` `3.3` section | yes | `docs/FUNCTION_TREE.md:226-233` |

### Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| Portfolio.vue renders local contribution cards based on weight and PnL | confirmed | `Portfolio.vue:56-76` computes `weight * pnl_pct` per position, sorted by absolute contribution |
| `perform_attribution_analysis(...)` returns simplified mock-shaped result | confirmed | `composite_business.py:523-561` returns random attribution data with `random.uniform` |
| `business_mock.py` exposes a mock attribution helper | confirmed | `business_mock.py:424-461` generates random `sector_attribution` and `allocation/selection/interaction_effect` |
| FUNCTION_TREE marks `3.3 归因分析` as unfinished | partially correct | `FUNCTION_TREE.md:233` shows `归因分析 | 🚧` but under section `3.3 回测分析`, not `3.3 归因分析` |
| No unified attribution engine exists | confirmed | grep found no `BrinsonBreakdown`, `AttributionOverview`, or factor attribution components in codebase |

## Checklist Results

### Architecture Checklist

| # | Check | Result | Notes |
|---|-------|--------|-------|
| A1 | Component boundaries | PASS | Shared engine, domain shells, and frontend skeleton are clearly delineated. Shared Logic and Reuse Rules section (lines 289-308) locks the boundary as hard constraint. |
| A2 | Data flow | PASS | Three normalized inputs (PortfolioSnapshot, BenchmarkSnapshot, FactorSnapshot) with explicit field lists. Domain adapters normalize raw inputs into these shapes; engine is pure consumer. |
| A3 | Coupling | PASS | Strategy and trade domains contribute only normalized adapters. Frontend has one orchestration layer. Document explicitly prohibits duplicate Brinson/factor math in domain shells (line 297). |
| A4 | Interface contracts | FAIL | Input and output models are well-specified, but the existing `BusinessDataSource` abstract interface at `src/interfaces/business_data_source.py:475` defines `perform_attribution_analysis` with a different contract. The document does not address how the new shared engine relates to this interface, whether it replaces it, extends it, or coexists alongside it. The mock and real implementations also have divergent signatures (mock takes `portfolio` parameter, real does not). |
| A5 | Scalability | N/A | Document explicitly scopes to one-period, fixed benchmark/factors. Non-Goals section locks out rolling-window, user-switchable benchmarks, and configurable factor sets. Acceptable for first batch. |
| A6 | Terminology consistency | FAIL | Factor names listed in Chinese in Goals (lines 35-39: 规模, 价值, 动量, 波动率, 质量) and in English in Chosen Scope (lines 66-70: size, value, momentum, volatility, quality). No explicit mapping table. Implementation surface will need to pick one canonical set and document the mapping. |
| A7 | Backward compatibility | FAIL | Document marks existing `Portfolio.vue` contribution cards, `composite_business.py` attribution, and `business_mock.py` helper as "non-canonical" (lines 103-108) but does not specify a migration or deprecation plan. Will the existing `performanceAttribution` section be replaced, removed, or coexist alongside the new attribution? |
| A8 | Implementation surface precision | FAIL | Document names 8 frontend components to create (lines 278-285) but does not specify which existing backend files need modification (e.g., `composite_business.py`, `business_mock.py`, the v1 router, the `BusinessDataSource` interface). Implementation Order step 2 says "Define shared snapshot models and shared attribution engine contracts" without naming the target module or file. |
| A9 | Named entities verified | FAIL | Section reference "3.3 归因分析" (line 9) does not match FUNCTION_TREE, where the section header is "3.3 回测分析" and "归因分析" is a sub-item row. |

### Completeness Checklist

| # | Check | Result | Notes |
|---|-------|--------|-------|
| C1 | Required sections | PASS | Context, Goals, Non-Goals, Chosen Scope, Capability Boundary, Shared Engine Contract, Output Model, API Shape, Frontend IA, Shared Logic Rules, Data Freshness, Testing Strategy, Governance Closure, Implementation Order. Complete for a design doc. |
| C2 | Edge cases | FAIL | Data Freshness section (lines 310-341) covers stale snapshots well. Missing edge cases: empty portfolio (zero positions), single-position portfolio (no diversification), portfolio with missing industry classification, benchmark data unavailable for the target date, factor data partially available (some factors missing but not all). |
| C3 | Implicit assumptions | FAIL | Document assumes backtest-result snapshots contain position-level data (symbol, weight, return, industry) but does not verify against existing `backtest_schemas.py` or `strategy_schemas.py`. Also assumes a canonical industry classification system exists and is populated for all held instruments. Codebase has multiple industry classification references (`src/data_access/interfaces.py`, `src/adapters/akshare/stock_info.py`, etc.) but no single canonical source is designated. |
| C4 | Acceptance criteria | PASS | Governance Closure section (lines 400-413) provides four concrete, verifiable conditions for moving `3.3` to done. |
| C5 | Missing roles/stakeholders | N/A | Single-user local deployment system per CLAUDE.md. |

## Findings

### Critical Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 1 | Shared Engine Contract (lines 110-161) | Factor and benchmark data sourcing is unspecified. The doc defines `FactorSnapshot` fields and internal construction formulas (lines 154-160) but does not state where the raw data comes from. The Non-Goals exclude "new external premium factor-data provider" (line 53), which is clear about what NOT to use, but silent on what TO use. Similarly, `BenchmarkSnapshot` requires benchmark weight/return/industry for CSI 300 constituents without naming a data source. | Implementation cannot begin without knowing which existing adapters, tables, or APIs provide market cap, PB/PE, trailing returns, volatility, ROE, and index constituent data. | Grep found CSI300/沪深300 references in 72 files across adapters (akshare, baostock, tdx, financial) but no single canonical benchmark data source is documented. Industry classification appears in 19 files with no designated authority. | Add a "Data Source Dependencies" subsection naming the specific existing adapters or services for: (1) benchmark constituent weights and returns, (2) industry classification, (3) factor raw data (market cap, PB/PE, trailing returns, etc.). |

### Medium Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 2 | Shared Engine Contract / Capability Boundary (lines 80-161) | Existing `BusinessDataSource` abstract interface (`src/interfaces/business_data_source.py:475`) defines `perform_attribution_analysis(self, user_id, start_date, end_date)` as an abstract method. The doc does not mention this interface or specify how the new shared engine relates to it. Additionally, the mock implementation (`business_mock.py:424`) has a divergent signature including a `portfolio` parameter that the real implementation and interface lack. | The new engine either replaces, extends, or coexists with this interface. Without explicit direction, implementers risk creating a parallel contract that leaves the old interface dangling or creates conflicting method signatures. | `src/interfaces/business_data_source.py:475` defines the abstract method. `src/data_sources/mock/business_mock.py:424` has `(user_id, portfolio, start_date, end_date)`. `src/data_sources/real/composite_business.py:523` has `(user_id, start_date, end_date)`. | Add a section specifying: (1) whether `BusinessDataSource.perform_attribution_analysis` is deprecated, replaced, or updated; (2) how the signature discrepancy between mock and real is resolved; (3) which file(s) the shared engine lives in. |
| 3 | API Shape (lines 231-252) | Proposed `/api/v1/strategy/backtests/{backtest_id}/attribution` places backtest attribution under a `/strategy/` path, but the current v1 API routes backtest endpoints under `/api/v1/backtest` (registered via `analysis/backtest.py` with `prefix="/backtest"`). The proposed path creates a new hierarchy. | Inconsistent API routing. Clients that already use `/api/v1/backtest/*` for backtest operations will find attribution at a different path hierarchy. | `web/backend/app/api/v1/analysis/backtest.py:49-51` uses `prefix="/backtest"`. `web/backend/app/api/v1/router.py:50` includes `backtest_router` directly (no `/strategy/` prefix). Test files reference `/api/v1/strategy/backtest/run` from the older non-v1 routes. | Either: (a) align with existing v1 structure using `/api/v1/backtest/{backtest_id}/attribution`, or (b) explicitly document that the new route follows the older `/api/v1/strategy/` convention and explain the rationale. |
| 4 | Capability Boundary / Explicit non-truth surfaces (lines 103-108) | No migration or deprecation plan for existing non-canonical surfaces. The doc marks `Portfolio.vue` contribution cards, `composite_business.py` attribution, and `business_mock.py` helper as "non-canonical" but does not specify what happens to them. | Without a migration plan, the existing `performanceAttribution` section in Portfolio.vue may coexist with the new attribution, creating two competing views of the same concept. The old `perform_attribution_analysis` method in both mock and real implementations may conflict with the new shared engine. | `Portfolio.vue:56-76` computes and renders contribution cards. `composite_business.py:523-561` and `business_mock.py:424-461` both implement `perform_attribution_analysis`. All three would remain unless explicitly addressed. | Add a "Migration Notes" subsection specifying: (1) whether `Portfolio.vue` contribution cards are removed, replaced, or kept as a lightweight complement; (2) whether `perform_attribution_analysis` in `composite_business.py` and `business_mock.py` is updated to delegate to the new engine or deprecated. |
| 5 | Context (line 9) | FUNCTION_TREE section reference is imprecise. Doc says "3.3 归因分析" but the FUNCTION_TREE header is "3.3 回测分析" with "归因分析" as a sub-row within it. | Readers looking for "3.3 归因分析" as a section title will not find it. Minor but undermines credibility of cross-references. | `docs/FUNCTION_TREE.md:226` header is `### 3.3 回测分析`, line 233 is `| 归因分析 | 🚧 | Brinson归因、因子归因 |`. | Change to "FUNCTION_TREE currently marks the `归因分析` row under `3.3 回测分析` as unfinished." |
| 6 | Implicit assumptions (lines 114-161) | Document assumes backtest-result snapshots contain position-level data (symbol, weight, return, industry) but does not verify this against existing backtest result schemas. Also assumes a canonical industry classification exists for all held instruments. | If backtest results don't contain weight/return/industry per position, the strategy-domain adapter will need significant data enrichment. If industry classification is sparse, Brinson attribution will have incomplete industry breakdowns. | `web/backend/app/schemas/backtest_schemas.py` and `web/backend/app/models/strategy_schemas.py` exist but were not checked for position-level fields. 19 files reference industry classification with no canonical source. | Add a "Prerequisites and Assumptions" section that: (1) verifies backtest-result schemas contain the required fields or specifies what enrichment is needed; (2) designates which industry classification source to use. |

### Low Issues

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 7 | Goals / Chosen Scope (lines 34-70) | Factor names appear in Chinese in Goals and English in Chosen Scope with no explicit mapping. | Lines 35-39: 规模, 价值, 动量, 波动率, 质量. Lines 66-70: size, value, momentum, volatility, quality. | Add a two-column mapping table or use a single consistent language with the other in parentheses. |
| 8 | Implementation Order (lines 427-439) | Step 2 says "Define shared snapshot models and shared attribution engine contracts" without naming target files or modules. | No file paths specified for any of the 9 implementation steps. | For each step, name at least the primary file or module to be created or modified. |

## Strengths

- **Scope discipline**: Non-Goals section is unusually thorough (8 explicit exclusions). First-batch lock to single benchmark, fixed factor set, and one-period analysis prevents scope creep.
- **Shared truth source principle**: The "Shared Logic and Reuse Rules" section (lines 289-308) is a strong architectural guardrail. Explicitly prohibiting duplicate Brinson/factor math in domain shells is clear and enforceable.
- **Data freshness by domain**: The three-tier staleness strategy (strategy: hard fail, trade current: degrade, trade historical: hard fail) is well-reasoned and the rationale for each tier is grounded in the audit-style vs. live-monitoring distinction.
- **Testing strategy**: Four-layer coverage (unit, contract, frontend, E2E) with specific items per layer is implementation-ready. The stale/degrade/fail paths are explicitly listed as test cases.
- **Governance closure**: The FUNCTION_TREE promotion criteria (lines 404-413) are concrete and verifiable, which prevents premature marking as complete.

## Detailed Recommendations

1. **Add a "Data Source Dependencies" subsection** under Shared Engine Contract. For each of the three input snapshots, name the specific existing adapter, service, or table that provides the raw data. This is the single most impactful gap -- without it, implementation step 2 cannot proceed deterministically.

2. **Add an "Interface Alignment" subsection** addressing the `BusinessDataSource` abstract interface. State explicitly: (a) the old `perform_attribution_analysis` method is deprecated in favor of the new shared engine, or (b) the old interface is updated to delegate to the new engine, or (c) they coexist with clear separation of concerns.

3. **Add a "Migration Notes" subsection** under Capability Boundary specifying what happens to the three non-canonical surfaces. Even a one-sentence decision per surface ("remove", "replace", "keep as lightweight complement") is sufficient.

4. **Reconcile API path structure** with the existing v1 routing. The current v1 router at `web/backend/app/api/v1/router.py` registers backtest routes at `/api/v1/backtest`, not `/api/v1/strategy/backtests`. Either adjust the proposed paths or document the divergence with rationale.

5. **Add a "Prerequisites and Assumptions" section** that lists what must already exist for this design to work: position-level data in backtest results, industry classification coverage, factor raw data availability. Verify each against the codebase.

6. **Add a factor name mapping table** with both Chinese and English names to prevent implementation ambiguity.

## Scoring

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Technical Accuracy | 4 | Brinson/factor attribution model is correct; snapshot input design is sound; freshness tiers are well-reasoned. |
| Completeness | 3 | Data sourcing for all three input snapshots is missing; interface alignment not addressed; migration plan absent. |
| Codebase Alignment | 3 | Existing files are correctly identified; FUNCTION_TREE reference slightly imprecise; API paths diverge from v1 routing; existing abstract interface not addressed. |
| Actionability | 3 | Implementation order is clear but lacks file-level targets; data sourcing gap blocks step 2. |
| Terminology Consistency | 3 | Factor names in mixed languages without mapping; otherwise consistent. |
| **Overall** | **3.2** | |

## Verdict

**APPROVE_WITH_NOTES**

The architectural structure, scope discipline, and testing strategy are strong. The document needs three additions before implementation can begin deterministically: (1) data source dependencies for factor/benchmark/industry data, (2) interface alignment with the existing `BusinessDataSource` abstract, and (3) migration decisions for the three non-canonical surfaces. None of these are architectural flaws -- they are specification gaps that an implementer would need to resolve regardless.
