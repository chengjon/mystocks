# Apifox MCP 集成指南 - Claude Code

> **历史文档说明**:
> 本文件是某阶段的历史文档、过程记录或专题材料，不是当前基线、当前系统总览或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内描述、背景、结论和上下文如未重新复核，应视为历史快照，不得直接当作当前事实。


> ✅ **已配置**: Apifox MCP 服务器已添加到项目
> 🎯 **功能**: 让 Claude Code 直接访问 Apifox API 文档
> 📋 **Site ID**: 4478210

---

## 🚀 配置完成

### 当前配置 (`.mcp.json`)

```json
{
  "mcpServers": {
    "apifox-api-docs": {
      "command": "npx",
      "args": [
        "-y",
        "apifox-mcp-server@latest",
        "--site-id=4478210"
      ]
    }
  }
}
```

### VS Code vs Claude Code 配置对比

| 项目 | VS Code | Claude Code |
|------|---------|-------------|
| **配置文件** | `settings.json` | `.mcp.json` (项目根目录) |
| **Command** | `cmd /c npx` (Windows) | `npx` (跨平台) |
| **服务器名称** | 可含中文空格 | 建议用英文短横线 |
| **自动启动** | VS Code 启动时 | Claude Code 启动时 |

**关键差异**:
- ❌ **移除** `cmd` 和 `/c` (Windows 特定，Claude Code 跨平台)
- ✅ **直接使用** `npx` 命令
- ✅ **保留** `-y` (自动确认安装)
- ✅ **保留** `--site-id=4478210` (你的 Apifox 站点 ID)

---

## 📋 使用步骤

### 1. 重启 Claude Code 会话

配置修改后需要重启 Claude Code 才能加载新的 MCP 服务器：

```bash
# 如果使用命令行启动 Claude Code
exit  # 退出当前会话
claude  # 重新启动

# 或者在新终端启动
cd /opt/claude/mystocks_spec
claude
```

### 2. 验证 MCP 服务器连接

启动后，Claude Code 会自动连接 Apifox MCP 服务器。你可以通过以下方式验证：

**方式 1: 查看启动日志**
```
[MCP] Connecting to apifox-api-docs...
[MCP] Connected: apifox-api-docs
```

**方式 2: 询问 Claude**
```
你：列出当前可用的 MCP 工具
Claude：我可以访问以下 Apifox API 文档工具...
```

### 3. 使用 Apifox API 文档

一旦连接成功，Claude Code 可以：

**查询 API 信息**:
```
你：查看我的 Apifox 项目中有哪些 API 端点？
你：获取 /api/users 端点的详细文档
你：这个 API 需要哪些请求参数？
```

**生成代码**:
```
你：根据 Apifox 文档生成调用 /api/login 的 Python 代码
你：为所有用户管理 API 生成 TypeScript 接口定义
```

**API 对比**:
```
你：对比 Apifox 文档和当前项目的 API 实现
你：检查哪些 API 还没有实现
```

---

## 🔧 高级配置

### 添加环境变量 (可选)

如果 Apifox API 需要认证，可以添加环境变量：

```json
{
  "mcpServers": {
    "apifox-api-docs": {
      "command": "npx",
      "args": [
        "-y",
        "apifox-mcp-server@latest",
        "--site-id=4478210"
      ],
      "env": {
        "APIFOX_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 配置多个 Apifox 项目

```json
{
  "mcpServers": {
    "apifox-project-1": {
      "command": "npx",
      "args": [
        "-y",
        "apifox-mcp-server@latest",
        "--site-id=4478210"
      ]
    },
    "apifox-project-2": {
      "command": "npx",
      "args": [
        "-y",
        "apifox-mcp-server@latest",
        "--site-id=9876543"
      ]
    }
  }
}
```

### 指定 npx 版本 (可选)

如果需要锁定特定版本：

```json
{
  "mcpServers": {
    "apifox-api-docs": {
      "command": "npx",
      "args": [
        "-y",
        "apifox-mcp-server@1.0.0",
        "--site-id=4478210"
      ]
    }
  }
}
```

---

## 🐛 故障排查

### 问题 1: MCP 服务器无法连接

**症状**: 启动 Claude Code 时看到连接错误
```
[MCP] Failed to connect to apifox-api-docs
```

**解决方案**:

1. **检查 Node.js 和 npx 可用性**
```bash
node --version  # 应显示 v14+ 或更高
npx --version   # 应显示 npx 版本
```

2. **手动测试 MCP 服务器**
```bash
npx -y apifox-mcp-server@latest --site-id=4478210
# 应该启动服务器并显示初始化信息
```

3. **检查网络连接**
```bash
curl https://registry.npmjs.org/apifox-mcp-server
# 确保可以访问 npm registry
```

### 问题 2: 找不到 site-id

**症状**: MCP 服务器启动但无法获取 API 文档
```
Error: Site 4478210 not found
```

**解决方案**:

1. **验证 Site ID**
   - 登录 Apifox Web 界面
   - 打开项目设置
   - 确认 "站点 ID" 或 "Site ID"

2. **检查访问权限**
   - 确保该站点是公开的或你有访问权限
   - 如果是私有项目，需要配置 API Key

### 问题 3: npx 每次都重新下载

**症状**: 启动很慢，每次都显示 "Installing apifox-mcp-server..."

**解决方案**: 预安装到全局

```bash
npm install -g apifox-mcp-server@latest

