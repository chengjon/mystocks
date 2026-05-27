# Steward Tree Governance Split Report - 2026-05-27

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: for review
- Workline: CODEBASE-MAP steward tree governance split
- Branch: `g2-179-steward-tree-governance-split`
- Base branch: `origin/wip/root-dirty-20260403`
- Base HEAD: `3b8f95945fcb489316ddfaf919835d372122fa5f`
- Prepared at: `2026-05-27T15:32:41+08:00`
- Scope: governance documents only

Boundary note: this report does not authorize backend source edits, frontend
source edits, tests, generated client updates, docs/API edits, OpenSpec proposal
creation, issue label changes, PM2 commands, runtime rollout, compatibility
deletion, or GitHub PR merge decisions.

## Objective

Improve the steward tree's function and operating efficiency by:

1. Adding an explicit governance contract for steward-tree responsibilities and
   boundaries with context-mode, GitNexus, GitHub PRs, Graphiti, and OpenSpec.
2. Adding a machine-readable steward index.
3. Splitting the oversized root steward tree by usage while preserving the full
   historical snapshot.

## Changes

| Change | Path |
|---|---|
| Root steward tree converted into short entrypoint | `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` |
| Full previous tree archived | `.planning/codebase/steward-tree/archive/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.full-2026-05-27.md` |
| Steward governance contract added | `.planning/codebase/steward-tree/README.md` |
| Machine-readable steward index added | `.planning/codebase/steward-tree/steward-index.json` |
| Current gate register added | `.planning/codebase/steward-tree/current-next-gates.md` |
| Branch register added | `.planning/codebase/steward-tree/branch-register.md` |
| Evidence index added | `.planning/codebase/steward-tree/evidence-index.md` |
| Completed ledger added | `.planning/codebase/steward-tree/completed-ledger.md` |
| Freshness matrix added | `.planning/codebase/steward-tree/freshness-matrix.md` |
| Track files added | `.planning/codebase/steward-tree/tracks/*.md` |

## External State

PR `#331` remains a separate source implementation lane:

- URL: `https://github.com/chengjon/mystocks/pull/331`
- Branch: `g2-178-strategy-adapter-provider-implementation`
- State at split: `OPEN`
- Mergeability at split: `MERGEABLE`

This governance split intentionally does not include PR `#331` source changes.

## Expected Benefits

- The root steward entrypoint becomes fast to read and review.
- Current gates can be found without scanning historical rows.
- Automation can read `steward-index.json` instead of parsing narrative Markdown.
- Freshness and external PR state are explicit.
- Long-term history remains recoverable from the archive.

## Residual Follow-Up

- Add a steward-tree guard that validates `steward-index.json` and referenced
  split file existence.
- Update `steward-index.json` after PR `#331` merges, closes, or changes state.
- Gradually normalize older G2 historical rows from the archive into track files
  only when they become active again.
