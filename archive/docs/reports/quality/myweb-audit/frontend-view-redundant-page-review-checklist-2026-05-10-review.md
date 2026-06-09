# Review: frontend-view-redundant-page-review-checklist-2026-05-10.md

**Type**: .md / workflow | **Perspective**: completeness + consistency (auto) | **Date**: 2026-05-10 | **Reviewer**: Claude

---

## Executive Summary

A well-structured per-page decision checklist that enforces "classify before archive" governance. The gate structure (Truth-Source → Functional Coverage → Reusable Assets → Guard → Successor → Eligibility) is logically sound and prevents the primary failure mode from historical batches (treating "not in router" as deletion evidence). Two medium issues: the checklist references archive subdirectories without mapping them to lifecycle statuses defined in the parent spec, and the router import count in the codebase (43 dynamic imports, not a specific number the checklist depends on) is a live value that should be noted. One medium gap: no explicit rollback procedure if an archived page is later found to have a hidden reference.

## Document Metadata

| Field | Value |
|-------|-------|
| Source | docs/reports/quality/myweb-audit/frontend-view-redundant-page-review-checklist-2026-05-10.md |
| File Type | .md |
| Doc Type | workflow (checklist with decision gates) |
| Sections | 8 |
| Referenced Files | 2 found / 0 missing |
| Referenced Symbols | 0 explicit |

## Evidence Verification

### Files Referenced

| File | Exists? | Location |
|------|---------|----------|
| `router/index.ts` | yes | `web/frontend/src/router/index.ts` |
| `MenuConfig.ts` | yes | `web/frontend/src/layouts/MenuConfig.ts` |

### Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| Checklist guards against archiving pages only because they are "not visible in the current menu or not directly imported by the router" | confirmed | Truth-Source Checks (6 items) and Redundant Eligibility Gate (7 conditions) both require positive evidence before archive |
| `*-mainline-gate.spec.ts` files exist and guard non-canonical views | confirmed | 22 mainline-gate spec files found in `web/frontend/tests/unit/config/` |
| Pages are guarded by test specs that import views | confirmed | 20+ spec files in `tests/unit/views/` and `tests/unit/config/` import from `views/` |
| Archive directory has 4 subdirectories | unverified | `views/archive/` does not exist yet; the checklist proposes it (consistent with parent spec) |

## Checklist Results

### Completeness

| # | Check | Result | Notes |
|---|-------|--------|-------|
| C1 | Required sections | PASS | All workflow sections present: Metadata, Truth-Source, Functional Coverage, Assets, Guards, Successor, Eligibility Gate, Final Decision, Archive Target. |
| C2 | Edge cases | PASS | Covers the critical edge cases from historical batches: pages guarded by specs, compat routes, hidden references, demo pages. |
| C3 | Implicit assumptions | FAIL | Assumes the executor knows which `*-mainline-gate.spec.ts` files guard which pages, but does not require recording this mapping. |
| C4 | Acceptance criteria | PASS | Redundant Eligibility Gate is fully verifiable: all 7 conditions must be `Pass` with evidence. |
| C5 | Missing roles/stakeholders | PASS | Single-reviewer scope is appropriate for a per-page checklist. |

### Consistency

| # | Check | Result | Notes |
|---|-------|--------|-------|
| N1 | Terminology | PASS | Lifecycle statuses (`candidate-review`, `absorb-assets`, `compat-retained`, `experimental`, `archive-candidate`) match parent spec exactly. |
| N2 | Naming conventions | PASS | File paths and spec patterns use project conventions. |
| N3 | Formatting | PASS | Tables are uniform. Evidence columns are consistent. |
| N4 | Cross-references | FAIL | Archive Target section references 4 subdirectories (`demo/`, `legacy/`, `replaced/`, `experimental/`) but does not map lifecycle statuses to these directories. |
| N5 | Style consistency | PASS | English throughout, consistent tone. |

## Findings

### Medium Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 1 | Archive Target (lines 112-118) | Archive subdirectories have "When to use" descriptions but no explicit mapping from lifecycle status to directory. The parent spec (`2026-05-10-frontend-view-governance-design.md`) also lacks this mapping, which was identified as a gap in its review. | Executor must make a subjective judgment per page. Inconsistent directory placement across batch executors. | Codebase: 22 mainline-gate specs exist, meaning ~22 directories/pages could be archived — inconsistency risk scales. Document: searched entire checklist for "lifecycle" or status-to-directory mapping, none found. | Add a mapping row to the Archive Target table, e.g.: `experimental` status → `views/archive/experimental/`, `archive-candidate` with successor → `views/archive/replaced/`, demo-only → `views/archive/demo/`, legacy remnant → `views/archive/legacy/`. |
| 2 | Guard And Test Checks (lines 60-70) | Checklist asks "Is the page imported or read by any `*.spec.ts` file?" and "Has the relevant test guard been migrated?" but provides no mechanism to discover which spec files guard a given page. | Executor may answer "No" incorrectly because they did not find the right spec. Historical batches (04-07 audit) found specs in unexpected locations. | Codebase: spec files referencing views are in `tests/unit/config/` (22 gate files), `tests/unit/views/` (10+ files), `tests/unit/components/` — three separate directories. Document: searched for "how to discover" or "grep" or "search pattern", none found. | Add a discovery step to the Guard section: "Run `grep -rl '<page-path-or-name>' web/frontend/tests/` and list all matching spec files as evidence." Alternatively, reference a pre-built guard map from the proposed Step 0 (lessons-learned doc optimization 1). |

