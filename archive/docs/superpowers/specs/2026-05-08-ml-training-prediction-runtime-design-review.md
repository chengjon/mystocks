# Review: 2026-05-08-ml-training-prediction-runtime-design.md

**Type**: .md / arch (design spec) | **Perspective**: arch + completeness + consistency + feasibility | **Date**: 2026-05-08 | **Reviewer**: Claude

---

## Executive Summary

This is a well-structured design spec for unifying two duplicated ML training/prediction surfaces into a shared runtime with dual business shells. The document accurately diagnoses the current repo state: duplicated backend ML logic across `web/backend/app/api/ml.py` and `web/backend/app/api/v1/strategy/machine_learning.py`, menu/router drift for `/ml/*` pages, and missing frontend workbench surfaces. The proposed architecture (shared runtime + dual shells) is sound and appropriately scoped for a first batch. Key gaps: the design does not address 5 existing ML-related generic endpoints that fall outside the proposed 4-endpoint contract, defers financial-snapshot data sources entirely to implementation without naming them, and leaves mandatory dependency pinning as an implementation-plan decision rather than a design-level requirement.

## Document Metadata

| Field | Value |
|-------|-------|
| Source | `docs/superpowers/specs/2026-05-08-ml-training-prediction-runtime-design.md` |
| File Type | `.md` |
| Doc Type | arch (design spec) |
| Sections | 15 |
| Referenced Files | 13 found / 0 missing |
| Referenced Symbols | 4 found / 2 new (not yet in codebase, expected) |

## Evidence Verification

### Files Referenced

| File | Exists? | Location |
|------|---------|----------|
| `web/backend/app/api/ml.py` | yes | `web/backend/app/api/ml.py` |
| `web/backend/app/api/v1/strategy/machine_learning.py` | yes | `web/backend/app/api/v1/strategy/machine_learning.py` |
| `web/frontend/src/config/menu.config.js` | yes | `web/frontend/src/config/menu.config.js` |
| `web/frontend/src/router/index.ts` | yes | `web/frontend/src/router/index.ts` |
| `web/frontend/src/views/ml/` | no | Directory does not exist (expected -- design target) |
| `src/ml_strategy/feature_engineering.py` | yes | `src/ml_strategy/feature_engineering.py` |
| `src/ml_strategy/price_predictor.py` | yes | `src/ml_strategy/price_predictor.py` |
| `src/ml_strategy/ml_strategy.py` | yes | `src/ml_strategy/ml_strategy.py` |
| `src/ml_strategy/strategy/ml_strategy_base.py` | yes | `src/ml_strategy/strategy/ml_strategy_base.py` |
| `web/backend/app/services/data_service.py` | yes | `web/backend/app/services/data_service.py` |
| `web/backend/app/services/feature_engineering_service.py` | yes | `web/backend/app/services/feature_engineering_service.py` |
| `web/backend/app/services/ml_runtime/` | no | Directory does not exist (expected -- design target) |
| `docs/FUNCTION_TREE.md` | yes | `docs/FUNCTION_TREE.md` |

### Functions/Classes Referenced

| Symbol | Found? | Location |
|--------|--------|----------|
| `MLPredictionService` | yes | `web/backend/app/services/ml_prediction_service.py:26` |
| `RollingFeatureGenerator` | yes | `src/ml_strategy/feature_engineering.py` |
| `get_daily_ohlcv` | yes | `web/backend/app/services/data_service.py:112` |
| `DataService.get_daily_ohlcv` | yes | `web/backend/app/services/data_service.py:112` |
| `future_1d_return` | no | Not in codebase; new target introduced by this design (expected) |
| `feature_schema_signature` | no | Not in codebase; new concept introduced by this design (expected) |

### Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| ml.py "still depends on optional MLPredictionService" | confirmed | `web/backend/app/services/ml_prediction_service.py` exists; `MLPredictionService` is imported in `ml.py` |
| machine_learning.py "exposes runtime ML strategy training, prediction, and listing" | confirmed | Routes: `/train`, `/predict`, `/backtest`, `""` (list) at `prefix="/strategies"` |
| menu.config.js "already contains `/ml/training` and `/ml/prediction`" | confirmed | Lines 123 and 130 in `menu.config.js` |
| router "does not currently mount canonical `/ml/training` or `/ml/prediction` routes" | confirmed | Grep for `/ml/training` and `/ml/prediction` in `router/index.ts` returns no matches |
| "there is no canonical `web/frontend/src/views/ml/`" | confirmed | Glob returns empty |
| FUNCTION_TREE marks 7.1 模型训练 and 预测推理 as unfinished | confirmed | Both marked `🚧` in `docs/FUNCTION_TREE.md` lines 407-408 |
| Generic routes at `/api/ml/*` | confirmed | `ml.py` prefix `/ml` mounted at `/api` via `router_registry.py:93` |
| Strategy routes at `/api/v1/strategies/*` | confirmed | `machine_learning.py` prefix `/strategies` mounted under `api_v1_router` prefix `/api/v1` via `v1/router.py:26,37` |
| Dependencies not pinned in requirements.txt | confirmed | `web/backend/requirements.txt` has zero matches for lightgbm, scikit-learn, xgboost, joblib |
| lightgbm available in freeze | confirmed | `config/requirements_freeze.txt:246` has `lightgbm==4.6.0` |

## Checklist Results

### Architecture (`--arch`)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| A1 | Component boundaries | PASS | Shared runtime vs dual shells vs non-truth surfaces clearly delineated (Sections "Shared runtime", "Dual shells", "Explicit non-truth surfaces") |
| A2 | Data flow | PASS | Training flow (9-step) and prediction flow (7-step) are explicit with clear stage boundaries |
| A3 | Coupling | PASS | Shells depend on shared runtime; shells do not depend on each other; `src/ml_strategy/` positioned as lower-level reuse target |
| A4 | Interface contracts | PASS | FeatureAssembly input/output, TrainingDataset, ModelRegistryRecord fields all specified |
| A5 | Scalability | MED | Synchronous training guardrails mentioned but no async/queue escalation path for future batches. Doc acknowledges this is first-batch only so N/A for now, but no forward pointer. |
| A6 | Terminology consistency | PASS | "shared runtime", "generic ML shell", "strategy ML shell" used consistently throughout |
| A7 | Backward compatibility | PASS | Migration plan addresses deprecation of legacy surfaces in two phases |
| A8 | Implementation surface precision | MED | Backend module split is precise (6 files named). Frontend has 8 components + 3 composable/API surfaces named but only `MlModelRegistryTable` has functional requirements specified. The rest are listed without behavior specs. |
| A9 | Named entities verified | PASS | All referenced existing files, functions, and classes verified against codebase. Two symbols (`future_1d_return`, `feature_schema_signature`) are new introductions by this design -- correctly absent from current codebase. |

### Completeness (`--completeness`)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| C1 | Required sections | PASS | Has Context, Goals, Non-Goals, Scope, Capability Boundary, Contract, Data Sources, Dependencies, Training Flow, Prediction Flow, API Contract, Frontend, Migration, Testing, FUNCTION_TREE Closure, Implementation Order |
| C2 | Edge cases | PASS | Missing T+1 sample filtering, stale snapshot handling, schema mismatch, insufficient data, symbol scope validation all addressed |
| C3 | Implicit assumptions | MED | Assumes `feature_engineering_service.py` can be reused for technical indicator assembly but does not verify its current API shape. Financial snapshot sources are deferred to implementation without naming. |
| C4 | Acceptance criteria | PASS | FUNCTION_TREE Closure section provides 6 concrete verifiable criteria |
| C5 | Missing roles/stakeholders | PASS | Single-user local deployment context is explicit; no multi-role concerns |

### Consistency (`--consistency`)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| N1 | Terminology | PASS | Terms used consistently: "shared runtime", "shell", "feature_profile", "feature_schema_signature", "model_family", "domain" |
| N2 | Naming conventions | PASS | Module names, component names, and API paths follow project conventions |
| N3 | Formatting | PASS | Consistent heading hierarchy, list style, and code-block usage |
| N4 | Cross-references | PASS | Internal section references resolve correctly |
| N5 | Style consistency | PASS | Uniform formal/technical writing style throughout |

### Feasibility (`--feasibility`)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| F1 | Technical risk | MED | Consolidating two independent ML surfaces into one shared runtime is the highest-risk item. The doc acknowledges the `src/ml_strategy/` overlap but provides no migration strategy for it beyond "evaluate reuse". 30+ files in `src/ml_strategy/` may create a third parallel stack if reuse evaluation fails. |
| F2 | Dependency availability | MED | lightgbm and scikit-learn exist in `config/requirements_freeze.txt` but are absent from `web/backend/requirements.txt`. xgboost is absent from both. The design does not lock which are mandatory vs optional for first batch -- it defers to "implementation plan should explicitly decide". |
| F3 | Timeline realism | N/A | No timeline estimates provided; cannot assess |
| F4 | Resource constraints | N/A | Single-developer local deployment; no staffing concerns |
| F5 | Rollback plan | PASS | Two-phase migration with compatibility fallback in Phase 1 and cleanup in Phase 2 provides a rollback path |

