# B4.012-M3a-E3b-E2d Hooks Guide Cleanup Index Bridge No-Source Review

Date: 2026-06-24

## Scope

Candidate node: `b4-012-m3a-e3b-e2d-hooks-guide-cleanup-index-bridge`

Parent: `b4-012-m3a-e3b-e2-web-frontend-guides-family-split`

This is a no-source review for the repository-hygiene docs-truth queue. No files were modified during the audit.

## Boundary

In scope for a future implementation package:

- `docs/reports/cleanup/index-artifacts/INDEX_root.md`
- `docs/reports/worklogs/claude-auto/`

Out of scope:

- `docs/guides/hooks/` content changes or retirement.
- `docs/INDEX.md`, `docs/guides/INDEX.md`, and `docs/guides/hooks/INDEX.md`.
- Source, runtime, tests, OpenSpec, root agent-rule files, and external dirty files.

## Evidence

Focused failure:

```text
pytest -q --no-cov -o addopts='' --tb=short tests/unit/scripts/test_repository_hygiene_paths.py::test_hook_guides_are_converged_under_guides_hooks_family
```

Result:

- Failed at `tests/unit/scripts/test_repository_hygiene_paths.py:799`
- Assertion missing from cleanup root bridge: `hooks/WEB_DEV_HOOKS_GUIDE.md`

Read-only audit found all expected canonical hook guide files already exist under `docs/guides/hooks/`:

- `WEB_DEV_HOOKS_GUIDE.md`
- `web-dev-hooks-guide.md`
- `hooks使用指南.md`
- `hooks详细说明.md`
- `hooks错误处理方法.md`
- `pre_commit_hook_setup_guide.md`
- `hook-analysis-report.md`
- `hook-optimization-summary.md`
- `INDEX.md`

The old `docs/web-dev/` path does not exist.

Existing index signals already satisfy the focused test outside the cleanup root bridge:

- `docs/INDEX.md` references `guides/hooks/INDEX.md`
- `docs/INDEX.md` references `guides/hooks/WEB_DEV_HOOKS_GUIDE.md`
- `docs/INDEX.md` references `guides/hooks/web-dev-hooks-guide.md`
- `docs/INDEX.md` references `guides/hooks/pre_commit_hook_setup_guide.md`
- `docs/INDEX.md` does not expose `guides/hooks/hook-analysis-report.md`
- `docs/INDEX.md` does not expose `guides/hooks/hook-optimization-summary.md`
- `docs/guides/INDEX.md` references the hooks family
- `docs/guides/hooks/INDEX.md` includes the transition-index signal
- `docs/reports/final_execution_summary.md` references `docs/guides/hooks/pre_commit_hook_setup_guide.md`

Missing cleanup root bridge entries:

- `hooks/WEB_DEV_HOOKS_GUIDE.md`
- `hooks/web-dev-hooks-guide.md`
- `hooks/hooks使用指南.md`
- `hooks/hooks详细说明.md`
- `hooks/hooks错误处理方法.md`

## Decision

Prepare a narrow implementation authorization to add only the missing hooks bridge entries to `docs/reports/cleanup/index-artifacts/INDEX_root.md`.

Do not change hook guide content, global docs indexes, source/runtime/test files, OpenSpec files, or any external dirty files in this package.

## Proposed Gates

- `git diff --cached --check`
- FUNCTION_TREE validate
- GitNexus verify-staged and detect-changes, risk low
- Focused repository-hygiene hook guide test passes
- OPENDOG verification is fresh
- Exact staged set contains only authorized files
