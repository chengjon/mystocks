# Backend OpenSpec G-Line Integration Decision

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

日期: 2026-05-18

范围: 判断另一条线推进的 `consolidate-backend-health-endpoints` 是否应与本条 OpenSpec governance / issue publication 线合并推进。

## 结论

不合并推进。

本条线只吸收 G 线最新状态作为对齐事实，不把 G 线 residual verification、PM2 gate、strategy refactor 或跨域 OpenAPI 文档治理合并进 issue 1 approval gate。

## 当前事实

G 线已有两次路径级提交进入当前提交历史:

| Commit | 说明 | 主要文件 |
|---|---|---|
| `cd1e4795b` | `docs(health): record residual verification blockers` | `docs/reports/quality/backend-health-status-residual-blockers-2026-05-18.md` |
| `b3bbf4314` | `docs(health): close implementation boundary tasks` | `docs/reports/quality/backend-health-status-implementation-boundary-2026-05-18.md` |

当前 `openspec/changes/consolidate-backend-health-endpoints/tasks.md` 状态:

| 项 | 状态 | 说明 |
|---|---|---|
| `3.1-3.4` | closed | 按 verified no-op implementation 收口；未新增 alias、未移除 readiness compatibility、未退役 endpoint。 |
| `4.6` | open | 仍受跨域 OpenAPI documentation/schema 债阻塞，不是 health endpoint smoke 回归。 |
| `4.7` | open | 完整 PM2 integration workflow 会执行 `pm2 stop all` / `pm2 delete all`，需要显式批准或 approved named equivalent。 |

G 线当前可概括为: `27 done / 2 open`。

## 不合并原因

1. G 线剩余项不是 issue publication gate 的前置条件。

Issue 1 仍只审批 backend OpenSpec orchestration、C/E/F/G proposal scope、publication order 和后续 issue 解锁规则。G 线 residual verification 不应扩大 issue 1 的审批面。

2. `4.6` 属于独立 OpenAPI documentation stabilization。

`4.6` 涉及 `strategy_mgmt_compat` duplicate operationId、announcement stale path expectations、data/kline success example、sentiment success example、position success example 等跨域文档/schema 失败。它可以被 G 线引用为 residual blocker，但不应伪装成 health/status endpoint consolidation 的实现尾项。

3. `4.7` 是运行态审批问题。

完整 PM2 workflow 会改变本地 PM2 进程状态。没有明确批准前，本条线不能执行，也不能用只读状态检查替代完整 gate。

4. Strategy refactor 不是 G 线 closure 证据。

当前提交历史顶部存在 `eecfd5796 refactor(strategy): split get_monitoring_db.py into sub-modules`，它改动 `web/backend/app/api/strategy_management/*`。该提交可作为 strategy domain refactor 事实独立记录，但不能证明 health endpoint residual blockers 已闭合，也不能替代 OpenAPI documentation stabilization 或 PM2 gate。

## Publication Package Impact

G 线最新进展使原 issue draft `08-build-health-status-taxonomy.md` 和
`09-decide-health-status-canonical-paths.md` 不再适合作为后续可发布任务原样发布。

原因:

- G tasks `2.1-2.7` 已完成 canonical liveness、readiness、services health、status taxonomy、domain smoke/status separation、backup ownership deferral 和 rollback trigger decision。
- G tasks `3.1-3.4` 已按 verified no-op implementation 关闭。
- 剩余 `4.6` / `4.7` 不是原 08/09 草稿描述的 taxonomy / canonical path 决策工作，而是跨域 OpenAPI documentation stabilization 和 PM2 workflow approval。

因此当前 publication package 应保持:

| 类别 | 数量 | 说明 |
|---|---:|---|
| Retained body files | 15 | 保留完整审计上下文 |
| Publishable commands | 3 | Issue 1、14、15 |
| Audit-only / do-not-publish | 3 | 03/04/05，P3 已解决 |
| Publication hold / reclassification required | 2 | 08/09，G 线已覆盖原任务，应先重分类或替换为 residual-tail issues |
| Superseded / merged | 7 | 02/06/07/10/11/12/13，已合并进 14/15 |

## 执行口径

本线可做:

- 在 summary / cross-line response 中记录 G 线已推进到 `27 done / 2 open`。
- 将 issue drafts 08/09 从后续可发布命令中移出，保留为 publication hold / reclassification records。
- 将 issue drafts 02/06/07/10/11/12/13 从后续可发布命令中移出，保留为 superseded / merged source bodies。
- 保持 issue 1 approval gate 不变。
- 保持 issue 1 first 的发布规则不变；后续 manifest command order 仅包含 01/14/15，直到 08/09 被重分类。

本线不做:

- 不把 G 线 residual verification 合并进 issue 1 runbook。
- 不把 strategy refactor 作为 G 线验收证据。
- 不关闭 `4.6` 或 `4.7`。
- 不执行完整 PM2 gate。
- 不原样发布 issue drafts 08/09。
- 不发布或解锁任何 implementation issue。

## 后续建议

| 后续项 | 建议 |
|---|---|
| `4.6` | 拆为独立 OpenAPI documentation stabilization 批次；解决跨域 OpenAPI 文档/schema 测试失败后，再回填 G 线 closure evidence。 |
| `4.7` | 等待显式批准完整 PM2 integration workflow，或批准一个不 stop/delete PM2 的 named equivalent。 |
| Strategy refactor | 单独作为 strategy implementation/refactor 线处理，不纳入 G 线 closure。 |
| 本线 issue publication | 继续按 issue 1 approval gate 推进；未经批准不执行 `gh issue create`。 |

## 当前判定

G 线进展可以被本条线吸收为事实更新，但不改变本条线的核心结论:

- Issue 1 仍为 approval gate。
- 后续可发布 issue package 仅包含 3 条 publishable commands；08/09 仍需重分类。
- Governance line 不执行 backend implementation。
- OpenSpec archive 仍未解锁。
