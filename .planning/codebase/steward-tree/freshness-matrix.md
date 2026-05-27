# Steward Tree Freshness Matrix

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active freshness policy
- Prepared at: `2026-05-27T15:32:41+08:00`
- Base HEAD checked: `3b8f95945fcb489316ddfaf919835d372122fa5f`

Boundary note: freshness labels prevent stale evidence from being treated as
current truth. They do not authorize implementation or PR merge actions.

## Freshness Labels

| Label | Meaning | Required action before execution |
|---|---|---|
| `current_head` | Artifact was generated or checked at the current branch HEAD | May be used for the scoped decision it supports |
| `commit_scoped` | Artifact is valid for a named commit but not necessarily current HEAD | Recheck if source or route state changed |
| `stale_aware` | Artifact is older than current HEAD but still useful as context | Refresh before using as gate evidence |
| `external_review_input` | Artifact was provided for review but not accepted as project truth | Needs review acceptance before promotion |
| `contradiction_unresolved` | Two current artifacts disagree | Stop and create reconciliation evidence |

## Current Freshness Rows

| Artifact | Freshness | Checked against | Stale condition |
|---|---|---|---|
| Root steward entrypoint | `current_head` | `3b8f95945fcb489316ddfaf919835d372122fa5f` | Any later merge changes steward files |
| Full archived snapshot | `commit_scoped` | `3b8f95945fcb489316ddfaf919835d372122fa5f` | Any use as current execution truth |
| `steward-index.json` | `current_head` | `3b8f95945fcb489316ddfaf919835d372122fa5f` | PR `#331` changes state or base HEAD changes |
| PR `#331` status | `external_current_at_split` | GitHub PR state at split | PR state, mergeability, or base changes |
| Existing retrospective/practice guide | `stale_aware` | Historical review dates | Any use as current gate truth |

## Required Fields For New Generated Evidence

Generated evidence should record:

- `generated_at`
- `git_head`
- `current_head_checked_at_review`
- `stale_if_head_mismatch`
- `source_command`
- `output_artifact`
- `review_status`
