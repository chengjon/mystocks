# B4.011-M2a-HOLD-B-Generated-Pair Authorization Prep

Date: 2026-06-11
Branch: `wip/root-dirty-20260403`
Baseline HEAD: `7520326d9`
Mode: no-source generated evidence pair review and authorization preparation
Source edits authorized: false

## Scope

This review covers only the generated backend full-path route table evidence
pair left in the HOLD-B docs/reports retirement set:

- `docs/reports/quality/generated/backend-fullpath-route-table.json`
- `docs/reports/quality/generated/backend-fullpath-route-table.md`
- `archive/docs/reports/quality/generated/backend-fullpath-route-table.json`
- `archive/docs/reports/quality/generated/backend-fullpath-route-table.md`

No source, test, runtime, route, OpenSpec, ST-HOLD, marketKlineData,
docs/guides, docs/superpowers, web, src, tests, scripts, external dirty,
modified tracked docs/reports files, untracked docs/reports files, or non-pair
quality reports are included.

## Current Boundary

- Active gates: none.
- Staged changes before review: empty.
- Remaining `docs/reports` dirty distribution before this prep: `M 5 / D 2 / ?? 11`.
- Target worktree status: both active generated-pair paths are deleted in the
  worktree; archive counterparts exist.
- This prep package does not retire, restore, move, overwrite, regenerate, or
  delete the generated evidence files.

## Drift Matrix

| File | Active HEAD lines | Archive HEAD lines | Archive -> active diff | Reference signal | Risk class |
| --- | ---: | ---: | ---: | --- | --- |
| `docs/reports/quality/generated/backend-fullpath-route-table.json` | 24 | 18 | +12 / -6 | full-path refs: docs 6, governance 4, source/test 0, other 7 | Generated evidence pair |
| `docs/reports/quality/generated/backend-fullpath-route-table.md` | 42 | 32 | +16 / -6 | full-path refs: docs 6, governance 4, source/test 0, other 14 | Generated evidence pair |

The JSON active HEAD blob parses successfully and contains these top-level keys:

- `generated_at`
- `git_branch`
- `git_head`
- `summary`
- `full_path_duplicates`
- `local_decorator_duplicates_count`
- `orphan_files`

## Generator Signal

The only source/test basename references are in
`scripts/dev/backend_audit_fullpath_routes.py`, where the script writes
`backend-fullpath-route-table.json` and `backend-fullpath-route-table.md` under
an `output_dir`. No source/test full-path reference to the active
`docs/reports/quality/generated/**` paths was detected.

## Decision

The two files are a generated evidence pair and should be handled together.
They are documentation/evidence artifacts, not runtime inputs. Because they are
paired JSON/Markdown outputs from a generator script, they should not be mixed
with ordinary Markdown report retirement or residual dirty cleanup.

Recommended implementation shape, if separately approved:

1. Overwrite each matching `archive/docs/reports/quality/generated/**` path with
   the corresponding active HEAD blob.
2. Retire the matching active `docs/reports/quality/generated/**` paths.
3. Stage only the two active deletions, the two archive updates, and associated
   FUNCTION_TREE governance metadata.
4. Do not regenerate the pair, do not touch the generator script, and do not
   touch remaining `M 5 / ?? 11` docs/reports dirty files.

## Required Gates For Implementation

- Exact staging only.
- `git diff --cached --check`.
- GitNexus `verify-staged`.
- GitNexus `detect_changes --scope staged`.
- OPENDOG verification with no cleanup blockers.
- Post-commit GitNexus `analyze --index-only`.
- Final verification that active paths are absent, archive paths are present,
  active gates are clear, and remaining dirty files are unchanged outside this
  scope.

## Authorization Request

Request `B4.011-M2a-HOLD-B-Generated-Pair deletion-retirement implementation`
authorization for only these four paths:

- `docs/reports/quality/generated/backend-fullpath-route-table.json`
- `docs/reports/quality/generated/backend-fullpath-route-table.md`
- `archive/docs/reports/quality/generated/backend-fullpath-route-table.json`
- `archive/docs/reports/quality/generated/backend-fullpath-route-table.md`

Allowed action would be limited to active HEAD -> archive overwrite followed by
active path retirement. Regeneration, generator script changes, remaining
modified/untracked docs reports, docs/guides, docs/superpowers, web, src,
tests, scripts, OpenSpec, ST-HOLD, marketKlineData, and external dirty paths
remain forbidden.
