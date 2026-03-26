Amp CLI

本指南介绍如何将 CLIProxyAPI 与 Amp CLI 及 Amp IDE 扩展配合使用，让你能够通过 OAuth 在 Amp CLI 中使用现有的 Google/ChatGPT/Claude 订阅。
概述

Amp CLI 集成通过增加专用路由来支持 Amp 的 API 调用模式，同时仍与现有 CLIProxyAPI 功能保持完全兼容。因此，你可以在同一台代理服务器上同时使用传统的 CLIProxyAPI 功能和 Amp CLI。
主要特性

    提供商路由别名：将 Amp 的 /api/provider/{provider}/v1... 路径模式映射到 CLIProxyAPI 的处理程序。
    管理代理：通过安全的上游 API 密钥，将账户管理请求转发到 Amp 控制平面。
    智能回退：自动将未配置的模型路由到 ampcode.com。
    安全优先：管理路由需要 API 密钥认证（可选：限制到 localhost）。
    自动处理 gzip：自动解压来自 Amp 上游的响应。

你可以做什么

    将 Amp CLI 与你的 Google 账户配合使用（Gemini 3 Pro Preview、Gemini 2.5 Pro、Gemini 2.5 Flash）
    将 Amp CLI 与你的 ChatGPT Plus/Pro 订阅配合使用（GPT-5、GPT-5 Codex 模型）
    将 Amp CLI 与你的 Claude Pro/Max 订阅配合使用（Claude Sonnet 4.5、Opus 4.1）
    将 Amp IDE 扩展（VS Code、Cursor、Windsurf 等）与同一个代理配合使用
    在同一个代理服务器下运行多个 CLI 工具（Factory + Amp）
    自动将未配置的模型路由到 ampcode.com

你应该对哪些提供商进行 OAuth 登录？

重要提示：你需要对哪些提供商进行 OAuth 登录，取决于你安装的 Amp 版本当前使用的模型和功能。Amp 会为不同的代理模式和专用子代理使用不同的提供商：

    Smart 模式：使用 Google/Gemini 模型（Gemini 3 Pro）
    Rush 模式：使用 Anthropic/Claude 模型（Claude Haiku 4.5）
    Oracle 子代理：使用 OpenAI/GPT 模型（GPT-5 medium reasoning）
    Librarian 子代理：使用 Anthropic/Claude 模型（Claude Sonnet 4.5）
    Search 子代理：使用 Anthropic/Claude 模型（Claude Haiku 4.5）
    Review 功能：使用 Google/Gemini 模型（Gemini 2.5 Flash-Lite）

有关 Amp 使用哪些模型的最新信息，请参阅 Amp 模型文档。
回退行为

CLIProxyAPI 采用智能回退机制：

    已在本地完成该提供商的 OAuth 登录（--login、--codex-login、--claude-login）：
        请求会使用你的 OAuth 订阅（ChatGPT Plus/Pro、Claude Pro/Max、Google 账户）
        你可以使用订阅自带的用量配额
        不消耗 Amp 点数

    未在本地完成该提供商的 OAuth 登录：
        请求会自动转发到 ampcode.com
        使用 Amp 后端的提供商连接
        如果该提供商为付费服务（OpenAI、Anthropic 付费层级），则需要 Amp 点数
        如果 Amp 点数余额不足，可能会导致报错

建议：对你拥有订阅的所有提供商都进行 OAuth 登录，以最大化订阅价值并尽量减少 Amp 点数消耗。如果你未订阅 Amp 使用的全部提供商，请确保你有足够的 Amp 点数用于回退请求。
架构
请求流程

Amp CLI/IDE
  ↓
  ├─ 提供商 API 请求 (/api/provider/{provider}/v1/...)
  │   ↓
  │   ├─ 模型在本地配置了吗？
  │   │   是 → 使用本地 OAuth 令牌（OpenAI/Claude/Gemini 处理程序）
  │   │   否 → 转发到 ampcode.com（反向代理）
  │   ↓
  │   响应
  │
  └─ 管理请求 (/api/auth, /api/user, /api/threads, ...)
      ↓
      ├─ 使用 CLIProxyAPI 的 `api-keys` 进行认证
      ↓
      ├─ 可选：限制为 localhost
      ↓
      └─ 反向代理到 ampcode.com（使用 `upstream-api-key`）
          ↓
          响应（若为 gzip 压缩则自动解压）

组件

Amp 集成是作为一个模块化的路由模块（internal/api/modules/amp/）实现的，包含以下组件：

    路由别名 (routes.go)：将 Amp 风格的路径映射到标准处理程序
    反向代理 (proxy.go)：将管理请求转发到 ampcode.com
    回退处理程序 (fallback_handlers.go)：将未配置的模型路由到 ampcode.com
    密钥管理 (secret.go)：带缓存的多源 API 密钥解析
    主模块 (amp.go)：协调注册和配置

配置
基础配置

将 ampcode 块添加到你的 config.yaml 中（从 v6.5.37 开始，旧版的 amp-upstream-* 键会在加载时自动迁移并重写为该结构）：

