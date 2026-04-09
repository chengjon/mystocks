# AI Tools Guide Family

> **导航说明**:
> 本文件是 `docs/guides/ai-tools/` 的 transition index，不是仓库共享规则、当前 agent 执行口径或唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)；若涉及具体执行入口，再结合根目录 `AGENTS.md`、根目录 `CLAUDE.md` 与当前代码核对。

## Current Entry Order

这一 family 当前角色是 `supporting`，用于保留 AI / agent 工作流、CLI 扩展说明和专题修复资料，不承担仓库级 trunk。推荐阅读顺序：

1. [`AI_QUICK_START.md`](./AI_QUICK_START.md)
2. [`AGENTS.md`](./AGENTS.md)
3. [`CLAUDE.md`](./CLAUDE.md)
4. [`GEMINI.md`](./GEMINI.md)
5. [`GRAPHITI_MCP_WORKFLOW.md`](./GRAPHITI_MCP_WORKFLOW.md)
6. [`OMC_WORKFLOW_GUIDE.md`](./OMC_WORKFLOW_GUIDE.md)
7. [`OMO_SETUP_GUIDE.md`](./OMO_SETUP_GUIDE.md)
8. [`OpenCode生产级配置与固化指南.md`](./OpenCode生产级配置与固化指南.md)

## Active Supporting Guides

- [`AI_QUICK_START.md`](./AI_QUICK_START.md)
  - 按任务类型把 AI/开发者路由到正确治理入口与功能域
- [`AGENTS.md`](./AGENTS.md)
  - agent 执行配置的扩展说明
- [`CLAUDE.md`](./CLAUDE.md)
  - Claude 扩展开发指南与历史执行说明
- [`GEMINI.md`](./GEMINI.md)
  - Gemini CLI 质量保证工作流参考
- [`GRAPHITI_MCP_WORKFLOW.md`](./GRAPHITI_MCP_WORKFLOW.md)
  - Graphiti 记忆工作流说明
- [`OMC_WORKFLOW_GUIDE.md`](./OMC_WORKFLOW_GUIDE.md)
  - OMC 使用与故障排查入口
- [`OMO_SETUP_GUIDE.md`](./OMO_SETUP_GUIDE.md)
  - OMO/OpenCode 本地配置入口
- [`OpenCode生产级配置与固化指南.md`](./OpenCode生产级配置与固化指南.md)
  - OpenCode 生产级配置与固化说明

## Retained Specialized References

- [`AGENTS_DOCUMENTATION_INDEX.md`](./AGENTS_DOCUMENTATION_INDEX.md)
  - Claude Code Agents 文档索引
- [`CLAUDE_AGENTS_SUMMARY.md`](./CLAUDE_AGENTS_SUMMARY.md)
  - Claude agents 摘要说明
- [`CLAUDE_CODE_AGENTS_MANAGEMENT_GUIDE.md`](./CLAUDE_CODE_AGENTS_MANAGEMENT_GUIDE.md)
  - Claude agents 管理细则
- [`AI_TEST_OPTIMIZER_TRAINING.md`](./AI_TEST_OPTIMIZER_TRAINING.md)
  - AI test optimizer 训练材料
- [`AI_TEST_OPTIMIZER_USER_GUIDE.md`](./AI_TEST_OPTIMIZER_USER_GUIDE.md)
  - AI test optimizer 使用指南
- [`GEMINI_PROXY_CONFIGURATION_GUIDE.md`](./GEMINI_PROXY_CONFIGURATION_GUIDE.md)
  - Gemini 代理配置专题
- [`AMP配置.md`](./AMP配置.md)
  - AMP 配置说明
- [`amp-help.md`](./amp-help.md)
  - AMP 使用帮助
- [`aider-local-maintenance.md`](./aider-local-maintenance.md)
  - aider 本地维护说明
- [`claude_code_lsp_guide.md`](./claude_code_lsp_guide.md)
  - Claude Code LSP 使用说明
- [`claude_code_plugin_marketplace_fix.md`](./claude_code_plugin_marketplace_fix.md)
  - 插件市场修复记录
- [`.ai-collaboration.md`](./.ai-collaboration.md)
  - AI 协作文档残留入口
- [`.ai-progress.md`](./.ai-progress.md)
  - AI 进度记录残留入口

## Retention Rule

- 该 family 当前保留为 `supporting`，不升级为新的 canonical docs trunk
- 根导航只保留当前仍有较高直接使用价值的 agent 入口、快速路由和 OMC/OMO 主流程说明，其余专题化材料统一通过本 index 进入
- 若后续专题化修复与 training 材料的实际入链继续下降，可继续按 bounded batch 单独评估 archive/delete
