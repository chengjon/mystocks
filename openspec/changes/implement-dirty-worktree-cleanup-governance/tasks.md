## 1. Governance Setup

- [ ] 1.1 Review and approve this OpenSpec change before any high-risk mutation.
- [ ] 1.2 Confirm `docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE.md` is the procedure of record for this cleanup wave.
- [ ] 1.3 Confirm current baseline counts with `git status --porcelain=v1 -z`, `git diff --shortstat`, `git stash list`, and `git worktree list`.
- [ ] 1.4 Record PM2 status for `mystocks-backend` and `mystocks-frontend`.
- [ ] 1.5 Confirm the guide uses one authoritative 0-9 step sequence and that approval protocol, generated/runtime artifacts, and product-code rules are sub-controls under those steps.
- [ ] 1.6 Confirm command examples use MyStocks/Python/Vue validation placeholders and do not carry over Rust-specific commands such as `cargo test`.
- [ ] 1.7 Confirm all status inventory commands intentionally use `--porcelain=v1` with `-z` when machine parsing is required.
- [ ] 1.8 Confirm the guide's Common Failure Modes section explicitly covers root-clean false completion, versioned ignore overreach, squash-merge branch misclassification, WIP worktree deletion, and premature rescue branch deletion.

## 2. Recovery Snapshot

- [ ] 2.1 Create a timestamped recovery directory under the project-approved recovery location.
- [ ] 2.2 Save tracked diff, deleted-file inventory, untracked-file archive, and status inventory.
- [ ] 2.3 Generate `phase0-manifest.json` with hashes, sizes, branch, HEAD, and inventory error count.
- [ ] 2.4 Generate `restore-instructions.md` with tracked and untracked restore commands.
- [ ] 2.5 Verify the tracked diff with `git apply --check` in an isolated verification worktree or temporary clone.
- [ ] 2.6 Ensure `phase0-manifest.json` includes at minimum `created_at`, `repo_path`, `original_head`, `original_branch`, `tracked_diff_sha256`, `tracked_diff_bytes`, `untracked_archive_sha256`, `untracked_archive_bytes`, `inventory_errors`, and `missing_required_files`.
- [ ] 2.7 Ensure `restore-instructions.md` includes created time, repository path, original HEAD, original branch, tracked restore, untracked restore, rescue branch, and fallback notes.
- [ ] 2.8 Document `git apply --check` limitations for new files, deleted files, binary files, file mode changes, and index/working-tree divergence.

## 3. Classification

- [ ] 3.1 Create a single canonical classification manifest and derive any summary tables from it.
- [ ] 3.2 Classify all dirty entries into documentation/governance, OpenSpec, frontend, backend/API, Python source/scripts/tests, root config/tooling, generated/runtime, worktree/stash, and review-required buckets.
- [ ] 3.3 Mark each bucket with owner, risk, intended disposition, and required validation gate.
- [ ] 3.4 Preserve unknown entries as `review_required`; do not delete them based only on static search.
- [ ] 3.5 Publish the classification report under `docs/reports/cleanup/`.
- [ ] 3.6 Detect multi-branch dirty lines by mapping dirty paths to active worktrees, branches, and open/known cleanup changes before assigning ownership.
- [ ] 3.7 Treat acceptance baselines that cannot be measured exactly as observations, not hard gates.

## 4. Clean Review Worktree And Slice Protocol

- [ ] 4.1 Create a clean review worktree from the approved base branch before extracting slices.
- [ ] 4.2 Record the clean review worktree path, branch name, base commit, and intended owner in cleanup evidence.
- [ ] 4.3 Keep explicit approval gates separate from routine read-only inventory steps.
- [ ] 4.4 Treat Slice Validation as a general validation phase with sub-gates for code, documentation, OpenSpec, configuration, generated artifacts, and local tooling.
- [ ] 4.5 Keep generated/runtime artifact disposition in the slice protocol, not as an untracked side note.
- [ ] 4.6 Ensure final cleanup removes the clean review worktree and its associated cleanup branch when no longer needed.

## 5. Documentation And Governance Slice