# 供客户端（例如 Amp CLI、VS Code）向 CLIProxyAPI 认证的 API 密钥
api-keys:
  - "your-client-secret-key" # 给你的客户端使用的示例密钥

ampcode:
  # Amp 上游控制平面（管理路由必需）
  upstream-url: "https://ampcode.com"
  # CLIProxyAPI 用来向 ampcode.com 认证的 API 密钥
  # 从 https://ampcode.com/settings 获取
  upstream-api-key: "your-ampcode-api-key-goes-here"
  # 可选：将管理路由限制在 localhost（默认：false）
  restrict-management-to-localhost: false
  # 可选：将缺失的 Amp 模型映射到本地模型
  # model-mappings:
  #   - from: "claude-opus-4.5"
  #     to: "claude-sonnet-4"

安全设置
管理路由的 API 密钥认证

从 v6.6.15 版本开始，Amp 管理路由（/api/auth、/api/user、/api/threads、/threads 等）由 CLIProxyAPI 的标准 API 密钥认证中间件保护。

    如果你在 config.yaml 中配置了 api-keys（推荐），这些路由要求请求携带有效的 API 密钥（Authorization: Bearer <key> 或 X-Api-Key: <key>），否则返回 401 Unauthorized。
    本地认证成功后，代理会移除客户端的 Authorization/X-Api-Key，并使用 ampcode.upstream-api-key 调用上游的 ampcode.com 服务。

ampcode.restrict-management-to-localhost

默认值：false

启用后，管理路由（/api/auth、/api/user、/api/threads 等）只接受来自 localhost（127.0.0.1、::1）的连接。这可以防止：

    浏览器“路过式”攻击（Drive-by browser attacks）
    对管理端点的远程访问
    基于 CORS 的攻击
    请求头欺骗攻击（例如 X-Forwarded-For: 127.0.0.1）

工作原理

此限制使用实际的 TCP 连接地址 (RemoteAddr)，而不是像 X-Forwarded-For 这样的 HTTP 头部。这可以防止头部欺骗攻击，但有重要的影响：

    ✅ 适用于直接连接：直接在你的机器或服务器上运行 CLIProxyAPI
    ⚠️ 在反向代理后可能无法工作：如果部署在 nginx、Cloudflare 或其他代理之后，连接将看起来来自代理的 IP，而不是 localhost

反向代理部署

如果你需要在反向代理（nginx, Caddy, Cloudflare Tunnel 等）后面运行 CLIProxyAPI：

    保持 localhost 限制为禁用状态（默认）：

    ampcode:
      restrict-management-to-localhost: false

    确保已启用 API 密钥认证（推荐）：
        在 config.yaml 中配置 api-keys，并让客户端发送密钥
        结合防火墙/VPN/零信任控制来减少暴露面

    nginx 配置示例（阻止对管理路由的外部访问）：

    location /api/auth { deny all; }
    location /api/user { deny all; }
    location /api/threads { deny all; }
    location /api/internal { deny all; }

注意：ampcode.restrict-management-to-localhost 是一个额外的加固选项；在反向代理后面，通常保持为 false。
设置
1. 配置 CLIProxyAPI

创建或编辑 config.yaml。你需要准备两类 API 密钥：

    api-keys：供像 Amp CLI 这样的客户端连接到你的 CLIProxyAPI 实例。
    ampcode.upstream-api-key：供 CLIProxyAPI 连接到 ampcode.com 后端。请从 https://ampcode.com/settings 获取。

port: 8317
auth-dir: "~/.cli-proxy-api"

# 供客户端（例如 Amp CLI）使用的 API 密钥
api-keys:
  - "your-client-secret-key" # 你可以更改此密钥

# Amp 集成
ampcode:
  upstream-url: "https://ampcode.com"
  # 你在 ampcode.com 的个人 API 密钥
  upstream-api-key: "paste-your-ampcode-api-key-here"
  restrict-management-to-localhost: false

# 其他标准设置...
debug: false
logging-to-file: true

2. 对提供商进行 OAuth 登录

对你想使用的提供商进行 OAuth 登录：

Google 账户 (Gemini 2.5 Pro, Gemini 2.5 Flash, Gemini 3 Pro Preview):

./cli-proxy-api --login

ChatGPT Plus/Pro (GPT-5, GPT-5 Codex):

./cli-proxy-api --codex-login

Claude Pro/Max (Claude Sonnet 4.5, Opus 4.1):

./cli-proxy-api --claude-login

令牌会保存到：

    Gemini: ~/.cli-proxy-api/gemini-<email>.json
    OpenAI Codex: ~/.cli-proxy-api/codex-<email>.json
    Claude: ~/.cli-proxy-api/claude-<email>.json

3. 启动代理

./cli-proxy-api --config config.yaml

4. 配置 Amp CLI
选项 A：设置文件

Amp CLI 使用两个配置文件：

    设置文件：~/.config/amp/settings.json - 通用设置
    密钥文件：~/.local/share/amp/secrets.json - 敏感凭证（API 密钥）

