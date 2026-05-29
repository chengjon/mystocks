# Steward Tree Branch Register

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active branch / PR register
- Prepared at: `2026-05-29T21:17:11+08:00`
- Base HEAD checked: `fd9efeefc31cdbe5aa702b47f736b5bc8b9d4bea`

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
| `#363` | `g2-210-data-quality-monitor-residual-ownership-decision` | `wip/root-dirty-20260403` | `MERGED` at `619be9cac1f9516b3df42a41ca362ca9d42d5c9a` | Decision package selecting G2.211 singleton/backing API authorization |
| `#364` | `g2-211-data-quality-monitor-singleton-authorization` | `wip/root-dirty-20260403` | `MERGED` at `535a6d9c1565b4ced7942cb4082104f2fb0506fd` | Authorization package selecting G2.212 data-quality monitor singleton/backing API implementation |
| `#365` | `g2-212-data-quality-monitor-singleton-implementation` | `wip/root-dirty-20260403` | `MERGED` at `e7d9fe63285181f0227661628272487dc63d4e2c` | Path-limited singleton/backing API provider seam implementation closed for G2.213 refresh |
| `#366` | `g2-213-data-quality-monitor-singleton-closeout-refresh` | `wip/root-dirty-20260403` | `MERGED` at `3d3f8285f3a83cb4dda60d9b7eb8cf36fdf77117` | No-source closeout selecting G2.214 non-Strategy provider queue refresh |
| `#367` | `g2-214-non-strategy-provider-queue-refresh` | `wip/root-dirty-20260403` | `MERGED` at `a508fb263173b2014d307c4baec3b1eca0f42340` | No-source queue refresh selecting G2.215 indicator/data `get_data_service` ownership decision |
| `#368` | `g2-215-indicator-data-get-data-service-decision` | `wip/root-dirty-20260403` | `MERGED` at `cec3f727534008d2a48221c656c22f82f351e3d7` | No-source ownership decision selecting G2.216 indicator/data `DataService` provider authorization |
| `#369` | `g2-216-indicator-data-service-provider-authorization` | `wip/root-dirty-20260403` | `MERGED` at `68ba10829b89095f8b907d249f59198995543ebc` | No-source authorization selecting G2.217 `DataService` provider/reset seam implementation |
| `#370` | `g2-217-data-service-provider-reset-seam` | `wip/root-dirty-20260403` | `MERGED` at `4d2b69e449975d145976e10c8af965e16dc60a1e` | Path-limited implementation adding `DataService` provider/reset seam while preserving default singleton fallback |
| `#371` | `g2-218-data-service-provider-closeout-refresh` | `wip/root-dirty-20260403` | `MERGED` at `d4ee917ad642939c4c60000998b8bea5ca7c9a65` | No-source closeout selecting G2.219 `get_execution_tracking_evidence_service` ownership decision |
| `#372` | `g2-219-execution-tracking-evidence-provider-decision` | `wip/root-dirty-20260403` | `MERGED` at `b51256b775f7b4c6e5baad8c82a7f86446c0151b` | No-source ownership decision selecting G2.220 trade execution tracking evidence provider authorization |
| `#373` | `g2-220-execution-tracking-evidence-provider-authorization` | `wip/root-dirty-20260403` | `MERGED` at `3d2dc3e8204388cc157c23df59f584a3efb268fe` | No-source authorization selecting G2.221 path-limited execution tracking provider injection |
| `#374` | `g2-221-execution-tracking-evidence-provider-injection` | `wip/root-dirty-20260403` | `MERGED` at `14339f44a8c4a145615fe35836dec8fc376ce75b` | Path-limited implementation closing execution tracking route-body provider calls |
| `#375` | `g2-222-execution-tracking-provider-closeout-refresh` | `wip/root-dirty-20260403` | `MERGED` at `e7402fffe29bee5f7f2a4ada5a60a4bf26876969` | No-source execution tracking provider closeout / residual refresh |
| `#376` | `g2-223-unified-data-service-ownership-decision` | `wip/root-dirty-20260403` | `MERGED` at `5eef37a097d55d209a69485bc29e89dd3aeb4076` | No-source `get_unified_data_service` ownership decision selecting G2.224 authorization |
| `#377` | `g2-224-industry-concept-unified-data-service-cleanup-authorization` | `wip/root-dirty-20260403` | `MERGED` at `36c38fbf233945b7e45ed67b50591665942d4b32` | No-source authorization selecting G2.225 `industry_concept_analysis.py` cleanup implementation |
| `#378` | `g2-225-industry-concept-unified-data-service-cleanup` | `wip/root-dirty-20260403` | `MERGED` at `5837b8af55499e8ee9d7ba14cf543abb9bc45e39` | Path-limited implementation closing `industry_concept_analysis.py` direct `UnifiedDataService()` calls |
| `#379` | `g2-226-industry-concept-unified-data-service-closeout-refresh` | `wip/root-dirty-20260403` | `MERGED` at `854878cd2e09384daddaa8547e8cebc970ec2b74` | No-source closeout / residual refresh selecting G2.227 `get_prewarming_strategy` ownership decision |
| `#380` | `g2-227-cache-prewarming-strategy-ownership-decision` | `wip/root-dirty-20260403` | `MERGED` at `f2b528e5feaf7fd89f19a857e75a3c3442ba9c6b` | No-source ownership decision selecting G2.228 cache prewarming strategy provider authorization |
| `#381` | `g2-228-cache-prewarming-strategy-provider-authorization` | `wip/root-dirty-20260403` | `MERGED` at `4d77ee68a1a4a30516134b995c82fa777c3b44d6` | No-source authorization selecting G2.229 cache prewarming route DI implementation |
| `#382` | `g2-229-cache-prewarming-route-di-implementation` | `wip/root-dirty-20260403` | `MERGED` at `4a0e41eac399e052ed3ebc9facc7dbf08761ab0a` | Path-limited cache prewarming route DI implementation |
| `#383` | `g2-230-cache-prewarming-route-di-closeout-refresh` | `wip/root-dirty-20260403` | `MERGED` at `2652d59b02dedaecd4ac05a2f95fce8ab4ae2e3c` | No-source cache prewarming route DI closeout selecting G2.231 residual candidate refresh |
| `#384` | `g2-231-service-lifecycle-residual-candidate-refresh` | `wip/root-dirty-20260403` | `MERGED` at `05c84d1f4f5e42d9db0ace21ef3ba110dacbc184` | No-source residual refresh selecting G2.232 data-source config manager provider authorization |
| `#385` | `g2-232-data-source-config-manager-provider-authorization` | `wip/root-dirty-20260403` | `MERGED` at `1f63a46657858920a3df9799ffc0c45ccf3b3dd8` | No-source authorization selecting G2.233 data-source config manager provider injection |
| `#386` | `g2-233-data-source-config-manager-provider-injection` | `wip/root-dirty-20260403` | `MERGED` at `875b57fd2b61dd3f4b5b26e95ea5b31ddc0b6d8f` | Path-limited provider injection closing active `data_source_config.py` route-body manager calls |
| `#387` | `g2-234-data-source-config-manager-provider-closeout-refresh` | `wip/root-dirty-20260403` | `MERGED` at `659a1dffb1d1306c8fe09ce2bdd9e17ab87dd8a5` | No-source closeout / residual refresh selecting G2.235 service lifecycle residual candidate refresh |
| `#388` | `g2-235-service-lifecycle-residual-candidate-refresh` | `wip/root-dirty-20260403` | `MERGED` at `383598ab2a30da31513468b97537183322b46af9` | No-source residual candidate refresh selecting G2.236 monitoring calculator factory ownership decision |
| `#389` | `g2-236-monitoring-calculator-factory-decision` | `wip/root-dirty-20260403` | `MERGED` at `f39aca8815d59739787349ed1025e7a1b7e2c050` | No-source ownership / provider seam decision selecting G2.237 monitoring calculator factory provider authorization |
| `#390` | `g2-237-monitoring-calculator-factory-provider-authorization` | `wip/root-dirty-20260403` | `MERGED` at `ef11ae6577bf62d15b814af732ba291696e5b084` | No-source provider authorization selecting G2.238 monitoring calculator factory provider injection |
| `#391` | `g2-238-monitoring-calculator-factory-provider-injection` | `wip/root-dirty-20260403` | `MERGED` at `fd9efeefc31cdbe5aa702b47f736b5bc8b9d4bea` | Path-limited monitoring calculator factory provider injection closing 8 active route-body factory calls |

## Steward Governance Branch

| Branch | Base | Purpose | Source authority |
|---|---|---|---|
| `g2-239-monitoring-calculator-factory-provider-closeout-refresh` | `origin/wip/root-dirty-20260403` at `fd9efeefc31cdbe5aa702b47f736b5bc8b9d4bea` | Close out accepted G2.238 and refresh the next service lifecycle residual gate | No |

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

G2.239 is the no-source closeout / residual refresh after PR `#391` merged
G2.238. It records the accepted monitoring calculator factory provider result,
refreshes steward evidence, and recommends G2.240 as a no-source service
lifecycle residual candidate refresh. It must not expand into calculator domain
source, route contracts, OpenAPI, frontend, config, scripts, tests, or OpenSpec.
