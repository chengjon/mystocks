# B4.012-M3a-E3b-E2e Superpowers Guide Bootstrap No-Source Review

Date: 2026-06-24

## Scope

Candidate node: `b4-012-m3a-e3b-e2e-superpowers-guide-bootstrap`

Parent: `b4-012-m3a-e3b-e2-web-frontend-guides-family-split`

This is a no-source review for the repository-hygiene docs-truth queue. No source, runtime, test, OpenSpec, or external dirty files were modified during the audit.

## Boundary

In scope for a future implementation package:

- `docs/guides/superpowers/`
- `docs/reports/cleanup/directory-organization/DIRECTORY_ORGANIZATION_PLAN.md`
- `docs/reports/worklogs/claude-auto/`

Read-only source evidence:

- `archive/docs/guides-merged/superpowers/`

Out of scope:

- Deleting or modifying `archive/docs/guides-merged/superpowers/`
- Recreating or modifying `docs/superpowers/`
- Editing `docs/INDEX.md`
- Editing source, runtime, tests, OpenSpec, root agent-rule files, or external dirty files

## Evidence

Focused failure:

```text
pytest -q --no-cov -o addopts='' --tb=short tests/unit/scripts/test_repository_hygiene_paths.py::test_superpowers_docs_are_converged_under_guides_family
```

Current result:

- Fails with `FileNotFoundError`
- Missing: `docs/guides/superpowers/INDEX.md`

Existing source assets are present in archive:

- `archive/docs/guides-merged/superpowers/INDEX.md`
- `archive/docs/guides-merged/superpowers/plans/2026-03-23-frontend-test-gates.md`
- `archive/docs/guides-merged/superpowers/plans/2026-03-25-guides-onboarding-migration.md`

Current active path state:

- `docs/superpowers/` does not exist.
- `docs/guides/superpowers/` does not exist.
- `docs/INDEX.md` already references `guides/superpowers/INDEX.md`.
- `docs/INDEX.md` already avoids exposing the two plan files directly.
- `docs/INDEX.md` already contains `Supporting Guides](guides/superpowers/INDEX.md)`.
- `docs/reports/cleanup/directory-organization/DIRECTORY_ORGANIZATION_PLAN.md` does not yet reference `docs/guides/superpowers/`.

Archive `INDEX.md` signals:

- Contains `transition index`.
- References `2026-03-23-frontend-test-gates.md`.
- References `2026-03-25-guides-onboarding-migration.md`.

## Decision

Prepare a narrow implementation authorization to bootstrap the canonical `docs/guides/superpowers/` family from the existing archived guide assets and add the missing directory-plan anchor.

The implementation should preserve archive compatibility by copying/restoring the canonical guide files only. It must not delete archive files or recreate `docs/superpowers/`.

## Proposed Gates

- `git diff --cached --check`
- FUNCTION_TREE validate
- GitNexus verify-staged and detect-changes, risk low
- Focused repository-hygiene superpowers guide test passes
- OPENDOG verification is fresh
- Exact staged set contains only authorized files
