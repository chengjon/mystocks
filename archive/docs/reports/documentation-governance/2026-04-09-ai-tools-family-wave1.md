# AI Tools Family Wave 1

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/ai-tools/` 导航暴露面的第一轮 bounded 收口，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前文档系统 trunk、治理口径或审批门禁，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与当前代码为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/guides/ai-tools/` 导航暴露面的第一轮 bounded 收口。

## Why

- `docs/guides/ai-tools/` 当前角色是 `supporting`，不是仓库级 trunk
- `docs/INDEX.md` 仍把 AI quick start、agent 执行入口、workflow 说明、训练材料、专题修复和残留进度文档全部平铺暴露
- 这会让高频入口与历史专题材料处于同一优先级，增加根导航噪音

## Changes

- 将 `docs/guides/ai-tools/INDEX.md` 改写为 family transition index
- 收薄 `docs/INDEX.md` 中 Ai Tools family 的根导航
- 根导航现在优先保留：
  - `guides/ai-tools/INDEX.md`
  - `guides/ai-tools/AI_QUICK_START.md`
  - `guides/ai-tools/AGENTS.md`
  - `guides/ai-tools/CLAUDE.md`
  - `guides/ai-tools/GEMINI.md`
  - `guides/ai-tools/GRAPHITI_MCP_WORKFLOW.md`
  - `retired historical workflow guide` (retired 2026-05-13)
  - `guides/ai-tools/OMO_SETUP_GUIDE.md`
  - `guides/ai-tools/OpenCode生产级配置与固化指南.md`
  - `Supporting Guides` -> `guides/ai-tools/INDEX.md`
- 将 agent 管理摘要、optimizer 训练、AMP、代理配置、插件修复与残留进度文档收回到 family index 内部阅读

## Gate Check

- canonical replacement:
  - 无新增 canonical trunk；该 family 继续保持 `supporting`
- family transition index:
  - `docs/guides/ai-tools/INDEX.md`
- active navigation:
  - `docs/INDEX.md` 已减少对 training/fix/residual leaf docs 的直接暴露
- retention duty:
  - `AGENTS_DOCUMENTATION_INDEX.md`
  - `CLAUDE_AGENTS_SUMMARY.md`
  - `CLAUDE_CODE_AGENTS_MANAGEMENT_GUIDE.md`
  - `AI_TEST_OPTIMIZER_TRAINING.md`
  - `AI_TEST_OPTIMIZER_USER_GUIDE.md`
  - `GEMINI_PROXY_CONFIGURATION_GUIDE.md`
  - `AMP配置.md`
  - `amp-help.md`
  - `aider-local-maintenance.md`
  - `claude_code_lsp_guide.md`
  - `claude_code_plugin_marketplace_fix.md`
  - `.ai-collaboration.md`
  - `.ai-progress.md`
  - 以上文档继续保留为 specialized/reference docs

## Expected Effect

- 当时根导航优先暴露 AI quick start、agent 主入口与 historical workflow / OMO 主流程说明；其中 historical workflow guide 已于 2026-05-13 退役
- 训练材料、专题修复与残留索引不再与高频入口平级暴露，但仍可通过 family index 进入
- 后续若这些专题化材料的实际入链继续下降，可继续逐份评估 archive/delete
