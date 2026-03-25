# Directory Governance Integration PR Draft

## Suggested PR Title

`chore(governance): tighten root hygiene and archive legacy directory drafts`

## Summary

This branch combines two previously isolated governance batches into one reviewable integration branch:

1. `chore(governance): tighten root hygiene and local-only config rules`
2. `docs(cleanup): archive legacy directory-organization drafts`

## What Changed

### Root Governance

- tightened root file governance across:
  - `directory-structure.yaml`
  - `check_directory_structure.py`
  - `check_structure.py`
  - `tree-lint.sh`
- clarified dirty-worktree GitNexus usage in:
  - `AGENTS.md`
  - `CLAUDE.md`
- converted `opencode.json` / `tui.json` to local-only root config treatment
- removed retired `.aider.*` root files from the working tree contract

### Runtime Artifact Hygiene

- moved pytest HTML/XML/data/cache defaults under canonical `var/` / `reports/` locations
- updated runtime cleanup helpers and active test runners
- removed root runtime artifacts from the expected repository baseline

### Directory-Organization Docs

- kept `DIRECTORY_ORGANIZATION_PLAN.md` as the current project-level baseline
- moved older directory-organization drafts into `docs/reports/cleanup/directory-organization/legacy/`
- removed root-level ArtDeco redirect docs from `docs/guides/`
- updated top-level and reports indexes to the new paths

## Validation

Primary validation executed in the source worktrees for the two micro-batches:

- Batch A:
  - `gitnexus_detect_changes({scope: "staged"})` => `17 files / low`
  - `python -m scripts.maintenance.check_structure --format text . --staged` => `errors: 0, warnings: 0`

- Batch B:
  - `gitnexus_detect_changes({scope: "staged"})` => `19 files / low`
  - `python -m scripts.maintenance.check_structure --format text . --staged` => `errors: 0, warnings: 0`

Integration-branch validation executed locally:

```bash
pytest tests/unit/governance/test_function_tree_doc_sync.py \
  tests/unit/scripts/test_check_structure_policy.py \
  tests/unit/scripts/test_docs_indexer.py \
  tests/unit/scripts/test_pytest_runtime_artifacts.py \
  tests/unit/scripts/test_repository_hygiene_paths.py \
  tests/unit/core/test_docker_root_compatibility.py \
  -q --no-cov -o tdd_guard_project_root=/opt/claude/mystocks_spec \
  --timing-file=/tmp/test_timing.csv

python -m scripts.maintenance.check_structure --format text .

bash scripts/tree-lint.sh
```

## Reviewer Notes

- The repository's main worktree still contains large unrelated staged and unstaged debt. This branch was assembled in isolated linked worktrees specifically to avoid mixing those unrelated changes into the governance result.
- `scope="unstaged"` from the dirty main worktree remains unsuitable as a micro-batch risk signal; the relevant GitNexus checks for this work were executed against isolated staged batches.