## Findings

### Critical Issues

(None)

### Medium Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 1 | API Contract: Generic workbench shell | Doc proposes 4 generic endpoints but current `ml.py` has 9. Five existing endpoints are unaccounted for: `/features/generate`, `/models/hyperparameter-search`, `/models/evaluate`, `/tdx/data`, `/tdx/stocks/{market}`. At minimum `/features/generate` and `/models/evaluate` overlap directly with the shared runtime's feature assembly and model registry responsibilities. | Implementation may leave orphaned endpoints or accidentally break existing consumers. | Checked `web/backend/app/api/ml.py` -- 9 `@router` decorators found at lines 431, 471, 496, 547, 604, 679, 698, 739, 794. Doc only lists 4 endpoints (train, list, detail, predict). | Add a section explicitly listing which existing endpoints are in-scope, out-of-scope, or to-be-deprecated for the first batch. At minimum address `/features/generate` and `/models/evaluate`. |
| 2 | Data Source Dependencies: Financial snapshot features | Financial snapshot data sources are deferred: "should be named explicitly during implementation" (line 291). Unlike market data (names `DataService.get_daily_ohlcv`) and technical indicators (names `RollingFeatureGenerator` and `feature_engineering_service.py`), financial features have no named canonical access surface. | Implementer must discover the correct adapter/service surface without design guidance, risking inconsistent or incorrect data access. | Grep for `financial` adapter surfaces in `web/backend/app/services/` shows no clear single canonical financial-snapshot access service. The doc acknowledges the gap at line 291-292 but does not close it. | Name at least one canonical financial-data access surface in the design. If none exists, explicitly state "first batch financial features require identifying or creating a canonical adapter -- this is a design gap to close before implementation." |
| 3 | Dependency Requirements | Design lists lightgbm, scikit-learn, joblib, xgboost but does not lock which are mandatory. States "implementation plan should explicitly decide" (line 327). Meanwhile `web/backend/requirements.txt` has zero of these packages. `config/requirements_freeze.txt` has lightgbm, scikit-learn, joblib but not xgboost. | Without a design-level mandate, the implementation plan may defer dependency pinning, leaving the runtime dependent on unlisted packages that may not be installed in a fresh environment. | Grep for `lightgbm|scikit-learn|xgboost|joblib` in `web/backend/requirements.txt` returns zero matches. `config/requirements_freeze.txt` has lightgbm, scikit-learn, joblib but not xgboost. | Lock at minimum: lightgbm mandatory, scikit-learn mandatory, joblib mandatory, xgboost optional+dependency-gated. Add to the design as a hard requirement that these must be added to `web/backend/requirements.txt`. |
| 4 | Relationship to `src/ml_strategy/` | Section "Relationship to `src/ml_strategy/`" (lines 119-139) is advisory only. Lists 4 files for "explicit evaluation of reuse" but provides no guidance on what happens if reuse is impractical -- which functions to call directly, which to refactor, which to deprecate. Given 30+ files in `src/ml_strategy/`, the risk of creating a third parallel ML stack is real. | Without concrete reuse guidance, implementer may duplicate existing `src/ml_strategy/` functionality inside `web/backend/app/services/ml_runtime/`, creating the third independent ML engine the doc explicitly warns against. | `src/ml_strategy/` contains 30+ Python files including feature_engineering.py (with `RollingFeatureGenerator`), price_predictor.py, ml_strategy.py, strategy/ml_strategy_base.py. Doc mentions all four but says only "evaluate reuse" without specifying expected reuse mode (call, refactor, wrap, or deprecate). | For each of the 4 named `src/ml_strategy/` files, state the expected reuse mode: (a) call directly from ml_runtime, (b) refactor and absorb into ml_runtime, or (c) deprecate in favor of ml_runtime reimplementation. This closes the "third stack" risk. |

