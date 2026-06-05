# MyStocks Dirty Worktree Cleanup Guide

> **Status**: Review draft
>
> **Date**: 2026-06-05
>
> **Project**: MyStocks (`/opt/claude/mystocks_spec`)
>
> **Branch baseline**: `wip/root-dirty-20260403`
>
> **Current observed HEAD**: `7e657ab2f6`
>
> **Upstream reference**: `/opt/claude/quantix-rust/docs/guides/DIRTY_WORKTREE_CLEANUP_GUIDE.md`
>
> **Review companion**: `docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE_REVIEW.md`

This guide adapts the Quantix dirty-worktree cleanup SOP to MyStocks. It is not a source-edit authorization. It is the operating guide for the upcoming dirty worktree governance pass.

The canonical governance source remains [`architecture/STANDARDS.md`](../../../architecture/STANDARDS.md). If this guide and `STANDARDS.md` conflict, `STANDARDS.md` wins.

---

## 1. Purpose

The goal is to turn a large, mixed dirty worktree into reviewable, reversible, auditable batches without losing useful work or silently accepting risky cleanup.

For MyStocks, a dirty worktree is considered cleanly governed only when:

| State | Meaning |
|---|---|
| Valuable work preserved | Useful code, tests, docs, reports, or config changes are either committed in narrow batches or explicitly deferred with a disposition record. |
| Risky cleanup isolated | Deletions, retirements, root realignment, generated artifact cleanup, and source/test changes are not mixed in one commit. |
| Recovery path exists | Before destructive operations, tracked and untracked work can be restored from a documented snapshot. |
| Current evidence is explicit | Git status, GitNexus, OPENDOG, tests, and frontend gates are reported with dates and commands, not assumed from old baselines. |
| Residual dirty is explained | Remaining dirty files have a queue, owner line, or reason to preserve. |

This guide is especially for dirty states with hundreds of files across `web/`, `docs/`, `tests/`, `scripts/`, `openspec/`, and `src/`.

It is not needed for a small single-purpose change that can be reviewed with a normal `git diff`, focused tests, and a single commit.

---

## 2. Current Snapshot

The current dirty distribution was measured on 2026-06-05 after closing `G2.375 data_source_config.old deletion-retirement`.

```text
branch: wip/root-dirty-20260403
HEAD:   7e657ab2f6

total_dirty: 1417

by status:
 M: 831
??: 474
 D: 112

by top-level directory:
web:        413
docs:       361
tests:      231
scripts:    190
openspec:   109
reports:     47
src:         36
governance:  10

by risk bucket:
untracked_file:                 461
source_or_tests:                316
frontend:                       241
other:                          206
deletion_retirement_candidate:  112
docs:                            65
untracked_governance_report:     13
governance_docs:                  3
```

Known active side lines:

| Line | Current rule |
|---|---|
| `data_source_config` | Closed by `df5aba5c2` and `7e657ab2f`. Do not reopen unless new evidence appears. |
| route-header migration | See `docs/reports/worklogs/claude-auto/route-header-migration-line-handoff-2026-06-05.md`. Keep route-header leftovers out of dirty cleanup commits unless that line is explicitly resumed. |
| governance rule solidification | `AGENTS.md`, `CLAUDE.md`, and `architecture/STANDARDS.md` contain the newly added cleanup cadence rules and are currently a separate docs batch. |

OPENDOG observation: verification evidence is stale. This does not block no-source inventory, but it blocks risky cleanup until fresh verification is recorded or the stale evidence caveat is explicitly accepted.

---

## 3. Authority Model

Dirty cleanup uses the same source/no-source governance model as other G2 work.

| Mode | Allowed actions | Forbidden actions |
|---|---|---|
| `no-source` | Inventory, classification, report writing, decision tables, read-only Git/GitNexus/OPENDOG checks. | Editing code/tests, deleting files, staging cleanup, committing cleanup, root realignment. |
| docs-authorized | Editing named documentation/report files only. | Touching source, tests, config, generated files, or unrelated docs. |
| source-authorized | Editing/staging/committing explicitly named source or test files only. | Expanding scope without approval, mixing unrelated dirty paths, broad cleanup. |
| deletion-retirement authorized | Accepting deletion for explicitly named files or path groups after evidence and gates. | Blanket `git clean`, `git reset --hard`, deleting unreviewed groups, mixing deletion with behavior changes. |

