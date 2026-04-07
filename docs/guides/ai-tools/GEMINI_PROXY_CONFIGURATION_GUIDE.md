# Gemini 代理配置成功经验与固化指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


> 说明：该指南已从仓库根目录迁移到 `docs/guides/`，作为当前活跃工具文档维护。

## 0. 适用范围
- 项目：`/opt/claude/mystocks_spec`
- 目标：Gemini CLI 在代理环境下稳定运行，并可快速定位配置问题
- 原则：`先清洗 -> 再配置 -> 再验证`

## 1) 正确设置方法

### 1.1 项目级 `.env`
文件：`/opt/claude/mystocks_spec/.gemini/.env`

```bash
GEMINI_API_KEY=<YOUR_API_KEY>
GOOGLE_GEMINI_BASE_URL=https://fucaixie.xyz
```

要点：
- Base URL 必须是根地址，不能带 `/v1` 或 `/v1beta`。

### 1.2 项目级 `settings.json`
文件：`/opt/claude/mystocks_spec/.gemini/settings.json`

```json
{
  "$schema": "https://raw.githubusercontent.com/google-gemini/gemini-cli/main/schemas/settings.schema.json",
  "model": { "name": "gemini-3.1-pro" },
  "general": { "checkpointing": { "enabled": false } },
  "context": { "fileName": ["GEMINI.md"] },
  "agents": {
    "overrides": {
      "codebase_investigator": { "enabled": false },
      "cli_help": { "enabled": false }
    }
  },
  "useWriteTodos": false,
  "mcp": {
    "excluded": ["chrome-devtools", "context7", "playwright", "puppeteer"]
  }
}
```

要点：
- `tools.exclude` 已弃用，改用 Policy Engine。
- `context.fileName` 固定为 `GEMINI.md`，减少上下文干扰。

### 1.3 Policy Engine（替代 `tools.exclude`）
文件：`/opt/claude/mystocks_spec/.gemini/policies/tool-guard.toml`

```toml
[[rule]]
toolName = "codebase_investigator"
decision = "deny"
priority = 950

deny_message = "This workspace disables codebase_investigator. Use standard file tools instead."

[[rule]]
toolName = "write_todos"
decision = "deny"
priority = 950

deny_message = "This workspace disables write_todos. Use regular workflow tracking files instead."
```

### 1.4 `GEMINI.md` 内容规范（按官方）
参考：`/opt/mydoc/cliproxyapi/gemini/docs/Provide-context.md`

要点：
- 仅保留稳定、长期有效的项目约束。
- 不写临时任务日志和一次性操作过程。
- 不写其他 CLI 平台的工具名或调用规则，避免误导工具调用。

### 1.5 固化启动
脚本：`/opt/claude/mystocks_spec/scripts/gemini_clean_start.sh`

```bash
cd /opt/claude/mystocks_spec
./scripts/gemini_clean_start.sh
```

---

## 2) 如何确认当前方法正确

### 2.1 静态检查

```bash
sed -n '1,120p' /opt/claude/mystocks_spec/.gemini/.env
sed -n '1,260p' /opt/claude/mystocks_spec/.gemini/settings.json
sed -n '1,200p' /opt/claude/mystocks_spec/.gemini/policies/tool-guard.toml
sed -n '1,260p' /opt/claude/mystocks_spec/.gemini/GEMINI.md
```

### 2.2 运行时合并配置检查

```bash
node --input-type=module -e "import {loadSettings} from '/root/.nvm/versions/node/v24.7.0/lib/node_modules/@google/gemini-cli/dist/src/config/settings.js'; const s=loadSettings('/opt/claude/mystocks_spec'); console.log(JSON.stringify({model:s.merged.model?.name,useWriteTodos:s.merged.useWriteTodos,contextFileName:s.merged.context?.fileName,toolsExclude:s.merged.tools?.exclude},null,2));"
```

通过标准：
- `model = gemini-3.1-pro`
- `useWriteTodos = false`
- `contextFileName = ["GEMINI.md"]`
- `toolsExclude` 不存在

### 2.3 代理模型可见性检查

```bash
curl -sS -H "Authorization: Bearer <YOUR_API_KEY>" "https://fucaixie.xyz/v1/models" | jq -r '.data[].id' | rg '^gemini-'
```

---

## 3) 设置前必须清洗的位置（防干扰）

