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
| `main` | `docs/api/README.md` | `keep-canonical` | `docs/api/README.md` + code contract truth | root trunk linked from `docs/README.md` | executed in api wave 2 | `docs/README.md` continues routing to the canonical API trunk; hygiene tests were refreshed so `docs/api/INDEX.md` stays a preferred-entrypoint index and `docs/api/README.md` no longer needs to flatten integration/supporting leaf docs |
| `main` | `docs/api/legacy-cn/` | `delete` | `docs/api/README.md` and runtime API contract truth | `cleaned` | executed in API wave 1 | bounded legacy cluster deleted after active-tree link cleanup |
| `main` | `docs/reports/README.md` | `keep-canonical` | `docs/reports/README.md` | root trunk linked from `docs/README.md` | open | keep as historical evidence entrypoint only |
| `main` | `docs/reports/legacy-cn/` | `archive` | `docs/reports/README.md` | `cleaned` | executed in reports wave 1 | archived to `archive/docs/reports/legacy-cn-2026-04-08/` |
| `main` | `docs/guides/` | `keep-supporting` | `docs/README.md` + concern-specific guide families | high inbound usage across `AGENTS.md`, `docs/testing/`, and historical plans | open | guide families now route by concern; subtree-wide delete remains inappropriate |
| `main` | `docs/guides/README.md` + `docs/guides/INDEX.md` | `merge-into-trunk` | `docs/README.md` + concern-specific guide families | transition index active | executed in guides wave 2 | wave 1 already converted the two root entrypoints into transition indexes; wave 2 closes the register after re-validating that `docs/guides/` now routes only by concern-specific families and no longer acts as a parallel canonical trunk |
| `main` | `docs/guides/documentation/` | `merge-into-trunk` | `docs/overview/documentation-system.md` | active navigation cleaned; historical direct links retained | executed in documentation wave 2 | family index and `docs/INDEX.md` now route readers to `documentation-system.md`, `CANONICAL_TRUNK_ADMISSION_GUIDE.md`, and `DOCUMENTATION_WORKFLOW_GUIDE.md` first; specialized methodology guides remain supporting because direct links still exist in plans, reviews, and AI guide docs |
| `main` | `docs/guides/governance/` | `keep-supporting` | `architecture/STANDARDS.md` + `docs/overview/documentation-system.md` | localized subtree links present | executed in governance wave 1 | family index now routes readers to `architecture/STANDARDS.md` and `documentation-system.md` first; `FEATURE_MANAGEMENT_WORKFLOW.md` and `TECHNICAL_DEBT_MANAGEMENT.md` remain supporting workflow guides rather than a second governance truth source |
| `main` | `docs/guides/hooks/` | `keep-supporting` | `docs/guides/hooks/WEB_DEV_HOOKS_GUIDE.md` + `docs/guides/hooks/web-dev-hooks-guide.md` + `docs/guides/hooks/pre_commit_hook_setup_guide.md` | root navigation compacted; residual `Web Dev` alias rerouted to `guides/hooks/` | executed in hooks wave 1 | family index now acts as a transition index; root navigation prioritizes the bilingual web-dev hook guides plus pre-commit setup, while diagnostics and historical notes remain behind the family index |
| `main` | `docs/architecture/legacy-cn/` | `archive` | `docs/architecture/README.md` + retained architecture indexes | `cleaned` | executed in architecture wave 1 | active-tree links removed from `docs/architecture/INDEX.md`, `docs/INDEX.md`, and `architecture/INDEX.md`; archived to `archive/docs/architecture/legacy-cn-2026-04-08/` |
| `main` | `docs/worklogs/` | `merge-into-trunk` | `docs/reports/worklogs/` | `cleaned` | executed in worklogs wave 1 | active-tree navigation moved to `docs/reports/worklogs/`; incremental worklogs merged into reports trunk and the parallel root directory removed |
| `main` | `docs/web-dev/` | `merge-into-trunk` | `docs/guides/hooks/WEB_DEV_HOOKS_GUIDE.md` + `docs/guides/hooks/web-dev-hooks-guide.md` | `cleaned` | executed in web-dev wave 2 | tracked hook guides, taxonomy, hygiene tests, and `docs/INDEX.md` no longer route readers to `docs/web-dev/`; the compatibility shell was then removed |
| `main` | `docs/overview/README.md` + `docs/overview/INDEX.md` | `merge-into-trunk` | `docs/README.md` + `docs/overview/documentation-system.md` | transition index active | executed in wave 3 | overview root entrypoints now act only as transition/supporting indexes |
| `main` | `docs/operations/README.md` | `keep-canonical` | `docs/operations/README.md` | root trunk linked from `docs/README.md` | executed in operations/testing wave 2 | `docs/README.md` continues routing to the canonical operations trunk; hygiene tests were refreshed so secondary-index expectations match the current preferred-runbook model instead of requiring a flat leaf index |
| `main` | `docs/operations/INDEX.md` | `merge-into-trunk` | `docs/operations/README.md` | transition index active | executed in wave 3 | root operations index now routes by active runbook family only |
| `main` | `docs/testing/README.md` | `keep-canonical` | `docs/testing/README.md` | root trunk linked from `docs/README.md` | executed in operations/testing wave 2 | `docs/README.md` continues routing to the canonical testing trunk; hygiene tests were refreshed so supporting/compatibility docs stay retained without forcing `docs/testing/INDEX.md` back into a broad flat index |
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
