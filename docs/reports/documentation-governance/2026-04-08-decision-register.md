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
| `main` | `docs/reports/README.md` | `keep-canonical` | `docs/reports/README.md` | root trunk linked from `docs/README.md` | executed in reports wave 2 | `docs/README.md` continues routing to the canonical historical-evidence trunk; hygiene coverage now fixes the trunk role so `docs/reports/README.md` stays an evidence entrypoint instead of drifting back toward current-truth narration |
| `main` | `docs/reports/legacy-cn/` | `archive` | `docs/reports/README.md` | `cleaned` | executed in reports wave 1 | archived to `archive/docs/reports/legacy-cn-2026-04-08/` |
| `main` | `docs/guides/` | `keep-supporting` | `docs/README.md` + concern-specific guide families | high inbound usage across `AGENTS.md`, `docs/testing/`, and historical plans | executed in guides wave 3 | guides root remains a family-routed supporting surface; `docs/README.md` stays the docs trunk, while `docs/guides/README.md` and `docs/guides/INDEX.md` only route by concern and do not justify subtree-wide deletion |
| `main` | `docs/guides/README.md` + `docs/guides/INDEX.md` | `merge-into-trunk` | `docs/README.md` + concern-specific guide families | transition index active | executed in guides wave 2 | wave 1 already converted the two root entrypoints into transition indexes; wave 2 closes the register after re-validating that `docs/guides/` now routes only by concern-specific families and no longer acts as a parallel canonical trunk |
| `main` | `docs/guides/documentation/` | `merge-into-trunk` | `docs/overview/documentation-system.md` | active navigation cleaned; historical direct links retained | executed in documentation wave 2 | family index and `docs/INDEX.md` now route readers to `documentation-system.md`, `CANONICAL_TRUNK_ADMISSION_GUIDE.md`, and `DOCUMENTATION_WORKFLOW_GUIDE.md` first; specialized methodology guides remain supporting because direct links still exist in plans, reviews, and AI guide docs |
| `main` | `docs/guides/governance/` | `keep-supporting` | `architecture/STANDARDS.md` + `docs/overview/documentation-system.md` | localized subtree links present | executed in governance wave 1 | family index now routes readers to `architecture/STANDARDS.md` and `documentation-system.md` first; `FEATURE_MANAGEMENT_WORKFLOW.md` and `TECHNICAL_DEBT_MANAGEMENT.md` remain supporting workflow guides rather than a second governance truth source |
| `main` | `docs/guides/hooks/` | `keep-supporting` | `docs/guides/hooks/WEB_DEV_HOOKS_GUIDE.md` + `docs/guides/hooks/web-dev-hooks-guide.md` + `docs/guides/hooks/pre_commit_hook_setup_guide.md` | root navigation compacted; residual `Web Dev` alias rerouted to `guides/hooks/` | executed in hooks wave 1 | family index now acts as a transition index; root navigation prioritizes the bilingual web-dev hook guides plus pre-commit setup, while diagnostics and historical notes remain behind the family index |
| `main` | `docs/guides/mock-data/` | `keep-supporting` | `docs/guides/mock-data/MOCK_REAL_DATA_SWITCHING_GUIDE.md` + `docs/guides/mock-data/MOCK_DATA_USAGE_RULES.md` + `docs/guides/mock-data/MOCK_REAL_DATA_INDEX.md` | root navigation compacted; historical leaf docs moved behind family index | executed in mock-data wave 1 | family index now routes readers to the current switching guide, usage rules, and mock/real topic index first; roadmap, phase plan, and old snapshot docs remain retained as historical references rather than primary entrypoints |
| `main` | `docs/guides/openspec-cmd/` | `keep-supporting` | `openspec/AGENTS.md` + `docs/guides/openspec-cmd/README.md` + `docs/guides/openspec-cmd/check.md` | root navigation compacted; template/example moved behind family index | executed in openspec-cmd wave 1 | family index now routes readers to OpenSpec main guidance and the `check` command first; template and report example remain retained as supporting references |
| `main` | `docs/guides/pm2/` | `keep-supporting` | `docs/guides/pm2/PM2_PLAYWRIGHT_TESTING_GUIDE.md` + `docs/guides/pm2/PM2_QUICK_START_GUIDE.md` + `docs/guides/pm2/PM2_TMUX_LNV_COLLABORATION_GUIDE.md` | root navigation compacted; review doc moved behind family index | executed in pm2 wave 1 | family index now routes readers to the active PM2 execution guides first; the review document remains retained as historical feedback rather than a primary entrypoint |
| `main` | `docs/guides/quant-trading/` | `keep-supporting` | `docs/guides/quant-trading/algorithm_system_usage_guide.md` + `docs/guides/quant-trading/risk_management_system_plan.md` | root navigation compacted; phase/historical docs moved behind family index | executed in quant-trading wave 1 | family index now routes readers to the system overview and risk-management plan first; phase 4/5 completion reports and the historical implementation plan remain retained as supporting references |
| `main` | `docs/guides/templates/` | `keep-supporting` | `docs/guides/templates/INITIALIZATION_PROMPT.md` | root navigation compacted; specialized templates moved behind family index | executed in templates wave 1 | family index now routes readers to the initialization prompt first; task-card and tech-debt exception templates remain retained as supporting references |
| `main` | `docs/guides/tdx-integration/` | `keep-supporting` | `docs/guides/tdx-integration/README.md` + `docs/guides/tdx-integration/WINDOWS_TDX_BRIDGE_SETUP.md` | root navigation compacted; analysis/example docs moved behind family index | executed in tdx-integration wave 1 | family index now routes readers to the TDX overview and Windows bridge setup first; historical analysis, capture, analysis, visualization, and example docs remain retained as supporting references |
| `main` | `docs/guides/typescript/` | `keep-supporting` | `docs/guides/typescript/Typescript_QUICKSTART.md` + `docs/guides/typescript/Typescript_USER_GUIDE.md` + `docs/guides/typescript/Typescript_BEST_PRACTICES.md` + `docs/guides/typescript/Typescript_CONFIG_REFERENCE.md` | root navigation compacted; training/fix/plan docs moved behind family index | executed in typescript wave 1 | family index now routes readers to quickstart, user guide, best practices, and config reference first; training materials, troubleshooting, fix guides, and extension-system plans remain retained as supporting references |
| `main` | `docs/guides/data-interface/` | `keep-supporting` | `docs/guides/data-interface/UNIFIED_INTERFACE_GUIDE.md` + `docs/guides/data-interface/DATA_INTERFACE_SCANNER_GUIDE.md` | root navigation compacted; analysis leaf routed via family index | executed in data-interface wave 1 | family index now acts as a transition index; root navigation prioritizes the unified interface and scanner guides, while `analyze_api_data_usage_README.md` remains retained behind the family index as a specialized tool reference |
| `main` | `docs/guides/data-source/` | `keep-supporting` | `docs/guides/data-source/NEW_API_SOURCE_INTEGRATION_GUIDE.md` + `docs/guides/data-source/DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md` + `docs/guides/data-source/DATA_SOURCE_TOOLS_QUICK_REFERENCE.md` | root navigation compacted; cleaning/monitoring/optimization leaf docs routed via family index | executed in data-source wave 1 | family index now acts as a transition index; root navigation prioritizes the integration, management, and quick-reference guides, while data cleaning, monitoring, endpoint registration, expansion, and optimization materials remain retained behind the family index as specialized references |
| `main` | `docs/guides/ai-tools/` | `keep-supporting` | `docs/guides/ai-tools/AI_QUICK_START.md` + `docs/guides/ai-tools/AGENTS.md` + `docs/guides/ai-tools/CLAUDE.md` + `docs/guides/ai-tools/GEMINI.md` + `docs/guides/ai-tools/GRAPHITI_MCP_WORKFLOW.md` + `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md` + `docs/guides/ai-tools/OMO_SETUP_GUIDE.md` + `docs/guides/ai-tools/OpenCode生产级配置与固化指南.md` | root navigation compacted; training/fix/index leaf docs routed via family index | executed in ai-tools wave 1 | family index now acts as a transition index; root navigation prioritizes AI quick-start, core agent entry docs, and OMC/OMO workflows, while agent-management summaries, optimizer training, AMP, proxy, plugin-fix, and residual progress docs remain retained behind the family index as specialized references |
| `main` | `docs/guides/chrome-devtools/` | `keep-supporting` | `docs/guides/chrome-devtools/CHROME_DEVTOOLS_MCP_GUIDE.md` + `docs/guides/chrome-devtools/chrome-devtools-wsl2-guide.md` + `docs/guides/chrome-devtools/mystocks-chromedevtools-testing-guide.md` | root navigation compacted; fix/solution leaf docs routed via family index | executed in chrome-devtools wave 1 | family index now acts as a transition index; root navigation prioritizes the MCP usage guide, WSL2 setup, and project testing guide, while fix and solution summaries remain retained behind the family index as specialized references |
| `main` | `docs/guides/superpowers/` | `keep-supporting` | `docs/guides/superpowers/INDEX.md` | root navigation compacted; historical plan files routed via family index | executed in superpowers wave 1 | family index now acts as a transition index for a light family that only retains historical implementation plans; root navigation no longer exposes the plan files directly |
| `main` | `docs/guides/frontend/` | `keep-supporting` | `docs/guides/frontend/frontend-change-hygiene-and-micro-commit-guide.md` + `docs/guides/frontend/PR_GATE_QUICK_REFERENCE.md` + `docs/guides/frontend/DASHBOARD_API_INTEGRATION_GUIDE.md` + `docs/guides/frontend/DASHBOARD_API_ENRICHMENT_GUIDE.md` + `docs/guides/frontend/history-mode-deployment-guide.md` + `docs/guides/frontend/SASS_DEPRECATION_FIX.md` + `docs/guides/frontend/css-scss-development-guide.md` | root navigation compacted; task/history/topic docs routed via family index | executed in frontend wave 1 | family index now acts as a transition index; root navigation prioritizes hygiene, gate, dashboard integration, deployment, Sass fix, and CSS/SCSS guidance, while routing tasks, dayjs docs, service-adapter guidance, UI enhancement, and other historical task materials remain retained behind the family index as specialized references |
| `main` | `docs/guides/web/` | `keep-supporting` | `docs/guides/web/ARTDECO_START_HERE.md` + `docs/guides/web/ARTDECO_MASTER_INDEX.md` + `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md` + `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md` + `docs/guides/web/ARTDECO_GRID_QUICK_REFERENCE.md` + `docs/guides/web/ARTDECO_MENU_DATA_FETCHING_IMPLEMENTATION_GUIDE.md` + `docs/guides/web/WEB_FRONTEND_STARTUP_GUIDE.md` + `docs/guides/web/WEB_ACCESS_VERIFICATION_STANDARD.md` | root navigation compacted; high-inbound historical/theme/runtime leaf docs routed via family index | executed in web wave 1 | family index now acts as a transition index; root navigation preserves only the high-inbound ArtDeco entrypoints, unified spec, key implementation/runtime guides, while theme/showcase/report/migration/planning materials remain retained behind the family index as specialized references |
| `main` | `docs/guides/multi-cli-tasks/` | `keep-supporting` | `docs/guides/multi-cli-tasks/CLI_REGISTRATION_GUIDE.md` + `docs/guides/multi-cli-tasks/TASK_POOL_USAGE_GUIDE.md` + `docs/guides/multi-cli-tasks/CLI_WORKFLOW_GUIDE.md` + `docs/guides/multi-cli-tasks/MAIN_CLI_WORKFLOW_STANDARDS.md` + `docs/guides/multi-cli-tasks/MONGO_MULTICLI_COORDINATION_GUIDE.md` + `docs/guides/multi-cli-tasks/MONGO_MULTICLI_OPERATION_CHECKLIST.md` + `docs/guides/multi-cli-tasks/MULTI_CLI_WORKTREE_MANAGEMENT.md` + `docs/guides/multi-cli-tasks/BRANCH_STRATEGY.md` | root navigation compacted; maestro/symphony/prompt/config/roles leaf docs routed via family index | executed in multi-cli-tasks wave 1 | family index now acts as a transition index; root navigation prioritizes active registration, task-pool, workflow, Mongo coordination, worktree and branch runbooks, while Maestro/Symphony, config, roles, prompt strategy, optimization, and other historical helper materials remain retained behind the family index as specialized references |
| `main` | `docs/architecture/legacy-cn/` | `archive` | `docs/architecture/README.md` + retained architecture indexes | `cleaned` | executed in architecture wave 1 | active-tree links removed from `docs/architecture/INDEX.md`, `docs/INDEX.md`, and `architecture/INDEX.md`; archived to `archive/docs/architecture/legacy-cn-2026-04-08/` |
| `main` | `docs/worklogs/` | `merge-into-trunk` | `docs/reports/worklogs/` | `cleaned` | executed in worklogs wave 3 | active-tree navigation stays on `docs/reports/worklogs/`; recurring `docs/worklogs/claude-auto/2026-04-09.md` was first reclosed in wave 2, then reappeared with 3 additional entries and was merged back into the canonical reports trunk again in wave 3 |
| `main` | `docs/web-dev/` | `merge-into-trunk` | `docs/guides/hooks/WEB_DEV_HOOKS_GUIDE.md` + `docs/guides/hooks/web-dev-hooks-guide.md` | `cleaned` | executed in web-dev wave 2 | tracked hook guides, taxonomy, hygiene tests, and `docs/INDEX.md` no longer route readers to `docs/web-dev/`; the compatibility shell was then removed |
| `main` | `docs/overview/README.md` + `docs/overview/INDEX.md` | `merge-into-trunk` | `docs/README.md` + `docs/overview/documentation-system.md` | transition index active | executed in wave 3 | overview root entrypoints now act only as transition/supporting indexes |
| `main` | `docs/operations/README.md` | `keep-canonical` | `docs/operations/README.md` | root trunk linked from `docs/README.md` | executed in operations/testing wave 2 | `docs/README.md` continues routing to the canonical operations trunk; hygiene tests were refreshed so secondary-index expectations match the current preferred-runbook model instead of requiring a flat leaf index |
| `main` | `docs/operations/INDEX.md` | `merge-into-trunk` | `docs/operations/README.md` | transition index active | executed in wave 3 | root operations index now routes by active runbook family only |
| `main` | `docs/testing/README.md` | `keep-canonical` | `docs/testing/README.md` | root trunk linked from `docs/README.md` | executed in operations/testing wave 2 | `docs/README.md` continues routing to the canonical testing trunk; hygiene tests were refreshed so supporting/compatibility docs stay retained without forcing `docs/testing/INDEX.md` back into a broad flat index |
| `main` | `docs/testing/INDEX.md` | `merge-into-trunk` | `docs/testing/README.md` | transition index active | executed in wave 3 | root testing index no longer routes readers into legacy branches |
| `main` | `docs/testing/legacy-cn/` | `archive` | `docs/testing/README.md` | `cleaned` | executed in wave 3 | archived to `archive/docs/testing/legacy-cn-2026-04-08/` after active-tree link cleanup |