- [ ] 5.1 Inventory `docs/`, `reports/`, root docs, `TASK*.md`, `README.md`, `CLAUDE.md`, `DESIGN.md`, and `PRODUCT.md`.
- [ ] 5.2 Apply documentation-governance lifecycle classification before deleting or archiving any document.
- [ ] 5.3 Ensure recommended document fallback paths include full repository-relative prefixes.
- [ ] 5.4 Update or archive documentation through a docs-only branch.
- [ ] 5.5 Run documentation validation commands relevant to changed docs and publish evidence.

## 6. OpenSpec Slice

- [ ] 6.1 Inventory deleted, modified, and untracked `openspec/changes/` and `openspec/specs/` entries.
- [ ] 6.2 Separate active proposals from completed archive-ready proposals.
- [ ] 6.3 Validate every retained or changed proposal with `openspec validate --strict`.
- [ ] 6.4 Archive only completed changes using the OpenSpec archive workflow.

## 7. Frontend Slice

- [ ] 7.1 Extract `web/frontend/` changes into one or more clean review worktree branches.
- [ ] 7.2 Separate UI/product changes, tests, config, local `.omc` state, and generated artifacts.
- [ ] 7.3 Run frontend lint/type/build or E2E gates according to touched surface.
- [ ] 7.4 Report structural syntax errors, type-inference baseline comparison, PM2 status, and actual E2E suite results when frontend tasks are completed.

## 8. Backend And API Slice

- [ ] 8.1 Extract `web/backend/` changes into clean review worktree branches.
- [ ] 8.2 Separate API schema/contract changes from reports and task notes.
- [ ] 8.3 Run targeted backend tests and contract validation for touched endpoints.
- [ ] 8.4 Publish API cleanup evidence and affected endpoint list.

## 9. Python Source, Scripts, And Tests Slice

- [ ] 9.1 Extract `src/`, `scripts/`, and `tests/` changes into responsibility-based branches.
- [ ] 9.2 Run GitNexus impact analysis before modifying or committing code-symbol changes.
- [ ] 9.3 Run staged-scope GitNexus detection before each commit.
- [ ] 9.4 Run targeted `pytest` and `ruff` checks for each slice.

## 10. Root Config, Tooling, Worktrees, And Stash

- [ ] 10.1 Review `.env.example`, `.planning/STATE.md`, `.github/workflows/*`, `package.json`, `.agents/`, and `plugins/`.
- [ ] 10.2 Keep local tool state local unless it belongs to an approved tooling-governance slice.
- [ ] 10.3 Audit all worktrees and map them to active PRs, branches, or stale cleanup candidates.
- [ ] 10.4 Review `stash@{0}` and either extract, archive, or drop it only after explicit approval.
- [ ] 10.5 Keep `git stash --include-untracked` in a single explicit high-risk/blocked-command list; do not duplicate it in separate policy lists.
- [ ] 10.6 For `.gitignore` changes, document whether each ignored path is team-shared and stable; keep single-machine noise in `.git/info/exclude`.
- [ ] 10.7 For squash-merged branches, do not rely only on `git branch --merged`; also check PR state, `mergedAt`, ahead/behind, file-level diff, and owner approval.
- [ ] 10.8 For each candidate worktree removal, record status, branch, recent log, and whether it contains substantive WIP before deleting.
- [ ] 10.9 Preserve `rescue/*` branches until recovery packages are externally archived, path-level disposition is approved, and final closeout confirms an alternate recovery path.
- [ ] 10.10 Remove stale review worktrees only after their branches are merged, archived, or explicitly abandoned.

## 11. Final Realignment And Closeout

- [ ] 11.1 Confirm all accepted cleanup slices have landed.
- [ ] 11.2 Confirm root status contains only approved residual local config or is clean.
- [ ] 11.3 Confirm every registered worktree has been enumerated with `git worktree list --porcelain` and checked with `git -C <worktree-path> status --porcelain=v1`; do not treat root-clean as whole-repository clean.
- [ ] 11.4 Dispose of residual untracked files with explicit retain/archive/delete decisions.
- [ ] 11.5 Remove clean review worktrees such as `.worktrees/dirty-cleanup-review-base` and associated cleanup branches after their slices are merged or abandoned.
- [ ] 11.6 Publish final cleanup report with before/after counts, validation evidence, rollback references, removed worktrees, retained rescue branches, and residual exceptions.
- [ ] 11.7 Run final `gitnexus_detect_changes` for staged scope before any final cleanup commit.
