# Tech Debt Register

> **历史分析说明**:
> 本文件用于记录当前确认的技术债治理条目、owner、DDL 和下一步动作。
> 它是治理执行台账，不是共享规则正文；规则口径仍以 `architecture/STANDARDS.md` 与 `docs/standards/technical-debt-governance-charter-v1.md` 为准。

**Generated:** 2026-04-10  
**OpenSpec change:** `tech-debt-governance-2026q1`

## Register

| ID | Topic | Owner | DDL | Severity | Source | Next action |
|---|---|---|---|---|---|---|
| TD-001 | Phase 2 历史计划与当前工作区真相偏差 | main | 2026-04-17 | high | `docs/reports/2026-04-07-project-status-and-tech-debt-priorities.md` | 以 `reports/governance/2026-04-12-phase2-historical-repo-truth-alignment.md` 固定 repo-truth 解释，并继续评估是否需要 Phase 3 sister note |
| TD-002 | `.planning` 自动统计与 phase 工件命名不一致 | main | 2026-04-17 | medium | same report | 对齐统计规则或修正文档 |
| TD-003 | 后端 static analysis 总问题 `1253` | backend | 2026-04-24 | high | `reports/analysis/tech-debt-baseline.json` | 以 `reports/governance/2026-04-12-backend-static-analysis-bucketing-plan.md` 固定 wave map，并从 Wave 1A 切首批 runtime truth debt |
| TD-004 | backend docstring issues `619` | backend | 2026-05-01 | medium | baseline | 判定哪些进入 gate，哪些保留观察项 |
| TD-005 | backend type annotation issues `400` | backend | 2026-05-01 | high | baseline | 优先核心路径补类型 |
| TD-006 | backend security issues `49` | backend | 2026-04-24 | high | baseline | 以 `reports/governance/2026-04-12-backend-security-remediation-seed.md` 固定首批 security review lanes，并从 Lane A 起步 |
| TD-007 | `skip_xfail_count` 基线 `102` | test | 2026-04-24 | high | baseline | 以 `reports/governance/2026-04-12-skip-xfail-inventory-baseline.md` 为 inventory 初稿，继续补全全量条目与 owner |
| TD-008 | `backend_todo_count` 基线 `50` | main | 2026-04-24 | medium | baseline | 以 `reports/governance/2026-04-12-backend-todo-inventory-baseline.md` 固定 inventory 初稿，并继续补 baseline counting rule 与 owner/TTL |
| TD-009 | `backend_placeholder_count` 基线 `502` | main | 2026-04-24 | high | baseline | 以 `reports/governance/2026-04-12-backend-placeholder-inventory-baseline.md` 为 inventory 初稿，继续补齐高风险 runtime path 与 verdict |
| TD-010 | frontend structural mess 仍有未完成大 change | frontend-governance | 2026-04-24 | high | OpenSpec active list | 继续 `restructure-frontend-directory` 等主线治理 |
| TD-011 | data access layers overlap 未完全收口 | backend | 2026-04-24 | high | 2026-04-07 status report | 做 canonical coverage audit |
| TD-012 | root shim chains 仍待处置 | main | 2026-05-01 | medium | 2026-04-07 status report | 建立 shim inventory 与退出条件 |
| TD-013 | naming / mechanical split debt 仍散落 | main | 2026-05-01 | medium | 2026-04-07 status report | 建立 targeted cleanup list |
| TD-014 | reports / docs 中历史 technical-debt 文档过多 | docs-governance | 2026-05-01 | medium | docs inventory | 按 trunk-first 做归档/减面 |
| TD-015 | architecture governance formal capability缺失 | openspec | 2026-04-10 | medium | `tech-debt-governance-2026q1` | 归档当前 change，生成 formal spec |

## Notes

- DDL 使用治理执行日历，不等同于产品功能发布承诺。
- severity 只用于排期，不代表运行时故障等级。
- 后续如引入例外，必须补 owner / issue / ttl。