## 2026-04-09 Execution Sync

按 2026-04-09 已完成提交补充，以下条线应视为当前轮次已闭环输入，不再回到待执行队列：

- `bd7579111 governance(tech-debt): standardize default drift report artifact`
  - `scripts/dev/quality_gate/tech_debt_governance_gate.py` 的 `baseline-drift-report` 默认输出已统一为 `reports/analysis/tech-debt-baseline-drift-report.json`
  - `tests/unit/test_tech_debt_governance_gate.py` 已新增断言锁定该默认值
  - 补充执行记录显示定点验证 `14 passed`，旧默认产物名已不再作为当前口径保留
- `9ced0498b docs(governance): reclose recurring worklogs root`
  - `docs/worklogs/claude-auto/2026-04-09.md` 已重新并回 `docs/reports/worklogs/claude-auto/2026-04-09.md`
  - `docs/reports/worklogs/INDEX.md`、`docs/INDEX.md` 与本台账已同步刷新
- `2026-04-09-worklogs-wave3.md`
  - `docs/worklogs/claude-auto/2026-04-09.md` 在同日再次复发，且携带 3 条新增记录
  - 新增记录已补并入 `docs/reports/worklogs/claude-auto/2026-04-09.md`
  - 平行根目录 `docs/worklogs/` 已再次删除；当前问题已记录为 recurring artifact，而不是新的 canonical family
  - `AGENTS.md` 与 `CLAUDE.md` 已补充执行层约束，固定 Claude Auto / Agent worklog 落点为 `docs/reports/worklogs/claude-auto/`
- `2549953ab docs(state): refresh root task control snapshots`
  - root 控制面快照 `TASK.md` 与 `TASK-REPORT.md` 的自动更新已单独收口，不再与文档治理波次混排
- `ui-ux-pro-max` 目录已按用户澄清降级为“skill 运行产物 / 残留文档”，不再视为 guide family、门禁或根导航候选
  - 当前处理原则改为：退出 `docs/INDEX.md` 主导航与 hygiene 主守护
  - 若需确认该能力本身，应回到项目 skill 源文件而不是使用这组产物文档

据此，下一步仍应遵循 trunk-first / family-first，而不是回头重复处理已闭环条线。当前建议顺序为：

1. only start a new wave where direct root-nav overexposure is still material

补充 checkpoint 结论：

- `2026-04-09-guides-family-checkpoint.md` 已记录本轮 family-level 收口后的阶段性暂停依据
- 当前没有新的 immediate cleanup wave 必须继续展开
- 后续仅在出现新的 material root-nav overexposure、retained specialized references 入链下降到可做 bounded archive/delete，或 audit 再次出现阻塞项时，才启动下一轮 family wave

以下 family 仍需谨慎评估，避免在高入链或高耦合面做过度清理：

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
