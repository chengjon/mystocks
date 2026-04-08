# Documentation Governance Decision Register

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **治理台账说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 的首轮 cluster decision register。
> 它用于指导后续 archive/delete/merge 波次，不等同于立即执行清理动作；所有删除仍须遵守 `architecture/STANDARDS.md` 与 delete gate。

## Default Action Rule

当 cluster 已有 canonical replacement，且不再承担 retention / compatibility 义务时，默认动作是：

```text
delete > rewrite
archive > rewrite
```

仅在仍需保留历史审计、兼容告知或过渡导航时，才保留 rewrite 作为短期手段。

## Status Vocabulary

- `keep-canonical`
- `keep-supporting`
- `merge-into-trunk`
- `archive`
- `delete`
- `needs-replacement`

## Register

| Owner | Subtree / Cluster | Decision status | Canonical replacement | Inbound-link status | Execution gate | Notes |
|---|---|---|---|---|---|---|
| `main` | `docs/api/README.md` | `keep-canonical` | `docs/api/README.md` + code contract truth | root trunk linked from `docs/README.md` | open | keep as API navigation only; do not let it outrank OpenAPI truth |
| `main` | `docs/api/legacy-cn/` | `delete` | `docs/api/README.md` and runtime API contract truth | `cleaned` | executed in API wave 1 | bounded legacy cluster deleted after active-tree link cleanup |
| `main` | `docs/reports/README.md` | `keep-canonical` | `docs/reports/README.md` | root trunk linked from `docs/README.md` | open | keep as historical evidence entrypoint only |
| `main` | `docs/reports/legacy-cn/` | `archive` | `docs/reports/README.md` | `cleaned` | executed in reports wave 1 | archived to `archive/docs/reports/legacy-cn-2026-04-08/` |
| `main` | `docs/guides/` | `keep-supporting` | `docs/README.md` + concern-specific guide families | high inbound usage across `AGENTS.md`, `docs/testing/`, and historical plans | open | guide families now route by concern; subtree-wide delete remains inappropriate |
| `main` | `docs/guides/README.md` + `docs/guides/INDEX.md` | `merge-into-trunk` | `docs/README.md` + concern-specific guide families | transition index active | open | broad catch-all role removed; files now serve only as transition indexes |
| `main` | `docs/guides/documentation/` | `merge-into-trunk` | `docs/overview/documentation-system.md` | localized subtree links present | open | converge workflow/structure notes into the new documentation governance trunk |
| `main` | `docs/guides/governance/` | `keep-supporting` | `architecture/STANDARDS.md` + `docs/overview/documentation-system.md` | localized subtree links present | open | keep focused workflow helpers, but do not let this subtree become a second governance truth source |
| `main` | `docs/architecture/legacy-cn/` | `archive` | `docs/architecture/README.md` + retained architecture indexes | `cleaned` | executed in architecture wave 1 | active-tree links removed from `docs/architecture/INDEX.md`, `docs/INDEX.md`, and `architecture/INDEX.md`; archived to `archive/docs/architecture/legacy-cn-2026-04-08/` |
| `main` | `docs/worklogs/` | `merge-into-trunk` | `docs/reports/worklogs/` | `cleaned` | executed in worklogs wave 1 | active-tree navigation moved to `docs/reports/worklogs/`; incremental worklogs merged into reports trunk and the parallel root directory removed |
| `main` | `docs/web-dev/` | `merge-into-trunk` | `docs/guides/hooks/WEB_DEV_HOOKS_GUIDE.md` + `docs/guides/hooks/web-dev-hooks-guide.md` | `cleaned` | executed in web-dev wave 2 | tracked hook guides, taxonomy, hygiene tests, and `docs/INDEX.md` no longer route readers to `docs/web-dev/`; the compatibility shell was then removed |
| `main` | `docs/overview/README.md` + `docs/overview/INDEX.md` | `merge-into-trunk` | `docs/README.md` + `docs/overview/documentation-system.md` | transition index active | executed in wave 3 | overview root entrypoints now act only as transition/supporting indexes |
| `main` | `docs/operations/README.md` | `keep-canonical` | `docs/operations/README.md` | root trunk linked from `docs/README.md` | open | keep as operations/runbook trunk |
| `main` | `docs/operations/INDEX.md` | `merge-into-trunk` | `docs/operations/README.md` | transition index active | executed in wave 3 | root operations index now routes by active runbook family only |
| `main` | `docs/testing/README.md` | `keep-canonical` | `docs/testing/README.md` | root trunk linked from `docs/README.md` | open | keep as testing guidance trunk |
| `main` | `docs/testing/INDEX.md` | `merge-into-trunk` | `docs/testing/README.md` | transition index active | executed in wave 3 | root testing index no longer routes readers into legacy branches |
| `main` | `docs/testing/legacy-cn/` | `archive` | `docs/testing/README.md` | `cleaned` | executed in wave 3 | archived to `archive/docs/testing/legacy-cn-2026-04-08/` after active-tree link cleanup |

## Blocked Clusters

以下 cluster 当前禁止删除：

1. `docs/guides/`
   - reason: inbound usage remains high and guide families serve different concerns
   - required next step: continue family-by-family cleanup instead of subtree-wide deletion

## Immediate Cleanup Eligibility

当前无 remaining gated cluster。

## Decision Basis

- trunk map: `docs/README.md`, `docs/overview/documentation-system.md`
- machine-readable taxonomy: `config/governance/documentation-taxonomy.yaml`
- measured inventory: `2026-04-08-first-pass-inventory.md`
- audit command: `python scripts/governance/audit_documentation_system.py`
