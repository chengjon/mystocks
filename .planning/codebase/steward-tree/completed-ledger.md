# Steward Tree Completed Ledger

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: summarized completed ledger
- Prepared at: `2026-05-28T11:53:30+08:00`
- Base HEAD checked: `e672f1523c30037202310278daf71488681d9a1f`

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
| Non-Strategy provider governance queue | Next-candidate selection moved remaining provider-shaped residuals out of direct implementation candidacy | G2.184 merged by PR `#337`; G2.185 merged by PR `#338`; G2.186 merged by PR `#339`; G2.187 merged by PR `#340`; G2.188 merged by PR `#341`; G2.189 merged by PR `#342`; G2.190 merged by PR `#343`; G2.191 merged by PR `#344`; G2.192 merged by PR `#345`; G2.193 merged by PR `#346`; G2.194 merged by PR `#347`; G2.195 merged by PR `#348`; G2.196 merged by PR `#349`; G2.197 merged by PR `#350`; G2.198 merged by PR `#351`; G2.199 merged by PR `#352`; G2.200 merged by PR `#353`; G2.201 merged by PR `#354`; G2.202 is the active decision package selecting G2.203 authorization-only legacy adapter compatibility closure |
| Steward-tree practice learning | Retrospective and practice guide captured the need for machine-readable state and split documents | This branch implements the split and JSON index |

## Closeout Rule

A completed row should not be reopened by the steward tree alone. Reopen only
when one of these exists:

- current HEAD verification contradicts the closeout evidence
- a new PR or issue introduces a conflicting implementation
- an OpenSpec task explicitly reopens the capability
- the human maintainer approves a new decision package
