# Steward Tree Completed Ledger

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: summarized completed ledger
- Prepared at: `2026-05-31T21:34:35+08:00`
- Base HEAD checked: `16df80c30eb4fceec78a13630e40167f0e4037ca`

Boundary note: this ledger summarizes accepted or reviewed work. Use the
archived full tree for exhaustive older G2 rows and the relevant PR/report for
exact verification output.

## Milestone Summary

| Range / lane | Completion value | Current handling |
|---|---|---|
| Route/OpenAPI and control-plane governance | Established route table, OpenAPI exposure, health/probe taxonomy, and consumer-contract evidence as first-class governance facts | Continue through route/OpenAPI track, not ad hoc route edits |
| Core split / wrapper governance | Completed early low-risk wrapper migration and held Batch 2 behind explicit reconciliation gates | Keep Batch 2 blocked until the shared evidence and Task 3.2 gates are explicit |
| Error contract migration | Canonical API error path became the active route error contract after P3-C5 completion evidence | Treat as closed unless current HEAD contradicts completion evidence |
| Service lifecycle DI conveyor | Proven candidate classification, authorization, implementation, closeout, and residual refresh pattern across multiple services; G2.274 accepted/merged by PR `#427` at `16df80c30` | Continue with G2.275 risk `get_monitoring_db` route-provider implementation review, then G2.276 closeout / residual refresh if accepted |
| Strategy route/provider residuals | Route provider, backtest resolver, adapter wrapper, and canonical adapter provider decisions narrowed residual `get_strategy_service` surfaces | G2.178 merged by PR `#331`; G2.180 merged by PR `#333`; G2.181 merged by PR `#334`; G2.182 merged by PR `#335`; G2.183 merged by PR `#336` and closes the current Strategy getter residual track with retained residuals |
| Non-Strategy provider governance queue | Next-candidate selection moved remaining provider-shaped residuals out of direct implementation candidacy | G2.184-G2.274 have progressed through PR `#337`-`#427`; current review target is G2.275 risk `get_monitoring_db` provider implementation in future PR `#428` |
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

## Closeout Rule

A completed row should not be reopened by the steward tree alone. Reopen only
when one of these exists:

- current HEAD verification contradicts the closeout evidence
- a new PR or issue introduces a conflicting implementation
- an OpenSpec task explicitly reopens the capability
- the human maintainer approves a new decision package
