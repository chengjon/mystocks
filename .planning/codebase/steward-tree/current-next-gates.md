# Steward Tree Current Next Gates

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active gate register
- Prepared at: `2026-05-28T01:04:38+08:00`
- Base HEAD checked: `7154ffbb067dcddc52d80f15342961b51234ac09`

Boundary note: this file records gates. It does not authorize code changes,
issue label changes, OpenSpec proposal creation, PM2 commands, or PR merges.

## Gate Register

| Priority | Gate | Owner lane | Status | Next action |
|---|---|---|---|---|
| P0 | Review G2.191 data-quality route provider authorization | G/#79 service lifecycle DI | PR `#343` merged at `7154ffbb067dcddc52d80f15342961b51234ac09`; G2.191 authorizes only a future route-file implementation lane and keeps current PR source authority at none | If accepted, start G2.192 data-quality route provider implementation lane |
| P0 | Preserve G2.190 data-quality / adapter cross-cutting decision | G/#79 service lifecycle DI | PR `#343` merged; `get_data_quality_monitor` is `CRITICAL` with 20 direct callers across route, adapter, legacy adapter, and wrapper surfaces | Do not batch route, adapter constructor, legacy adapter, and singleton wrapper migration together |
| P0 | Preserve G2.189 risk stop-loss provider closeout / candidate refresh | G/#79 service lifecycle DI | PR `#342` merged; stop-loss pair is closed for route-body provider migration and retained as provider backing getters | Do not reopen stop-loss or start data-quality source implementation from G2.189 |
| P0 | Preserve G2.188 risk stop-loss route service provider implementation | G/#79 service lifecycle DI | PR `#341` merged; G2.188 closed the stop-loss route-body provider migration while retaining src-level stop-loss provider backing getters | Do not delete retained getters or expand into alerts, legacy `app.api.risk_management`, or other risk route migrations |
| P0 | Preserve G2.187 risk stop-loss route service provider authorization | G/#79 service lifecycle DI | PR `#340` merged; G2.187 authorized only `web/backend/app/api/risk/stop_loss.py` plus focused tests for G2.188 | Do not expand G2.188 into alerts resolver, legacy `app.api.risk_management`, or other risk route migrations |
| P0 | Preserve G2.186 remaining getter inventory refresh | G/#79 service lifecycle DI | PR `#339` merged; G2.186 refreshed remaining direct getter inventory and selected stop-loss route provider authorization as the next narrow gate | Do not start a backend source lane from G2.186 |
| P0 | Preserve G2.185 provider governance decision | G/#79 service lifecycle DI + Route/OpenAPI governance | PR `#338` merged; provider residuals are retained active route contracts and excluded from direct implementation-candidate counts | Do not start a backend source lane from G2.185 |
| P0 | Preserve G2.184 next non-Strategy candidate decision | G/#79 service lifecycle DI | PR `#337` merged; G2.184 selected route dependency/provider governance as the next decision target | Do not start a backend source lane from G2.184 |
| P0 | Preserve G2.183 Strategy getter residual closeout | G/#79 service lifecycle DI | PR `#336` merged; remaining Strategy getter residuals classified as retained and tested | Do not reopen generic Strategy getter implementation unless current HEAD contradicts G2.183 evidence |
| P0 | Keep steward split structure active | CODEBASE-MAP steward governance | PR `#332` merged at `750fb7c797ff95f27152439ed988a7115252129e` | Future steward updates must use split files and `steward-index.json`, not the archived single-file tree |
| P1 | Preserve implementation authorization boundary | All lanes | Active | Every source lane still needs its own authorization packet |
| P1 | Keep Core Batch 2 blocked | Core split / compatibility wrappers | Blocked | Resolve Task 3.2 and shared evidence gate disposition before selecting Batch 2 |
| P1 | Use route/OpenAPI governance for route changes | Route/OpenAPI lane | Active | Route source changes require route ownership, OpenAPI exposure, and consumer-contract evidence |
| P2 | Keep Graphiti digest-only | Memory/governance | Active | Record accepted milestones after PR or decision package exists; do not use Graphiti as repo truth |
| P2 | Maintain machine-readable index | Steward governance | New | Update `steward-index.json` whenever an active gate changes |

## Immediate Review Questions

- Does G2.191 clearly authorize only a future G2.192 implementation lane, not source edits in PR `#344`?
- Is the future G2.192 scope limited to `web/backend/app/api/data_quality.py` and focused route/provider tests?
- Are adapter constructor migration, legacy adapter compatibility, and singleton wrapper deletion explicitly forbidden?
- Does G2.191 require OpenAPI dependency leak and `app.main` smoke with a valid runtime environment before G2.192 merge?
- Are implementation, authorization, decision, and evidence lanes still distinct?
