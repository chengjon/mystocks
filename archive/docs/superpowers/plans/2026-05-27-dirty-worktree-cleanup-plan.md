# Dirty Worktree Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce the MyStocks root dirty worktree safely without losing unknown work or mixing unrelated code, docs, OpenSpec, test, and generated-artifact changes.

**Architecture:** Treat the current root tree as an evidence source, not as the integration branch. Preserve and classify first, move only clearly generated local artifacts in the root tree, and extract remaining work through clean review worktrees and small PR-sized slices.

**Tech Stack:** Git porcelain v1, Git worktrees, GitNexus impact checks for code slices, MyStocks PM2 services, pytest, ruff, Vue/Vite verification where frontend slices are touched.

---

## 1. Current Baseline

- Branch: `wip/root-dirty-20260403`
- HEAD: `80b8389ed`
- Current dirty total: `1360`
- Tracked modified: `822`
- Tracked deleted: `113`
- Untracked: `425`
- PM2 status at cleanup time: `mystocks-backend=online`, `mystocks-frontend=online`

## 2. Completed In This Session

- [x] Read `architecture/STANDARDS.md` and `openspec/AGENTS.md` before editing governance docs.
- [x] Compared the MyStocks guide against `quantix-rust/docs/guides/DIRTY_WORKTREE_CLEANUP_GUIDE_REVIEW.md`.
- [x] Verified the current guide uses the corrected 0-9 step numbering and generalized Slice Validation structure.
- [x] Moved clear generated/runtime untracked directories out of the repository:
  - `.playwright/`
  - `.playwright-cli/`
  - `.zread/`
- [x] Preserved those directories at `/tmp/mystocks-dirty-worktree-cleanup-2026-05-27/runtime-generated/`.
- [x] Updated `docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE.md` with the current baseline and execution boundary.

## 3. Remaining Cleanup Slices

- [ ] 3.1 Documentation/governance slice: review `docs/`, `reports/`, `TASK*.md`, `README.md`, `CLAUDE.md`, `DESIGN.md`, and `PRODUCT.md`; keep or archive by document owner and report type.
- [ ] 3.2 OpenSpec slice: review deleted and untracked `openspec/changes/` entries; archive only completed changes and preserve active proposals.
- [ ] 3.3 Frontend slice: extract `web/frontend/` changes into clean worktree branches; run frontend lint/type/E2E gates per touched surface.
- [ ] 3.4 Backend/API slice: extract `web/backend/` changes; run targeted API tests and contract checks.
- [ ] 3.5 Python source/scripts/tests slice: separate source changes from test/tooling changes; run GitNexus impact before code-symbol edits and targeted pytest/ruff checks.
- [ ] 3.6 Root config/tooling slice: review `.env.example`, `.planning/STATE.md`, `package.json`, `.github/workflows/*`, `.agents/`, and `plugins/`.
- [ ] 3.7 Worktree/stash slice: audit 117 worktrees and `stash@{0}`; remove only stale worktrees after their branch/PR status is verified.

## 4. Non-Negotiable Gates

- [ ] Do not run `git reset --hard`, `git clean -fdx`, or blanket stash/apply operations on the root dirty tree.
- [ ] Stage intended paths before any `gitnexus_detect_changes(scope="staged")` check.
- [ ] For code slices, run `gitnexus_impact` before editing symbols and report HIGH/CRITICAL risk before proceeding.
- [ ] Keep PM2 services online unless a later slice explicitly requires a maintenance window.
- [ ] Keep runtime-generated backups in `/tmp` until the relevant cleanup slice is accepted.
- [ ] Do not claim cleanup completion from root-clean status alone; enumerate every registered worktree and record its status.
- [ ] Do not put single-machine logs, reports, or tool noise into versioned `.gitignore`; use `.git/info/exclude` unless the path is team-shared and stable.
- [ ] Do not delete squash-merged branches by relying only on `git branch --merged`; check PR state, merge timestamp, ahead/behind, file-level diff, and owner approval.
- [ ] Do not delete worktrees with substantive WIP; commit locally, hand off, or assign them to a cleanup slice.
- [ ] Do not delete `rescue/*` branches until recovery packages, path-level disposition, owner approval, and final closeout are complete.
