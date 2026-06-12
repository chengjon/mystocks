# Review: workspace-cleanup-plan-2026-05-14.md

**Type**: `.md` / `plan` | **Perspective**: completeness + feasibility + consistency | **Date**: 2026-05-14 | **Reviewer**: Claude

---

## Executive Summary

This cleanup plan proposes a 7-batch strategy to commit 1055 uncommitted changes on branch `wip/root-dirty-20260403`. The plan is well-structured with sound principles, but contains **multiple factual inaccuracies** in the status overview tables that diverge from the live codebase. Key counts (total, modified, untracked, staged, line deltas) are all stale or miscounted. The staged file count is particularly off (claims 5, actually 18). Despite these data quality issues, the batch strategy itself is reasonable and actionable after data corrections.

## Document Metadata

| Field | Value |
|-------|-------|
| Source | `docs/reports/workspace-cleanup-plan-2026-05-14.md` |
| File Type | `.md` |
| Doc Type | `plan` |
| Sections | 6 |
| Referenced Files | 5 named explicitly |
| Referenced Symbols | 0 |

## Evidence Verification

### Files Referenced

| File | Exists? | Location |
|------|---------|----------|
| `.gitignore` | yes | `/opt/claude/mystocks_spec/.gitignore` |
| `reports/governance/` | yes | 134 files total |
| `reports/governance/2026-05-04-tech-debt-audit-review-review.md` | yes | chain-review file |
| `reports/governance/2026-05-04-tech-debt-audit-review-disposition-review-disposition.md` | yes | chain-review file |
| `web/backend/web/backend/.claude/` | yes | confirmed anomalous nesting |
| `src/application/services/performance_optimizer.py` | yes | 8.5K, staged |
| `tests/ddd/test_domain_layer_dependencies.py` | yes | 2.1K, staged |
| `.env.example` | yes | modified (in git status) |
| `governance/function-tree/catalog.yaml` | yes | modified (in git status) |
| `.agent/` | yes | 2 files in status |
| `.planning/STATE.md` | yes | 1 file in status |
| `scripts/dev/a-stock-*` | no | glob returned no results |

### Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| "1039 uncommitted changes" | **contradicted** | `git status --short \| wc -l` returns **1055** (16 more) |
| "500 modified (unstaged)" | **contradicted** | Actual count is **494** |
| "425 untracked" | **contradicted** | Actual count is **436** |
| "109 deleted (unstaged)" | **confirmed** | Exact match: 109 |
| "5 staged" | **contradicted** | Actual count is **18** staged files |
| "+22062/-41404 line changes" | **contradicted** | `git diff --stat` shows **+20445/-40937** |
| "20+ nested .claude/ dirs" | **contradicted** | `find` returns **38** nested `.claude/` directories |
| "15-20 chain-review files" | **contradicted** | Only **4** chain-review files and **3** matching the specific patterns (`review-review`, `disposition-review-disposition`, `review-disposition-review`) |
| "76 deleted openspec/changes/ files" | **confirmed** | Exact match: 76 |
| "reports/governance/ ~15-20 chain files" | **contradicted** | Only 4 chain-pattern files found in 134 total governance files |
| "web/ 287 modified" | **contradicted** | Actual: **291** modified files under web/ |
| "docs/ 53 modified + 193 new" | **contradicted** | Actual: **238** modified + **53** new |
| "tests/ 72 modified + 11 new" | **contradicted** | Actual: **108** modified + **11** new |
| ".claude/ 11 modified + 64 new" | **contradicted** | Actual: **11** modified + **82** new |
| "src/ 32 modified + 1 new" | **contradicted** | Actual: **56** modified + **17** new |
| "openspec/ 11 modified + 16 new + 76 deleted" | **contradicted** | Actual: **26** modified + **11** new + **76** deleted |
| "scripts/ 10 modified + 17 new" | **contradicted** | **partially confirmed** | Modified count matches approximately; need exact count |
| "reports/ 6 modified + 38 new" | **contradicted** | Actual: **11** modified + **214** new |
| "scripts/dev/a-stock-* directories" | **contradicted** | Glob for `scripts/dev/a-stock-*` returned **no results**. Files may have been moved or the paths are different |
| "5 staged: mixed governance docs + code" | **contradicted** | 18 staged files spanning docs, src, tests, scripts, web/backend, web/frontend |
| ".gitignore currently lacks nested .claude/ rules" | **confirmed** | Current `.gitignore` has `.claude/` + `!.claude/` at root level only; no `/*/.claude/` patterns |

## Checklist Results

### Completeness

