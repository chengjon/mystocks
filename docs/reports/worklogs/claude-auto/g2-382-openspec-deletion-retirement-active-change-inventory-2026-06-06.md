# G2.382 OpenSpec deletion-retirement active-change inventory / no-source

## 结论
本节点只做 OpenSpec 删除候选盘点与活跃契约校验，不签发任何删除授权，不恢复、不删除、不 stage 任何候选文件。

证据时间：2026-06-06。

结论分层：
- 可归档: 19
- 已迁移: 0
- 高危误删: 0
- 需恢复: 0

## 盘点范围
- 删除候选: 76 个 OpenSpec tracked 文件
- 涉及 change 目录: 19 个
- `openspec list` 活跃 change 数: 16
- `openspec list --specs` 现有 spec 数: 47
- 活跃 change 与删除候选的交集: 0

## 校验口径
- `openspec validate --changes --strict`: 通过，退出码 0
- `openspec validate --specs --strict`: 通过，退出码 0
- 上一次未带目标参数的 `openspec validate --strict` 仅能作为命令形态 caveat，不作为契约失败证据

## 风险分层决策表
| 分层 | change | 删除文件数 | 当前契约态 | archive 对齐 | 决策备注 |
|---|---|---:|---|---|---|
| 可归档 | add-broker-acknowledgement-reconciliation-contract | 6 | architecture-governance, broker-acknowledgement-reconciliation, trading-execution-safety | 5/6 same, drift: `specs/trading-execution-safety/spec.md` | 归档路径存在，属于内容漂移型可归档 |
| 可归档 | add-broker-channel-topology-for-miniqmt-and-tdx | 4 | broker-truth-channel-topology | 4/4 same | 强匹配，可归档 |
| 可归档 | add-containerized-runtime-deployment-capability | 1 | 无新增 spec delta | 1/1 same | 强匹配，可归档 |
| 可归档 | add-kronos-integration-contract | 4 | kronos-integration-contract | 4/4 same | 强匹配，可归档 |
| 可归档 | add-miniqmt-live-bridge-runtime-contract | 5 | miniqmt-live-bridge-runtime, trading-execution-safety | 4/5 same, drift: `specs/trading-execution-safety/spec.md` | 归档路径存在，属于内容漂移型可归档 |
| 可归档 | add-miniqmt-primary-broker-adapter-runtime | 5 | miniqmt-primary-broker-adapter-runtime, trading-execution-safety | 4/5 same, drift: `specs/trading-execution-safety/spec.md` | 归档路径存在，属于内容漂移型可归档 |
| 可归档 | add-page-audit-orchestration-governance | 4 | frontend-audit-orchestration | 4/4 same | 强匹配，可归档 |
| 可归档 | add-portfolio-attribution-analysis | 4 | portfolio-attribution-analysis | 4/4 same | 强匹配，可归档 |
| 可归档 | add-stop-hook-graphiti-task-closeout | 4 | agent-memory-workflow | 4/4 same | 强匹配，可归档 |
| 可归档 | add-windows-qmt-agent-reference-service | 5 | trading-execution-safety, windows-qmt-agent-reference-service | 5/5 same | 强匹配，可归档 |
| 可归档 | add-windows-qmt-agent-runtime-contract | 5 | trading-execution-safety, windows-qmt-agent-live-contract | 4/5 same, drift: `specs/trading-execution-safety/spec.md` | 归档路径存在，属于内容漂移型可归档 |
| 可归档 | add-windows-qmt-contract-acceptance-harness | 4 | windows-qmt-agent-contract-acceptance | 4/4 same | 强匹配，可归档 |
| 可归档 | add-windows-qmt-contract-formal-sequence | 4 | trading-execution-safety, windows-qmt-contract-formal-sequence | 4/4 same | 强匹配，可归档 |
| 可归档 | add-windows-qmt-service-readiness-probe | 4 | trading-execution-safety, windows-qmt-service-readiness-probe | 4/4 same | 强匹配，可归档 |
| 可归档 | align-artdeco-stateful-primitives-with-design | 4 | artdeco-design-governance | 4/4 same | 强匹配，可归档 |
| 可归档 | align-business-route-status-and-tooltip-surfaces | 4 | artdeco-design-governance | 4/4 same | 强匹配，可归档 |
| 可归档 | implement-pinia-api-standardization | 4 | api-integration | 1/4 same, drift: `proposal.md`, `specs/api-integration/spec.md`, `tasks.md` | 归档路径存在，属于内容漂移型可归档 |
| 可归档 | update-frontend-view-governance | 1 | 无新增 spec delta | 0/1 same, drift: `tasks.md` | 归档路径存在，属于内容漂移型可归档 |
| 可归档 | update-miniqmt-phase-a-contract-hardening | 4 | trading-execution-safety | 4/4 same | 强匹配，可归档 |

## 决策说明
1. 这些删除候选均来自已有 OpenSpec change 目录，且没有任何一个落入当前 `openspec list` 的活跃 change 集合。
2. 19 个 change 目录全部可以追溯到 archive 目录，其中 13 个为强匹配，6 个存在内容漂移但仍保持完整归档路径。
3. 漂移主要集中在 `specs/trading-execution-safety/spec.md` 与 `implement-pinia-api-standardization` / `update-frontend-view-governance` 的任务或 proposal 文档，说明后续如果要做删除退役授权，应单独拆成“强归档匹配包”和“内容漂移复核包”。
4. 本节点不签发删除授权，不对任何候选文件执行恢复、删除或 stage。

## 下一步建议
- 先把 13 个强归档匹配 change 目录拆成一个独立的 OpenSpec 退役授权小包。
- 再把 6 个内容漂移 change 目录拆成一个独立复核小包，先处理 `specs/trading-execution-safety/spec.md` 相关漂移，再决定是否进入删除退役授权。
- remaining frontend / backend / scripts 三类删除项保持延后，按用户指定的独立节点继续盘点。

## 备注
- 本报告仅为 no-source 盘点记录。
- 本节点未修改、未删除、未恢复、未 stage 任何 OpenSpec 候选文件。
