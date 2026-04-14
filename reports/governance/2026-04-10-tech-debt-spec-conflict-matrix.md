# Tech Debt Spec Conflict Matrix

> **历史分析说明**:
> 本文件用于记录 2026Q1 技术债治理中已识别的规范冲突或重叠点，供治理排期与收口使用。
> 它不是共享规则正文；冲突的最终裁定仍以 `architecture/STANDARDS.md`、已归档 OpenSpec formal specs 和当前实现为准。

**Generated:** 2026-04-10  
**OpenSpec change:** `tech-debt-governance-2026q1`

## Matrix

| ID | Conflict | Canonical target | Current status | Owner | Next action |
|---|---|---|---|---|---|
| SC-001 | 仓库共享规则入口曾分散在 `AGENTS.md` / `CLAUDE.md` / 各类报告 | `architecture/STANDARDS.md` | monitoring | main | 继续清理残余重复规则引用 |
| SC-002 | 技术债治理规则正文与执行章程边界易混淆 | `STANDARDS.md` + charter v1 | resolved | main | 保持“规则正文 vs 执行细则”分离 |
| SC-003 | 根 `TASK.md` 曾与治理任务看板混用 | Mongo-exported root snapshots | resolved | main | 禁止把 root TASK 回退成手写看板 |
| SC-004 | `reports/governance/*` 与 `docs/reports/*` 的职责边界不稳 | `reports/governance/` 承载执行工件 | monitoring | docs-governance | 后续 family 清理继续收口 |
| SC-005 | 历史阶段报告里的固定质量数字会冒充当前值 | `reports/analysis/tech-debt-baseline.json` | monitoring | main | 报告中继续显式区分 baseline / measured |
| SC-006 | drift report 旧产物名与脚本默认值不一致 | `reports/analysis/tech-debt-baseline-drift-report.json` | resolved | main | 保持脚本与单测锁定默认值 |
| SC-007 | `docs/reports/*technical-debt*` 历史建议与当前基线口径不同步 | baseline + charter + SoT | planned | main | 后续按 trunk-first 策略做文档减面 |
| SC-008 | OpenSpec active changes 与实际 formal specs 曾不同步 | archived formal specs | monitoring | openspec | 继续及时归档 completed changes |
| SC-009 | 页面 API `verified/pending` 曾在历史矩阵与当前状态工件之间漂移 | current formal spec + newer closeout artifacts | resolved | frontend-governance | 不再把历史矩阵当当前真相 |
| SC-010 | `main.js` / `main-standard.ts` / router 历史资产真相冲突 | `index.html -> main-standard.ts -> router/index.ts` | resolved | frontend-governance | 继续按 formal spec 执行 |
| SC-011 | 文档系统 canonical / report / plan / supporting 分类曾混乱 | documentation governance spec | monitoring | docs-governance | 后续继续 family wave 收口 |
| SC-012 | `docs/standards/` 与 `reports/governance/` 可能重复承载模板或流程 | charter in docs, templates in reports | monitoring | main | 不在 `docs/standards/` 复制模板 |
| SC-013 | 技术债“基线不增”与“观察项”边界容易混用 | charter v1 section 5 | monitoring | main | 明确哪些指标是 gate、哪些只是观察项 |
| SC-014 | 历史 `.planning` phase 统计与当前工作区真相存在口径差 | current workspace truth + refreshed docs | open | main | 以 `2026-04-12-phase2-historical-repo-truth-alignment.md` 固定 Phase 2 解释，并继续评估是否需要 Phase 3 sister note |
| SC-015 | `docs/worklogs/` 与 `docs/reports/worklogs/` 曾复发并存 | canonical worklogs under docs/reports | resolved | docs-governance | 保持复发防护测试 |
| SC-016 | `ui-ux-pro-max` 产物曾被误当 active docs family | skill artifact only | resolved | docs-governance | 保持退出根导航 |
| SC-017 | API contract truth 在 Markdown 清单与 OpenAPI 之间可能重叠 | FastAPI routes + Pydantic + /openapi.json | monitoring | backend-governance | 不再新增手写并行契约真相 |
| SC-018 | Graphiti / Mongo 边界曾被助手专用流程固化 | Mongo workflow truth + Graphiti memory spec | resolved | main | 继续复用 shared CLI contract |
| SC-019 | transcript archive / ledger 与 task report summary 角色边界 | `symphony-service` formal spec | resolved | main | 保持 summary-first export |
| SC-020 | `tech-debt-governance-2026q1` 原 proposal 想建立 `technical_debt/governance/*` 新树 | current docs/reports/report-governance trunks | resolved | main | 采用现有 trunk，不新增平行目录 |

## Status Legend

- `resolved`: 当前 formal spec / canonical trunk 已明确
- `monitoring`: 已裁定，但需防复发
- `planned`: 需要后续波次清理
- `open`: 仍待继续收口
