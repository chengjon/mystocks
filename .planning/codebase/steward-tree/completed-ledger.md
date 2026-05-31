# Steward Tree Completed Ledger

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: summarized completed ledger
- Prepared at: `2026-06-01T07:48:42+08:00`
- Base HEAD checked: `bdfdeb353f725f9e875ab50ee4e8ed22902a5818`

Boundary note: this ledger summarizes accepted or reviewed work. Use the
archived full tree for exhaustive older G2 rows and the relevant PR/report for
exact verification output.

## Milestone Summary

| Range / lane | Completion value | Current handling |
|---|---|---|
| Route/OpenAPI and control-plane governance | Established route table, OpenAPI exposure, health/probe taxonomy, and consumer-contract evidence as first-class governance facts | Continue through route/OpenAPI track, not ad hoc route edits |
| Core split / wrapper governance | Completed early low-risk wrapper migration and held Batch 2 behind explicit reconciliation gates | Keep Batch 2 blocked until the shared evidence and Task 3.2 gates are explicit |
| Error contract migration | Canonical API error path became the active route error contract after P3-C5 completion evidence | Treat as closed unless current HEAD contradicts completion evidence |
| Service lifecycle DI conveyor | Proven candidate classification, authorization, implementation, closeout, and residual refresh pattern across multiple services; G2.285 accepted/merged by PR `#438` at `bdfdeb35` | Continue with G2.286 `governance_dashboard.get_postgres_connection` provider authorization; no source implementation is authorized until that package is human accepted |
| Strategy route/provider residuals | Route provider, backtest resolver, adapter wrapper, and canonical adapter provider decisions narrowed residual `get_strategy_service` surfaces | G2.178 merged by PR `#331`; G2.180 merged by PR `#333`; G2.181 merged by PR `#334`; G2.182 merged by PR `#335`; G2.183 merged by PR `#336` and closes the current Strategy getter residual track with retained residuals |
| Non-Strategy provider governance queue | Next-candidate selection moved remaining provider-shaped residuals out of direct implementation candidacy | G2.184-G2.285 have progressed through PR `#337`-`#438`; current review target is G2.286 authorization in future PR `#439` |
| Steward-tree practice learning | Retrospective and practice guide captured the need for machine-readable state and split documents | This branch implements the split and JSON index |

## Recent Closeouts

