# Tech Debt Register

> **历史分析说明**:
> 本文件用于记录当前确认的技术债治理条目、owner、DDL 和下一步动作。
> 它是治理执行台账，不是共享规则正文；规则口径仍以 `architecture/STANDARDS.md` 与 `docs/standards/technical-debt-governance-charter-v1.md` 为准。

**Generated:** 2026-04-10  
**OpenSpec change:** `tech-debt-governance-2026q1`

## Register

| ID | Topic | Owner | DDL | Severity | Source | Next action |
|---|---|---|---|---|---|---|
| TD-001 | Phase 2 历史计划与当前工作区真相偏差 | main | 2026-04-17 | high | `docs/reports/2026-04-07-project-status-and-tech-debt-priorities.md` | 刷新 `.planning` 相关历史说明 |
| TD-002 | `.planning` 自动统计与 phase 工件命名不一致 | main | 2026-04-17 | medium | same report | 对齐统计规则或修正文档 |
| TD-003 | 后端 static analysis 总问题 `1253` | backend | 2026-04-24 | high | `reports/analysis/tech-debt-baseline.json` | 分层拆分 critical / warning 治理批次 |
| TD-004 | backend docstring issues `619` | backend | 2026-05-01 | medium | baseline | 判定哪些进入 gate，哪些保留观察项 |
| TD-005 | backend type annotation issues `400` | backend | 2026-05-01 | high | baseline | 优先核心路径补类型 |
| TD-006 | backend security issues `49` | backend | 2026-04-24 | high | baseline | 先复核真实性并建立 remediation list |
| TD-007 | `skip_xfail_count` 基线 `102` | test | 2026-04-24 | high | baseline | 生成可审计的 skip/xfail inventory |
| TD-008 | `backend_todo_count` 基线 `50` | main | 2026-04-24 | medium | baseline | 过滤无 owner TODO 并按 TTL 整理 |
| TD-009 | `backend_placeholder_count` 基线 `502` | main | 2026-04-24 | high | baseline | 先做 placeholder inventory，再定 P0/P1 |
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
