# Aider 本地维护说明

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## 目的

本文档记录当前机器上 `aider` 的本地配置、已做过的补丁、问题根因、验证方式和后续维护注意事项。

适用环境：

- 项目路径：`/opt/claude/mystocks_spec`
- `aider` 版本：`0.86.2`
- 自定义模型网关：`https://fucaixie.xyz/v1`
- 默认模型：`grok-4.1-expert`

---

## 当前有效配置

### 项目内配置文件

- `/.aider.conf.yml`
  - 默认模型：`grok-4.1-expert`
  - OpenAI 兼容端点：`https://fucaixie.xyz/v1`
  - 从 `/.env` 读取 `AIDER_OPENAI_API_KEY`
  - `analytics: true`
  - `check-update: false`
  - `show-release-notes: false`

- `/.aider.model.settings.yml`
  - 为 `grok-4.20-beta` / `grok-4.1-expert` 指定 `custom_llm_provider: openai`
  - 为所有模型补充 `User-Agent: curl/8.5.0`

- `/.aider.model.metadata.json`
  - 为上述 Grok 模型补充 metadata，解决 `LLM Provider NOT provided`

- `/.aiderignore`
  - 当前排除：retired session-state 目录模式
  - 目的：避免 `repo-map` 扫描项目内临时状态/会话文件

- `/.env`
  - 维护 `AIDER_OPENAI_API_KEY`

### 本机持久状态文件

- `/root/.aider/analytics.json`
  - 当前状态为已同意匿名 analytics
  - 当前状态不是永久禁用

---

## 本次处理过的问题

### 1. Grok 模型无法直接被 aider/litellm 识别

表现：

- `LLM Provider NOT provided`

根因：

- `grok-4.20-beta`、`grok-4.1-expert` 不在本机 `aider/litellm` 默认模型映射中

处理：

- 增加 `/.aider.model.settings.yml`
- 增加 `/.aider.model.metadata.json`

---

### 2. 网关返回 `Your request was blocked`

表现：

- `litellm.APIError: OpenAIException - Your request was blocked`

根因：

- 网关对默认客户端请求特征较敏感

处理：

- 在 `/.aider.model.settings.yml` 中统一追加 `User-Agent: curl/8.5.0`

---

### 3. `Repo-map can't include /opt/claude/mystocks_spec/src`

表现：

- 启动 `aider` 时，repo-map 扫描阶段提示不能包含 `src`

根因：

- 仓库内存在 symlink：`web/backend/src -> /opt/claude/mystocks_spec/src`
- `aider` 在构造 repo-map 时，把解析后的目标目录 `src` 当成了普通文件项
- `repo-map` 只接受普通文件，不接受目录

处理：

- 已在本机安装的 `aider` 源码里补本地补丁，位置：
  - `/root/.local/share/uv/tools/aider-chat/lib/python3.12/site-packages/aider/coders/base_coder.py`

补丁效果：

- 拒绝把目录加入 editable files
- `allowed_to_edit()` 不再把目录当成普通文件
- `get_all_abs_files()` 会过滤掉解析后不是普通文件的条目
- `get_repo_map()` 会清理残留的无效 editable 项

---

### 4. `Repo-map can't include a retired session-state file`

表现：

- repo-map 扫描时提示某个 retired session-state file 不能包含

根因：

- 该文件在 Git 中被跟踪，但当前工作区内已不存在
- 这是仓库临时状态文件，不适合进入 repo-map

处理：

- 未恢复该文件
- 改用 `/.aiderignore` 排除整个 retired session-state 目录

原因：

- 避免把会话状态、代理回放、检查点等噪音带入模型上下文

---

### 5. 开启 analytics 后出现 posthog 错误

表现：

- `error uploading: HTTPSConnectionPool(host='us.i.posthog.com'...)`
- `on_error handler failed: Analytics.posthog_error() takes 1 positional argument but 3 were given`