Broad approval such as "continue cleanup" is not permission for destructive commands. Each high-risk operation needs path-specific and action-specific approval.

Mode transitions are approved only by the human operator running the session. Agents must not self-authorize escalation from `no-source` to docs-authorized, source-authorized, or deletion-retirement authorized.

---

## 4. Global Principles

| ID | Principle | Operational meaning |
|---|---|---|
| P1 | Do not mix intents | A commit should express one intent: docs, report, source fix, test change, generated artifact policy, or deletion-retirement. |
| P2 | Inventory before cleanup | Large dirty states start with a no-source atlas and decision table. Do not start by deleting files. |
| P3 | Same-domain no-source batching | Same-domain, same-risk, same-authority inventory can be one G node and one report. Do not split every file into a separate confirmation node. |
| P4 | Source work splits by risk | Source/test/frontend implementation remains split by risk and contract surface, even if its inventory was batched. |
| P5 | Deletion is separate | Full-file deletion, legacy retirement, and root realignment must be separately authorized and separately gated. |
| P6 | Unused is not enough | Static "unused" evidence is only a candidate signal. Confirm runtime paths, imports, route/menu registration, string lookup, generated entrypoints, docs contracts, and tests. |
| P7 | Path-scoped staging | Before every commit, run `git diff --cached --name-status` and ensure only the intended paths are staged. |
| P8 | GitNexus direct CLI only | Use `gitnexus analyze`, not `npx gitnexus analyze`. If GitNexus is stale, refresh with direct CLI or state the caveat. |
| P9 | OPENDOG is advisory | OPENDOG guidance helps prioritize and flag stale verification, but does not replace Git, tests, imports, GitNexus, or user approval. |
| P10 | Preserve parallel lines | Existing route-header, frontend, docs, OpenSpec, and data-source lines must not be silently folded into dirty cleanup commits. |
| P11 | Define fallback verification | If GitNexus or OPENDOG is unavailable, use the documented manual fallback path and record the unavailable tool, command, and replacement evidence. |
| P12 | Higher-risk bucket wins | When a file matches multiple buckets, classify it under the higher-risk authority. Deletion-retirement takes precedence over ordinary source/frontend cleanup. |

---

## 5. Terms

| Term | Meaning |
|---|---|
| Dirty worktree | A worktree with tracked modifications, untracked files, staged changes, deleted tracked files, or mixed line ownership. |
| Dirty atlas | A no-source report that groups all dirty files by status, path, risk, and proposed disposition. |
| Disposition | The proposed treatment for a file or group: commit, defer, inventory further, delete after authorization, archive, ignore locally, or preserve unknown. |
| Clean review worktree | A separate worktree created from a known baseline to reconstruct and validate narrow cleanup slices. |
| Root realignment | High-risk operation that resets the root dirty worktree to a baseline after useful work is extracted. Not part of early cleanup. |
| Deletion-retirement | Accepting removal of a tracked file after proving it is redundant, formally retired, or safely replaced. |
| G2 node | A governance work item in this dirty-state cleanup line, such as `G2.376`, with a declared mode, authority boundary, evidence, gates, and closeout. |

Governance node concepts and authority modes are defined by the project's active governance state and the function-tree/G2 program records. If a future operator is unfamiliar with the node model, check the current governance program tree or OPENDOG governance state before escalating authority.

---

## 6. Recommended G2 Flow For MyStocks

### Step 0. Freeze And Boundary Declaration

Before any dirty cleanup node, declare:

```text
node_id:
mode: no-source | docs-authorized | source-authorized | deletion-retirement authorized
source_edit_authority:
test_edit_authority:
allowed paths:
forbidden paths:
expected gates:
parallel line caveats:
```