编辑 ~/.config/amp/settings.json 配置 URL：

{
  "amp.url": "http://localhost:8317"
}

编辑 ~/.local/share/amp/secrets.json 配置 API 密钥：

{
  "apiKey@http://localhost:8317": "your-client-secret-key"
}

选项 B：环境变量

export AMP_URL=http://localhost:8317
export AMP_API_KEY=your-client-secret-key

有了这个配置，amp login 命令就不再需要了。
5. 使用 Amp

现在你已经准备好使用 Amp 了。所有请求都将通过你的代理进行路由。

amp "用 Python 写一个 hello world 程序"

6. (可选) 配置 Amp IDE 扩展

该代理也适用于 VS Code、Cursor、Windsurf 等 Amp IDE 扩展。

    在你的 IDE 中打开 Amp 扩展设置。
    将 Amp URL 设置为 http://localhost:8317。
    将 Amp API Key 设置为你配置的密钥（例如 your-client-secret-key）。
    开始在你的 IDE 中使用 Amp。 CLI 和 IDE 可以同时使用该代理。

用法
支持的路由
提供商别名（始终可用）

即使没有配置 ampcode.upstream-url，这些路由也能工作：

    /api/provider/openai/v1/chat/completions
    /api/provider/openai/v1/responses
    /api/provider/anthropic/v1/messages
    /api/provider/google/v1beta/models/:action

Amp CLI 调用这些路由时，会使用你在 CLIProxyAPI 中为对应提供商配置的 OAuth 令牌。
管理路由（需要 ampcode.upstream-url）

这些路由会通过反向代理转发到 ampcode.com：

    /api/auth - 认证
    /api/user - 用户资料
    /api/meta - 元数据
    /api/threads - 对话线程
    /api/telemetry - 用量遥测
    /api/internal - 内部 API

安全：需要一个 API 密钥；ampcode.restrict-management-to-localhost 是可选的（默认：false）。
模型回退行为

当 Amp 请求一个模型时：

    检查本地配置：CLIProxyAPI 是否有该模型提供商的 OAuth 令牌？
    如果有：路由到本地处理程序（使用你的 OAuth 订阅）
    如果没有：转发到 ampcode.com（使用 Amp 的默认路由）

这实现了无缝的混合使用：

    你已配置的模型（Gemini, ChatGPT, Claude）→ 你的 OAuth 订阅
    你未配置的模型 → Amp 的默认提供商

API 调用示例

使用本地 OAuth 进行聊天补全：

curl http://localhost:8317/api/provider/openai/v1/chat/completions \
  -H "Authorization: Bearer <your-cli-proxy-api-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-5",
    "messages": [{"role": "user", "content": "Hello"}]
  }'

管理端点（需要 API 密钥）：

curl http://localhost:8317/api/user \
  -H "Authorization: Bearer <your-cli-proxy-api-key>"

故障排查
常见问题
症状	可能的原因	解决方法
/api/provider/... 404	路由路径不正确	确保路径完全匹配：/api/provider/{provider}/v1...
/api/user 401	缺少/无效的 API 密钥	配置 api-keys 并发送 Authorization: Bearer <key> 或 X-Api-Key: <key>
/api/user 403	启用了 localhost 限制且请求来自远程	从同一台机器运行或将 ampcode.restrict-management-to-localhost 设置为 false
提供商返回 401/403	缺少/过期的 OAuth	重新运行 --codex-login 或 --claude-login
Amp gzip 错误	响应解压缩问题	更新到最新版本；自动解压应能处理此问题
模型请求未走代理	Amp URL 配置错误	检查 amp.url 设置或 AMP_URL 环境变量
CORS 错误	受保护的管理端点	使用 CLI/终端，而不是浏览器
诊断

检查代理日志：

# 如果 logging-to-file: true
tail -f var/log/requests.log

# 如果在 tmux 中运行
tmux attach-session -t proxy

临时启用调试模式：

debug: true

测试基础连通性：

# 检查代理是否正在运行
curl http://localhost:8317/v1/models

# 检查 Amp 专用路由
curl http://localhost:8317/api/provider/openai/v1/models

验证 Amp 配置：

# 检查 Amp 是否正在使用代理
amp config get amp.url

# 或检查环境变量
echo $AMP_URL

安全检查清单

    ✅ 配置并保护 api-keys（管理路由需要 API 密钥认证）
    ✅ 在可能的情况下启用 ampcode.restrict-management-to-localhost: true 以进行额外加固（默认：false）
    ✅ 不要将代理公网暴露（绑定到 localhost 或使用防火墙/VPN）
    ✅ 在配置文件中安全地存储你的 ampcode.upstream-api-key
    ✅ 定期重新运行登录命令以轮换 OAuth 令牌
    ✅ 如果处理敏感数据，将配置文件和 auth-dir 存储在加密磁盘上
    ✅ 保持代理二进制文件为最新版本，以获取安全修复
