# Steward Tree Branch Register

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active branch / PR register
- Prepared at: `2026-05-27T21:33:48+08:00`
- Base HEAD checked: `b54e7d043720a8c8bc67ad96f4f7eaad0b23ceba`

Boundary note: this register records relationship state only. It does not merge
PRs, change issue labels, or authorize source implementation.

## Recent GitHub PRs Relevant To The Steward Tree

| PR | Branch | Base | State | Relationship |
|---|---|---|---|---|
| `#331` | `g2-178-strategy-adapter-provider-implementation` | `wip/root-dirty-20260403` | `MERGED` at `8bfb4dc74b06d6bb930e48ebf3d27bb28d908704` | Source implementation lane for G2.178 |
| `#332` | `g2-179-steward-tree-governance-split` | `wip/root-dirty-20260403` | `MERGED` at `750fb7c797ff95f27152439ed988a7115252129e` | Steward tree split and machine-readable index |
| `#333` | `g2-180-strategy-adapter-provider-closeout` | `wip/root-dirty-20260403` | `MERGED` at `ba929aee2e7fc0de0278f80f30caa185fafa6b5c` | Governance closeout for G2.178 and residual scan handoff |
| `#334` | `g2-181-strategy-getter-residual-refresh-decision` | `wip/root-dirty-20260403` | `MERGED` at `0398eb81259bba5c7d8c8ba6479056554e13d064` | Residual refresh and next target selection |
| `#335` | `g2-182-strategy-route-provider-fallback-decision` | `wip/root-dirty-20260403` | `MERGED` at `597f8186092b4ad3d0704326e292c5e4fa075f15` | Retained route/provider fallback decision |
| `#336` | `g2-183-strategy-getter-remaining-residual-decision` | `wip/root-dirty-20260403` | `MERGED` at `d454193fdae08ad875c423e0b5aa959d79bedc67` | Strategy getter remaining residual closeout with retained residuals |
| `#337` | `g2-184-next-nonstrategy-service-getter-candidate-decision` | `wip/root-dirty-20260403` | `MERGED` at `b54e7d043720a8c8bc67ad96f4f7eaad0b23ceba` | Next non-Strategy candidate decision selecting provider governance |

## Steward Governance Branch

| Branch | Base | Purpose | Source authority |
|---|---|---|---|
| `g2-185-route-dependency-provider-governance-decision` | `origin/wip/root-dirty-20260403` at `b54e7d043720a8c8bc67ad96f4f7eaad0b23ceba` | Classify active route dependency/provider residuals and select the next queue-refresh gate | None |

## OpenSpec Relationship

This split does not create an OpenSpec change because it is a documentation and
coordination refactor. Architecture source changes still route through the
owning OpenSpec branch or an approved implementation authorization package.

| OpenSpec lane | Steward relationship | Current split action |
|---|---|---|
| `migrate-backend-singletons-to-lifecycle-di` | Owns the service lifecycle DI architecture path | Preserve state in `tracks/service-lifecycle-di.md` and `steward-index.json` |
| `split-backend-core-modules-with-compatibility-wrappers` | Owns Core split and compatibility wrapper gates | Preserve blocked Batch 2 gate in `tracks/core-split-and-compatibility.md` |
| route / OpenAPI governance changes | Own route, OpenAPI, probe, and consumer-contract decisions | Preserve governance boundaries in `tracks/route-openapi-governance.md` |

## Merge Ordering Note

G2.185 is a provider-governance decision branch only. It records the merged
state of PR `#337`, classifies active FastAPI dependency providers as retained
route contracts, and must not introduce backend source edits or a new
implementation lane.
