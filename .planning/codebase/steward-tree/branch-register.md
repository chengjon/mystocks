# Steward Tree Branch Register

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active branch / PR register
- Prepared at: `2026-05-28T20:48:36+08:00`
- Base HEAD checked: `33b6ace2f68e23bcf07a12f53511d1f7b9fb8230`

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
| `#344` | `g2-191-data-quality-route-provider-authorization` | `wip/root-dirty-20260403` | `MERGED` at `b899a173909d3818370dddbf35b039832266bd1d` | Authorization package for G2.192 data-quality route provider implementation |
| `#345` | `g2-192-data-quality-route-provider-implementation` | `wip/root-dirty-20260403` | `MERGED` at `2b0c3ce373fba38bacd62eff5436822527dccda1` | Path-limited data-quality route provider implementation closed for G2.193 refresh |
| `#346` | `g2-193-data-quality-route-provider-closeout-refresh` | `wip/root-dirty-20260403` | `MERGED` at `ea659d52903a5e9884d396069526ea08f15109a6` | Governance closeout / remaining surface refresh selecting G2.194 adapter constructor seam design |
| `#347` | `g2-194-data-quality-adapter-seam-design` | `wip/root-dirty-20260403` | `MERGED` at `e30e16605df6aaa333989a7ac247bab3dcd0dd01` | Governance design decision selecting G2.195 adapter_split constructor provider authorization |
| `#348` | `g2-195-data-quality-adapter-split-authorization` | `wip/root-dirty-20260403` | `MERGED` at `fabd674e8a748cdd2c51a80eebb5ad20b52bc737` | Authorization package for G2.196 adapter_split constructor provider implementation |
| `#349` | `g2-196-data-quality-adapter-split-implementation` | `wip/root-dirty-20260403` | `MERGED` at `e4245ebe54c5ad6d2aebf4802d165d59700c9eeb` | Path-limited `adapter_split` constructor provider implementation closed for G2.197 refresh |
| `#350` | `g2-197-data-quality-monitor-closeout-refresh` | `wip/root-dirty-20260403` | `MERGED` at `3acf90c3ab17dbb3b47150a03f1cdee1c96dc8f1` | Closeout / remaining candidate refresh selecting G2.198 residual adapter ownership decision |
| `#351` | `g2-198-data-quality-residual-adapter-ownership-decision` | `wip/root-dirty-20260403` | `MERGED` at `a6b54ddfb24055552d634757f01dc03bd6ca6e62` | Decision selecting canonical service adapter provider authorization as G2.199 |
| `#352` | `g2-199-data-quality-canonical-service-adapter-authorization` | `wip/root-dirty-20260403` | `MERGED` at `41bef3787160ec3bf7b9b31220df9d99a3437474` | Authorization package for G2.200 canonical service adapter provider implementation |
| `#353` | `g2-200-data-quality-canonical-service-adapter-provider` | `wip/root-dirty-20260403` | `MERGED` at `cbd9b3a7ee730c72a63dbc7adb6490564c12c71e` | Path-limited canonical service adapter provider implementation closed for G2.201 refresh |
| `#354` | `g2-201-data-quality-canonical-service-adapter-closeout-refresh` | `wip/root-dirty-20260403` | `MERGED` at `e672f1523c30037202310278daf71488681d9a1f` | Governance closeout selecting G2.202 legacy adapter compatibility ownership decision |
| `#355` | `g2-202-data-quality-legacy-adapter-ownership-decision` | `wip/root-dirty-20260403` | `MERGED` at `bf5d5ffba6bfc837c009a3d937cf0a9e6549883f` | Decision package selecting G2.203 legacy adapter compatibility closure authorization |
| `#356` | `g2-203-data-quality-legacy-adapter-compatibility-closure-authorization` | `wip/root-dirty-20260403` | `MERGED` at `142a2bf1c0c5f979cf9c32415d2f25832e7e62cd` | Authorization package for G2.204 thin-wrapper compatibility implementation |
| `#357` | `g2-204-data-quality-legacy-adapter-compatibility-wrapper` | `wip/root-dirty-20260403` | `MERGED` at `a621ba4ae66f581074a3b66539e296cbf0ced1b5` | Path-limited thin-wrapper implementation closed for G2.205 refresh |
| `#358` | `g2-205-data-quality-legacy-adapter-closeout-refresh` | `wip/root-dirty-20260403` | `MERGED` at `44909f5d048700115da6a9eb9345957b8af3d077` | Governance closeout selecting G2.206 `market_data_adapter.py` compatibility facade ownership decision |
| `#359` | `g2-206-data-quality-market-data-adapter-ownership-decision` | `wip/root-dirty-20260403` | `MERGED` at `ded789ee5d49d6ddcce5d8a69af1901a8481d1f0` | Decision package selecting G2.207 provider seam authorization |
| `#360` | `g2-207-data-quality-market-data-adapter-provider-authorization` | `wip/root-dirty-20260403` | `MERGED` at `b4b34375eef0186b81be9a24491328dab72c2e21` | Authorization package for G2.208 `market_data_adapter.py` provider seam implementation |
| `#361` | `g2-208-data-quality-market-data-adapter-provider-implementation` | `wip/root-dirty-20260403` | `MERGED` at `90d8f12cc01f9fb360abc531673e3ed9535706e7` | Path-limited `market_data_adapter.py` provider seam implementation closed for G2.209 refresh |
| `#362` | `g2-209-data-quality-market-data-adapter-provider-closeout` | `wip/root-dirty-20260403` | `MERGED` at `33b6ace2f68e23bcf07a12f53511d1f7b9fb8230` | Governance closeout selecting G2.210 data-quality monitor residual ownership decision |

## Steward Governance Branch

| Branch | Base | Purpose | Source authority |
|---|---|---|---|
| `g2-210-data-quality-monitor-residual-ownership-decision` | `origin/wip/root-dirty-20260403` at `33b6ace2f68e23bcf07a12f53511d1f7b9fb8230` | Decide remaining data-quality monitor singleton/backing API ownership and next authorization gate | No |

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

G2.210 is a no-source residual ownership decision branch after PR `#362` merged
G2.209. It is limited to governance evidence, steward tree updates, and a task
card. If accepted, the next gate is a G2.211 singleton/backing API authorization
package, not a direct source implementation lane.