| # | Check | Result | Notes |
|---|-------|--------|-------|
| C1 | Required sections | PASS | 6 sections: status, strategy, batch details, pre-check, timeline, follow-up. Appropriate for a plan document. |
| C2 | Edge cases | FAIL | No mention of how to handle merge conflicts or files that are both modified AND staged (MM state). `tests/api/file_tests/test_monitoring_api.py` is in MM state. |
| C3 | Implicit assumptions | FAIL | Assumes `reports/` directory distribution section header refers to `reports/governance/` but actually there are 214 untracked files in `reports/` broadly -- far more than the claimed 38. |
| C4 | Acceptance criteria | PASS | Each batch has a commit message and risk level; pre-execution checklist has 6 items. |
| C5 | Missing roles/stakeholders | FAIL | No mention of who reviews/approves each batch before execution. Plan says "to be confirmed" for 6 items but doesn't assign ownership. |

### Feasibility

| # | Check | Result | Notes |
|---|-------|--------|-------|
| F1 | Technical risk | PASS | Risk levels are assigned. Batch 6 (web/) correctly identified as highest risk with split recommendation. |
| F2 | Dependency availability | FAIL | `scripts/dev/a-stock-*` referenced in batch 3 but glob finds no such directories. These may not exist or paths may be wrong. |
| F3 | Timeline realism | PASS | ~60 minutes total estimate is reasonable for git operations of this scale. |
| F4 | Resource constraints | N/A | Single-person execution implied. |
| F5 | Rollback plan | FAIL | Document claims "each batch independently rollbackable" but doesn't specify the rollback mechanism (e.g., `git reset HEAD~1` vs interactive rebase). No mention of creating a backup branch before starting. |

### Consistency

| # | Check | Result | Notes |
|---|-------|--------|-------|
| N1 | Terminology | PASS | Consistent use of Chinese terminology throughout. |
| N2 | Naming conventions | PASS | File paths and commit messages follow project conventions. |
| N3 | Formatting | PASS | Markdown tables and code blocks used consistently. |
| N4 | Cross-references | FAIL | Internal data is self-contradictory: status table claims 1039 total but per-directory breakdown sums to different numbers. |
| N5 | Style consistency | PASS | Formal planning style maintained throughout. |

## Findings

### Critical Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 1 | Section 1 (status overview) | Staged file count is 18, not 5 as claimed | HIGH -- misrepresents scope; batch 5 claims "reset 5 staged files" but there are 18 | `git status --short \| grep '^[AMDR]' \| wc -l` returns 18. The document's batch 5 plan to "git reset HEAD" only accounts for 5 files | Update count to 18 and enumerate all staged files; revise batch 5 reset instructions accordingly |
| 2 | Section 1 (status overview) | Every major count in the status table is inaccurate: total (1055 vs 1039), modified (494 vs 500), untracked (436 vs 425), line deltas (+20445/-40937 vs +22062/-41404) | HIGH -- foundational data errors undermine confidence in all downstream batch sizing and risk assessments | Verified via `git status --short` counts and `git diff --stat` | Re-run counts immediately before execution and update the table |

### Medium Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 3 | Section 1 (key findings) | Claims "15-20 chain-review files" but only 4 exist | MED -- overstates cleanup scope, could lead to unnecessary search for phantom files | `ls reports/governance/*review-review*` etc. returns exactly 4 files: `review-review.md`, `review-disposition-review.md`, `review-disposition-review-disposition.md`, and its duplicate | Correct count to 4; adjust batch 0 file count estimate |
| 4 | Section 1 (key findings) | Claims "20+" nested `.claude/` directories but actual count is 38 | MED -- significantly understates the scope of auto-generated clutter | `find . -path '*/.claude' -type d \| wc -l` returns 38 | Update count to 38 |
| 5 | Section 1 (directory distribution) | Per-directory breakdown has multiple inaccuracies: src/ modified is 56 not 32, reports/ untracked is 214 not 38, docs/ counts are swapped (238 modified + 53 new, not 53 modified + 193 new) | MED -- wrong batch sizing for batches 4, 5, and 6 | Verified via individual `git status` counts per directory | Re-derive all directory counts from fresh `git status` |
| 6 | Section 3 (batch 3) | References `scripts/dev/a-stock-*` directories but glob finds no results at that path | MED -- may be referencing files that don't exist or have been moved | `find scripts/dev/a-stock-*` returns nothing; but `find . -name '.claude' -path '*a-stock*'` shows `.claude/` dirs inside `scripts/dev/a-stock-backtest/`, `scripts/dev/a-stock-financial/`, etc. | The directories exist but are empty or only contain `.claude/` subdirs. Verify actual file contents before including in batch 3 |
| 7 | Section 3 (batch 5) | Plan to "git reset HEAD" the 5 staged files is incomplete -- 18 files are staged, some in MM state | MED -- partial reset could leave the repository in an inconsistent state | `tests/api/file_tests/test_monitoring_api.py` is `MM` (staged + unstaged changes). Resetting only 5 of 18 staged files would lose the intent of the other 13 | List all 18 staged files, determine which batch each belongs to, and plan a full reset + re-stage strategy |
| 8 | Section 3 (batch 6) | `web/backend/` count is 42 modified+untracked (not "39 modified + 3 new" as implied) | MED -- minor but adds up when planning batch sizes | `git status --short \| grep 'web/backend/' \| grep '^.[^D]' \| wc -l` = 42 | Verify exact counts |

