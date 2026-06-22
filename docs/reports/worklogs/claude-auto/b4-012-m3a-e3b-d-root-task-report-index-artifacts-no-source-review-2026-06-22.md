# B4.012-M3a-E3b-D Root TASK-REPORT Index Artifacts No-Source Review

Date: 2026-06-22
Program: artdeco-web-design-governance
Node: b4-012-m3a-e3b-d-root-task-report-index-artifacts-family
Mode: no-source review and authorization preparation

## Boundary

This review follows B4.012-M3a repository hygiene docs-truth governance after E3b-C reports/index closeout.

No source, runtime, test, OpenSpec, docs/guides, docs/INDEX.md, or OpenStock provider/data-source runtime files are modified by this review.

## Trigger

E3b-C closed the reports/index family and left one focused repository-hygiene assertion outside its allowed paths:

- `tests/unit/scripts/test_repository_hygiene_paths.py::test_guides_index_root_is_converged_under_reports_cleanup`

The remaining assertion expects the root task artifact to point readers to:

- `docs/reports/cleanup/index-artifacts/INDEX_root.md`

## Current Truth Matrix

| File | Current state | Has `docs/reports/cleanup/index-artifacts/INDEX_root.md` |
| --- | --- | --- |
| `TASK-REPORT.md` | tracked modified before this package | no |
| `docs/reports/cleanup/index-artifacts/INDEX_root.md` | tracked, created by E3b-C | not required inside itself |
| `docs/reports/cleanup/FILE_CLEANUP_TASK.md` | tracked | yes |
| `reports/governance/2026-03-09-batch-3-root-doc-inventory.md` | tracked | yes |

## Risk Assessment

- Impact: low runtime risk; documentation/root task artifact only.
- Staging risk: medium, because `TASK-REPORT.md` already has an external unstaged append hunk unrelated to this package.
- Required implementation discipline: if source/docs authorization is granted, stage only the intended root task artifact reference hunk and keep the pre-existing append hunk unstaged.
- No deletion, migration, or source behavior change is needed.

## Proposed Implementation Authorization

Allowed paths:

- `TASK-REPORT.md`
- `docs/reports/cleanup/index-artifacts/INDEX_root.md`
- `docs/reports/worklogs/claude-auto/`

Allowed action:

- Add the missing root task artifact reference to `TASK-REPORT.md`, preserving existing content and not staging unrelated external append hunks.

Non-goals:

- Do not modify source/runtime/test/OpenSpec files.
- Do not modify `docs/guides/`, `docs/INDEX.md`, or unrelated reports families.
- Do not stage the pre-existing unrelated `TASK-REPORT.md` append hunk.
- Do not touch OpenStock provider/data-source runtime work.

Focused verification:

- `pytest -q --no-cov -o addopts='' --tb=no tests/unit/scripts/test_repository_hygiene_paths.py::test_guides_index_root_is_converged_under_reports_cleanup`

Expected outcome:

- The focused assertion passes after the root task artifact records the canonical reports cleanup index path.
- The broader repository hygiene file may still contain unrelated docs-truth family failures.
