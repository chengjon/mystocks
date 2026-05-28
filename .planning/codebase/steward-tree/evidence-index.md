# Steward Tree Evidence Index

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active evidence index
- Prepared at: `2026-05-28T23:28:14+08:00`
- Base HEAD checked: `3d3f8285f3a83cb4dda60d9b7eb8cf36fdf77117`

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
| `.planning/codebase/generated/data-quality-adapter-cross-cutting-decision-2026-05-28.json` | G2.190 data-quality / adapter cross-cutting decision evidence | Accepted by PR `#343`; superseded for route authorization by G2.191 |
| `docs/reports/quality/backend-data-quality-adapter-cross-cutting-decision-2026-05-28.md` | G2.190 human-readable decision package | Accepted by PR `#343`; superseded for route authorization by G2.191 |
| `.planning/codebase/generated/data-quality-route-provider-authorization-2026-05-28.json` | G2.191 data-quality route provider authorization evidence | Accepted by PR `#344`; superseded for implementation review by G2.192 |
| `docs/reports/quality/backend-data-quality-route-provider-authorization-2026-05-28.md` | G2.191 human-readable authorization package | Accepted by PR `#344`; superseded for implementation review by G2.192 |
| `.planning/codebase/generated/data-quality-route-provider-implementation-2026-05-28.json` | G2.192 data-quality route provider implementation evidence | Accepted by PR `#345`; superseded for closeout / remaining candidate refresh by G2.193 |
| `docs/reports/quality/backend-data-quality-route-provider-implementation-2026-05-28.md` | G2.192 human-readable implementation package | Accepted by PR `#345`; superseded for closeout / remaining candidate refresh by G2.193 |
| `.planning/codebase/generated/data-quality-route-provider-closeout-refresh-2026-05-28.json` | G2.193 data-quality route provider closeout / refresh evidence | Accepted by PR `#346`; superseded for adapter constructor seam design by G2.194 |
| `docs/reports/quality/backend-data-quality-route-provider-closeout-refresh-2026-05-28.md` | G2.193 human-readable closeout / refresh report | Accepted by PR `#346`; superseded for adapter constructor seam design by G2.194 |
| `.planning/codebase/generated/data-quality-adapter-seam-design-decision-2026-05-28.json` | G2.194 data-quality adapter constructor seam design decision evidence | Accepted by PR `#347`; superseded for implementation authorization by G2.195 |
| `docs/reports/quality/backend-data-quality-adapter-seam-design-decision-2026-05-28.md` | G2.194 human-readable adapter seam design decision report | Accepted by PR `#347`; superseded for implementation authorization by G2.195 |
| `.planning/codebase/generated/data-quality-adapter-split-constructor-provider-authorization-2026-05-28.json` | G2.195 data-quality `adapter_split` constructor provider authorization evidence | Accepted by PR `#348`; superseded for implementation evidence by G2.196 |
| `docs/reports/quality/backend-data-quality-adapter-split-constructor-provider-authorization-2026-05-28.md` | G2.195 human-readable authorization package | Accepted by PR `#348`; superseded for implementation evidence by G2.196 |
| `.planning/codebase/generated/data-quality-adapter-split-constructor-provider-implementation-2026-05-28.json` | G2.196 data-quality `adapter_split` constructor provider implementation evidence | Accepted by PR `#349`; superseded for closeout / remaining candidate refresh by G2.197 |
| `docs/reports/quality/backend-data-quality-adapter-split-constructor-provider-implementation-2026-05-28.md` | G2.196 human-readable implementation report | Accepted by PR `#349`; superseded for closeout / remaining candidate refresh by G2.197 |
| `.planning/codebase/generated/data-quality-monitor-closeout-refresh-2026-05-28.json` | G2.197 data-quality monitor closeout / remaining candidate refresh evidence | Accepted by PR `#350`; superseded for residual adapter ownership decision by G2.198 |
| `docs/reports/quality/backend-data-quality-monitor-closeout-refresh-2026-05-28.md` | G2.197 human-readable closeout / refresh report | Accepted by PR `#350`; superseded for residual adapter ownership decision by G2.198 |
| `.planning/codebase/generated/data-quality-residual-adapter-ownership-decision-2026-05-28.json` | G2.198 residual data-quality adapter ownership decision evidence | Accepted by PR `#351`; superseded for canonical service adapter authorization by G2.199 |
| `docs/reports/quality/backend-data-quality-residual-adapter-ownership-decision-2026-05-28.md` | G2.198 human-readable residual adapter ownership decision report | Accepted by PR `#351`; superseded for canonical service adapter authorization by G2.199 |
| `.planning/codebase/generated/data-quality-canonical-service-adapter-provider-authorization-2026-05-28.json` | G2.199 canonical service adapter provider authorization evidence | Accepted by PR `#352`; superseded for implementation evidence by G2.200 |
| `docs/reports/quality/backend-data-quality-canonical-service-adapter-provider-authorization-2026-05-28.md` | G2.199 human-readable authorization package | Accepted by PR `#352`; superseded for implementation evidence by G2.200 |
| `.planning/codebase/generated/data-quality-canonical-service-adapter-provider-implementation-2026-05-28.json` | G2.200 canonical service adapter provider implementation evidence | Accepted by PR `#353`; superseded for residual refresh by G2.201 |
| `docs/reports/quality/backend-data-quality-canonical-service-adapter-provider-implementation-2026-05-28.md` | G2.200 human-readable implementation report | Accepted by PR `#353`; superseded for residual refresh by G2.201 |
| `.planning/codebase/generated/data-quality-canonical-service-adapter-closeout-refresh-2026-05-28.json` | G2.201 canonical service adapter closeout / residual refresh evidence | Accepted by PR `#354`; superseded for legacy adapter ownership by G2.202 |
| `docs/reports/quality/backend-data-quality-canonical-service-adapter-closeout-refresh-2026-05-28.md` | G2.201 human-readable closeout / residual refresh report | Accepted by PR `#354`; superseded for legacy adapter ownership by G2.202 |
| `.planning/codebase/generated/data-quality-legacy-adapter-ownership-decision-2026-05-28.json` | G2.202 legacy data adapter compatibility ownership decision evidence | Accepted by PR `#355`; superseded for closure authorization by G2.203 |
| `docs/reports/quality/backend-data-quality-legacy-adapter-ownership-decision-2026-05-28.md` | G2.202 human-readable ownership decision report | Accepted by PR `#355`; superseded for closure authorization by G2.203 |
| `.planning/codebase/generated/data-quality-legacy-adapter-compatibility-closure-authorization-2026-05-28.json` | G2.203 legacy adapter compatibility closure authorization evidence | Accepted by PR `#356`; superseded for wrapper implementation by G2.204 |
| `docs/reports/quality/backend-data-quality-legacy-adapter-compatibility-closure-authorization-2026-05-28.md` | G2.203 human-readable compatibility closure authorization report | Accepted by PR `#356`; superseded for wrapper implementation by G2.204 |
| `.planning/codebase/generated/data-quality-legacy-adapter-compatibility-wrapper-implementation-2026-05-28.json` | G2.204 legacy adapter compatibility wrapper implementation evidence | Accepted by PR `#357`; superseded for closeout / residual refresh by G2.205 |
| `docs/reports/quality/backend-data-quality-legacy-adapter-compatibility-wrapper-implementation-2026-05-28.md` | G2.204 human-readable wrapper implementation report | Accepted by PR `#357`; superseded for closeout / residual refresh by G2.205 |
| `.planning/codebase/generated/data-quality-legacy-adapter-compatibility-wrapper-closeout-refresh-2026-05-28.json` | G2.205 legacy adapter wrapper closeout / residual refresh evidence | Accepted by PR `#358`; superseded for `market_data_adapter.py` ownership by G2.206 |
| `docs/reports/quality/backend-data-quality-legacy-adapter-compatibility-wrapper-closeout-refresh-2026-05-28.md` | G2.205 human-readable closeout / residual refresh report | Accepted by PR `#358`; superseded for `market_data_adapter.py` ownership by G2.206 |
| `.planning/codebase/generated/data-quality-market-data-adapter-ownership-decision-2026-05-28.json` | G2.206 `market_data_adapter.py` ownership decision evidence | Accepted by PR `#359`; superseded for provider seam authorization by G2.207 |
| `docs/reports/quality/backend-data-quality-market-data-adapter-ownership-decision-2026-05-28.md` | G2.206 human-readable ownership decision report | Accepted by PR `#359`; superseded for provider seam authorization by G2.207 |
| `.planning/codebase/generated/data-quality-market-data-adapter-provider-authorization-2026-05-28.json` | G2.207 `market_data_adapter.py` provider seam authorization evidence | Accepted by PR `#360`; superseded for implementation evidence by G2.208 |
| `docs/reports/quality/backend-data-quality-market-data-adapter-provider-authorization-2026-05-28.md` | G2.207 human-readable provider seam authorization package | Accepted by PR `#360`; superseded for implementation evidence by G2.208 |
| `.planning/codebase/generated/data-quality-market-data-adapter-provider-implementation-2026-05-28.json` | G2.208 `market_data_adapter.py` provider seam implementation evidence | Accepted by PR `#361`; superseded for closeout / residual refresh by G2.209 |
| `docs/reports/quality/backend-data-quality-market-data-adapter-provider-implementation-2026-05-28.md` | G2.208 human-readable provider seam implementation report | Accepted by PR `#361`; superseded for closeout / residual refresh by G2.209 |
| `.planning/codebase/generated/data-quality-market-data-adapter-provider-closeout-refresh-2026-05-28.json` | G2.209 `market_data_adapter.py` provider seam closeout / residual refresh evidence | Accepted by PR `#362`; superseded for residual ownership by G2.210 |
| `docs/reports/quality/backend-data-quality-market-data-adapter-provider-closeout-refresh-2026-05-28.md` | G2.209 human-readable closeout / residual refresh report | Accepted by PR `#362`; superseded for residual ownership by G2.210 |
| `.planning/codebase/generated/data-quality-monitor-residual-ownership-decision-2026-05-28.json` | G2.210 data-quality monitor residual ownership decision evidence | Accepted by PR `#363`; superseded for singleton/backing API authorization by G2.211 |
| `docs/reports/quality/backend-data-quality-monitor-residual-ownership-decision-2026-05-28.md` | G2.210 human-readable residual ownership decision report | Accepted by PR `#363`; superseded for singleton/backing API authorization by G2.211 |
| `.planning/codebase/generated/data-quality-monitor-singleton-authorization-2026-05-28.json` | G2.211 data-quality monitor singleton/backing API authorization evidence | Accepted by PR `#364`; superseded for implementation evidence by G2.212 |
| `docs/reports/quality/backend-data-quality-monitor-singleton-authorization-2026-05-28.md` | G2.211 human-readable singleton/backing API authorization report | Accepted by PR `#364`; superseded for implementation evidence by G2.212 |
| `.planning/codebase/generated/data-quality-monitor-singleton-implementation-2026-05-28.json` | G2.212 data-quality monitor singleton/backing API implementation evidence | Accepted by PR `#365`; superseded for closeout / residual refresh by G2.213 |
| `docs/reports/quality/backend-data-quality-monitor-singleton-implementation-2026-05-28.md` | G2.212 human-readable singleton/backing API implementation report | Accepted by PR `#365`; superseded for closeout / residual refresh by G2.213 |
| `.planning/codebase/generated/data-quality-monitor-singleton-closeout-refresh-2026-05-28.json` | G2.213 data-quality monitor singleton/backing API closeout / residual refresh evidence | Accepted by PR `#366`; superseded for broader provider queue selection by G2.214 |
| `docs/reports/quality/backend-data-quality-monitor-singleton-closeout-refresh-2026-05-28.md` | G2.213 human-readable singleton/backing API closeout / residual refresh report | Accepted by PR `#366`; superseded for broader provider queue selection by G2.214 |
| `.planning/codebase/generated/nonstrategy-provider-queue-refresh-2026-05-28.json` | G2.214 non-Strategy provider queue refresh / next-candidate decision evidence | Accepted by PR `#367`; superseded for `get_data_service` ownership by G2.215 |
| `docs/reports/quality/backend-nonstrategy-provider-queue-refresh-2026-05-28.md` | G2.214 human-readable non-Strategy provider queue refresh report | Accepted by PR `#367`; superseded for `get_data_service` ownership by G2.215 |
| `.planning/codebase/generated/indicator-data-get-data-service-ownership-decision-2026-05-28.json` | G2.215 indicator/data `get_data_service` ownership decision evidence | Current for HEAD `a508fb263173b2014d307c4baec3b1eca0f42340`; review input until PR `#368` is accepted |
| `docs/reports/quality/backend-indicator-data-get-data-service-ownership-decision-2026-05-28.md` | G2.215 human-readable ownership decision report | Review input until PR `#368` is accepted |

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
| GitHub PR `#342` | `MERGED` | G2.189 stop-loss provider closeout / candidate refresh merged by commit `5565e2b0967958c406a4115dc840a9e90a0b2aab` |
| GitHub PR `#343` | `MERGED` | G2.190 data-quality / adapter decision merged by commit `7154ffbb067dcddc52d80f15342961b51234ac09` |
| GitHub PR `#344` | `MERGED` | G2.191 data-quality route provider authorization merged by commit `b899a173909d3818370dddbf35b039832266bd1d` |
| GitHub PR `#345` | `MERGED` | G2.192 data-quality route provider implementation merged by commit `2b0c3ce373fba38bacd62eff5436822527dccda1` |
| GitHub PR `#346` | `MERGED` | G2.193 data-quality route provider closeout / refresh merged by commit `ea659d52903a5e9884d396069526ea08f15109a6` |
| GitHub PR `#347` | `MERGED` | G2.194 data-quality adapter constructor seam design merged by commit `e30e16605df6aaa333989a7ac247bab3dcd0dd01` |
| GitHub PR `#348` | `MERGED` | G2.195 data-quality adapter_split constructor provider authorization merged by commit `fabd674e8a748cdd2c51a80eebb5ad20b52bc737` |
| GitHub PR `#349` | `MERGED` | G2.196 data-quality adapter_split constructor provider implementation merged by commit `e4245ebe54c5ad6d2aebf4802d165d59700c9eeb` |
| GitHub PR `#350` | `MERGED` | G2.197 data-quality monitor closeout / refresh merged by commit `3acf90c3ab17dbb3b47150a03f1cdee1c96dc8f1` |
| GitHub PR `#351` | `MERGED` | G2.198 residual adapter ownership decision merged by commit `a6b54ddfb24055552d634757f01dc03bd6ca6e62` |
| GitHub PR `#352` | `MERGED` | G2.199 canonical service adapter authorization merged by commit `41bef3787160ec3bf7b9b31220df9d99a3437474` |
| GitHub PR `#353` | `MERGED` | G2.200 canonical service adapter provider implementation merged by commit `cbd9b3a7ee730c72a63dbc7adb6490564c12c71e` |
| GitHub PR `#354` | `MERGED` | G2.201 canonical service adapter closeout / residual refresh merged by commit `e672f1523c30037202310278daf71488681d9a1f` |
| GitHub PR `#355` | `MERGED` | G2.202 legacy adapter ownership decision merged by commit `bf5d5ffba6bfc837c009a3d937cf0a9e6549883f` |
| GitHub PR `#356` | `MERGED` | G2.203 legacy adapter compatibility closure authorization merged by commit `142a2bf1c0c5f979cf9c32415d2f25832e7e62cd` |
| GitHub PR `#357` | `MERGED` | G2.204 legacy adapter compatibility wrapper implementation merged by commit `a621ba4ae66f581074a3b66539e296cbf0ced1b5` |
| GitHub PR `#358` | `MERGED` | G2.205 legacy adapter wrapper closeout / residual refresh merged by commit `44909f5d048700115da6a9eb9345957b8af3d077` |
| GitHub PR `#359` | `MERGED` | G2.206 `market_data_adapter.py` ownership decision merged by commit `ded789ee5d49d6ddcce5d8a69af1901a8481d1f0` |
| GitHub PR `#360` | `MERGED` | G2.207 `market_data_adapter.py` provider seam authorization merged by commit `b4b34375eef0186b81be9a24491328dab72c2e21` |
| `origin/wip/root-dirty-20260403` | `b4b34375eef0186b81be9a24491328dab72c2e21` | Base used for this implementation branch |
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
