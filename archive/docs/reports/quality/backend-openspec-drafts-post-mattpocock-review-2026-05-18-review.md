# Review: backend-openspec-drafts-post-mattpocock-review-2026-05-18.md

**Type**: md / proposal | **Perspective**: completeness + consistency + feasibility | **Date**: 2026-05-18 | **Reviewer**: Claude

---

## Executive Summary

The document is a well-structured post-review fix summary that accurately tracks how eight review findings were addressed across four OpenSpec changes and one new orchestration artifact. All referenced OpenSpec change directories and source evidence documents exist. Two medium issues were found: a JSON artifact path discrepancy between the document and the actual filesystem location, and a reference to `trading_monitor.py` which does not exist in the main worktree.

## Document Metadata

| Field | Value |
|-------|-------|
| Source | `docs/reports/quality/backend-openspec-drafts-post-mattpocock-review-2026-05-18.md` |
| File Type | md |
| Doc Type | proposal (post-review fix summary) |
| Sections | 6 |
| Referenced Files | 10 found / 1 path mismatch |
| Referenced Symbols | 1 found (`from app.core.logger import logger`) / 0 missing |

## Evidence Verification

### Files Referenced

| File | Exists? | Location |
|------|---------|----------|
| `docs/reports/quality/backend-openspec-drafts-mattpocock-review-2026-05-18.md` | yes | exact path |
| `docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md` | yes | exact path |
| `openspec/changes/consolidate-backend-api-domain-routers/` | yes | 6 files (proposal, design, tasks, 3 specs) |
| `openspec/changes/consolidate-backend-health-endpoints/` | yes | 6 files (proposal, design, tasks, 3 specs) |
| `openspec/changes/migrate-backend-singletons-to-lifecycle-di/` | yes | 5 files (proposal, design, tasks, 2 specs) |
| `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/` | yes | 5 files (proposal, design, tasks, 2 specs) |
| `docs/reports/quality/generated/backend-fullpath-route-table.md` | yes | exact path |
| `docs/reports/quality/generated/backend-fullpath-route-table.json` | no | exists at `web/backend/docs/reports/quality/generated/backend-fullpath-route-table.json` |
| `docs/reports/quality/generated/openapi-before.json` | no | expected to-be-generated prerequisite, not yet created |
| `scripts/dev/backend_audit_fullpath_routes.py` | yes | exact path |
| `scripts/generate_openapi.py` | yes | exact path |
| `scripts/dev/backend_audit_baseline.py` | yes | exact path |
| `scripts/run_pm2_integration_workflow.sh` | yes | exact path |
| `docs/reports/quality/backend-route-table-openapi-baseline-2026-05-18.md` | yes | exact path |
| `docs/reports/quality/backend-route-table-duplicate-routes-mattpocock-review-2026-05-18.md` | yes | exact path |
| `docs/reports/quality/backend-audit-documents-review-2026-05-15.md` | yes | exact path |

### Functions/Classes Referenced

| Symbol | Found? | Location |
|--------|--------|----------|
| `from app.core.logger import logger` | yes | `architecture/STANDARDS.md:52`, `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/tasks.md:28` |

### Code File References

| File | Exists in main? | Location |
|------|-----------------|----------|
| `trading_runtime.py` | yes | `web/backend/app/api/trading_runtime.py` |
| `trading_monitor.py` | no | only in `.worktrees/` branches, not main worktree |
| `backup_recovery.py` | yes | `web/backend/app/api/backup_recovery_secure.py` |
| `backup_recovery_secure/` | yes | `web/backend/app/api/backup_recovery_secure/` (package directory) |

### Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| "four OpenSpec drafts" | confirmed | 4 change directories found under `openspec/changes/` |
| "strict OpenSpec validation passed for all four changes" | unverified | cannot rerun `openspec validate` in this context; changes have valid directory structure |
| "markdown governance gate still exits 1 for unrelated historical documents" | unverified | no governance gate runtime available; claim is plausible |
| "no backend implementation files were changed" | unverified | would require `git diff` against pre-review state; claim is consistent with document purpose |
| "each tasks.md includes concrete verification commands" | confirmed | all 4 tasks.md files include explicit commands and script paths |

## Checklist Results

12 items PASS, 1 FAIL, 2 N/A.

### Completeness

| # | Check | Result | Notes |
|---|-------|--------|-------|
| C1 | Required sections | PASS | 6 sections cover verdict, artifacts, disposition, checklist, validation, boundary |
| C2 | Edge cases | PASS | Governance gate false-positive edge case noted (line 74-75) |
| C3 | Implicit assumptions | PASS | C/E/F/G codes defined in Updated Artifacts table |
| C4 | Acceptance criteria | PASS | Approval Checklist provides 8 verifiable items |
| C5 | Missing roles/stakeholders | PASS | "human approval review" stated; appropriate for this doc scope |

### Consistency