### Low Issues

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | VERSION_MAPPING drift | `web/backend/app/api/VERSION_MAPPING.py:55` uses `"prefix": "/api/v1/strategy"` (singular) while the actual runtime path is `/api/v1/strategies` (plural via `machine_learning.py` prefix). Doc does not mention this inconsistency. | VERSION_MAPPING.py line 55 vs actual router at `v1/router.py:26` + `machine_learning.py:26`. | Note that VERSION_MAPPING.py needs updating as part of implementation. Low risk since VERSION_MAPPING is likely documentation/metadata only, but stale references cause confusion. |
| 2 | xgboost availability | Doc says xgboost is "optional and dependency-gated in the first batch" (line 324) but xgboost is absent from both `web/backend/requirements.txt` and `config/requirements_freeze.txt`. | Grep confirms no xgboost in either requirements file. | Clarify: is xgboost "optional but available if installed" or "not currently available, aspirational only"? If aspirational, mark it as a future-batch consideration rather than a first-batch optional feature. |
| 3 | Strategy list endpoint | Doc claims `GET /api/v1/strategies` (line 446) but actual route is `@router.get("")` with prefix `/strategies` under `/api/v1`, yielding `/api/v1/strategies` with no trailing path segment. This is correct but the empty-string route definition is fragile. | `machine_learning.py:523` has `@router.get("", ...)` | No doc change needed -- the path is correct. Flag for implementation to use a named path like `/list` or `/` for clarity. |

## Strengths

- **Accurate repo-state diagnosis**: The Context section's description of duplicated ML surfaces, menu/router drift, and missing frontend pages is fully verified against the live codebase.
- **Clear architecture**: Shared runtime + dual shells is a clean separation that avoids collapsing generic and strategy-domain ML into one mixed surface.
- **Explicit non-truth surfaces**: Listing current surfaces that are NOT the future canonical runtime (lines 114-116) prevents ambiguity during implementation.
- **Concrete closure criteria**: FUNCTION_TREE Closure section (lines 634-647) provides 6 verifiable acceptance criteria.
- **Feature leakage prevention**: T-1 feature discipline and missing T+1 sample filtering are well-specified guardrails.
- **Implementation order is sound**: The 10-step execution order keeps route truth, runtime truth, and shell truth from drifting.

## Detailed Recommendations

1. **Add endpoint disposition table**: Create a table mapping each of the 9 current `ml.py` endpoints to its first-batch status (keep-as-is, route-through-runtime, deprecate, out-of-scope). This prevents orphaned endpoints.

2. **Lock mandatory dependencies at design level**: State explicitly in the design that lightgbm, scikit-learn, and joblib are mandatory first-batch dependencies that must be added to `web/backend/requirements.txt`. Move xgboost to a "future batch" note unless it's already installable.

3. **Name financial snapshot access surface**: Even if the answer is "use `DataService` method X" or "create a thin adapter in ml_runtime", the design should name it rather than deferring entirely.

4. **Specify reuse mode for `src/ml_strategy/` files**: For each of the 4 named files (feature_engineering.py, price_predictor.py, ml_strategy.py, ml_strategy_base.py), state whether ml_runtime should call it, absorb it, or deprecate it. This prevents the third-stack risk the doc itself warns about.

5. **Add VERSION_MAPPING.py to implementation checklist**: Note that `VERSION_MAPPING.py` uses stale singular `strategy` prefix and should be updated when the strategy routes are refactored.

## Scoring

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Technical Accuracy | 4 | All codebase claims verified correct. API paths match live router mounts. FUNCTION_TREE status confirmed. |
| Completeness | 3 | Financial snapshot sources deferred to implementation. 5 of 9 existing generic endpoints unaddressed. Dependency pinning deferred. |
| Codebase Alignment | 4 | All referenced files, functions, and classes verified. `src/ml_strategy/` relationship is acknowledged but imprecise. |
| Actionability | 4 | Implementation order is explicit. Module split is precise. Closure criteria are testable. |
| Terminology Consistency | 5 | Consistent use of "shared runtime", "shell", "domain" throughout. No ambiguous synonyms. |
| **Overall** | **4.0** | |

## Verdict

**APPROVE_WITH_NOTES**

The design is architecturally sound, well-grounded in verified codebase reality, and appropriately scoped. The four medium findings (orphaned endpoints, unnamed financial data sources, unlocked dependency requirements, vague `src/ml_strategy/` reuse mode) should be addressed before or during implementation planning but do not block design approval. None introduce fundamental architectural risk -- they are specification gaps that, if left unaddressed, would create implementation ambiguity rather than structural failure.
