# Steward Tree Evidence Index

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active evidence index
- Prepared at: `2026-05-28T00:19:16+08:00`
- Base HEAD checked: `0aac0e16f16480bd99eebb8726e21a7db6566b39`

Boundary note: this index points to evidence artifacts. It does not promote
review input into accepted truth without a matching review, PR, or OpenSpec
state transition.

## Primary Evidence Artifacts

| Evidence | Role | Freshness policy |
|---|---|---|
| `.planning/codebase/steward-tree/archive/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.full-2026-05-27.md` | Full historical steward snapshot | Historical; refresh current state before using as execution truth |
| `.planning/codebase/CODEBASE-MAP-STEWARD-TREE-RETROSPECTIVE-2026-05-22.md` | Lessons and improvement opportunities | Historical; use as rationale for this split |
| `.planning/codebase/CODEBASE-MAP-STEWARD-TREE-PRACTICE-GUIDE-2026-05-24.md` | Reusable operating model for other projects | Historical; superseded for this repo by `steward-tree/README.md` |
| `.planning/codebase/steward-tree/steward-index.json` | Machine-readable active steward state | Current for this branch; stale if base HEAD or PR state changes |
| `.planning/codebase/steward-tree/current-next-gates.md` | Human-readable active gates | Current for this branch; stale if base HEAD changes |
| `.planning/codebase/generated/strategy-adapter-provider-closeout-2026-05-27.json` | G2.180 closeout and residual-refresh evidence | Current for HEAD `8bfb4dc74b06d6bb930e48ebf3d27bb28d908704` |
| `docs/reports/quality/backend-strategy-adapter-provider-closeout-2026-05-27.md` | G2.180 human-readable closeout report | Accepted by PR `#333`; superseded for residual next-gate selection by G2.181 |
| `.planning/codebase/generated/strategy-getter-residual-refresh-decision-2026-05-27.json` | G2.181 residual class refresh and next-gate decision evidence | Current for HEAD `ba929aee2e7fc0de0278f80f30caa185fafa6b5c` |
| `docs/reports/quality/backend-strategy-getter-residual-refresh-decision-2026-05-27.md` | G2.181 human-readable residual-refresh decision package | Accepted by PR `#334`; superseded for route/provider fallback classification by G2.182 |
| `.planning/codebase/generated/strategy-route-provider-fallback-decision-2026-05-27.json` | G2.182 route/provider fallback classification evidence | Current for HEAD `0398eb81259bba5c7d8c8ba6479056554e13d064` |
| `docs/reports/quality/backend-strategy-route-provider-fallback-decision-2026-05-27.md` | G2.182 human-readable route/provider fallback decision package | Accepted by PR `#335`; superseded for remaining-residual closeout by G2.183 |
| `.planning/codebase/generated/strategy-getter-remaining-residual-decision-2026-05-27.json` | G2.183 remaining Strategy getter residual closeout evidence | Current for HEAD `597f8186092b4ad3d0704326e292c5e4fa075f15` |
| `docs/reports/quality/backend-strategy-getter-remaining-residual-decision-2026-05-27.md` | G2.183 human-readable remaining-residual decision package | Accepted by PR `#336`; superseded for next-gate selection by G2.184 |
| `.planning/codebase/generated/next-nonstrategy-service-getter-candidate-decision-2026-05-27.json` | G2.184 next non-Strategy service getter candidate decision evidence | Current for HEAD `d454193fdae08ad875c423e0b5aa959d79bedc67`; stale if HEAD changes |
| `docs/reports/quality/backend-next-nonstrategy-service-getter-candidate-decision-2026-05-27.md` | G2.184 human-readable next-candidate decision package | Accepted by PR `#337`; superseded for provider classification by G2.185 |
| `.planning/codebase/generated/route-dependency-provider-governance-decision-2026-05-27.json` | G2.185 route dependency/provider governance decision evidence | Current for HEAD `b54e7d043720a8c8bc67ad96f4f7eaad0b23ceba`; accepted by PR `#338` |
| `docs/reports/quality/backend-route-dependency-provider-governance-decision-2026-05-27.md` | G2.185 human-readable provider-governance decision package | Accepted by PR `#338`; superseded for remaining getter queue refresh by G2.186 |
| `.planning/codebase/generated/service-lifecycle-remaining-getter-inventory-refresh-2026-05-27.json` | G2.186 remaining getter inventory refresh evidence | Current for HEAD `720248521d705af067d0a2600710444e439d7605`; stale if HEAD changes |
| `docs/reports/quality/backend-service-lifecycle-remaining-getter-inventory-refresh-2026-05-27.md` | G2.186 human-readable inventory refresh decision package | Accepted by PR `#339`; superseded for stop-loss authorization by G2.187 |
| `.planning/codebase/generated/risk-stop-loss-route-provider-authorization-2026-05-27.json` | G2.187 risk stop-loss route provider authorization evidence | Accepted by PR `#340`; superseded for implementation review by G2.188 |
| `docs/reports/quality/backend-risk-stop-loss-route-provider-authorization-2026-05-27.md` | G2.187 human-readable authorization package | Accepted by PR `#340` |
| `.planning/codebase/generated/risk-stop-loss-route-provider-implementation-2026-05-27.json` | G2.188 risk stop-loss route provider implementation evidence | Accepted by PR `#341`; superseded for remaining candidate selection by G2.189 |
| `docs/reports/quality/backend-risk-stop-loss-route-provider-implementation-2026-05-27.md` | G2.188 human-readable implementation package | Accepted by PR `#341` |
| `.planning/codebase/generated/risk-stop-loss-provider-closeout-refresh-2026-05-28.json` | G2.189 stop-loss provider closeout and candidate-refresh evidence | Current for HEAD `0aac0e16f16480bd99eebb8726e21a7db6566b39`; review input until PR `#342` is accepted |
| `docs/reports/quality/backend-risk-stop-loss-provider-closeout-refresh-2026-05-28.md` | G2.189 human-readable closeout and candidate-refresh report | Review input until PR `#342` is accepted |

