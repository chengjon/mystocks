# B4.012-M3a-E3a-R3 Root Overview Docs Truth Review

Date: 2026-06-24
Program: artdeco-web-design-governance
Node: b4-012-m3a-e3a-r3-root-overview-docs-truth-review
Parent: b4-012-m3a-e3a-repository-hygiene-unit-script-authorization
Mode: no-source decision audit
Source edits authorized: false
Current HEAD: 8803d240a383

## Scope

This review isolates the root/overview docs failures identified by R2:

- `test_docs_root_entrypoints_are_frozen_to_index_and_function_tree`
- `test_docs_claude_doc_is_converged_under_overview_family`
- `test_docs_iflow_doc_is_converged_under_overview_family`

It is read-only. No docs, tests, source, OpenSpec, runtime, or root agent-rule files were modified in this package.

## Current Facts

Current `docs/` root files:

- `FUNCTION_TREE.md`
- `INDEX.md`
- `PRODUCT.md`
- `README.md`
- `codex-invalid-matcher-troubleshooting.md`

The repository-hygiene assertion expects only:

- `FUNCTION_TREE.md`
- `INDEX.md`

Tracked/untracked split:

- `docs/FUNCTION_TREE.md`: tracked, currently modified outside this package
- `docs/INDEX.md`: tracked, currently modified outside this package
- `docs/PRODUCT.md`: tracked
- `docs/README.md`: tracked
- `docs/codex-invalid-matcher-troubleshooting.md`: untracked external file, must remain isolated

Overview placement facts:

- `docs/CLAUDE.md`: absent
- `docs/overview/claude.md`: present
- `docs/IFLOW.md`: absent
- `docs/overview/IFLOW.md`: present
- `docs/INDEX.md` already contains `overview/claude.md`
- `docs/INDEX.md` already contains `overview/IFLOW.md`
- `docs/INDEX.md` no longer contains root `CLAUDE.md` or root `IFLOW.md` links

Remaining reference gaps observed by string probe:

- `README.md` does not contain `docs/overview/IFLOW.md`
- `docs/guides/README.md` does not contain `docs/overview/IFLOW.md`

## Decision

The root/overview family should not be fixed by changing the repository-hygiene test first. The current failures represent real docs-truth drift:

1. `docs/` root is not frozen to the expected two-entrypoint surface.
2. `docs/CLAUDE.md` and `docs/IFLOW.md` have mostly converged into `docs/overview/`, but downstream references are not fully converged.
3. `docs/codex-invalid-matcher-troubleshooting.md` is untracked and must not be bundled with tracked docs repairs.
4. Existing external modifications to `README.md`, `docs/FUNCTION_TREE.md`, and `docs/INDEX.md` must be isolated unless a follow-up package explicitly includes them.

## Recommended Follow-Up Package

Create a separate implementation authorization before editing any docs or assertions:

`B4.012-M3a-E3a-R3-A root overview docs truth implementation`

Candidate scope for authorization, pending fresh preflight:

- tracked docs entrypoint truth:
  - `docs/README.md`
  - `docs/PRODUCT.md`
  - `docs/INDEX.md`
  - `README.md`
  - `docs/guides/README.md`
  - `docs/overview/claude.md`
  - `docs/overview/IFLOW.md`
- optional test assertion update only if the canonical docs-root policy changes:
  - `tests/unit/scripts/test_repository_hygiene_paths.py`

Explicit exclusions for that package unless separately authorized:

- `docs/codex-invalid-matcher-troubleshooting.md`
- root `AGENTS.md`
- root `CLAUDE.md`
- `docs/FUNCTION_TREE.md`
- OpenSpec files
- source/runtime/frontend/backend files
- external dirty files

## Governance Outcome

R3 root overview docs truth review is ready to move to `decision-prepared`.

E3a remains blocked until the root/overview, active guides, reports, API-docs, and cleanup-index families are resolved through separate authorized packages.
