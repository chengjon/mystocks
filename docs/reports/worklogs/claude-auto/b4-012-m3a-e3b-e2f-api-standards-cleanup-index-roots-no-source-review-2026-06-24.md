# B4.012-M3a-E3b-E2f API + Standards Cleanup Index Roots No-Source Review

Date: 2026-06-24

## Scope

Candidate node: `b4-012-m3a-e3b-e2f-api-standards-cleanup-index-roots`

Parent: `b4-012-m3a-e3b-e2-web-frontend-guides-family-split`

This is a no-source review for the repository-hygiene docs-truth queue. No source, runtime, test, OpenSpec, or external dirty files were modified during the audit.

## Boundary

In scope for a future implementation package:

- `docs/reports/cleanup/index-artifacts/api/INDEX_root.md`
- `docs/reports/cleanup/index-artifacts/standards/INDEX_root.md`
- `docs/reports/INDEX.md`
- `docs/reports/cleanup/INDEX.md`
- `docs/reports/worklogs/claude-auto/`

Read-only source evidence:

- `archive/docs/reports/cleanup/index-artifacts/api/INDEX_root.md`
- `archive/docs/reports/cleanup/index-artifacts/standards/INDEX_root.md`

Out of scope:

- Deleting or modifying `archive/docs/reports/cleanup/index-artifacts/`
- Recreating `docs/api/INDEX_root.md` or `docs/standards/INDEX_root.md`
- Editing `docs/api/INDEX.md` or `docs/standards/INDEX.md`
- Editing source, runtime, tests, OpenSpec, root agent-rule files, or external dirty files

## Evidence

Focused failures:

```text
pytest -q --no-cov -o addopts='' --tb=short \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_api_index_root_is_converged_under_reports_cleanup_index_artifacts \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_standards_index_root_is_converged_under_reports_cleanup_index_artifacts
```

Current result:

- `test_api_index_root_is_converged_under_reports_cleanup_index_artifacts` fails because `docs/reports/cleanup/index-artifacts/api/INDEX_root.md` is missing.
- `test_standards_index_root_is_converged_under_reports_cleanup_index_artifacts` fails because `docs/reports/cleanup/index-artifacts/standards/INDEX_root.md` is missing.

Archive source assets are present:

- `archive/docs/reports/cleanup/index-artifacts/api/INDEX_root.md`
  - Size: 23848 bytes
  - SHA-256 prefix: `ec3d49cf7dcfa335`
  - Heading: `# Api`
- `archive/docs/reports/cleanup/index-artifacts/standards/INDEX_root.md`
  - Size: 4060 bytes
  - SHA-256 prefix: `51bdff7d7722aaa0`
  - Heading: `# Standards`

Current active path state:

- `docs/api/INDEX_root.md` does not exist.
- `docs/standards/INDEX_root.md` does not exist.
- `docs/reports/cleanup/index-artifacts/api/INDEX_root.md` does not exist.
- `docs/reports/cleanup/index-artifacts/standards/INDEX_root.md` does not exist.
- `docs/api/INDEX.md` does not expose `INDEX_root.md`.

Missing index signals:

- `docs/reports/INDEX.md` lacks `cleanup/index-artifacts/api/INDEX_root.md`.
- `docs/reports/INDEX.md` lacks `cleanup/index-artifacts/standards/INDEX_root.md`.
- `docs/reports/cleanup/INDEX.md` lacks `index-artifacts/api/INDEX_root.md`.
- `docs/reports/cleanup/INDEX.md` lacks `index-artifacts/standards/INDEX_root.md`.

## Decision

Prepare a narrow implementation authorization to restore the API and standards cleanup index root artifacts from archive into the canonical reports cleanup path and add the missing reports/cleanup index anchors.

The implementation must preserve archive compatibility and must not recreate legacy active paths under `docs/api/` or `docs/standards/`.

## Proposed Gates

- `git diff --cached --check`
- FUNCTION_TREE validate
- GitNexus verify-staged and detect-changes, risk low
- Focused repository-hygiene API/standards cleanup-index tests pass
- OPENDOG verification is fresh
- Exact staged set contains only authorized files
