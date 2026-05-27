# CODEBASE-MAP OpenSpec Steward Tree Index

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active split index
- Split prepared at: `2026-05-27T15:32:41+08:00`
- Split branch: `g2-179-steward-tree-governance-split`
- Base branch: `origin/wip/root-dirty-20260403`
- Base HEAD: `3b8f95945fcb489316ddfaf919835d372122fa5f`
- Scope: governance-only steward tree restructuring
- Original full tree snapshot:
  `.planning/codebase/steward-tree/archive/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.full-2026-05-27.md`

Boundary note: this file is the active steward entrypoint. It does not authorize
backend source edits, frontend source edits, tests, generated client updates,
docs/API edits, OpenSpec proposal creation, issue label changes, PM2 commands,
runtime rollout, compatibility deletion, or GitHub PR merge decisions.

## Purpose

The steward tree coordinates long-running CODEBASE-MAP architecture remediation
work. It is a control surface for state, gates, evidence, and ownership. It does
not replace OpenSpec, GitHub PRs, source code, runtime probes, generated
artifacts, Graphiti memory, GitNexus, or context-mode.

The previous single-file tree had grown to more than `3800` lines and roughly
`433 KB`. This split keeps the same historical record while separating day-to-day
uses:

- quick current-state lookup
- machine-readable state lookup
- evidence and freshness checks
- branch / PR relationship review
- completed work ledger review
- long-form historical recovery

## Source Hierarchy

| Rank | Source | Role |
|---|---|---|
| 1 | Current source code, runtime probes, tests, and generated artifacts | Actual implementation and verification truth |
| 2 | OpenSpec `changes/` and `specs/` | Capability proposal, approval, task, and archival truth |
| 3 | GitHub PRs and issues | Review, merge, issue state, and delivery truth |
| 4 | Steward tree split files | Cross-artifact coordination, next gates, forbidden scope, and evidence index |
| 5 | Graphiti memory | Searchable digest of accepted milestones, not a truth source |
| 6 | context-mode session index | Short-lived searchable analysis and command-output memory |
| 7 | Historical archived steward snapshots | Recovery reference; stale unless refreshed against current HEAD |

If these sources disagree, do not resolve by editing the steward tree alone.
Record the contradiction, refresh the relevant artifact, and route the decision
through the owning OpenSpec / PR / human gate.

## Split Files By Use

| Use | File |
|---|---|
| Steward operating model and tool responsibilities | `.planning/codebase/steward-tree/README.md` |
| Machine-readable active steward index | `.planning/codebase/steward-tree/steward-index.json` |
| Current next gates | `.planning/codebase/steward-tree/current-next-gates.md` |
| OpenSpec / GitHub branch register | `.planning/codebase/steward-tree/branch-register.md` |
| Evidence artifact index | `.planning/codebase/steward-tree/evidence-index.md` |
| Completed milestone ledger | `.planning/codebase/steward-tree/completed-ledger.md` |
| Freshness and stale-artifact policy | `.planning/codebase/steward-tree/freshness-matrix.md` |
| Service lifecycle DI track | `.planning/codebase/steward-tree/tracks/service-lifecycle-di.md` |
| Route / OpenAPI governance track | `.planning/codebase/steward-tree/tracks/route-openapi-governance.md` |
| Core split and compatibility wrapper track | `.planning/codebase/steward-tree/tracks/core-split-and-compatibility.md` |
| Full historical snapshot | `.planning/codebase/steward-tree/archive/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.full-2026-05-27.md` |

## Current Read Path

1. Read `.planning/codebase/steward-tree/steward-index.json` for automation,
   dashboards, or quick state inspection.
2. Read `.planning/codebase/steward-tree/current-next-gates.md` for the next
   allowed governance or implementation move.
3. Read the relevant track file under `.planning/codebase/steward-tree/tracks/`
   before preparing a new decision, authorization, implementation, or closeout
   lane.
4. Use the archived full snapshot only when recovering older G2 history that has
   not yet been normalized into a split track file.

## Current External State Notes

- PR `#331`
  (`g2-178-strategy-adapter-provider-implementation`) is open and mergeable at
  the time of this split. It is a separate source implementation lane and is not
  included in this governance-only branch.
- This branch intentionally starts from `origin/wip/root-dirty-20260403` at
  `3b8f95945fcb489316ddfaf919835d372122fa5f` to avoid mixing steward
  restructuring with PR `#331` source changes.
- Any merge ordering conflict between this split and PR `#331` should be handled
  by a path-limited reconciliation after one of the PRs lands.

## Update Protocol

Every steward update must include:

1. A node or file-level state change.
2. A source artifact or verification reference.
3. A next gate.
4. A forbidden-scope statement when the node is not an implementation lane.
5. Freshness fields when the update references generated artifacts.
6. A matching update to `steward-index.json` when automation should see it.

Do not append large narrative history to this entrypoint. Add long-form history
to the relevant track file, evidence file, completed ledger, or archive.

## Review Checklist

- [ ] The split preserves the full historical snapshot.
- [ ] The active entrypoint is short enough to use as a daily navigation file.
- [ ] `steward-index.json` lists the active gates and split files.
- [ ] Current gate text distinguishes governance-only, authorization, source
      implementation, closeout, and external/open PR states.
- [ ] PR `#331` remains a separate source implementation PR unless explicitly
      merged by the human maintainer.
