# OpenCode 生产级配置与固化指南（fucai 版）

本指南基于 2026-02-28 的实战修复经验，目标是让 OpenCode + OMO 配置稳定、可审计、可复现。

- 官方配置文档：
  https://github.com/anomalyco/opencode/blob/dev/packages/web/src/content/docs/config.mdx
- 本指南适配端点：`https://fucaixie.xyz/v1`

## 治理状态说明（2026-03-25）

- 根目录 `opencode.json` 与 `tui.json` 当前均按 **local-only** 配置处理。
- 它们默认由 `.gitignore` 忽略，不再作为仓库显式根入口提交治理。
- 仓库内真正需要持续维护和评审的真源仍是 `.config/opencode/model/model-catalog.json` 与生成脚本。

## 一、关键结论（本次根因）

本次异常（`invalid token`、无效模型）根因是两类：

1. Token 来源不一致
- 配置仍指向旧密钥文件（非 fucaixie key），请求被网关拒绝。

2. Provider 旧命名污染
- 历史 `cpap*` 分组与当前配置合并，导致出现 `kiro-*` 等无效模型引用。

结论：必须统一 provider 分组与密钥来源，且禁止手改生成文件。

## 二、最终架构（单一真源）

### 1. 只改一个文件

- `/.config/opencode/model/model-catalog.json`

它是唯一可编辑的模型配置源，包含：
- 默认模型
- provider 启用列表
- 外部模型清单
- OMO agent 到模型映射

### 2. 自动生成文件（禁止手改）

由脚本自动生成：
- `opencode.json`（项目根目录 local-only 配置；仅在本机需要时保留）
- `/.config/oh-my-opencode.noco.json`
- `/.config/opencode/model/main.model`
- `/.config/opencode/model/small.model`
- `/.config/opencode/model/fucai.base_url`
- `/.config/opencode/model/fucai.api_key`
- `/.config/opencode/model/omo.*.model`
- `/.config/opencode/model/model-stack.env`

### 3. 生成脚本

- `scripts/opencode/sync_opencode_model_catalog.py`

## 三、Provider 规范（强制）

只允许以下分组：
- `opencode`（原生 Free 模型）
- `fucai`
- `fucai-gpt`
- `fucai-claude`
- `fucai-mini`

必须移除的旧分组：
- `cpap`, `cpap-*`, `google` 等历史分组

## 四、模型与端点规范

### 1. 端点与密钥

- BaseURL：`https://fucaixie.xyz/v1`
- API Key：`REPLACE_WITH_FUCAI_API_KEY`

建议通过文件引用注入：
- `{file:/opt/claude/mystocks_spec/.config/opencode/model/fucai.base_url}`
- `{file:/opt/claude/mystocks_spec/.config/opencode/model/fucai.api_key}`

### 2. 模型来源

外部模型必须来自：
`curl https://fucaixie.xyz/v1/models -H "Authorization: Bearer <KEY>"`

并排除 Gemini 系列（`id` 中包含 `gemini`）。

## 五、当前基线（已验证）

### 1. 你选择的 6 模型（已对齐 fucai 命名）

- `sisyphus`: `fucai-claude/claude-opus-4-6`
- `oracle`: `fucai-gpt/gpt-5.3-codex`
- `librarian`: `fucai-claude/claude-opus-4-5`
- `explore`: `fucai/grok-4.20-beta`
- `frontend`: `fucai-gpt/gpt-5.3`
- `document_writer`: `fucai-gpt/gpt-5.3`
- `multimodal_looker`: `fucai/grok-4-heavy`

### 2. 一致性结果

- 端点非 Gemini 模型：54
- catalog 非 Gemini 模型：54
- 差异：0

## 六、标准操作流程

1. 修改单一真源：
```bash
vim /opt/claude/mystocks_spec/.config/opencode/model/model-catalog.json
```

2. 一键生成：
```bash
python3 /opt/claude/mystocks_spec/scripts/opencode/sync_opencode_model_catalog.py
```

3. 语法校验：
```bash
jq empty /opt/claude/mystocks_spec/.config/oh-my-opencode.noco.json \
  /opt/claude/mystocks_spec/.config/opencode/model/model-catalog.json

[ -f /opt/claude/mystocks_spec/opencode.json ] && \
  jq empty /opt/claude/mystocks_spec/opencode.json
```

4. 角色核验：
```bash
jq -r '.oh_my_opencode.agents | to_entries[] | "\(.key)=\(.value.model)"' \
  /opt/claude/mystocks_spec/.config/oh-my-opencode.noco.json
```

## 七、排障清单

### 症状：`invalid token`

检查顺序：
1. `fucai.api_key` 文件内容是否正确。
2. 若本地存在项目级 `opencode.json`，其 provider 的 `apiKey` 是否引用 `fucai.api_key`。
3. 配置中是否残留旧 provider（`cpap*`）。

### 症状：出现 `kiro-*` 等无效模型

检查顺序：
1. `model-catalog.json` 是否仍有旧模型名。
2. `opencode.json`（如本地存在） / OMO 是否由脚本重新生成。
3. 是否存在全局配置合并污染（建议指定项目级 `OPENCODE_CONFIG`）。

## 八、安全建议

- `fucai.api_key` 建议权限：`chmod 600`
- 不要在 provider 内硬编码 key
- 每次改动都先备份

## 九、版本信息

- 版本：v3.0（fucai 分组统一版）
- 最后更新：2026-02-28
