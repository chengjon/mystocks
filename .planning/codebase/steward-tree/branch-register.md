# Steward Tree Branch Register

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: active branch / PR register
- Prepared at: `2026-05-27T17:22:14+08:00`
- Base HEAD checked: `ba929aee2e7fc0de0278f80f30caa185fafa6b5c`

Boundary note: this register records relationship state only. It does not merge
PRs, change issue labels, or authorize source implementation.

## Recent GitHub PRs Relevant To The Steward Tree

| PR | Branch | Base | State | Relationship |
|---|---|---|---|---|
| `#331` | `g2-178-strategy-adapter-provider-implementation` | `wip/root-dirty-20260403` | `MERGED` at `8bfb4dc74b06d6bb930e48ebf3d27bb28d908704` | Source implementation lane for G2.178 |
| `#332` | `g2-179-steward-tree-governance-split` | `wip/root-dirty-20260403` | `MERGED` at `750fb7c797ff95f27152439ed988a7115252129e` | Steward tree split and machine-readable index |
| `#333` | `g2-180-strategy-adapter-provider-closeout` | `wip/root-dirty-20260403` | `MERGED` at `ba929aee2e7fc0de0278f80f30caa185fafa6b5c` | Governance closeout for G2.178 and residual scan handoff |

## Steward Governance Branch

| Branch | Base | Purpose | Source authority |
|---|---|---|---|
| `g2-181-strategy-getter-residual-refresh-decision` | `origin/wip/root-dirty-20260403` at `ba929aee2e7fc0de0278f80f30caa185fafa6b5c` | Recheck Strategy getter residual classes and select the next governance target | None |

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

G2.181 is a residual-refresh decision branch only. It records the already merged
state of PR `#333`, selects route/provider fallback as the recommended next
governance target, and must not introduce another Strategy service getter
implementation.