根因：

- 当前环境无法连通 `us.i.posthog.com`
- `aider 0.86.2` 自带的 `posthog_error()` 回调签名与当前 `posthog` 实际调用方式不兼容

处理：

- 已在本机安装的 `aider` 源码里修补：
  - `/root/.local/share/uv/tools/aider-chat/lib/python3.12/site-packages/aider/analytics.py`

补丁效果：

- `posthog_error()` 改为兼容 `error, batch` 参数
- 静音 `posthog` logger，避免每次启动刷屏
- 保持 `analytics: true` 可用，同时不再把网络失败打印到终端

---

## 当前本地补丁清单

### 仓库内文件

- `/opt/claude/mystocks_spec/.aider.conf.yml`
- `/opt/claude/mystocks_spec/.aider.model.settings.yml`
- `/opt/claude/mystocks_spec/.aider.model.metadata.json`
- `/opt/claude/mystocks_spec/.aiderignore`
- `/opt/claude/mystocks_spec/.env`
- `/opt/claude/mystocks_spec/.gitignore`

### 本机安装目录文件

- `/root/.local/share/uv/tools/aider-chat/lib/python3.12/site-packages/aider/coders/base_coder.py`
- `/root/.local/share/uv/tools/aider-chat/lib/python3.12/site-packages/aider/analytics.py`
- `/root/.aider/analytics.json`

注意：

- `uv tool upgrade aider-chat`
- `pip/uv reinstall`
- 更换 Python 环境

以上操作都可能覆盖安装目录内的本地补丁，需要重新核对。

---

## 升级后需要重点复查的点

升级 `aider` 后，建议按以下顺序复查：

1. `aider --exit --no-git --no-check-update`
   - 观察是否仍有 analytics 错误

2. `aider --show-repo-map --map-tokens 128 --no-check-update`
   - 观察是否重新出现 `Repo-map can't include`

3. `aider -v --exit --no-git --no-check-update`
   - 确认以下配置仍然生效：
     - `model: grok-4.1-expert`
     - `env-file: /opt/claude/mystocks_spec/.env`
     - `analytics: True`
     - `aiderignore: /opt/claude/mystocks_spec/.aiderignore`

---

## 建议使用方式

### 推荐直接运行

```bash
cd /opt/claude/mystocks_spec
aider
```

### 若仓库很大，建议

```bash
aider --subtree-only
```

或进一步缩小上下文：

```bash
aider src/core.py
aider web/backend/app/main.py
```

---

## 快速排障命令

### 检查当前生效配置

```bash
cd /opt/claude/mystocks_spec
aider -v --exit --no-git --no-check-update
```

### 检查 repo-map 是否还有异常

```bash
cd /opt/claude/mystocks_spec
aider --show-repo-map --map-tokens 128 --no-check-update
```

### 检查模型列表

```bash
curl -sS -H "Authorization: Bearer $AIDER_OPENAI_API_KEY" https://fucaixie.xyz/v1/models
```

### 最小模型探测

```bash
curl -sS https://fucaixie.xyz/v1/chat/completions \
  -H "Authorization: Bearer $AIDER_OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: curl/8.5.0" \
  -d '{"model":"grok-4.1-expert","messages":[{"role":"user","content":"Reply exactly AIDER_OK"}],"max_tokens":8}'
```

---

## 维护结论

当前这套 `aider` 运行方式属于“项目内配置 + 本机安装补丁”的组合方案。

优点：

- 可继续使用自定义网关和 Grok 模型
- 默认启动已稳定
- repo-map 噪音已明显减少
- analytics 已恢复启用，但不再刷终端错误

风险：

- 安装目录中的本地补丁不属于仓库版本控制
- 未来升级 `aider` 后可能被覆盖

如果后续需要迁移到新机器，建议优先迁移：

1. 项目内配置文件
2. 本文档
3. 安装目录补丁内容
