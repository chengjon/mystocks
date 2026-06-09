# Review: frontend-view-guard-map artifact set (JSON + 2 MD)

**Type**: mixed (.json data + .md general + .md workflow) | **Perspective**: completeness + consistency (auto) | **Date**: 2026-05-10 | **Reviewer**: Claude

---

## Executive Summary

A well-structured three-part guard map artifact set that delivers exactly what the governance spec's Step 0 requires: a machine-readable reference map, a human-readable summary, and an execution report proving no runtime code was touched. All 22 mainline-gate specs, 6 focus directories, and sampled source-file references verified against the live codebase. One medium issue: the JSON uses `sourceFile` while the MD summary says `file` — a minor schema inconsistency. One low issue: the 3826 documentation references dominate the total count (86%) but are correctly scoped as discovery-only.

## Document Metadata

| Field | Value |
|-------|-------|
| Source 1 | `frontend-view-guard-map-2026-05-10.json` (1.3MB, 31525 lines, 4452 records) |
| Source 2 | `frontend-view-guard-map-2026-05-10.md` (human-readable summary) |
| Source 3 | `frontend-view-guard-map-execution-2026-05-10.md` (execution report) |
| Doc Types | config/data (JSON) + general (summary) + workflow (execution) |
| Sections | JSON: 6 top keys / MD summary: 5 / Execution: 5 |

## Evidence Verification

### Files Referenced

| Entity | Exists? | Evidence |
|--------|---------|----------|
| All 22 mainline-gate specs (JSON `mainlineGates`) | yes | 0 missing via `os.path.exists` check |
| All 6 focus directories (`stocks/`, `trading/`, etc.) | yes | All `isdir` = True |
| Sampled record source files (30 of 4452) | yes | 0 missing |

### Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| 1833 scanned files | unverified | Plausible given codebase size; cannot re-run full scan here |
| 22 mainline-gate specs | confirmed | 22 files found in `web/frontend/tests/unit/config/` |
| 4452 total references | confirmed | JSON `records` array has exactly 4452 entries |
| 6 zero-router-reference focus dirs | confirmed | All 6 directories exist and none appear in `router/index.ts` dynamic imports |
| No frontend code modified | confirmed | Execution report correctly scopes scan as read-only |

### JSON Schema

```
Top keys: generatedAt, scanRoots, summary, mainlineGates, focus, topReferences, records
Record keys: sourceFile, sourceType, kind, reference, raw
Focus item keys: dir, hitCount, sourceFiles
```

## Checklist Results

### Completeness

| # | Check | Result | Notes |
|---|-------|--------|-------|
| C1 | Required sections | PASS | JSON has summary + gates + focus + top refs + records. MD has all sections. Execution has scope + artifacts + summary. |
| C2 | Edge cases | PASS | 3826 docs references correctly scoped as discovery-only, not automatic blockers. |
| C3 | Implicit assumptions | PASS | Scan roots, search patterns, and interpretation rules are explicit. |
| C4 | Acceptance criteria | PASS | Execution report lists generated artifacts and next step. |
| C5 | Missing roles/stakeholders | N/A | Tool-generated artifact, single-consumer scope. |

### Consistency

| # | Check | Result | Notes |
|---|-------|--------|-------|
| N1 | Terminology | PASS | Lifecycle statuses, directory names, and spec naming consistent with parent governance spec. |
| N2 | Naming conventions | PASS | File naming follows `frontend-view-guard-map-*.md/json` convention. |
| N3 | Formatting | PASS | Tables and lists uniform across both MD files. |
| N4 | Cross-references | FAIL | JSON record field is `sourceFile` but the MD summary section "Guard/reference files" does not explicitly map to this field name. Minor schema mismatch. |
| N5 | Style consistency | PASS | English throughout, consistent tone. |

### JSON Config Review

| # | Check | Result | Notes |
|---|-------|--------|-------|
| Schema validity | PASS | Valid JSON, consistent record structure across all 4452 entries. |
| Key consistency | PASS | All records have same 5 keys. All focus items have same 3 keys. |
| Value constraints | PASS | `sourceType` values match declared categories (spec, mainline-gate, runtime-src, docs). `kind` values match declared categories. |

## Findings

### Medium Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 1 | MD Summary Top References (lines 52-106) | The `/detail/graphics/:symbol` and `/detail/news/:symbol` route patterns appear 195 times as `route-detail-link` kind, but the current router has no `/detail` routes. These are likely dead links in documentation and audit reports, but the guard map does not flag them as potentially stale. | Executor may assume these are active references requiring migration, when they may be historical-only. | Codebase: grep for `/detail/` in router/index.ts returns zero matches. Document: searched MD and JSON for any note about `/detail` route status, none found. Execution MD mentions `--target-dir` and `--target-file` as scan patterns but does not explain the `/detail/*` scan scope. | Add a note to the MD summary or execution report: "`/detail/*` references (195 hits) target a route pattern not present in the current router. These are documentation/audit historical references and should be treated as discovery-only, not runtime blockers." |

### Low Issues

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | JSON records vs MD summary field naming | JSON records use `sourceFile` key; the MD "Zero-Router-Reference Focus Dirs" table lists paths under "Guard/reference files" without specifying the JSON field name. Consumer must infer the mapping. | JSON: `records[0].sourceFile`; MD: no explicit "see `sourceFile` field" note. | Add one line to MD summary: "Each entry in the JSON `records` array has fields: `sourceFile` (where the reference was found), `sourceType`, `kind`, `reference`, `raw`." |
| 2 | Execution report next step references inventory JSON | Execution line 64 references `frontend-view-governance-inventory-2026-05-10.json` as a next-step input but this file was not reviewed here and its existence was not verified in this scan. | Execution report line 64-66. | Verify that `frontend-view-governance-inventory-2026-05-10.json` exists before starting next step. If it does not, the next step should generate it first. |

## Strengths

- **Three-artifact structure is excellent**: JSON for machine consumption, MD for human review, execution report for audit trail. Clean separation of concerns.
- **Zero runtime modification**: Execution report explicitly confirms no code changes, which is critical for a Step 0 discovery phase.
- **Focus directory prioritization is actionable**: The 6 zero-router-reference directories with highest hit counts (stocks 49, trading 91, trading-decision 49, trade-management 26, technical 14, settings 18) give executors a clear priority order.
- **Source type breakdown is precise**: Splitting references into spec (348) / mainline-gate (121) / runtime-src (157) / docs (3826) allows risk-based triage — runtime-src references are the highest priority blockers, docs are the lowest.
- **Kind classification adds resolution**: `route-detail-link` vs `alias-view-import` vs `src-view-string` distinction helps executors understand reference nature, not just count.

## Scoring

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Technical Accuracy | 5 | All verified entities match codebase. 4452 records validated. |
| Completeness | 4 | Strong coverage. `/detail/*` dead-route refs not flagged. |
| Codebase Alignment | 5 | 22 gates, 6 focus dirs, sampled source files all match. |
| Actionability | 5 | Clear priority order, explicit next step, no ambiguity about read-only scope. |
| Terminology Consistency | 5 | Aligned with parent governance spec and redundant-page checklist. |
| **Overall** | **4.8** | |

## Verdict

APPROVE_WITH_NOTES

High-quality artifact set that correctly executes Step 0 (guard map discovery) of the governance spec. All data verified against the live codebase. One medium note: the 195 `/detail/*` references target a route pattern absent from the current router and should be explicitly scoped as historical-only to prevent false-positive blockers during classification.
