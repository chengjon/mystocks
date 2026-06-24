# B4.012-M3a-E3b-E2e Superpowers Guide Bootstrap Closeout

Date: 2026-06-24

## Scope

Node: `b4-012-m3a-e3b-e2e-superpowers-guide-bootstrap`

Program: `.governance/programs/artdeco-web-design-governance`

Authorized paths:

- `docs/guides/superpowers/`
- `docs/reports/cleanup/directory-organization/DIRECTORY_ORGANIZATION_PLAN.md`
- `docs/reports/worklogs/claude-auto/`

Non-goals preserved:

- No source, runtime, test, or OpenSpec edits.
- No deletion or modification of `archive/docs/guides-merged/superpowers/`.
- No recreation of `docs/superpowers/`.
- No `docs/INDEX.md` edits.
- No external dirty-file staging.

## Landed Changes

Implementation commit: `72fc3a220`

Bootstrapped canonical superpowers guide family under `docs/guides/superpowers/` from existing archived assets:

- `INDEX.md`
- `plans/2026-03-23-frontend-test-gates.md`
- `plans/2026-03-25-guides-onboarding-migration.md`

Added a directory-plan anchor to `docs/reports/cleanup/directory-organization/DIRECTORY_ORGANIZATION_PLAN.md`:

- `docs/guides/superpowers/`

The copied canonical files match the archived source files byte-for-byte.

## Verification

Passed before implementation commit:

- `git diff --cached --check`
- `node /root/.codex/skills/myskills/skills/function-tree/scripts/ft-governance.cjs validate --root /opt/claude/mystocks_spec`
- `node .gitnexus/run.cjs verify-staged --repo mystocks`
- `node .gitnexus/run.cjs detect-changes --scope staged --repo mystocks`
- `pytest -q --no-cov -o addopts='' --tb=short tests/unit/scripts/test_repository_hygiene_paths.py::test_superpowers_docs_are_converged_under_guides_family`
- OPENDOG `run-verification` recorded the focused test as passed.
- `node .gitnexus/run.cjs analyze --force --index-only --verbose --worker-timeout 60`

GitNexus staged result before commit:

- Changed files: 7
- Changed symbols: 2
- Affected processes: 0
- Risk: low

Post-commit GitNexus result:

- Indexed commit: `72fc3a220`
- Nodes: 223,710
- Edges: 280,815
- Flows: 300

## Boundary Notes

This package intentionally restored the canonical docs path from archived guide assets rather than moving or deleting archive files. `docs/INDEX.md` already referenced the canonical superpowers guide entry and was left untouched.

The existing long-running worktree still contains unrelated external dirty files. Exact staging and staged GitNexus checks were used as the enforceable package boundary.

## Result

The superpowers guide canonical path now satisfies the focused repository-hygiene test. The next repository-hygiene docs-truth package should continue from another localized guide-family failure before touching higher-risk root entrypoint, runtime-log, or source/script assertions.
