# Steward Tree Completed Ledger

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: summarized completed ledger
- Prepared at: `2026-06-01T19:28:21+08:00`
- Base HEAD checked: `13a81aec15fc8e98e7e4e927abe6d27e3e16f93d`

Boundary note: this ledger summarizes accepted or reviewed work. Use the
archived full tree for exhaustive older G2 rows and the relevant PR/report for
exact verification output.

## Milestone Summary

| Range / lane | Completion value | Current handling |
|---|---|---|
| Route/OpenAPI and control-plane governance | Established route table, OpenAPI exposure, health/probe taxonomy, and consumer-contract evidence as first-class governance facts | Continue through route/OpenAPI track, not ad hoc route edits |
| Core split / wrapper governance | Completed early low-risk wrapper migration and held Batch 2 behind explicit reconciliation gates | Keep Batch 2 blocked until the shared evidence and Task 3.2 gates are explicit |
| Error contract migration | Canonical API error path became the active route error contract after P3-C5 completion evidence | Treat as closed unless current HEAD contradicts completion evidence |
| Service lifecycle DI conveyor | Proven candidate classification, authorization, implementation, closeout, and residual refresh pattern across multiple services; G2.301 accepted/merged by PR `#454` at `13a81aec` | Continue with G2.302 admin optimization provider authorization; do not auto-merge because it authorizes future source/test edits under the CRITICAL shared-helper-family target |
| Strategy route/provider residuals | Route provider, backtest resolver, adapter wrapper, and canonical adapter provider decisions narrowed residual `get_strategy_service` surfaces | G2.178 merged by PR `#331`; G2.180 merged by PR `#333`; G2.181 merged by PR `#334`; G2.182 merged by PR `#335`; G2.183 merged by PR `#336` and closes the current Strategy getter residual track with retained residuals |
| Non-Strategy provider governance queue | Next-candidate selection moved remaining provider-shaped residuals out of direct implementation candidacy | G2.184-G2.301 have progressed through PR `#337`-`#454`; current review target is G2.302 admin optimization provider authorization in future PR `#455` |
| Steward-tree practice learning | Retrospective and practice guide captured the need for machine-readable state and split documents | This branch implements the split and JSON index |

## Recent Closeouts