For the first large dirty pass, the recommended node is:

```text
G2.376 dirty worktree atlas and cleanup queue inventory / no-source
source_edit_authority=false
test_edit_authority=false
```

Allowed:

- read-only Git status/diff analysis
- OPENDOG advisory checks
- GitNexus freshness/status checks
- report writing under `docs/reports/worklogs/claude-auto/`
- decision tables and batch planning

Forbidden:

- deleting files
- restoring files
- staging cleanup
- committing cleanup
- modifying source/tests/frontend code
- changing route-header leftovers
- root realignment

### Step 1. Inventory

Inventory must be generated from the current repository state, not copied from an old report.

Use machine-readable status first:

```bash
git status --porcelain=v1 -z
git diff --name-status
git diff --cached --name-status
git branch --show-current
git rev-parse --short=10 HEAD
```

For agent execution, process these with a script or context-mode sandbox and print only aggregates:

```text
total dirty entries
status counts
top-level directory counts
risk buckets
staged path list
sample paths per bucket
```

Do not paste thousands of raw paths into the conversation.

### Step 2. Classification

Classify by risk and authority, not just by directory.

| Bucket | Examples | Default mode | Initial disposition |
|---|---|---|---|
| Governance docs | `AGENTS.md`, `CLAUDE.md`, `architecture/STANDARDS.md` | docs-authorized | Review and commit as its own docs batch. |
| Worklogs/reports | `docs/reports/worklogs/claude-auto/*.md` | docs-authorized or no-source | Commit if useful governance record; otherwise preserve/disposition. |
| Source/backend | `web/backend/`, `src/` | source-authorized | Domain inventory first, then focused implementation gates. |
| Frontend route/UI | `web/frontend/src/views/`, router, route headers | source-authorized | Respect route-header handoff; route/layout gates required. |
| Tests | `tests/`, frontend test dirs | test-authorized | Pair with the source behavior they verify or commit as a test-only batch. |
| OpenSpec | `openspec/changes/`, `openspec/specs/` | docs/spec-authorized | Check active change status before deletion or archive. |
| Deletions | `D` tracked paths | deletion-retirement authorized | Evidence table first; never accept by status alone. |
| Untracked generated/runtime | logs, coverage, build output, temp artifacts | deletion/ignore authorized | Confirm reproducibility and no hidden value before local cleanup. |
| Config/env | `.env.example`, `.gitignore`, PM2/Docker/config files | config-authorized | High review sensitivity; do not batch with source cleanup. |
| Unknown | Anything not explained | no-source | Preserve until disposition is explicit. |

Precedence rule: when a file matches multiple buckets, the higher-risk authority applies. For example, a deleted `web/frontend/src/views/` file is first a deletion-retirement candidate, not a normal frontend cleanup item; it must pass deletion gates before any route/UI disposition is accepted.

### Step 3. Recovery Snapshot Before Risky Actions

No recovery snapshot is required for a no-source atlas. A recovery snapshot is required before any destructive or root-realignment action.

Recommended snapshot contents:

```text
var/recovery/dirty-worktree-YYYY-MM-DD/
  tracked.diff
  staged.diff
  status-porcelain.txt
  status-short.txt
  untracked-files.tar
  phase0-manifest.json
  restore-instructions.md
```

Recommended commands, after explicit approval:

```bash
mkdir -p var/recovery/dirty-worktree-YYYY-MM-DD
git diff --binary > var/recovery/dirty-worktree-YYYY-MM-DD/tracked.diff
git diff --cached --binary > var/recovery/dirty-worktree-YYYY-MM-DD/staged.diff
git status --porcelain=v1 > var/recovery/dirty-worktree-YYYY-MM-DD/status-porcelain.txt
git status --short > var/recovery/dirty-worktree-YYYY-MM-DD/status-short.txt
git ls-files --others --exclude-standard -z | tar --null -T - -cf var/recovery/dirty-worktree-YYYY-MM-DD/untracked-files.tar
git branch rescue/dirty-worktree-YYYY-MM-DD
```