# 修改配置使用全局安装
{
  "mcpServers": {
    "apifox-api-docs": {
      "command": "apifox-mcp-server",
      "args": [
        "--site-id=4478210"
      ]
    }
  }
}
```

### 问题 4: Windows 路径问题

**症状**: Windows 环境下无法启动

**解决方案 1**: 使用完整路径
```json
{
  "mcpServers": {
    "apifox-api-docs": {
      "command": "C:\\Program Files\\nodejs\\npx.cmd",
      "args": [
        "-y",
        "apifox-mcp-server@latest",
        "--site-id=4478210"
      ]
    }
  }
}
```

**解决方案 2**: 使用 WSL (推荐)
- Claude Code 在 WSL2 环境中运行更稳定
- 跨平台兼容性更好

---

## 💡 使用场景示例

### 场景 1: API 实现检查

**任务**: 检查 Apifox 文档中的 API 是否都已实现

```
你：查看 Apifox 项目中所有的 API 端点列表

Claude：[列出所有 API]

你：对比这些 API 和我项目中 /opt/claude/mystocks_spec/web/backend/app/api/ 目录下已实现的路由

Claude：[分析并列出未实现的 API]
```

### 场景 2: 生成客户端 SDK

**任务**: 根据 Apifox 文档生成 TypeScript 客户端

```
你：根据 Apifox 文档生成完整的 TypeScript API 客户端，包括：
1. 所有接口的类型定义
2. HTTP 客户端封装
3. 错误处理
4. 请求/响应拦截器

Claude：[生成完整的 TypeScript 客户端代码]
```

### 场景 3: API 文档对比

**任务**: 对比 Apifox 文档和 FastAPI 自动生成的 OpenAPI 文档

```
你：对比 Apifox 文档和 http://localhost:8000/openapi.json 中的 API 定义，找出差异

Claude：[列出差异并提供同步建议]
```

### 场景 4: 测试用例生成

**任务**: 根据 API 文档生成自动化测试

```
你：为 Apifox 中的所有认证相关 API 生成 pytest 测试用例，包括：
1. 正常场景测试
2. 异常场景测试
3. 边界条件测试

Claude：[生成完整的测试套件]
```

---

## 📊 Apifox MCP 功能概览

| 功能 | 描述 | 使用场景 |
|------|------|----------|
| **API 列表查询** | 获取项目所有 API 端点 | 项目概览、实现检查 |
| **端点详情** | 获取单个 API 的完整文档 | 代码生成、测试编写 |
| **数据模型** | 获取请求/响应模型定义 | 类型定义、数据验证 |
| **示例代码** | 获取 API 调用示例 | 快速集成、学习参考 |
| **认证信息** | 获取 API 认证要求 | 安全实现、权限管理 |

---

## 🎯 与项目其他 MCP 服务器配合

你的项目可能还会使用其他 MCP 服务器，可以一起配置：

```json
{
  "mcpServers": {
    "apifox-api-docs": {
      "command": "npx",
      "args": ["-y", "apifox-mcp-server@latest", "--site-id=4478210"]
    },
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        "ANTHROPIC_API_KEY": "your-key"
      }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@context7/mcp-server"]
    }
  }
}
```

**协同使用场景**:
1. **Apifox MCP**: 提供 API 文档
2. **Task Master**: 管理 API 实现任务
3. **Context7**: 查询第三方库文档

---

## ✅ 配置检查清单

验证 Apifox MCP 配置是否正确：

- [ ] `.mcp.json` 文件位于项目根目录
- [ ] `command` 字段为 `npx` (不是 `cmd`)
- [ ] 包含 `-y` 参数 (自动确认)
- [ ] `--site-id` 参数正确
- [ ] Node.js 版本 >= 14
- [ ] 可以访问 npm registry
- [ ] Claude Code 已重启以加载新配置
- [ ] 启动日志显示 MCP 连接成功

---

## 📚 相关资源

- **Apifox 官方文档**: https://apifox.com/help/
- **Apifox MCP 服务器**: https://github.com/apifox/apifox-mcp-server
- **Claude Code MCP 文档**: https://docs.claude.com/en/docs/claude-code/mcp-servers
- **MCP 协议规范**: https://modelcontextprotocol.io/

---

## 🔄 更新和维护

### 更新 Apifox MCP 服务器

```bash
# 方式 1: 自动更新 (使用 @latest)
# 配置中已使用 @latest，每次启动会自动检查更新

# 方式 2: 手动更新全局安装
npm update -g apifox-mcp-server
```

### 查看版本信息

```bash
npx apifox-mcp-server --version
```

---

**最后更新**: 2025-11-10
**状态**: ✅ 已配置完成
**Site ID**: 4478210
**下一步**: 重启 Claude Code 开始使用