| Item | Accepted evidence | Follow-up |
|---|---|---|
| G2.302 admin optimization PostgreSQL session provider authorization | Generated authorization evidence records PR `#454` merged at `13a81aec15fc8e98e7e4e927abe6d27e3e16f93d`, future G2.303 scope limited to `optimization.py` and focused optimization tests, route/OpenAPI `548/500/0`, focused test `5/5`, and CRITICAL shared helper-family risk | G2.303 may only start as path-limited source implementation after PR `#455` human acceptance |
| G2.301 admin optimization PostgreSQL session ownership / provider-shape decision | PR `#454` merged at `13a81aec15fc8e98e7e4e927abe6d27e3e16f93d`; generated decision evidence records admin optimization direct calls `2`, four affected route handlers, focused test `5/5`, route/OpenAPI `548/500/0`, and CRITICAL shared helper-family risk | Superseded by G2.302 no-source provider authorization |
| G2.300 market stock list provider closeout / residual refresh | PR `#453` merged at `d407acdd207271274aeb6614afdedbf139f640ae`; generated closeout evidence records market stock list direct calls `0`, provider binding `1`, focused test `5/5`, route/OpenAPI `548/500/0`, and remaining residuals auth `4` / admin optimization `2` | Superseded by G2.301 admin optimization ownership / provider-shape decision |
| G2.299 market stock list `get_postgresql_session` provider implementation | PR `#452` merged at `3d89c7e64a93c7f2ca074dc502762ad203f15bdc`; target route `GET /api/v1/market/stocks`, direct helper calls `0`, provider binding `1`, focused test `5/5`, and route/OpenAPI `548/500/0` | Superseded by G2.300 closeout / residual refresh |
| G2.298 market stock list `get_postgresql_session` provider authorization | PR `#451` merged at `79a4fe5ae9f763e3e836b76c051bddbed270a930`; authorization limited G2.299 to `market_data_request.py` and focused market stock list tests | Superseded by G2.299 path-limited implementation review |
| G2.297 core database `get_postgresql_session` route-domain decision | PR `#450` merged at `555ff35e0c82e172b4312c59bc67d3674bd6f0ab`; remaining direct calls split as auth `4`, admin optimization `2`, market stock list `1`, and runtime/OpenAPI `548/500/0` | G2.298 authorizes only the market stock list route-domain candidate; auth and admin optimization remain separate future tracks |
| G2.296 admin audit provider closeout / residual refresh | PR `#449` merged at `030545a24b4a8c9a4df36d2f126eb4597685e0c0`; admin audit direct route-body calls `0`, provider bindings `3`, and runtime/OpenAPI `548/500/0` | G2.297 splits remaining core-database helper residuals by route domain |
| G2.295 admin audit `database_factory.get_postgresql_session` provider implementation | PR `#448` merged at `48cf7e12637341451d8d77370306774df9c48729`; moved 3 admin audit handlers to provider wiring, retained cleanup semantics, and kept route/OpenAPI stable | G2.296 records closeout and refreshes remaining core-database helper residuals |
| G2.294 admin audit `database_factory.get_postgresql_session` provider authorization | PR `#447` merged at `a31fd3ede177d5851c2394b8cea2fe42188a4021`; authorized only a future path-limited admin audit provider implementation after review | G2.295 implements the authorized provider wiring and must stop at PR `#448` review |
| G2.293 `get_postgresql_session` ownership / route-provider decision | PR `#446` merged at `a62d5e3fa4e9efbbe388e4bd317ae0cfae371319`; helper family split across auth, admin audit, admin optimization, and market route modules; shared `app.core.database.get_postgresql_session` marked CRITICAL impact | G2.294 authorizes only the bounded admin audit `database_factory` subgroup and must stop at PR `#447` review |
| G2.292 data_source_registry get_manager provider closeout | PR `#445` merged at `05cdf04f646d844c11e90e7c453ed4f985c8d382`; direct route-body `get_manager()` calls `0`, provider backing `1`, provider bindings `7`, runtime/OpenAPI `548/500/0` | G2.293 classifies `get_postgresql_session` ownership and splits future provider work by route domain/helper origin |
| G2.291 data_source_registry get_manager provider implementation | PR `#444` merged at `3d161e90547720f4ce95111ea511d3f8dc3174dc`; direct route-body `get_manager()` calls `0`, provider bindings `7`, focused regression `3/3`, runtime/OpenAPI `548/500/0` | G2.292 closes the provider lane and selects only a no-source `get_postgresql_session` ownership decision |
| G2.290 data_source_registry get_manager provider authorization | PR `#443` merged at `e517163385e96a6c7115e14b77fb89819b4cead4`; authorized only a path-limited G2.291 implementation lane | Superseded by the accepted/merged G2.291 provider implementation and G2.292 closeout review |
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
| G2.286 governance_dashboard get_postgres_connection provider authorization | PR `#439` merged at `e7c78892e1928d86fabecbe4135e7ce68fd0f01e`; path-limited `governance_dashboard.py` implementation lane authorized after human review | G2.287 implements only the authorized route-local provider seam and must stop at PR `#440` review |
| G2.287 governance_dashboard get_postgres_connection provider implementation | PR `#440` merged at `67ef9b9d8f9dd420de80995f624fa54e41493415`; direct route-body calls are `0`, manual close calls are `0`, provider bindings are `5`, and route/OpenAPI stayed `548/500/0` | G2.288 records closeout, refreshes residual candidates, and selects G2.289 no-source data_source_registry ownership decision |
| G2.288 governance_dashboard get_postgres_connection provider closeout / residual refresh | PR `#441` merged at `75ce550ceaf9f77b7659193b9cbd3c9ab2181c37`; governance dashboard provider lane remains closed and route/OpenAPI stayed `548/500/0` | G2.289 decides `data_source_registry.get_manager` ownership but must stop at PR `#442` review because GitNexus risk is MEDIUM and one process is affected |
| G2.289 data_source_registry get_manager ownership decision | PR `#442` merged at `1f0a909355f5db9002cfc2d0fcbba21e366dc0bf`; `get_manager` classified as bounded active route helper with `7` direct route-body callers and route/OpenAPI `548/500/0` | G2.290 authorizes only a future path-limited provider implementation and must stop at PR `#443` review |

## Closeout Rule

A completed row should not be reopened by the steward tree alone. Reopen only
when one of these exists:

- current HEAD verification contradicts the closeout evidence
- a new PR or issue introduces a conflicting implementation
- an OpenSpec task explicitly reopens the capability
- the human maintainer approves a new decision package

- G2.302 admin optimization PostgreSQL session provider authorization accepted/merged by PR `#455` at `4af141da7411d30b31b972ace51d104ae28606ed`; it is superseded by the G2.303 source implementation review gate.
