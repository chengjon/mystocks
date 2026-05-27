# Steward Tree Branch Register

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active branch / PR register
- Prepared at: `2026-05-28T01:04:38+08:00`
- Base HEAD checked: `7154ffbb067dcddc52d80f15342961b51234ac09`

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
| `#338` | `g2-185-route-dependency-provider-governance-decision` | `wip/root-dirty-20260403` | `MERGED` at `720248521d705af067d0a2600710444e439d7605` | Provider governance decision retaining active route contracts |
| `#339` | `g2-186-remaining-getter-inventory-refresh` | `wip/root-dirty-20260403` | `MERGED` at `a63a6cb9a277195905b046cd31777d95160ee2c6` | Remaining getter inventory refresh selecting stop-loss authorization |
| `#340` | `g2-187-risk-stop-loss-provider-authorization` | `wip/root-dirty-20260403` | `MERGED` at `2d3b9c7e3ff30c81a19d51e66c32d2c06c1e1c4a` | Authorization package for G2.188 stop-loss route provider implementation |
| `#341` | `g2-188-risk-stop-loss-provider-implementation` | `wip/root-dirty-20260403` | `MERGED` at `0aac0e16f16480bd99eebb8726e21a7db6566b39` | Path-limited stop-loss route provider implementation closed for G2.189 refresh |
| `#342` | `g2-189-risk-stop-loss-provider-closeout-refresh` | `wip/root-dirty-20260403` | `MERGED` at `5565e2b0967958c406a4115dc840a9e90a0b2aab` | Governance closeout and candidate refresh selecting data-quality / adapter cross-cutting decision |
| `#343` | `g2-190-data-quality-adapter-decision` | `wip/root-dirty-20260403` | `MERGED` at `7154ffbb067dcddc52d80f15342961b51234ac09` | Governance decision classifying data-quality / adapter monitor surface as cross-cutting |

## Steward Governance Branch

| Branch | Base | Purpose | Source authority |
|---|---|---|---|
| `g2-191-data-quality-route-provider-authorization` | `origin/wip/root-dirty-20260403` at `7154ffbb067dcddc52d80f15342961b51234ac09` | Authorize a future route-only data-quality provider implementation lane without source edits in this PR | None in this PR; future G2.192 source lane only after acceptance |

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

G2.191 is a governance-only authorization branch after PR `#343` merged G2.190.
It must not edit backend source, frontend source, tests, OpenSpec changes, or
API contract files. If accepted, it authorizes G2.192 as a route-only
implementation lane for `web/backend/app/api/data_quality.py` and focused tests.