### Low Issues

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | Redundant Eligibility Gate (line 94) | Condition "No active import, dynamic import, tab, page-config, docs, string-link, or test guard reference" lists 7 reference types in a single row. This is a compound condition that is hard to verify as a single pass/fail. | Document: single evidence cell for 7 distinct reference types. Codebase: reference types span router (43 imports), layout tabs (ArtDecoLayoutEnhanced), page configs (MenuConfig.ts), docs (docs/ directory), test guards (22+ specs). | Split into 7 individual rows, one per reference type, each with its own Pass/Fail and Evidence cell. |
| 2 | Final Decision (lines 99-108) | "Keep as canonical or special page" and "Move to archive in approved mutation batch" are both listed as decisions, but the former is a retention outcome and the latter is an execution action. Mixing outcomes and actions in one selection list may confuse classification vs. execution. | Document: all other decisions are lifecycle statuses, but "Move to archive" is an action step. | Split into two fields: "Lifecycle decision" (canonical / compat-retained / absorb-assets / experimental / archive-candidate) and "Execution action" (no action needed / scheduled for archive batch N). |

## Strengths

- **Gate structure is logically tight**: Truth-Source → Functional → Assets → Guards → Successor → Eligibility creates a clear dependency chain. A page cannot pass the Eligibility Gate without passing every upstream check.
- **Directly addresses the primary historical failure mode**: The checklist's entire design prevents "not in router = delete" reasoning, which caused the most damage in earlier batches.
- **Guard checks are thorough**: Separating mainline-gate specs from general specs, and requiring migration or retirement rationale, addresses the 04-07 audit discovery that 22+ mainline-gate specs guard non-canonical views.
- **Successor decision is mandatory**: Requiring either a canonical successor or explicit no-successor-needed rationale prevents the "duplicate-candidate with no exit condition" problem from Phase4Dashboard/TechnicalAnalysis.
- **Reusable Asset Checks include 6 asset classes**: One more than the parent spec's 5 classes (adds "Request provenance, freshness, or runtime-status logic"), which is a valuable expansion.

## Detailed Recommendations

1. **Add status-to-directory mapping** to Archive Target table. This was also flagged in the parent spec review. Without it, two executors may archive the same type of page to different directories.

2. **Add a spec discovery step** to Guard And Test Checks. Recommended text:
   ```
   Discovery: Run `grep -rl '<page-basename>' web/frontend/tests/` and list all matches.
   ```

3. **Split the compound eligibility condition** (line 94) into individual rows for each reference type. This makes partial passes visible (e.g., "no import but still has docs link").

4. **Split Final Decision into classification + action**. Classification determines lifecycle status; action determines whether and when to execute the move.

5. **Consider adding a "Previously classified" field** to Page Metadata. If a page was classified in the 04-07 audit (e.g., `views/stocks/` = "失效主路由层，但兼容保留中"), the reviewer should record the prior judgment and whether it is being upheld or changed.

## Scoring

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Technical Accuracy | 5 | All referenced files verified. Gate logic is correct. |
| Completeness | 4 | Strong gate structure. Missing spec discovery mechanism and status-to-directory mapping. |
| Codebase Alignment | 5 | Lifecycle statuses match parent spec. 22 mainline-gate specs confirmed. Archive targets match proposed structure. |
| Actionability | 4 | Highly actionable per-page form. Compound eligibility condition and mixed decision/action list reduce clarity slightly. |
| Terminology Consistency | 5 | Terminology perfectly aligned with parent governance spec. |
| **Overall** | **4.6** | |

## Verdict

APPROVE_WITH_NOTES

Well-designed checklist that directly addresses historical failure modes. The gate chain (Truth → Functional → Assets → Guards → Successor → Eligibility) is sound and prevents premature archival. Two medium gaps — archive directory mapping and spec discovery step — should be resolved before batch execution begins, but do not block checklist adoption for read-only inventory (Step 1).
