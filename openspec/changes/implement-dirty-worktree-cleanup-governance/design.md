## Context

MyStocks has accumulated a mixed dirty worktree on `wip/root-dirty-20260403`. The current baseline after removing clearly generated local runtime directories is `1360` dirty entries: `822` modified tracked files, `113` deleted tracked files, and `425` untracked files. The work spans product code, tests, documentation, OpenSpec changes, generated reports, root configuration, and local tool artifacts.

The cleanup guide at `docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE.md` is the execution procedure. This OpenSpec change turns that procedure into an approved task set and directory-governance requirement before implementation continues.

## Goals / Non-Goals

Goals:

- Preserve recoverability before any destructive operation.
- Prevent mixed commits by extracting cleanup into separately reviewable slices.
- Keep code, docs, OpenSpec, generated artifacts, and local tooling decisions separate.
- Keep `mystocks-backend` and `mystocks-frontend` availability explicit during cleanup.
- Produce evidence that each cleanup slice only affects the intended scope.

Non-Goals:

- Do not complete the full dirty-worktree cleanup in this proposal step.
- Do not reset or clean the root worktree as a shortcut.
- Do not decide whether unknown product-code changes are valid without slice-level impact analysis and tests.

## Decisions

- Decision: Use `directory-governance` as the governing capability.
  Rationale: existing directory governance already owns root artifacts, repository hygiene automation, cleanup preview, and canonical lifecycle targets.

- Decision: Keep documentation and OpenSpec cleanup as explicit slices rather than incidental side effects.
  Rationale: current specs require canonical documentation trunks and proposal-first governance, so cleanup must preserve decision history and active proposals.

- Decision: Use clean review worktrees for extraction.
  Rationale: the root dirty tree is evidence, not the integration surface; extracting from a clean base avoids validating against polluted local state.

- Decision: Treat the guide's 0-9 step map as the authoritative execution sequence.
  Rationale: the updated review identified numbering drift as the highest-friction failure mode. Approval protocol, generated artifacts, and product-code rules should be subordinate controls within the mapped steps, not parallel top-level flows.

- Decision: Maintain one classification source of truth.
  Rationale: duplicated inventory bucket tables and classification class tables drift quickly. Derived reports may exist, but they must point back to one canonical classification manifest.

- Decision: Treat generated/runtime artifacts as move-or-archive candidates before deletion.
  Rationale: the cleanup must be recoverable and should not assume unknown local state is disposable.

## Risks / Trade-offs

- Risk: dirty entries may include valuable in-progress work.
  Mitigation: snapshot tracked diff and untracked archives before mutation; classify unknown files as `review_required`.

- Risk: long-running cleanup may conflict with active feature branches.
  Mitigation: use one branch per cleanup slice and require staged-scope detection before commit.

- Risk: code cleanup could break frontend/backend behavior.
  Mitigation: require GitNexus impact checks for code symbols and run slice-specific tests before PR.

- Risk: documentation cleanup could remove historical evidence.
  Mitigation: apply documentation-governance lifecycle classification before deleting or archiving docs.

- Risk: `git apply --check` can give false confidence when file modes, new files, binary patches, or local index state differ from the restore target.
  Mitigation: run it only as a tracked-diff sanity check, document unsupported cases, and verify restoration in an isolated worktree or temporary clone when the snapshot includes new files or mode changes.

- Risk: a review worktree created for cleanup can become another stale worktree.
  Mitigation: record its path and branch in cleanup evidence and remove both during final closeout after related slices land or are abandoned.

- Risk: root-clean false completion; root `git status` can be clean while registered worktrees still contain WIP.
  Mitigation: final closeout must enumerate every registered worktree and record each `git status --porcelain=v1` result before claiming cleanup completion.

- Risk: local noise paths can be promoted into versioned `.gitignore` rules.
  Mitigation: require justification that an ignored path is team-shared and stable; otherwise use `.git/info/exclude`.

- Risk: squash-merged branches and rescue branches can be misclassified as stale.
  Mitigation: branch deletion must consider PR merge state, file-level diff, owner approval, and recovery status instead of relying only on `git branch --merged`.

## Migration Plan

1. Freeze and inventory the root dirty worktree.
2. Create a recovery snapshot and verify restore instructions.
3. Classify dirty entries into cleanup slices from a single canonical manifest.
4. Create a clean review worktree and record its lifecycle metadata.
5. Extract each slice in a clean review worktree.
6. Validate each slice using its specific gate.
7. Merge approved cleanup slices back through normal review.
8. Realign the root worktree only after all approved slices land.
9. Dispose of residual untracked files with explicit retain/archive/delete decisions and remove stale review worktrees.

## Rollback

Use the recovery snapshot and moved-artifact backup paths recorded by the cleanup guide and session plan. If a slice fails validation, drop only that slice branch and keep the root dirty tree untouched until a corrected slice is prepared.

## Open Questions

- Which active OpenSpec change directories are still live versus archive-ready?
- Which documentation report clusters should be retained as historical evidence?
- Which existing worktrees are associated with open PRs or unfinished local work?
