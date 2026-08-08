# API 文档独立归档（api-standalone-docs）

**归档性质**: 历史参考；保留供查阅，不再随活动 API 演进

## 内容清单

| 文件 | 类型 | 状态说明 |
|---|---|---|
| `apifox-import-success-2025-11-10.md` | 一次性事件记录 | 2025-11-10 MyStocks API 成功导入 Apifox；保留作为里程碑快照 |
| `apifox-mcp-playwright-legacy.md` | 旧方案评估 | **作者已标注弃用（2026-03-17）**：当前项目停用 Apifox MCP，活动记忆 MCP 切换为 Graphiti MCP；活动文档见 `docs/guides/ai-tools/GRAPHITI_MCP_WORKFLOW.md` |
| `contract-management-api-full.md` | API 源码级参考 | 记录契约管理平台的 REST 接口（版本、差异、验证、同步）；底层实现 `src/contract_testing/` 已不在仓库中；`docs/api/contracts/README.md` 仍将其作为"归档版本"链接 |
| `contract-testing-api-full.md` | API 源码级参考 | 记录 `src.contract_testing`（SpecificationValidator、TestHooksManager 等）；底层模块已不在仓库中；保留为历史设计参考 |

## 使用规范

- 这些文件**不再随代码演进**；如活动 API 文档与归档冲突，以活动文档为准
- **不应在新代码、新文档中新增引用**；现有引用（`docs/api/contracts/README.md:49,85`）作为"源码级归档参考"链接保留
- 若需复活任一文档对应的功能，先提案（OpenSpec），迁出本归档，再更新