Snapshot validation:

```bash
tar -tf var/recovery/dirty-worktree-YYYY-MM-DD/untracked-files.tar >/dev/null
git apply --check var/recovery/dirty-worktree-YYYY-MM-DD/tracked.diff
```

`git apply --check` may fail in the original dirty tree because of untracked collisions or already-deleted paths. If so, validate in a temporary clone or record the limitation in `restore-instructions.md`.

### Step 4. Clean Review Worktree

Use a clean review worktree only after the atlas is approved and a source/deletion batch is selected.

Recommended pattern:

```bash
git worktree add .worktrees/dirty-cleanup-review-base HEAD -b cleanup/dirty-worktree-review-base-YYYY-MM-DD
```

Rules:

- The root worktree is the salvage source.
- The clean review worktree is the reconstruction and validation area.
- Do not start by resetting the root worktree.
- Do not remove old worktrees until their branch, dirty status, and recovery value are classified.

### Step 5. Batch Planning

The first atlas should produce a table like this:

| Batch | Scope | Count | Authority | Risk | Proposed next action |
|---|---:|---:|---|---|---|
| B1 | Governance entry docs | 3 | docs-authorized | Low | Review and commit `AGENTS.md`, `CLAUDE.md`, `STANDARDS.md` as one docs batch. |
| B2 | Worklogs/reports | 13+ | docs-authorized | Low/medium | Review usefulness, commit or disposition as governance records. |
| B3 | Deletion-retirement candidates | 112 | deletion-retirement authorized | High | Split by domain; evidence table before any acceptance. |
| B4 | Frontend route/UI dirty | 241 | source-authorized | High | Respect route-header handoff; route-specific gates. |
| B5 | Backend/source/test dirty | 316+ | source/test-authorized | High | Domain inventory first; focused import/pytest/GitNexus gates. |
| B6 | OpenSpec/docs drift | 100+ | spec/docs-authorized | Medium/high | Check active change status before archive/delete. |
| B7 | Unknown untracked files | 461 | no-source first | Unknown | Classify as generated, report, source, config, or preserve. |

Counts must be refreshed in the atlas report; the table above is a starting model, not a current gate.

### Step 6. Validation Gates

Each batch type has its own gate. Do not substitute one gate for another.

| Batch type | Required gates |
|---|---|
| Governance/docs only | `git diff --check -- <paths>`, path-scoped review, no source/test files staged. |
| Backend API/source | GitNexus impact where a symbol/file is mapped, focused import smoke, focused pytest, `git diff --cached --check`, GitNexus staged detect before commit. |
| Frontend route/layout | Route config/static tests, frontend syntax/type gate per current baseline, PM2 service status if route is exercised, actual E2E/smoke result with browser/project/counts. |
| Tests only | Run the affected test file or suite and confirm it fails/passes only as intended; do not pair with unrelated source cleanup. |
| Deletion-retirement | Runtime/import reference search, GitNexus query/impact/detect where applicable, relevant tests, path-scoped staged list, explicit deletion rationale. |
| Generated/runtime cleanup | Reproducibility or archive proof, local-only disposition, no source/test files staged. |
| OpenSpec | `openspec list`, active change/spec status, `openspec validate` when changing specs or changes. |

GitNexus rules:

```bash
gitnexus analyze --index-only --wal-checkpoint-threshold 67108864
gitnexus detect-changes --scope staged --repo mystocks --cwd /opt/claude/mystocks_spec
```

Do not use:

```bash
npx gitnexus analyze
```

If GitNexus cannot map an old deleted file, report the exact result. For example: `target not_found`, `processes=[]`, or `No changes detected` with an up-to-date index. Do not invent a low-risk rating.

Tool fallback rules:

