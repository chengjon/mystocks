# B4.011-M2a Residual Docs Reports Dirty Review

Date: 2026-06-12
Branch: `wip/root-dirty-20260403`
Baseline HEAD: `da916c29b`
Mode: no-source residual dirty review
Source edits authorized: false

## Scope

This review covers only the remaining dirty state under `docs/reports` after
the HOLD-A, HOLD-B-Low, Quality-Medium, Quality-High, and Generated-Pair
retirement packages closed.

This review does not modify, stage, restore, delete, move, archive, or preserve
any residual dirty file. It only classifies the remaining dirty set and prepares
the next governance plan.

Explicitly out of scope:

- `docs/guides/**`
- `docs/superpowers/**`
- `web/**`
- `src/**`
- `tests/**`
- `scripts/**`
- OpenSpec
- ST-HOLD
- `marketKlineData`
- external dirty paths
- any source/test/runtime/generator changes

## Current Boundary

- HEAD: `da916c29b`
- Staged changes before review: empty
- Active gates before review: none
- Remaining `docs/reports` dirty distribution: `M 5 / ?? 12`
- Remaining tracked deletions under `docs/reports`: `0`

## Modified Tracked Files

All five modified tracked reports are active `docs/reports` files with no
tracked `archive/docs/reports/**` counterpart. They are not eligible for the
same active-HEAD-to-existing-archive retirement flow used by HOLD-A/HOLD-B.

| File | Worktree lines | HEAD lines | HEAD -> worktree diff | Source/test signal | Decision class |
| --- | ---: | ---: | ---: | --- | --- |
| `docs/reports/BACKTEST_API_DOCUMENTATION.md` | 523 | 521 | +2 / -0 | full-path source/test 0 | Modified tracked active report; needs preserve-vs-archive decision |
| `docs/reports/IMPLEMENT_WEB_FRONTEND_V2_NAVIGATION_STATUS_REPORT.md` | 478 | 469 | +9 / -0 | referenced by `tests/unit/scripts/test_repository_hygiene_paths.py` | Modified tracked active report with test anchor; do not retire without test-aware authorization |
| `docs/reports/PHASE2_MENU_REFACTORING_COMPLETION_REPORT.md` | 351 | 342 | +9 / -0 | full-path source/test 0 | Modified tracked active report; needs preserve-vs-archive decision |
| `docs/reports/codebase-cleanup-2026-03-29.md` | 177 | 177 | +1 / -1 | full-path source/test 0 | Modified tracked active report; needs preserve-vs-archive decision |
| `docs/reports/frontend-optimization-implementation-status-2026-01-27.md` | 889 | 880 | +9 / -0 | referenced by `tests/unit/scripts/test_repository_hygiene_paths.py` | Modified tracked active report with test anchor; do not retire without test-aware authorization |

Recommended next package: `B4.011-M2a-Residual-M5 modified tracked reports
decision review`, no-source first. This package should decide whether each
file stays active with its worktree changes, moves to archive, or needs a
separate test-aware retirement package.

## Untracked Files

None of the twelve untracked reports has a tracked archive counterpart at the
same relative path. They should not be blindly added, deleted, or moved without
provenance and destination review.

| File | Lines | Reference signal | Decision class |
| --- | ---: | --- | --- |
| `docs/reports/ARTDECO_DOCS_CODE_ALIGNMENT_AUDIT_2026-05-28-review.md` | 163 | docs-only references | Untracked ArtDeco/report pair candidate |
| `docs/reports/ARTDECO_DOCS_CODE_ALIGNMENT_AUDIT_2026-05-28.md` | 285 | docs-only references | Untracked ArtDeco/report pair candidate |
| `docs/reports/DASHBOARD_CRITIQUE_AUDIT.md` | 214 | docs-only references | Untracked standalone report candidate |
| `docs/reports/FRONTEND_DATA_SOURCE_DIAGNOSIS.md` | 198 | docs-only references | Untracked standalone report candidate |
| `docs/reports/GPU_DOCUMENTATION_INVENTORY.md` | 112 | docs-only references | Untracked standalone report candidate |
| `docs/reports/P3-C5-HANDOFF.md` | 181 | docs-only references | Untracked P3/C5 handoff candidate |
| `docs/reports/P3-C5-exception-consolidation-progress.md` | 96 | docs-only references | Untracked P3/C5 progress candidate |
| `docs/reports/PRODUCT_DESIGN_AUDIT.md` | 219 | docs-only references | Untracked standalone report candidate |
| `docs/reports/architecture/data-source-service-extraction-analysis-review-2026-06-09.md` | 268 | docs-only references | Untracked architecture review candidate |
| `docs/reports/worklogs/claude-auto/openstock-boundary-handoff-2026-06-11.md` | 60 | no references | External/OpenStock handoff candidate; keep separate from MyStocks docs/reports cleanup |
| `docs/reports/workspace-cleanup-plan-2026-05-14-review.md` | 166 | docs-only references | Untracked workspace cleanup pair candidate |
| `docs/reports/workspace-cleanup-plan-2026-05-14.md` | 253 | docs-only references | Untracked workspace cleanup pair candidate |

Recommended split:

1. `Residual-M5`: five modified tracked active reports. No-source decision
   first; implementation may need preserve-active or archive-add + active
   retirement. Two files have repository hygiene test anchors.
2. `Residual-Untracked-Reports`: eleven untracked MyStocks reports. Review
   provenance and target archive paths before any add/move/delete.
3. `Residual-OpenStock-Handoff`: one untracked OpenStock boundary handoff.
   Treat as external/provenance-sensitive and do not mix with MyStocks report
   archive batches.

## Decision

The previous HOLD-B retirement work is complete for all tracked deleted
`docs/reports` files: the deleted count is now zero. The remaining dirty set is
not deletion-retirement drift of existing archive counterparts. It is residual
modified active documentation plus untracked report artifacts.

No implementation should proceed from this review without a new package-specific
authorization.

## Required Gates For Any Follow-Up Implementation

- Exact staging only.
- `git diff --cached --check`.
- GitNexus `verify-staged`.
- GitNexus `detect_changes --scope staged`.
- OPENDOG verification with no cleanup blockers.
- Post-commit GitNexus `analyze --index-only`.
- Final verification that only the authorized residual family changed and that
  unrelated dirty paths are untouched.

## Recommended Next Authorization

Request no-source authorization for
`B4.011-M2a-Residual-M5 modified tracked reports decision review`.

The first follow-up should not edit files. It should decide the disposition for
the five modified tracked active reports, especially the two files anchored by
`tests/unit/scripts/test_repository_hygiene_paths.py`.
