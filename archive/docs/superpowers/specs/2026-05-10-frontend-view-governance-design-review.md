# Review: 2026-05-10-frontend-view-governance-design.md

**Type**: .md / spec | **Perspective**: completeness + feasibility (auto) | **Date**: 2026-05-10 | **Reviewer**: Claude

---

## Executive Summary

The spec defines a sound governance framework for classifying and archiving the 271 Vue view files against the 42 canonical routed views. Truth sources are correctly identified (MenuConfig.ts, router/index.ts). The classification model and execution plan are well-structured. One factual error exists (`/detail/*` referenced but absent from codebase), and two areas need sharper definition before execution.

## Document Metadata

| Field | Value |
|-------|-------|
| Source | docs/superpowers/specs/2026-05-10-frontend-view-governance-design.md |
| File Type | .md |
| Doc Type | spec |
| Sections | 9 |
| Referenced Files | 2 found / 1 missing |
| Referenced Symbols | 0 explicit / 2 implied |

## Evidence Verification

### Files Referenced

| File | Exists? | Location |
|------|---------|----------|
| `web/frontend/src/layouts/MenuConfig.ts` | yes | `web/frontend/src/layouts/MenuConfig.ts` |
| `web/frontend/src/router/index.ts` | yes | `web/frontend/src/router/index.ts` |
| `web/frontend/src/views/archive/` | no | Not yet created (expected — spec proposes creation) |

### Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| MenuConfig.ts is the single source of truth for visible main menu | confirmed | `ARTDECO_MENU_ITEMS` export with 7 domains, 36+ leaf items. `MENU_CONFIG_MAP` for layout compat. |
| router/index.ts dynamic imports define active routed page truth | confirmed | 43 `() => import(...)` calls (42 view files + 1 layout). |
| Current measured value is "about 42 views" | confirmed | 42 view-specific dynamic imports (excluding `ArtDecoLayoutEnhanced.vue` layout import). Exact match. |
| `/dashboard` is a special page | confirmed | Route `path: 'dashboard'` under `/` in router, maps to `ArtDecoDashboard.vue`. |
| `/login` is a special page | confirmed | Route `path: '/login'` at line 373. |
| `404` is a special page | confirmed | Route `path: '/:pathMatch(.*)*'` at line 379, maps to `NotFound.vue`. |
| `/detail/*` is a special page | **contradicted** | No `/detail` routes exist in router. No `views/detail/` directory exists. No dynamic import referencing a detail path. |
| 271 total view files vs ~42 canonical | confirmed | `find views -name '*.vue'` returns 271. Router imports 42 view files. Ratio ~6.5:1. |
| `import.meta.glob` patterns are a hidden reference risk | unverified | Grep for `import.meta.glob` across `web/frontend/src/**` returns **zero matches**. Not a current risk. |

## Checklist Results

### Completeness

| # | Check | Result | Notes |
|---|-------|--------|-------|
| C1 | Required sections | PASS | Context, Goals, Non-Goals, Truth Sources, Classification Model, Execution Plan, Verification all present. |
| C2 | Edge cases | FAIL | `/detail/*` listed in Truth Sources but does not exist. No mention of `stocks/` (6 files), `trading/` (4), `trading-decision/` (4), `trade-management/` (5), `technical/` (1), `settings/` (4) directories which contain 24 view files with zero router references. |
| C3 | Implicit assumptions | FAIL | Assumes `import.meta.glob` is a live risk (it is not currently used). Assumes `/detail/*` pages exist (they do not). Assumes archive subdirectory assignment is obvious from lifecycle status (no mapping defined). |
| C4 | Acceptance criteria | PASS | Verification section defines measurable gates per batch type (syntax errors, type status, service status, E2E counts). |
| C5 | Missing roles/stakeholders | PASS | Spec is appropriately scoped for developer execution. Non-Goals explicitly exclude visual polish and menu expansion. |

### Feasibility

| # | Check | Result | Notes |
|---|-------|--------|-------|
| F1 | Technical risk | PASS | Classification model and asset extraction scope (5 classes) constrain the work well. The 271:42 ratio is large but manageable in batches. |
| F2 | Dependency availability | PASS | All referenced files exist. No external tooling required beyond existing frontend toolchain. |
| F3 | Timeline realism | N/A | No timeline estimates provided. Spec is procedure-oriented, not schedule-oriented. |
| F4 | Resource constraints | N/A | Single-developer scope implied. |
| F5 | Rollback plan | FAIL | No rollback mechanism defined. If an archive move breaks a hidden reference discovered post-move, the spec does not specify how to revert or recover. Archive is isolation not deletion, which mitigates risk, but a rollback procedure is still needed for the router/layout side-effects. |

## Findings

### Critical Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 1 | Truth Sources table (line 36) | `/detail/*` listed as a special page but no detail routes or views exist anywhere in the codebase. | Factual error in a truth source definition could cause inventory step to search for non-existent files or create confusion about scope. | Searched router for `detail` routes — zero matches. Searched for `views/detail/` directory — does not exist. | Remove `/detail/*` from the Truth Sources table, or document it as a planned future route category with a note that it does not yet exist. |