| Item | Accepted evidence | Follow-up |
|---|---|---|
| G2.265 signal statistics stale contract cleanup | PR `#418` merged at `2b53352d6869f66147ce3892b1b0a7174ba064b4`; targeted tests `2/2`; runtime OpenAPI target paths `0` | G2.266 records closeout and selects `G2.267 no-source monitoring/signal residual provider classification refresh` |
| G2.266 signal statistics dormant contract closeout | PR `#419` merged at `eec68bb47a4ee98508480ef0ac2cdd3716e04b05`; stale contract branch closed | G2.267 classifies monitoring/signal residuals and selects G2.268 no-source authorization |
| G2.267 monitoring/signal residual classification | PR `#420` merged at `772e4a3ac8e05edaa243d660d67c7e5df18158f9`; active portfolio optimizer route-body candidate selected | G2.268 authorizes a future path-limited portfolio optimizer provider implementation lane |
| G2.268 monitoring portfolio optimizer provider authorization | PR `#421` merged at `1cb885e8267d76e47e0d08977002a80fafb56092`; path-limited implementation lane authorized | G2.269 implements the provider injection, then G2.270 should close out and refresh residuals |
| G2.269 monitoring portfolio optimizer provider implementation | PR `#422` merged at `7ed8f8e352f29c9c48bc4a45ea77661b08de89da`; direct route-body `get_portfolio_optimizer()` calls are `0`; focused tests `20/20`; runtime OpenAPI `548/500`, duplicate operation IDs `0` | G2.270 records closeout and selects the next no-source control-plane ownership decision |
| G2.270 monitoring portfolio optimizer provider closeout | PR `#423` merged at `5b3ffd1f114b612810e96c463c651befeb005222`; remaining active control-plane residual selected | G2.271 classifies pool monitoring ownership without source edits |
| G2.271 pool monitoring control-plane ownership decision | PR `#424` merged at `8e0fcd6738c4e3a889b4851d058f8121f32b8ce8`; pool monitoring deferred to route/OpenAPI/control-plane ownership | G2.272 refreshes service lifecycle residual candidates |
| G2.272 service lifecycle residual candidate refresh | PR `#425` merged at `bcf28e4668391f91ea97ee252b4da4eea64faf74`; `get_monitoring_db` selected only for no-source ownership decision | G2.273 disambiguates risk, strategy, and utility same-name helper ownership |
| G2.273 get_monitoring_db ownership decision | PR `#426` merged at `0de77f3d05b1b6242515f2b86fce03c0eba37aaa`; ownership split confirmed across risk, strategy, and utility helpers | G2.274 authorizes only the risk surface before any implementation |
| G2.274 risk get_monitoring_db provider authorization | PR `#427` merged at `16df80c30eb4fceec78a13630e40167f0e4037ca`; path-limited risk source lane authorized | G2.275 implements only the three authorized risk handlers and focused provider test |
| G2.275 risk get_monitoring_db provider implementation | PR `#428` merged at `daa4f22a557b054ab76042d4990b6e91d9faa7a7`; direct risk route-body calls are `0` and route/OpenAPI contracts stayed stable | G2.276 records closeout and selects the strategy-management residual for a no-source authorization gate |
| G2.276 risk get_monitoring_db provider closeout / residual refresh | PR `#429` merged at `f48ede2ce2202318efa3411fe22fb83a8d4d920b`; risk lane closed and strategy-management residual selected | G2.277 authorizes only the strategy-management route/helper surface before any G2.278 implementation |
| G2.277 strategy get_monitoring_db provider authorization | PR `#430` merged at `2d1d2c28fe59bd7b98f63a41b9a0ff4c343d0441`; path-limited strategy source lane authorized | G2.278 implements only the two authorized strategy source files and focused strategy test |
| G2.278 strategy get_monitoring_db provider implementation | PR `#431` merged at `c5496cab0a4213f74636af1c48772dc96c90bd1b`; direct strategy target calls are `0`, dependency parameters are `6`, route/OpenAPI contracts stayed stable | G2.279 records closeout, confirms risk route-body calls remain closed, and selects the next no-source residual candidate refresh |
| G2.279 strategy get_monitoring_db provider closeout / residual refresh | PR `#432` merged at `fcead56344110e33041319271c122e71d2b763a0`; strategy/risk direct calls remain closed and utility helper remains deferred | G2.280 refreshes residual candidates before any new authorization or source lane |
| G2.280 service lifecycle residual candidate refresh after get_monitoring_db | PR `#433` merged at `1707284bceeef8992641290d86790c1699975f5a`; `371` files scanned, `31` active interesting candidates recorded, and `get_lineage_tracker` selected | G2.281 decides data_lineage ownership but must stop at review because GitNexus risk is MEDIUM |
| G2.281 data_lineage get_lineage_tracker ownership decision | PR `#434` merged at `b8ba6ca75c573913d7b10553620e5d308c0d13f3`; `get_lineage_tracker` classified as bounded active route helper with five direct callers and MEDIUM GitNexus risk | G2.282 authorizes only a future path-limited `data_lineage.py` provider implementation and must stop at PR `#435` review |
| G2.282 data_lineage get_lineage_tracker provider authorization | PR `#435` merged at `891593d2dc4896f909333033a0b454529b9be38c`; path-limited `data_lineage.py` implementation lane authorized after human review | G2.283 implements only the authorized route-local provider seam and must stop at PR `#436` review |
| G2.283 data_lineage get_lineage_tracker provider implementation | PR `#436` merged at `511e9d091bc2b29777c522c595a9f1454f50b973`; direct route-body `get_lineage_tracker()` calls are `0`, dependency bindings are `5`, focused tests and route/OpenAPI smoke passed | G2.284 records closeout, refreshes residual candidates, and selects the next no-source ownership decision |
| G2.284 data_lineage get_lineage_tracker provider closeout / residual refresh | PR `#437` merged at `d34774837a0582f0e33d47425bb017b44e5aacd9`; lineage provider lane closed and runtime/OpenAPI remains `548/500/0` | G2.285 classifies `governance_dashboard.get_postgres_connection` ownership and must stop at PR `#438` review because GitNexus risk is MEDIUM |
| G2.285 governance_dashboard get_postgres_connection ownership decision | PR `#438` merged at `bdfdeb353f725f9e875ab50ee4e8ed22902a5818`; helper classified as a bounded active control-plane route helper with five direct route-body callers and MEDIUM GitNexus risk | G2.286 authorizes only a future path-limited provider implementation and must stop at PR `#439` review |

## Closeout Rule

A completed row should not be reopened by the steward tree alone. Reopen only
when one of these exists:

- current HEAD verification contradicts the closeout evidence
- a new PR or issue introduces a conflicting implementation
- an OpenSpec task explicitly reopens the capability
- the human maintainer approves a new decision package
