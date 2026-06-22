# B4.012-M3a-E3b-C repository hygiene reports/index authorization prep

Date: 2026-06-22
Repo: `/opt/claude/mystocks_spec`
Branch: `wip/root-dirty-20260403`
Mode: authorization preparation only

## Purpose

Prepare a narrow implementation authorization for the first docs-truth repair family under the repository hygiene atlas.

This package does not modify documentation truth yet. It only defines the boundary that a later source-authorized/docs-authorized implementation package must follow.

## Parent Evidence

Derived from:

- `docs/reports/worklogs/claude-auto/b4-012-m3a-e3b-b-repository-hygiene-docs-truth-repair-atlas-2026-06-22.md`
- `docs/reports/worklogs/claude-auto/b4-012-m3a-e3b-c-repository-hygiene-reports-index-family-2026-06-22.md`

Current known focused baseline:

- `pytest tests/unit/scripts/test_repository_hygiene_paths.py -q`
- Result: `87 failed, 15 passed`

## Proposed Allowed Paths

Implementation should be limited to reports/index documentation truth:

- `docs/reports/**`
- `reports/**`
- `docs/README.md`

The `docs/README.md` allowance is limited to the canonical link / summary pointing at `docs/reports/README.md`.

## Proposed Forbidden Paths

Do not include these in the reports/index implementation package:

- `tests/**`
- `src/**`
- `web/**`
- `openspec/**`
- `docs/guides/**`
- `docs/INDEX.md`
- `docs/architecture/**`
- `docs/overview/**`
- `.governance/programs/artdeco-web-design-governance/cards/b4-012-m3a-c5-other-adapter-compatibility-tests-authorization.yaml`
- `.governance/programs/artdeco-web-design-governance/cards/b4-013-m1a-watchlist-runtime-import-reexport.yaml`
- `.governance/programs/artdeco-web-design-governance/cards/b4-013-m3a-b5-query-runtime-fallback-cleanup.yaml`
- existing B4.013 untracked worklogs

If repair evidence proves `docs/INDEX.md`, `docs/guides/**`, or test assertions must change, stop and split that into the next family package instead of expanding this one.

## Proposed Non-Goals

- Do not rewrite repository hygiene tests in this family.
- Do not repair guide-navigation failures.
- Do not repair root-entrypoint contract failures.
- Do not move or delete source/runtime/OpenSpec files.
- Do not touch OpenStock provider/runtime boundaries.

## Proposed Commit Gates

- `git diff --cached --check`
- FUNCTION_TREE validate
- GitNexus `verify-staged`
- GitNexus `detect-changes --scope staged`
- OPENDOG verification fresh
- focused pytest for the exact reports/index test subset, or a documented unchanged baseline if the implementation is intentionally partial

## Proposed Closeout Gates

- staged files contain only the authorized reports/index documentation paths and governance evidence
- no source/runtime/test/OpenSpec files are staged
- `tests/unit/scripts/test_repository_hygiene_paths.py` focused result is reported with before/after delta
- FUNCTION_TREE node transitions to landed/closeout only after implementation evidence is recorded

## Decision

This node is ready to move from `decision-prepared` to `authorization-prepared` for reports/index family implementation review.