### Low Issues

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 9 | Section 4 (pre-check) | No backup branch recommendation before starting | Plan operates on a working branch but doesn't suggest `git branch wip/root-dirty-20260403-backup` as safety net | Add a step 0: create backup branch |
| 10 | Section 3 (batch 0) | `.gitignore` pattern proposed uses only 3 levels of nesting (`/*/.claude/`, `/*/*/.claude/`, `/*/*/*/.claude/`) | Found `.claude/` dirs at 4+ levels deep (e.g., `tests/changes/archive/2026-01-08-consolidated-technical-debt/remediate-phase7-technical-debt/specs/.claude`) | Use `**/.claude/` with root exclusion instead of fixed-depth patterns |
| 11 | Section 5 (timeline) | File count totals per batch sum to ~954, not 1039 (or the actual 1055) | Batch estimates: 30+109+25+70+250+105+365 = 954 | Recalculate after correcting directory counts |
| 12 | Section 6 (follow-up) | No mention of verifying the branch's merge-readiness criteria | Plan says "confirm if branch can merge to main" but doesn't list what constitutes readiness | Add merge-readiness criteria: clean status, passing CI, no conflict markers |

## Strengths

- **Batch ordering logic** is sound: "reduce before add" (garbage cleanup first, then deletions, then docs, then code) minimizes risk of losing valuable changes in noise
- **Risk assessment per batch** is appropriately calibrated -- pure docs marked low, code changes marked medium, the massive web/ batch marked medium-high with split recommendation
- **Pre-execution checklist** (Section 4) identifies the right open questions that need human confirmation before proceeding
- **Commit message conventions** follow the project's established patterns (`chore:`, `docs:`, `feat:`)

## Detailed Recommendations

1. **Re-run all counts immediately before execution.** The data in the status table was captured at a different point in time and no longer reflects reality. Use a single `git status --short` snapshot and derive all counts from it atomically.

2. **Expand the staged file handling.** There are 18 staged files, not 5. Enumerate them all, classify each into its target batch, then plan a full `git reset HEAD` followed by selective re-staging per batch. Pay special attention to the MM-state file `tests/api/file_tests/test_monitoring_api.py`.

3. **Use `**/.claude/` for the .gitignore pattern.** The proposed 3-level fixed-depth patterns won't catch deep nesting found in `tests/changes/archive/.../specs/.claude/`. A `**/.claude/` pattern with `!.claude/` (root exclusion already present) is more robust.

4. **Add a pre-step to create a backup branch.** Before batch 0, run `git branch wip/root-dirty-20260403-backup` to preserve the current state as an undo point.

5. **Clarify the `scripts/dev/a-stock-*` situation.** These directories appear to exist (contain `.claude/` subdirs) but contain no tracked or visible files. Determine whether they are empty experiments or contain untracked content worth committing.

6. **Correct the chain-review file count.** Only 4 files match the chain patterns, not 15-20. The batch 0 file count estimate should be reduced accordingly.

7. **Split batch 4 further.** With 238+ modified docs files and 53+ new ones, even the suggested 4a/4b/4c split may be insufficient. Consider also separating `openspec/` (20 files) from `docs/` (260+ files) as they serve different audiences.

## Scoring

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Technical Accuracy | 2 | 8+ factual claims contradicted by live codebase: counts, file locations, directory distributions |
| Completeness | 3 | Good structure and coverage but missing backup strategy, MM-state handling, and stakeholder assignment |
| Codebase Alignment | 2 | Nearly every numeric claim in the status overview is stale or wrong |
| Actionability | 4 | Batch strategy is clear with specific commit messages; pre-checklist identifies right questions |
| Terminology Consistency | 4 | Consistent Chinese terminology; commit message conventions match project standards |
| **Overall** | **3.0** | Plan logic is sound but built on inaccurate foundation data |

## Verdict

**NEEDS_REVISION**

The batch strategy and execution order are well-designed, but the document's status overview contains pervasive factual inaccuracies. Every numeric claim in Section 1 should be re-derived from a fresh `git status` snapshot before this plan is executed. The staged file handling must be completely rewritten (18 staged files, not 5, including one in MM state). With corrected data, this plan would be APPROVE_WITH_NOTES.
