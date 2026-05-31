# Steward Tree Completed Ledger

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: summarized completed ledger
- Prepared at: `2026-05-31T12:27:16+08:00`
- Base HEAD checked: `772e4a3ac8e05edaa243d660d67c7e5df18158f9`

Boundary note: this ledger summarizes accepted or reviewed work. Use the
archived full tree for exhaustive older G2 rows and the relevant PR/report for
exact verification output.

## Milestone Summary

| Range / lane | Completion value | Current handling |
|---|---|---|
| Route/OpenAPI and control-plane governance | Established route table, OpenAPI exposure, health/probe taxonomy, and consumer-contract evidence as first-class governance facts | Continue through route/OpenAPI track, not ad hoc route edits |
| Core split / wrapper governance | Completed early low-risk wrapper migration and held Batch 2 behind explicit reconciliation gates | Keep Batch 2 blocked until the shared evidence and Task 3.2 gates are explicit |
| Error contract migration | Canonical API error path became the active route error contract after P3-C5 completion evidence | Treat as closed unless current HEAD contradicts completion evidence |
| Service lifecycle DI conveyor | Proven candidate classification, authorization, implementation, closeout, and residual refresh pattern across multiple services; G2.267 accepted/merged by PR `#420` at `772e4a3ac8e` | Continue with no-source G2.268 authorization before any source lane |
| Strategy route/provider residuals | Route provider, backtest resolver, adapter wrapper, and canonical adapter provider decisions narrowed residual `get_strategy_service` surfaces | G2.178 merged by PR `#331`; G2.180 merged by PR `#333`; G2.181 merged by PR `#334`; G2.182 merged by PR `#335`; G2.183 merged by PR `#336` and closes the current Strategy getter residual track with retained residuals |
| Non-Strategy provider governance queue | Next-candidate selection moved remaining provider-shaped residuals out of direct implementation candidacy | G2.184 merged by PR `#337`; G2.185 merged by PR `#338`; G2.186 merged by PR `#339`; G2.187 merged by PR `#340`; G2.188 merged by PR `#341`; G2.189 merged by PR `#342`; G2.190 merged by PR `#343`; G2.191 merged by PR `#344`; G2.192 merged by PR `#345`; G2.193 merged by PR `#346`; G2.194 merged by PR `#347`; G2.195 merged by PR `#348`; G2.196 merged by PR `#349`; G2.197 merged by PR `#350`; G2.198 merged by PR `#351`; G2.199 merged by PR `#352`; G2.200 merged by PR `#353`; G2.201 merged by PR `#354`; G2.202 merged by PR `#355`; G2.203 merged by PR `#356`; G2.204 merged by PR `#357`; G2.205 merged by PR `#358`; G2.206 merged by PR `#359`; G2.207 merged by PR `#360`; G2.208 merged by PR `#361`; G2.209 merged by PR `#362`; G2.210 merged by PR `#363`; G2.211 merged by PR `#364`; G2.212 merged by PR `#365`; G2.213 merged by PR `#366`; G2.214 merged by PR `#367`; G2.215 merged by PR `#368`; G2.216 merged by PR `#369`; G2.217 merged by PR `#370`; G2.218 merged by PR `#371`; G2.219 merged by PR `#372`; G2.220 merged by PR `#373`; G2.221 merged by PR `#374`; G2.222 merged by PR `#375`; G2.223 merged by PR `#376`; G2.224 merged by PR `#377`; G2.225 merged by PR `#378`; G2.226 merged by PR `#379`; G2.227 merged by PR `#380`; G2.228 merged by PR `#381`; G2.229 merged by PR `#382`; G2.230 merged by PR `#383`; G2.231 merged by PR `#384`; G2.232 merged by PR `#385`; G2.233 merged by PR `#386`; G2.234 merged by PR `#387`; G2.235 merged by PR `#388`; G2.236 merged by PR `#389`; G2.237 merged by PR `#390`; G2.238 merged by PR `#391`; G2.239 merged by PR `#392`; G2.240 merged by PR `#393`; G2.241 merged by PR `#394`; G2.242 merged by PR `#395`; G2.243 merged by PR `#396`; G2.244 merged by PR `#397`; G2.245 merged by PR `#398`; G2.246 merged by PR `#399`; G2.247 merged by PR `#400`; G2.248 merged by PR `#401`; G2.249 merged by PR `#402`; G2.250 merged by PR `#403`; G2.251 merged by PR `#404`; G2.252 merged by PR `#405`; G2.253 merged by PR `#406`; G2.254 merged by PR `#407`; G2.255 merged by PR `#408`; G2.256 merged by PR `#409`; G2.257 merged by PR `#410`; G2.258 merged by PR `#411`; G2.259 merged by PR `#412`; G2.260 merged by PR `#413`; G2.261 merged by PR `#414`; G2.262 merged by PR `#415`; G2.263 merged by PR `#416`; G2.264 merged by PR `#417`; G2.265 is the active stale signal statistics contract cleanup implementation |
| Steward-tree practice learning | Retrospective and practice guide captured the need for machine-readable state and split documents | This branch implements the split and JSON index |

## Recent Closeouts

| Item | Accepted evidence | Follow-up |
|---|---|---|
| G2.265 signal statistics stale contract cleanup | PR `#418` merged at `2b53352d6869f66147ce3892b1b0a7174ba064b4`; targeted tests `2/2`; runtime OpenAPI target paths `0` | G2.266 records closeout and selects `G2.267 no-source monitoring/signal residual provider classification refresh` |
| G2.266 signal statistics dormant contract closeout | PR `#419` merged at `eec68bb47a4ee98508480ef0ac2cdd3716e04b05`; stale contract branch closed | G2.267 classifies monitoring/signal residuals and selects G2.268 no-source authorization |
| G2.267 monitoring/signal residual classification | PR `#420` merged at `772e4a3ac8e05edaa243d660d67c7e5df18158f9`; active portfolio optimizer route-body candidate selected | G2.268 authorizes a future path-limited portfolio optimizer provider implementation lane |

## Closeout Rule

A completed row should not be reopened by the steward tree alone. Reopen only
when one of these exists:

- current HEAD verification contradicts the closeout evidence
- a new PR or issue introduces a conflicting implementation
- an OpenSpec task explicitly reopens the capability
- the human maintainer approves a new decision package
