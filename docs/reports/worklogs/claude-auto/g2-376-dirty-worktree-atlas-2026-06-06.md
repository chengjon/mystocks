# G2.376 Dirty Worktree Atlas And Cleanup Queue Inventory

> **Date**: 2026-06-06
>
> **Mode**: `no-source`
>
> **source_edit_authority**: `false`
>
> **test_edit_authority**: `false`
>
> **Scope**: current dirty worktree atlas, queue classification, and next-batch recommendation
>
> **Guide**: `docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE.md`

## 1. Boundary

This node only inventories and classifies the dirty worktree.

Allowed:

- read-only `git status` / `git diff` analysis
- read-only GitNexus staged/freshness check
- read-only OPENDOG verification status check
- report writing under `docs/reports/worklogs/claude-auto/`
- cleanup queue recommendation

Forbidden:

- deleting files
- restoring files
- staging cleanup
- committing cleanup
- modifying source or test code
- touching route-header migration leftovers
- root realignment

## 2. Current Evidence

Measured from `/opt/claude/mystocks_spec` on 2026-06-06 Asia/Shanghai.

```text
branch: wip/root-dirty-20260403
HEAD:   7e657ab2f6d7c8e4218ea16421f08775f8cf7f6d

total_dirty: 1418
staged_paths: 0
stash_count: 1
worktree_count: 224
```

Status distribution:

| Status | Count |
|---|---:|
| ` M` | 831 |
| `??` | 475 |
| ` D` | 112 |

Top-level distribution:

| Top-level path | Count |
|---|---:|
| `web` | 413 |
| `docs` | 362 |
| `tests` | 231 |
| `scripts` | 190 |
| `openspec` | 109 |
| `reports` | 47 |
| `src` | 36 |
| `governance` | 10 |
| `.governance` | 2 |
| `.agents` | 1 |
| `.claude` | 1 |
| `.env.example` | 1 |
| `.github` | 1 |
| `.gitignore` | 1 |
| `.planning` | 1 |
| `AGENTS.md` | 1 |
| `architecture` | 1 |
| `CLAUDE.md` | 1 |
| `config` | 1 |
| `DELETION-CANDIDATES.md` | 1 |

## 3. Tool Status

| Tool | Result | Cleanup meaning |
|---|---|---|
| Git staged state | `staged_paths=0` | No staged cleanup is pending. Future commits must keep this property until an authorized batch is selected. |
| GitNexus direct CLI | `gitnexus detect-changes --scope staged --repo mystocks --cwd /opt/claude/mystocks_spec` returned successfully. Index is stale: indexed `6c536b98ccfc`, current `7e657ab2f6d7`. | Enough for no-source inventory. Not enough for source/deletion commits without direct `gitnexus analyze` refresh. |
| OPENDOG verification | freshness=`stale`, age_seconds=`1931754`, blocker=`Recorded verification evidence is stale and should be refreshed before risky changes.` | Does not block no-source atlas. Blocks risky cleanup unless fresh verification is recorded or caveat is explicitly accepted. |

Important: this report does not claim GitNexus risk for any source/deletion batch. GitNexus must be refreshed before source-authorized or deletion-retirement commits.

## 4. Classification Rules Applied

Classification used the guide's precedence model:

1. Deletion-retirement candidates override ordinary source/frontend/docs buckets.
2. Governance cleanup guide and entry documents are a separate docs-authorized bucket.
3. `docs/reports/worklogs/claude-auto/` worklogs are a separate governance-record bucket.
4. Frontend, backend/source/tests, OpenSpec, docs drift, config/scripts, and unknowns remain separate.
5. Unknown items are preserved until a later disposition node.

## 5. Mutually Exclusive Buckets

| Bucket | Count | Status mix | Default authority | Risk | Initial disposition |
|---|---:|---|---|---|---|
| B1 governance guide/docs | 6 | `M=3`, `??=3` | docs-authorized | Low | Review and commit as governance-docs batch if approved. |
| B2 `claude-auto` worklogs | 14 | `M=1`, `??=13` | docs-authorized or no-source | Low/Medium | Review as governance records; commit useful reports or disposition stale drafts. |
| B3 deletion-retirement candidates | 112 | `D=112` | deletion-retirement authorized | High | Do not accept now. Split by domain and require deletion evidence/gates. |
| B4 frontend route/UI candidates | 312 | `M=241`, `??=71` | source-authorized | High | Do not edit now. Respect route-header handoff and route/layout gates. |
| B5 backend-source-tests | 335 | `M=316`, `??=19` | source/test-authorized | High | Do not edit now. Domain inventories first, then focused gates. |
| B6 docs drift | 344 | `M=64`, `??=280` | docs-authorized or no-source | Medium | Split general docs from governance/reports; validate canonical docs before commit. |
| B6 OpenSpec drift | 33 | `M=11`, `??=22` | docs/spec-authorized | Medium/High | Check `openspec list` and active change state before archive/delete/commit. |
| B7 config-scripts-other | 213 | `M=188`, `??=25` | config/script-authorized | Medium/High | Needs separate inventory; do not batch with source or docs. |
| B8 unknown untracked | 42 | `??=42` | no-source first | Unknown | Preserve and classify. |
| B8 unknown tracked | 7 | `M=7` | no-source first | Unknown | Preserve and classify. |

