# B4.012-M3a-E3b-E1 Docs Guides Entrypoints Navigation Closeout

> **历史记录说明**:
> 本文件记录 B4.012-M3a-E3b-E1 的实施与验证结果，不是当前仓库文档真相源。
> 当前文档导航真相仍以 `docs/README.md`、`docs/guides/README.md`、`docs/guides/INDEX.md` 与 FUNCTION_TREE 治理状态为准。

## Scope

- Node: `b4-012-m3a-e3b-e1-docs-guides-entrypoints-navigation-family`
- Commit: `d0957bfe2` (`B4.012-M3a-E3b-E1: align docs guides entrypoints`)
- Edited docs:
  - `docs/guides/README.md`
  - `docs/guides/INDEX.md`
- Governance state files:
  - `.governance/active-gates.json`
  - `.governance/active-gates.md`
  - `.governance/programs/artdeco-web-design-governance/nodes.json`

No source, runtime, test, OpenSpec, root agent-rule, or external dirty files were modified or staged.

## Landed Change

- Added explicit canonical target registries to `docs/guides/README.md` and `docs/guides/INDEX.md`.
- Preserved `docs/guides/` as a supporting transition surface, not a canonical docs trunk.
- Kept the existing family navigation links intact while making repository-hygiene path assertions deterministic.

## Focused Verification

Command:

```bash
pytest -q --no-cov -o addopts='' --tb=no \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_active_documentation_entry_guides_no_longer_point_to_removed_quickstart_and_start_here_files \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_guides_readme_navigation_links_use_current_canonical_paths \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_guides_root_remains_supporting_surface_not_docs_trunk \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_active_guides_no_longer_point_runtime_logs_to_repo_root_logs_directory \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_active_workflow_docs_no_longer_point_to_removed_docs_top_level_families
```

Result:

- Passed: 3
- Failed: 2

Passing E1 assertions:

- `test_active_documentation_entry_guides_no_longer_point_to_removed_quickstart_and_start_here_files`
- `test_guides_readme_navigation_links_use_current_canonical_paths`
- `test_guides_root_remains_supporting_surface_not_docs_trunk`

Residual failures are authorization-outside file-existence blockers:

- `docs/guides/openspec-cmd/README.md` is missing and is outside the E1 allowed path set.
- `openspec/changes/frontend-optimization-six-phase/implementation-plan.md` is missing and OpenSpec edits are explicitly forbidden in E1.

## Full Hygiene Baseline

Command:

```bash
pytest -q --no-cov -o addopts='' --tb=no tests/unit/scripts/test_repository_hygiene_paths.py
```

Result after E1:

- Passed: 24
- Failed: 78

This reduces the E3b-E no-source baseline from `21 passed / 81 failed` to `24 passed / 78 failed`.

## Gates

- `git diff --cached --check`: passed.
- FUNCTION_TREE validate: passed.
- GitNexus `verify-staged`: `5 files, 5 symbols, affected processes 0, risk low`.
- GitNexus `detect-changes --scope staged`: `5 files, 5 symbols, affected processes 0, risk low`.
- OPENDOG verification: fresh, `failing_runs: []`.
- GitNexus post-commit analyze: completed successfully, `223,102 nodes | 280,180 edges | 2931 clusters | 300 flows`.

## Follow-Up

Do not reopen E1 for the two residual failures. They need separate authorization because they require either:

- a `docs/guides/openspec-cmd/` family package, or
- an OpenSpec workflow-doc package touching `openspec/changes/frontend-optimization-six-phase/`.