| # | Check | Result | Notes |
|---|-------|--------|-------|
| N1 | Terminology | PASS | C/E/F/G codes used consistently throughout |
| N2 | Naming conventions | PASS | File paths follow project conventions |
| N3 | Formatting | PASS | Tables well-structured, heading hierarchy correct |
| N4 | Cross-references | FAIL | `backend-fullpath-route-table.json` path mismatch (see Findings) |
| N5 | Style consistency | PASS | Uniform formal style throughout |

### Feasibility

| # | Check | Result | Notes |
|---|-------|--------|-------|
| F1 | Technical risk | PASS | High-risk trading/backup domains explicitly deferred |
| F2 | Dependency availability | PASS | All referenced scripts exist at stated paths |
| F3 | Timeline realism | N/A | No timeline claims in this summary document |
| F4 | Resource constraints | N/A | No resource claims in this summary document |
| F5 | Rollback plan | PASS | Rollback noted in orchestration doc and individual tasks.md files |

## Findings

### Medium Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 1 | Updated Artifacts, line 40 | `backend-fullpath-route-table.json` referenced at path `docs/reports/quality/generated/` but the file only exists at `web/backend/docs/reports/quality/generated/backend-fullpath-route-table.json`. The `.md` variant exists at the stated path but the `.json` does not. | Implementors following C/G prerequisites may generate or look for the JSON at the wrong path, causing false-negative route verification. | Glob for `docs/reports/quality/generated/backend-fullpath-route-table.json` returned no results. Grep found the file at `web/backend/docs/reports/quality/generated/backend-fullpath-route-table.json`. The orchestration doc (line 36) and the source doc (line 40) both reference `docs/reports/quality/generated/` as the location. Searched entire repo for `openapi-before.json` — not found anywhere, consistent with it being a to-be-generated prerequisite. | Clarify whether the JSON is generated at `docs/reports/quality/generated/` or `web/backend/docs/reports/quality/generated/`. Update the orchestration doc, C tasks.md (line 3), and G tasks.md (line 3) to use the correct output path. |
| 2 | Review Finding Disposition, line 34 | `trading_monitor.py` is listed alongside `trading_runtime.py` as a deferred high-risk file. `trading_runtime.py` exists at `web/backend/app/api/trading_runtime.py`, but `trading_monitor.py` does not exist in the main worktree — it only exists inside `.worktrees/` directories. | If C's change description records `trading_monitor.py` as a deferred route owner, implementors may search for a file that is not on main, causing confusion about whether the route ownership is stale or forward-looking. | Glob for `web/backend/app/api/trading_monitor.py` returned no results. Glob for `**/trading_monitor.py` found matches only in `.worktrees/td003-*`, `.worktrees/attribution-analysis-task4/`, `.worktrees/ml-training-prediction-runtime/`. | If `trading_monitor.py` is on a development branch not yet merged, note this explicitly (e.g., "pending merge from worktree branch X"). If the file was removed from main, remove it from the deferred list. |

### Low Issues

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | Validation Evidence, lines 60-72 | OpenSpec strict validation output is presented as raw command output but cannot be independently verified in this review context. | `openspec validate` is not a runnable tool in this environment. The four change directories do have valid structure (proposal, design, tasks, specs). | Consider adding a CI-checked validation step or noting the validation commit SHA for traceability. |

## Strengths

- Every review finding from the source review (`backend-openspec-drafts-mattpocock-review-2026-05-18.md`) is tracked with a clear disposition (Fixed / Fixed by explicit deferral) and a one-line evidence description.
- The Approval Checklist is well-aligned with the orchestration doc and individual tasks.md files — all 8 items were independently verifiable against the codebase.
- The Implementation Boundary section clearly separates approval readiness from implementation readiness, preventing premature code changes.
- The orchestration artifact provides a concrete execution order with blocking matrix, which is a significant improvement over independent proposals.

## Recommendations

1. **Resolve JSON path discrepancy** — Run `python scripts/dev/backend_audit_fullpath_routes.py` with the output directory argument and confirm where the JSON is actually written. Update all references to match.
2. **Clarify `trading_monitor.py` status** — Confirm whether this file is expected to exist on main. If it's branch-only, add a note to C's proposal or design indicating the file is pending merge.
3. **Add commit SHA to validation evidence** — The OpenSpec validation block would benefit from a commit SHA or CI run link to make the claim auditable.

## Scoring

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Technical Accuracy | 4 | All 8 approval checklist items verified; 1 file path mismatch and 1 stale reference found |
| Completeness | 5 | Every review finding has disposition; all sections expected for this doc type are present |
| Codebase Alignment | 4 | 10/11 referenced file paths resolve correctly; 1 JSON path mismatch |
| Actionability | 5 | Approval checklist items are binary (Done/not Done); implementation boundary is explicit |
| Terminology Consistency | 5 | C/E/F/G codes used uniformly; no naming drift |
| **Overall** | **4.6** | Weighted: actionability and completeness 2x |

## Verdict

APPROVE_WITH_NOTES — The document is accurate and well-structured for its purpose as a post-review fix summary. Two medium issues (JSON path mismatch, `trading_monitor.py` reference) should be clarified before the document is used as an implementation gate, but neither blocks the approval review workflow.