| Unavailable tool | Fallback evidence | Required report wording |
|---|---|---|
| GitNexus MCP | Use direct `gitnexus` CLI. | State MCP unavailable and direct CLI command/result. |
| Direct GitNexus CLI | Use `rg`/import scans, route/menu/registry checks, focused tests, and path-scoped Git diffs. | State GitNexus unavailable; list manual scopes checked and tests run. |
| OPENDOG | Use `git status`, `git diff`, existing reports, GitNexus, and focused project-native tests for prioritization. | State OPENDOG unavailable; do not claim OPENDOG-backed priority or freshness. |
| OpenSpec CLI | Use file-level inspection of `openspec/changes/` and `openspec/specs/`, then rerun CLI when available before committing spec changes. | State OpenSpec CLI unavailable and block spec commits unless separately approved. |

### Step 7. Commit Strategy

Before every commit:

```bash
git diff --cached --name-status
git diff --cached --check
```

Commit only when the staged list matches the authorized scope.

Use narrow messages:

```text
docs(governance): define dirty worktree cleanup guide
docs(governance): preserve dirty worktree atlas report
refactor(api): retire legacy data source config module
test(api): preserve data source config route contract
fix(web): preserve data route fallback state truth
```

Avoid vague messages:

```text
cleanup everything
fix dirty files
misc changes
update docs and code
```

If unrelated staged changes exist, do not run a normal commit. Use path-specific staging or stop and resolve the staging boundary.

### Step 8. Residual Disposition

Every remaining dirty group must end with one of these dispositions:

| Disposition | Meaning |
|---|---|
| Commit now | Evidence and gates are complete for a narrow batch. |
| Defer | Valuable but outside current line; keep with handoff. |
| Inventory deeper | Insufficient evidence; no source edit yet. |
| Delete after authorization | Deletion candidate with clear evidence and pending approval. |
| Archive | Useful historical or audit content, but not active source. |
| Local-only ignore | Runtime artifact or machine-local output that should not enter Git. |
| Preserve unknown | Cannot prove safety; leave untouched and document why. |

Unknown is acceptable. Silent deletion is not.

### Step 9. Final Cleanup And Root Realignment

Final cleanup is the last phase, not the start.

Allowed only after:

- all valuable batches are committed or explicitly deferred
- all deletion groups have approvals and gates
- recovery snapshot is validated
- all registered worktrees have been classified
- route-header and other parallel lines have handoff status
- user explicitly approves root realignment or residual deletion

Root realignment examples such as `git reset --hard` or broad `git clean` are intentionally not listed as normal commands. They are high-risk operations and require a separate approval message with exact scope.

---

## 7. High-Risk Operation Blacklist

These operations are not permanently banned, but they are forbidden without snapshot, classification, path scope, and explicit approval.

| Operation | Why risky | Safer alternative |
|---|---|---|
| `git reset --hard` | Destroys tracked dirty work. | Extract valuable batches first; create recovery snapshot; approve root realignment separately. |
| `git checkout .` / `git restore .` | Reverts broad paths and can erase unrelated user work. | Use path-specific restore only after approval. |
| `git clean -fd` / `git clean -fdx` | Deletes untracked evidence, reports, generated artifacts, and WIP. | Inventory untracked files, archive if needed, delete path groups only. |
| `rm -rf <dirty-dir>` | Bypasses Git evidence and recovery. | Create snapshot and disposition table; remove only approved path groups. |
| `git stash --include-untracked` | Hides mixed work and makes review/disposition opaque. | Use explicit recovery package and path-based batches. |
| `git add -A` | Stages unrelated dirty lines together. | Stage explicit pathspecs and verify `git diff --cached --name-status`. |
| `git commit` with dirty staged unknowns | Commits unrelated work. | Confirm staged list or use path-specific commit after scope review. |
| `git branch -D` / `git worktree remove` | Can discard WIP or audit context. | Check branch merge/squash status, worktree dirty status, and recovery value. |
| Editing `.gitignore` to hide real WIP | Masks work instead of classifying it. | Use local excludes only for proven machine-local artifacts. |

---

## 8. Acceptance Checklist

For `G2.376 dirty worktree atlas and cleanup queue inventory / no-source`, the guide expects:

