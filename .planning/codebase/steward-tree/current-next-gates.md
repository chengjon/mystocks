# Steward Tree Current Next Gates

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active gate register
- Prepared at: `2026-05-27T21:33:48+08:00`
- Base HEAD checked: `b54e7d043720a8c8bc67ad96f4f7eaad0b23ceba`

Boundary note: this file records gates. It does not authorize code changes,
issue label changes, OpenSpec proposal creation, PM2 commands, or PR merges.

## Gate Register

| Priority | Gate | Owner lane | Status | Next action |
|---|---|---|---|---|
| P0 | Review G2.185 route dependency/provider governance residual decision | G/#79 service lifecycle DI + Route/OpenAPI governance | PR `#337` merged at `b54e7d043720a8c8bc67ad96f4f7eaad0b23ceba`; G2.185 classifies provider residuals as retained active contracts and opens no source lane | If accepted, start G2.186 service lifecycle remaining getter inventory refresh after provider governance |
| P0 | Preserve G2.184 next non-Strategy candidate decision | G/#79 service lifecycle DI | PR `#337` merged; G2.184 selected route dependency/provider governance as the next decision target | Do not start a backend source lane from G2.184 |
| P0 | Preserve G2.183 Strategy getter residual closeout | G/#79 service lifecycle DI | PR `#336` merged; remaining Strategy getter residuals classified as retained and tested | Do not reopen generic Strategy getter implementation unless current HEAD contradicts G2.183 evidence |
| P0 | Keep steward split structure active | CODEBASE-MAP steward governance | PR `#332` merged at `750fb7c797ff95f27152439ed988a7115252129e` | Future steward updates must use split files and `steward-index.json`, not the archived single-file tree |
| P1 | Preserve implementation authorization boundary | All lanes | Active | Every source lane still needs its own authorization packet |
| P1 | Keep Core Batch 2 blocked | Core split / compatibility wrappers | Blocked | Resolve Task 3.2 and shared evidence gate disposition before selecting Batch 2 |
| P1 | Use route/OpenAPI governance for route changes | Route/OpenAPI lane | Active | Route source changes require route ownership, OpenAPI exposure, and consumer-contract evidence |
| P2 | Keep Graphiti digest-only | Memory/governance | Active | Record accepted milestones after PR or decision package exists; do not use Graphiti as repo truth |
| P2 | Maintain machine-readable index | Steward governance | New | Update `steward-index.json` whenever an active gate changes |

## Immediate Review Questions

- Does the split preserve the full historical steward tree in archive?
- Is the root entrypoint short enough to serve as a daily navigation file?
- Does `steward-index.json` include enough fields for automated guards?
- Does G2.185 correctly classify active FastAPI providers as route contracts rather than deletion candidates?
- Is G2.186 the right next gate for remaining getter inventory refresh after provider governance?
- Are implementation, authorization, decision, and evidence lanes still distinct?
