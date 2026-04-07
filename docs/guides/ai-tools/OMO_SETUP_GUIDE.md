# OMO Setup Guide

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## 目标

建立一套可维护、可审计、低风险的 OMO（oh-my-opencode）模型配置流程：

- 只维护一个文件：`.config/opencode/model/model-catalog.json`
- 通过脚本自动生成 OMO 与 OpenCode 配置
- 默认保留 OpenCode Free 模型能力，同时接入外部端点模型（排除 Gemini）

## 核心原则

1. 单一真源（Single Source of Truth）
- 模型与角色映射只在 `model-catalog.json` 修改。

### 治理状态说明（2026-03-25）

- 根目录 `opencode.json` 与 `tui.json` 当前按 **local-only** 配置处理。
- 这意味着它们可以因本地工具需要存在于仓库根目录，但默认由 `.gitignore` 忽略，不再作为仓库显式治理入口。
- 仓库级真源仍然是 `.config/opencode/model/model-catalog.json` 与生成脚本，而不是把根目录 `opencode.json` 当作需要提交和评审的主资产。

2. 自动生成，不手改产物
- 不直接手改以下生成文件：
  - `opencode.json`
  - `.config/oh-my-opencode.noco.json`
  - `.config/opencode/model/*.model`
  - `.config/opencode/model/model-stack.env`

3. Provider 一致性
- `opencode.json` 与 `oh-my-opencode.noco.json` 的 provider 必须一致。

4. 安全优先
- API Key 通过文件引用：`{file:/opt/claude/mystocks_spec/.config/opencode/model/fucai.api_key}`
- 不在 provider 中硬编码密钥。

## 文件结构

- 单一真源：
  - `.config/opencode/model/model-catalog.json`

- 自动生成：
  - `opencode.json`（项目根目录 local-only 配置；如本地存在，进入本仓库运行 `opencode` 时优先生效）
  - `.config/oh-my-opencode.noco.json`
  - `.config/opencode/model/main.model`
  - `.config/opencode/model/small.model`
  - `.config/opencode/model/fucai.base_url`
  - `.config/opencode/model/fucai.api_key`
  - `.config/opencode/model/omo.*.model`
  - `.config/opencode/model/model-stack.env`

- 生成脚本：
  - `scripts/opencode/sync_opencode_model_catalog.py`

## model-catalog.json 字段说明

```json
{
  "defaults": {
    "main_model": "fucai-claude/claude-opus-4-6",
    "small_model": "opencode/glm-4.7-free",
    "fucai_base_url": "https://fucaixie.xyz/v1",
    "fucai_api_key": "sk-***"
  },
  "enabled_providers": ["opencode", "fucai", "fucai-gpt", "fucai-claude", "fucai-mini"],
  "opencode_free_models": ["opencode/glm-4.7-free"],
  "external_models": {
    "fucai-gpt": ["gpt-5.3-codex"],
    "fucai-claude": ["claude-opus-4-6"],
    "fucai-mini": ["MiniMax 2.5"],
    "fucai": ["grok-4.20-beta"]
  },
  "omo_agents": {
    "sisyphus": "fucai-claude/claude-opus-4-6",
    "oracle": "fucai-gpt/gpt-5.3-codex",
    "librarian": "fucai-claude/claude-opus-4-5",
    "explore": "fucai/grok-4.20-beta",
    "frontend": "fucai-gpt/gpt-5.3",
    "document_writer": "fucai-gpt/gpt-5.3",
    "multimodal_looker": "fucai/grok-4-heavy"
  }
}
```

## 标准更新流程

1. 编辑单一真源文件
```bash
vim /opt/claude/mystocks_spec/.config/opencode/model/model-catalog.json
```

2. 运行生成脚本
```bash
python3 /opt/claude/mystocks_spec/scripts/opencode/sync_opencode_model_catalog.py
```

3. 验证配置
```bash
jq empty /opt/claude/mystocks_spec/.config/oh-my-opencode.noco.json \
  /opt/claude/mystocks_spec/.config/opencode/model/model-catalog.json

# 如本地存在项目级 opencode.json，再额外校验它
[ -f /opt/claude/mystocks_spec/opencode.json ] && \
  jq empty /opt/claude/mystocks_spec/opencode.json
```

4. 快速核对角色映射
```bash
jq -r '.oh_my_opencode.agents | to_entries[] | "\(.key)=\(.value.model)"' \
  /opt/claude/mystocks_spec/.config/oh-my-opencode.noco.json
```

## 当前基线角色映射（2026-02-28）

- `sisyphus`: `fucai-claude/claude-opus-4-6`
- `oracle`: `fucai-gpt/gpt-5.3-codex`
- `librarian`: `fucai-claude/claude-opus-4-5`
- `explore`: `fucai/grok-4.20-beta`
- `frontend`: `fucai-gpt/gpt-5.3`
- `document_writer`: `fucai-gpt/gpt-5.3`
- `multimodal_looker`: `fucai/grok-4-heavy`

## 常见问题

1. 修改后未生效
- 先确认执行过同步脚本。
- 再确认当前目录在项目仓库内。
- 若你依赖项目根目录 `opencode.json` 覆盖全局，请确认该 local-only 文件在本机工作区中确实存在。

2. provider 不一致
- 重新运行同步脚本，脚本会统一 provider 集合。

3. 出现 Gemini 模型
- 检查 `model-catalog.json` 是否误加入 Gemini。
- 重新运行同步脚本覆盖生成。

4. API 调用失败
- 检查 `fucai_base_url`。
- 检查 `.config/opencode/model/fucai.api_key` 是否有效。

## 建议的变更纪律

- 每次只改 `model-catalog.json` 后同步。
- 不要手改生成文件，避免漂移。
- 变更后至少执行一次 `jq empty` + 角色映射核对。