## External State Inputs

| Input | Current state at split | Notes |
|---|---|---|
| GitHub PR `#331` | `MERGED` | G2.178 source implementation lane closed by merge commit `8bfb4dc74b06d6bb930e48ebf3d27bb28d908704` |
| GitHub PR `#336` | `MERGED` | G2.183 remaining Strategy getter residual closeout merged by commit `d454193fdae08ad875c423e0b5aa959d79bedc67` |
| GitHub PR `#337` | `MERGED` | G2.184 next non-Strategy candidate decision merged by commit `b54e7d043720a8c8bc67ad96f4f7eaad0b23ceba` |
| GitHub PR `#338` | `MERGED` | G2.185 provider governance decision merged by commit `720248521d705af067d0a2600710444e439d7605` |
| GitHub PR `#339` | `MERGED` | G2.186 remaining getter inventory refresh merged by commit `a63a6cb9a277195905b046cd31777d95160ee2c6` |
| GitHub PR `#340` | `MERGED` | G2.187 stop-loss route provider authorization merged by commit `2d3b9c7e3ff30c81a19d51e66c32d2c06c1e1c4a` |
| GitHub PR `#341` | `MERGED` | G2.188 stop-loss route provider implementation merged by commit `0aac0e16f16480bd99eebb8726e21a7db6566b39` |
| `origin/wip/root-dirty-20260403` | `0aac0e16f16480bd99eebb8726e21a7db6566b39` | Base used for this closeout / candidate-refresh branch |
| Root worktree | Dirty/stale relative to remote | Not used as the edit surface for this split |

## Evidence Recording Rules

- Evidence collected from context-mode must be summarized into repo files before
  it becomes durable project evidence.
- GitNexus risk results belong in implementation or authorization reports, not
  only in chat memory.
- GitHub PR state must include PR number, branch, base, and checked timestamp.
- Generated artifact references must include `generated_at`, `git_head` when
  available, `current_head_checked_at_review`, and a stale policy.
- Graphiti entries should record accepted milestone summaries after the repo or
  GitHub artifact exists.