Deletion candidates by top-level path:

| Top-level path | Deletion count |
|---|---:|
| `openspec` | 76 |
| `web` | 32 |
| `DELETION-CANDIDATES.md` | 1 |
| `docs` | 1 |
| `scripts` | 1 |
| `tests` | 1 |

Untracked files by top-level path:

| Top-level path | Untracked count |
|---|---:|
| `docs` | 296 |
| `web` | 77 |
| `reports` | 41 |
| `openspec` | 22 |
| `scripts` | 13 |
| `tests` | 12 |
| `governance` | 9 |
| `.agents` | 1 |
| `.github` | 1 |
| `.governance` | 1 |
| `plugins` | 1 |
| `src` | 1 |

## 6. Known Parallel-Line Boundaries

| Line | Boundary decision |
|---|---|
| `data_source_config` | Closed by `df5aba5c2` and `7e657ab2f`. Do not reopen unless new evidence appears. |
| route-header migration | See `docs/reports/worklogs/claude-auto/route-header-migration-line-handoff-2026-06-05.md`. Do not stage or commit route-header leftovers in dirty cleanup. |
| cleanup guide/review | `DIRTY_WORKTREE_CLEANUP_GUIDE.md` and review companions belong to B1 governance docs. |
| `AGENTS.md` / `CLAUDE.md` / `STANDARDS.md` | Current governance-rule solidification belongs to B1. It should not be mixed with source/test cleanup. |

## 7. Decision Table

| Batch | Scope | Count | Authority | Risk | Evidence required before commit | Recommendation |
|---|---:|---:|---|---|---|---|
| B1 | Governance guide/docs | 6 | docs-authorized | Low | Path-scoped diff, `git diff --check`, no source/test staged. | Do next. This gives the dirty cleanup line a stable governing document. |
| B2 | `claude-auto` worklogs | 14 | docs-authorized | Low/Medium | Read relevance, path-scoped diff, no source/test staged. | Do after B1. Keep useful closeouts, disposition obsolete drafts. |
| B3 | Deletion-retirement candidates | 112 | deletion-retirement authorized | High | Split by domain, reference checks, GitNexus refreshed, focused tests where relevant, explicit deletion approval. | Do not start until B1/B2 are stable and GitNexus/OPENDOG caveats are resolved or accepted. |
| B4 | Frontend route/UI candidates | 312 | source-authorized | High | Route handoff review, route tests, frontend syntax/type gate, PM2/E2E where relevant. | Defer. Resume as route-specific or frontend-domain slices only. |
| B5 | Backend-source-tests | 335 | source/test-authorized | High | Domain inventory, GitNexus impact/detect, focused import/pytest gates. | Defer. Split by backend domain, not by raw file count. |
| B6a | General docs drift | 344 | docs-authorized/no-source | Medium | Canonical-doc check, diff check, stale-doc disposition. | Inventory after B1/B2; do not mix with OpenSpec. |
| B6b | OpenSpec drift | 33 | docs/spec-authorized | Medium/High | `openspec list`, active change/spec review, `openspec validate` before commit. | Separate node. Deletion/archive requires explicit approval. |
| B7 | Config/scripts/other | 213 | config/script-authorized | Medium/High | Path-specific inventory, command ownership, runtime impact checks. | Separate node after docs/report batches. |
| B8 | Unknown tracked/untracked | 49 | no-source first | Unknown | Classification evidence and owner/disposition. | Preserve until a later unknown-disposition inventory. |

## 8. Recommended Next Steps

Recommended immediate next node:

```text
G2.377 governance cleanup guide and rule-doc batch / docs-authorized
```

Suggested scope:

```text
source_edit_authority=false
test_edit_authority=false
docs_edit_authority=true

Allowed paths:
- architecture/STANDARDS.md
- AGENTS.md
- CLAUDE.md
- docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE.md
- docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE-review.md
- docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE_REVIEW.md
- docs/reports/worklogs/claude-auto/g2-376-dirty-worktree-atlas-2026-06-06.md

Forbidden:
- source files
- tests
- route-header migration leftovers
- deletion candidates
- generated/runtime artifacts
```

Why B1 first:

- It stabilizes the cleanup governing document before high-risk cleanup.
- It contains only docs/governance material.
- It keeps the new same-domain batching rule auditable.
- It does not require GitNexus source impact gates.

Recommended second node after B1:

```text
G2.378 claude-auto worklog governance records disposition / no-source or docs-authorized
```

Recommended third node after B1/B2:

```text
G2.379 deletion-retirement candidate domain split inventory / no-source
```

This should split the 112 deletion candidates by domain before any source-authorized deletion acceptance.

## 9. Closeout

G2.376 produced only this atlas report.

No code changed.
No tests changed.
No files were deleted.
No paths were staged.
No commit was made.

The dirty cleanup line can continue with B1 governance docs if approved.
