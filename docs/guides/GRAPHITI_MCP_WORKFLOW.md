# Graphiti MCP Workflow Guide

## Purpose

本指南定义 MyStocks 当前项目内对 `graphiti-mcp` 与 `graphiti-api` 的使用边界。

当前结论：

- `graphiti-mcp` 是 AI CLI 的长期记忆层
- `graphiti-api` 当前只作为已部署能力保留，不接入本仓库 runtime 代码
- Mongo control plane 仍是 main/worker 协同状态的唯一真相源

## Verified Endpoints

以下地址已于 `2026-03-16` 在当前环境中实际探活：

- Graphiti MCP health:
  - `http://localhost:8011/health`
- Graphiti MCP endpoint:
  - `http://localhost:8011/mcp`
- Graphiti API healthcheck:
  - `http://localhost:8010/healthcheck`
- Graphiti API docs:
  - `http://localhost:8010/docs`

说明：

- `http://localhost:8011/mcp/` 会重定向到 `/mcp`
- 项目 MCP 配置统一直接使用 `/mcp`

## Source-of-Truth Boundary

### Mongo Owns Coordination State

以下信息必须以 Mongo control plane 为准：

- work item creation
- assignment / dispatch
- claim / plan / submit
- ready_for_review / verified / merged
- worker progress percentage and review lifecycle

Graphiti 不得充当以下信息的权威来源：

- `work_item.status`
- 审批结果
- merge 状态
- task ownership

### Graphiti Owns Agent Memory

以下信息适合沉淀到 Graphiti：

- main CLI handoff 摘要
- worker 开工回执的自然语言说明
- 任务分解后的语义摘要
- 关键排障结论
- 文档审核结论
- 架构决策与历史事实

简化判断：

- 问“现在任务状态是什么” -> 查 Mongo
- 问“之前这个问题为什么这么改” -> 查 Graphiti

## Recommended `group_id` Layout

建议至少按职责隔离：

- `mystocks_spec_main`
  - main CLI 的长期记忆、派单结论、合并判断
- `mystocks_spec_workers`
  - worker 执行中的交付摘要、handoff 事实
- `mystocks_spec_docs`
  - 文档审核、术语收敛、规范决议
- `mystocks_spec_review`
  - review finding、follow-up 结论、验收判断

约束：

- 不要长期把所有内容都写进 `main`
- 不要把任务状态字段复制写入 Graphiti 当作状态库
- 同一类记忆尽量使用稳定 `group_id`，不要每次会话新建随机组

## Main CLI Usage

main CLI 适合在这些时机调用 Graphiti MCP：

1. 派单前
   - 搜索该任务域是否已有历史结论
2. worker 上报后
   - 写入一条 handoff / review memory
3. 合并前
   - 记录最终验收结论和 residual risks
4. 长链路中断恢复时
   - 通过 facts / episodes 恢复上下文

推荐调用顺序：

1. `get_status`
2. `search_nodes`
3. `search_memory_facts`
4. `add_memory`
5. `get_episodes`

## Worker CLI Usage

worker CLI 适合在这些时机调用 Graphiti MCP：

1. 接单开工
   - 读取与本任务相关的历史事实
2. 完成一个批次后
   - 写入批次摘要、验证结果、风险
3. 需要上报 main CLI 之前
   - 写入可复用的 handoff 说明

worker 不应把以下内容只写入 Graphiti 而不写 Mongo：

- 开工回执状态
- plan item 完成状态
- ready_for_review 申请

这些仍必须走 Mongo control plane。

## Graphiti API Status

`graphiti-api` 当前已部署并可用，但本次切换不把它接入仓库 runtime。

当前定位：

- 仅作为后续扩展能力保留
- 适用于未来的程序化写入/检索
- 若要把它接入 `coordctl`、`maestro`、后端服务或自动任务，必须单独立项

推荐后续场景：

- 自动沉淀交付总结到 Graphiti
- 由脚本批量导入架构说明、运维事件
- 做一个本仓库专用 Graphiti SDK

## First-Use Checklist

首次在本项目里用 Graphiti MCP 时，建议：

1. 先确认 `get_status`
2. 再用 `search_nodes`
3. 再用 `search_memory_facts`
4. 最后再调用 `add_memory`
5. 写入后不要立刻假定可检索，必要时用 `get_episodes` 观察落图进度

## Non-Goals For This Change

本次变更明确不做：

- 不把 Mongo 任务状态迁到 Graphiti
- 不在业务代码里新增 `graphiti-api` 调用
- 不自动导出 `TASK.md` / `TASK-REPORT.md` 到 Graphiti
- 不把 Graphiti 当 review gate 或审批系统
