# Technical Debt Governance Source of Truth

> **补充规范说明**:
> 本文件用于固定 2026Q1 技术债治理基线的权威引用关系，不是仓库共享规则的唯一事实来源。
> 仓库级共享规则总入口仍以 `architecture/STANDARDS.md` 为准；本文件只回答“技术债治理这条线当前应以哪些工件为准”。

**Generated:** 2026-04-10  
**OpenSpec change:** `tech-debt-governance-2026q1`

## 1. Purpose

把当前仓库已经存在、但分散在多个目录下的技术债治理工件整理成单一引用表，避免后续再出现：

- 基线文件、周报、脚本默认产物口径不一致
- 根 `TASK.md` 被误当成手写治理看板
- `docs/reports/*` 历史计划被误当成当前执行事实
- OpenSpec、治理章程、执行工件各写一套规则

## 2. Authoritative References By Domain

| Domain | Canonical artifact | Role | Notes |
|---|---|---|---|
| 仓库级共享规则 | `architecture/STANDARDS.md` | 唯一共享规则入口 | 结构性技术债判定、审批门禁、迁移收口规则都以此为准 |
| 技术债治理执行细则 | `docs/standards/technical-debt-governance-charter-v1.md` | 专题执行章程 | 负责门禁、基线、例外、周报、执行映射 |
| OpenSpec 治理能力 | `openspec/changes/tech-debt-governance-2026q1/` | 当前变更事实 | 在归档前，这条 change 是本次治理基线的提案真相 |
| 技术债基线 | `reports/analysis/tech-debt-baseline.json` | 机器基线真相 | 当前基线冻结值应从这里读取 |
| 漂移报告默认产物名 | `reports/analysis/tech-debt-baseline-drift-report.json` | 规范产物名 | 当前文件可不存在，但默认路径和命名已被脚本/测试锁定 |
| 技术债周报产物 | `reports/analysis/tech-debt-weekly-report*.md` | 周度结果工件 | 属于执行结果，不是规则正文 |
| 技术债 KPI / current snapshots | `reports/analysis/tech-debt-current*.json` `reports/analysis/tech-debt-kpi-report*.json` | 观察工件 | 反映某次统计结果，不替代基线文件 |
| 治理任务模板与实例 | `reports/governance/README.md` `reports/governance/_TEMPLATE.*` | 执行模板真相 | 所有治理任务/周报模板继续从这里继承 |
| 根任务工件 | `TASK.md` `TASK-REPORT.md` | Mongo 导出快照 | 不得再当作手写技术债看板真相 |
| 项目状态与优先级整理 | `docs/reports/2026-04-07-project-status-and-tech-debt-priorities.md` | 历史评估输入 | 可作为排期输入，但不是当前规则正文 |

## 3. Governance Boundaries

### 3.1 What lives here

- 引用关系
- 当前治理主干
- 工件角色边界

### 3.2 What does not live here

- 结构性技术债规则正文
- 运行时配置真相
- 历史周报中的临时结论
- 根 `TASK.md` 的手工维护状态

## 4. Execution Routing

### 4.1 New governance work

新技术债治理工作默认落在：

- `reports/governance/*.TASK.md`
- `reports/governance/*.TASK-REPORT.md`
- `reports/governance/*.WEEKLY.md`

### 4.2 Historical and analytical material

历史分析、阶段性计划、样例与观察项继续保留在：

- `docs/reports/`
- `reports/analysis/`

### 4.3 Root snapshots

根 `TASK.md` / `TASK-REPORT.md` 继续保持 Mongo control-plane exported snapshot 角色，不承载手工治理看板职责。

## 5. Linked Baseline Artifacts

- `reports/governance/2026-04-10-tech-debt-spec-conflict-matrix.md`
- `reports/governance/2026-04-10-tech-debt-register.md`
- `reports/governance/2026-04-10-tech-debt-governance-execution.TASK.md`
- `reports/governance/2026-04-10-tech-debt-governance-execution.TASK-REPORT.md`

## 6. Current Decision

`tech-debt-governance-2026q1` 不再引入新的顶层 `technical_debt/` 文档树。

理由：

- 当前仓库已有 `docs/standards/`、`reports/governance/`、`reports/analysis/` 三条稳定 trunk
- 新增平行目录会制造新的文档真相竞争
- 本次变更的目标是“治理基线收敛”，不是再开一层新入口