```text
[ ] Current branch and HEAD recorded.
[ ] Dirty total and counts by status recorded.
[ ] Counts by top-level directory recorded.
[ ] Counts by risk/authority bucket recorded.
[ ] Current staged files listed.
[ ] Parallel line handoffs checked, including route-header migration.
[ ] OPENDOG stale verification caveat recorded.
[ ] GitNexus freshness caveat recorded if not refreshed.
[ ] Deletion candidates grouped, not accepted.
[ ] Source/test/frontend candidates grouped, not edited.
[ ] Untracked files grouped, not deleted.
[ ] One decision table produced.
[ ] Next source-authorized/deletion-authorized batches proposed.
```

For source/deletion follow-up nodes:

```text
[ ] Explicit allowed paths.
[ ] Explicit forbidden paths.
[ ] GitNexus direct CLI used when required.
[ ] Focused tests/imports/build gates run.
[ ] `git diff --cached --name-status` matches scope.
[ ] `git diff --cached --check` passes.
[ ] Commit contains one intent only.
[ ] Remaining dirty state is reported.
```

---

## 9. Minimal Command Appendix

Read-only inventory:

```bash
git branch --show-current
git rev-parse --short=10 HEAD
git status --porcelain=v1 -z
git diff --name-status
git diff --cached --name-status
git worktree list
```

Scoped status:

```bash
git status --short -- <path1> <path2>
git diff --name-status -- <path>
git diff --cached --name-status -- <path>
```

GitNexus direct CLI:

```bash
gitnexus analyze --index-only --wal-checkpoint-threshold 67108864
gitnexus detect-changes --scope staged --repo mystocks --cwd /opt/claude/mystocks_spec
gitnexus impact <symbol-or-file> --repo mystocks --direction upstream --summary-only
gitnexus query "<concept or file name>" --repo mystocks --limit 5
```

Backend focused smoke example:

```bash
PYTHONPATH=/opt/claude/mystocks_spec/web/backend:/opt/claude/mystocks_spec python - <<'PY'
import importlib
module = importlib.import_module("app.api.data_source_config")
print("import app.api.data_source_config: ok")
print("router routes:", len(module.router.routes))
print("has settings:", hasattr(module, "settings"))
print("has HTTPException:", hasattr(module, "HTTPException"))
print("router response keys:", sorted(module.router.responses.keys()))
PY
```

Backend focused pytest example:

```bash
pytest tests/api/file_tests/test_data_source_config_api.py -q --no-cov
```

Frontend route/layout examples:

```bash
cd web/frontend
npm run test -- tests/unit/config/data-route-canonical-paths.spec.ts
npm run test:e2e:chromium -- <route-specific-spec>
```

Diff checks:

```bash
git diff --check -- <paths>
git diff --cached --check
```

---

## 10. Recommended First Node

Start with a no-source atlas:

```text
G2.376 dirty worktree atlas and cleanup queue inventory / no-source
```

Suggested output:

```text
docs/reports/worklogs/claude-auto/g2-376-dirty-worktree-atlas-2026-06-05.md
```

Required decision table:

| Batch | Scope | Count | Authority | Risk | Evidence | Recommendation |
|---|---:|---:|---|---|---|---|
| B1 | Governance docs | refreshed count | docs-authorized | low | diff + check | review/commit separately |
| B2 | Worklogs/reports | refreshed count | docs-authorized | low/medium | content relevance | commit or disposition |
| B3 | Deletions | refreshed count | deletion-authorized | high | refs/tests/GitNexus | split by domain |
| B4 | Frontend route/UI | refreshed count | source-authorized | high | route handoff + tests | resume specific line only |
| B5 | Backend/source/test | refreshed count | source/test-authorized | high | import/pytest/GitNexus | domain inventory first |
| B6 | OpenSpec/docs drift | refreshed count | docs/spec-authorized | medium/high | openspec status | validate before archive/delete |
| B7 | Unknown untracked | refreshed count | no-source | unknown | classification | preserve until disposition |
The atlas should end with the next two or three recommended batches, not with a request to approve all cleanup at once.