### 3.1 环境变量层

```bash
unset GEMINI_MODEL GEMINI_API_KEY GOOGLE_GEMINI_BASE_URL GOOGLE_GENAI_API_VERSION
env | grep -E '^GEMINI_|^GOOGLE_GEMINI_BASE_URL|^GOOGLE_GENAI_API_VERSION' || true
```

### 3.2 用户级配置层
检查并清理：
- `~/.gemini/.env`
- `~/.gemini/settings.json`
- `~/.gemini/policies/*.toml`
- `~/.gemini/GEMINI.md`

重点：
- 删除 `tools.exclude`
- 删除/修正错误模型固定值和 Base URL
- 清理冲突的全局 context 指令

### 3.3 Shell 启动脚本层

```bash
rg -n "GEMINI_MODEL|GEMINI_API_KEY|GOOGLE_GEMINI_BASE_URL|GOOGLE_GENAI_API_VERSION" \
  ~/.zshrc ~/.zprofile ~/.bashrc ~/.profile 2>/dev/null || true
```

### 3.4 会话缓存层
清理：
- `~/.gemini/tmp/mystocks-spec/checkpoint-now.json`
- `~/.gemini/tmp/mystocks-spec/chats/session-*.json`
- `~/.gemini/tmp/mystocks-spec/tool_output/*`
- `~/.gemini/tmp/mystocks-spec/tool-outputs/*`

建议：
- 启动后执行 `/memory show` 与 `/memory refresh` 确认 context 实际加载内容。

---

## 4) 本次实测结论（关键）

1. 代理下 `gemini-3.1-pro`/`gemini-3-pro`/`gemini-2.5-pro`/`gemini-2.5-flash` 都可见。
2. 代理对 Gemini 原生工具回调链路（`functionCall -> functionResponse`）存在不兼容。
3. 四个模型都可复现：

```text
No tool output found for function call call_1
```

结论：
- 该错误不是 `settings.json`/`GEMINI.md` 写法导致，而是代理函数回调转换层问题。
- 同代理内切模型名通常不能根治。

建议路径：
1. 优先切换到官方 Gemini 端点（完整兼容 Gemini CLI 工具回路）。
2. 或修复代理端的函数回调转换逻辑后再使用当前代理。

---

更新日期：2026-02-28

---

## 5) 代理实现方最小修复清单（针对 `call_1`）

1. 修复 `functionCall -> functionResponse` 关联逻辑  
- 在 `generateContent/streamGenerateContent` 转换链路中，按输入 `contents` 顺序重建待回调列表。  
- 为每个 `functionCall` 分配确定性 id（如 `call_1`, `call_2`），并在处理 `functionResponse` 时正确匹配并出队。  

2. 修复 Gemini/OpenAI 双向消息映射  
- Gemini `functionCall` -> OpenAI `assistant.tool_calls[]`（必须有稳定 `id`）。  
- Gemini `functionResponse` -> OpenAI `tool` 消息（必须携带匹配的 `tool_call_id`）。  
- OpenAI `assistant.tool_calls[]` -> Gemini `functionCall` 时，禁止丢失 `name/args`。  

3. 严格校验工具名与参数  
- 禁止生成空工具名；检测到空字符串时直接返回本地 400（不要继续转发到上游）。  
- 禁止注入占位工具名（如 `undefined_tool_name`）。  
- 对缺失必填参数的工具调用，返回确定性本地错误，不进入错误重试拼装。  

4. 统一错误包装，不再污染下游输入  
- 当前 `params must have required property 'pattern'` 这类本地校验错误，应留在本地并终止本轮工具回路。  
- 不应再把半成品工具调用拼回模型输入，避免触发 `Invalid 'input[x].name': empty string`。  

5. 为代理增加 4 个回归用例（必须）  
- 用例 A：单工具单回调（应成功）。  
- 用例 B：工具缺参（应返回本地参数错误，不出现空工具名）。  
- 用例 C：两个工具串行回调（应按 id 正确匹配）。  
- 用例 D：`streamGenerateContent` 与非流式结果一致。  

6. 交付验收标准  
- Gemini CLI 内执行“会触发工具调用”的提示，不再出现：  
  - `No tool output found for function call call_1`  
  - `Invalid 'input[7].name': empty string`  
- 同一会话中连续多次工具调用稳定通过。  