### Medium Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 1 | Truth Sources (line 36) | The doc claims "about 42 views" but the measured value is exactly 42 (43 dynamic imports minus 1 layout import). The doc itself says "the rule follows the route import set rather than a hardcoded count," which is correct — but the approximate number should either be exact or omitted. | Minor factual imprecision in a spec that emphasizes truth sources. | `grep -c "component.*import.*views"` in router/index.ts returns 43. Subtracting the layout import yields exactly 42. | Change "about 42 views" to "42 views" or remove the number entirely and rely only on "the route import set." |
| 2 | Hidden Reference Checks (line 71) | `import.meta.glob` listed as a check but zero such patterns exist in the current codebase. The check is valid as a defensive measure but should note current state. | Inventory step may spend time searching for something that does not exist. Execution could treat this as a false gap. | `grep -r "import.meta.glob" web/frontend/src/` returns no matches across any `.ts` or `.vue` file. | Add a note: "No `import.meta.glob` patterns currently exist in the codebase, but this check guards against future introduction." Alternatively, mark as low-risk in execution template. |
| 3 | Archive Rules (lines 79-91) | Archive subdirectory structure (`demo/`, `legacy/`, `replaced/`, `experimental/`) is proposed but no mapping from lifecycle status to subdirectory is defined. | Execution step 4 ("move only approved archive candidates") has no rule for choosing the target subdirectory. | Doc defines 6 lifecycle statuses but proposes 4 archive subdirectories. `compat-retained` and `absorb-assets` have no archive destination (they shouldn't be archived), but `candidate-review` transition to archive is unclear. | Add a mapping table, e.g.: `archive-candidate` -> `replaced/`, `experimental` -> `experimental/`, demo/lab views -> `demo/`, legacy migration remnants -> `legacy/`. |

### Low Issues

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | Execution Plan (line 98) | No rollback procedure for post-archive hidden-reference discoveries. Archive isolation mitigates deletion risk, but router/layout references may break if a view is moved and a hidden import is later discovered. | Spec says "Archived views must not be imported by router, menu, layout tabs, tests, or generated runtime config" but does not specify what happens if a violation is found post-move. | Add a step 4.5: "If a hidden reference to an archived view is discovered, move the view back to its original location and reclassify as `compat-retained`." |
| 2 | Context (line 7) | Mentions "ArtDeco compatibility wrappers" as a category but does not define how to identify them during classification. | MenuConfig.ts line 168 has `ARTDECO_MENU_ENHANCED = ARTDECO_MENU_ITEMS` compat alias. `MENU_CONFIG_MAP` maps both `ArtDecoDashboard` and `ArtDecoEnhanced` to the same items. | Add identification criteria: "A compatibility wrapper is any view that re-exports or wraps another canonical view without adding independent business logic." |

## Strengths

- Truth source identification is precise and verifiable: `MenuConfig.ts` (menu truth) and `router/index.ts` dynamic imports (route truth) are the correct anchors.
- Classification model with 6 statuses and explicit allowed actions per status prevents premature deletion and enforces classification before mutation.
- Asset Extraction Scope (5 classes) is well-scoped — avoids open-ended refactoring while preserving valuable business logic.
- Non-Goals section is clear and correctly excludes deletion, pre-move file operations, menu expansion, and visual polish.
- Verification requirements differentiate between read-only inventory batches and mutation batches, avoiding unnecessary gates.

## Detailed Recommendations

1. **Remove or qualify `/detail/*`** from the Truth Sources table. If detail pages are planned for the future, add them to a "Planned Extensions" section instead of the current truth sources. Currently this is a factual error in a document that emphasizes truth.

2. **Add status-to-directory mapping** for the archive. The four subdirectories (`demo/`, `legacy/`, `replaced/`, `experimental/`) need explicit mapping rules. Suggested:
   - `archive-candidate` with replacement successor -> `replaced/`
   - `experimental` status -> `experimental/`
   - Demo/lab views with no business logic -> `demo/`
   - Legacy migration remnants (shims, old naming) -> `legacy/`

3. **Mark `import.meta.glob` as currently unused** in the Hidden Reference Checks list to prevent wasted search effort. Keep it as a defensive check with a note.

4. **Add rollback step** to the execution plan for post-archive hidden-reference discoveries.

5. **Consider adding a pre-classification sweep** that identifies the 24 view files in directories with zero router references (`stocks/`, `trading/`, `trading-decision/`, `trade-management/`, `technical/`, `settings/`). These are the highest-risk candidates for hidden references because they exist outside the canonical routing structure entirely.

## Scoring

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Technical Accuracy | 4 | All file references verified. One factual error (`/detail/*`). Correct 42-view count. |
| Completeness | 4 | Strong classification model and execution plan. Missing archive mapping and rollback procedure. |
| Codebase Alignment | 5 | Truth sources (MenuConfig.ts, router/index.ts) are exact. Verification gates match existing toolchain. |
| Actionability | 4 | Execution plan is clear and phased. Status-to-directory gap reduces step-4 actionability. |
| Terminology Consistency | 5 | Lifecycle statuses and asset classes are clearly defined and consistently used throughout. |
| **Overall** | **4.4** | |

## Verdict

APPROVE_WITH_NOTES

Sound governance framework with correct truth sources and a well-structured classification model. One factual error (`/detail/*`) and one gap (status-to-archive-directory mapping) should be resolved before execution begins. The spec is ready for inventory step 1 with minor amendments.
