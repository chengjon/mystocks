# Steward Tree Completed Ledger

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: summarized completed ledger
- Prepared at: `2026-05-27T22:30:42+08:00`
- Base HEAD checked: `a63a6cb9a277195905b046cd31777d95160ee2c6`

Boundary note: this ledger summarizes accepted or reviewed work. Use the
archived full tree for exhaustive older G2 rows and the relevant PR/report for
exact verification output.

## Milestone Summary

| Range / lane | Completion value | Current handling |
|---|---|---|
| Route/OpenAPI and control-plane governance | Established route table, OpenAPI exposure, health/probe taxonomy, and consumer-contract evidence as first-class governance facts | Continue through route/OpenAPI track, not ad hoc route edits |
| Core split / wrapper governance | Completed early low-risk wrapper migration and held Batch 2 behind explicit reconciliation gates | Keep Batch 2 blocked until the shared evidence and Task 3.2 gates are explicit |
| Error contract migration | Canonical API error path became the active route error contract after P3-C5 completion evidence | Treat as closed unless current HEAD contradicts completion evidence |
| Service lifecycle DI conveyor | Proven candidate classification, authorization, implementation, and closeout pattern across multiple services | Continue with path-limited source lanes only after authorization |
| Strategy route/provider residuals | Route provider, backtest resolver, adapter wrapper, and canonical adapter provider decisions narrowed residual `get_strategy_service` surfaces | G2.178 merged by PR `#331`; G2.180 merged by PR `#333`; G2.181 merged by PR `#334`; G2.182 merged by PR `#335`; G2.183 merged by PR `#336` and closes the current Strategy getter residual track with retained residuals |
| Non-Strategy provider governance queue | Next-candidate selection moved remaining provider-shaped residuals out of direct implementation candidacy | G2.184 merged by PR `#337`; G2.185 merged by PR `#338`; G2.186 merged by PR `#339`; G2.187 defines the stop-loss route provider authorization package for review |
| Steward-tree practice learning | Retrospective and practice guide captured the need for machine-readable state and split documents | This branch implements the split and JSON index |

## Closeout Rule

A completed row should not be reopened by the steward tree alone. Reopen only
when one of these exists:

- current HEAD verification contradicts the closeout evidence
- a new PR or issue introduces a conflicting implementation
- an OpenSpec task explicitly reopens the capability
- the human maintainer approves a new decision package
