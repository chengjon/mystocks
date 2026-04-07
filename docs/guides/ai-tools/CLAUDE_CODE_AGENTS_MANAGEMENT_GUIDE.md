# Claude Code Agents 管理完全指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


**文档版本**: 1.0
**最后更新**: 2025-12-10
**作者**: Claude Code 实践总结
**范围**: MyStocks_spec 项目的 Agents 管理实践

---

## 📚 目录

1. [官方标准与要求](#官方标准与要求)
2. [Agents 三层架构](#agents-三层架构)
3. [配置文件详解](#配置文件详解)
4. [清理与管理策略](#清理与管理策略)
5. [常见问题与解决方案](#常见问题与解决方案)
6. [最佳实践](#最佳实践)
7. [检查清单](#检查清单)

---

## 官方标准与要求

### 来源
根据 `/opt/mydoc/Anthropic/Claude-code/sub-agents.md` 官方文档

### 子代理定义

子代理是Claude Code可以委派任务的预配置AI个性，具有以下特征：

- ✅ 具有特定的目的和专业领域
- ✅ 使用与主对话分离的自己的上下文窗口
- ✅ 可以配置允许使用的特定工具
- ✅ 包含指导其行为的自定义系统提示

### 必需配置字段

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | 是 | 使用小写字母和连字符的唯一标识符 |
| `description` | 是 | 子代理目的的自然语言描述 |
| `tools` | 否 | 特定工具的逗号分隔列表（省略则继承所有） |
| `model` | 否 | 使用的模型别名（sonnet/opus/haiku）或'inherit' |

### 文件格式标准

```markdown
---
name: agent-name
description: Description of what this agent does and when to use it
tools: Tool1, Tool2, Tool3  # 可选
model: inherit             # 可选
---

Your agent's system prompt goes here...
```

### 官方最佳实践

1. **从Claude生成开始** - 使用Claude生成初始代理，然后自定义
2. **设计专注的代理** - 单一、明确的职责
3. **编写详细的提示** - 具体指令、示例、约束
4. **限制工具访问** - 只授予必需的工具（最小权限原则）
5. **版本控制** - 将项目级代理检入版本控制

---

## Agents 三层架构

### 架构概览

```
Claude Code Agents
├── User Agents (用户级)
│   ├── 位置: ~/.claude/agents/
│   ├── 范围: 所有项目
│   ├── 优先级: 中等
│   └── 管理: 手动文件管理
│
├── Project Agents (项目级)
│   ├── 位置: /project/.claude/agents/
│   ├── 范围: 当前项目
│   ├── 优先级: 最高
│   └── 管理: 手动文件管理
│
└── Plugin Agents (插件级)
    ├── 来源: 已安装插件自动提供
    ├── 范围: 由插件定义
    ├── 优先级: 最低
    └── 管理: 通过插件配置控制
```

### 优先级规则

当存在重名代理时：
1. **Project Agents** (最高优先级)
2. **User Agents** (中等优先级)
3. **Plugin Agents** (最低优先级)

### 代理生命周期

```
文件层 (Files)
    ↓
配置层 (Settings)
    ↓
注册表层 (Registry)
    ↓
显示层 (/agents 命令)
```

---

## 配置文件详解

### 1. 用户级代理存储

**位置**: `~/.claude/agents/*.md`

**特点**:
- 手动创建和管理
- 在所有项目中可用
- 通过 `/agents` 命令显示

**示例**:
```bash
~/.claude/agents/
├── code-reviewer.md
├── database-architect-cn.md
├── first-principles-fullstack-architect.md
├── root-cause-debugger.md
├── contract-driven-dev-expert.md
└── web-fullstack-architect.md
```

### 2. 项目级代理存储

**位置**: `/project/.claude/agents/*.md`

**特点**:
- 项目特定
- 优先级最高
- 应检入版本控制
- 可用于创建项目特定的工作流

**示例**:
```bash
/opt/claude/mystocks_spec/.claude/agents/
├── (应保留为空或包含项目特定代理)
```

### 3. Settings 配置文件

**位置**: `~/.claude/settings.json`

**关键配置**:

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "your-token",
    "ANTHROPIC_BASE_URL": "your-url"
  },
  "hooks": {
    // 请勿包含指向不存在文件的hooks
  },
  "enabledPlugins": {
    "plugin-name": false,  // 禁用插件（关键！）
    "plugin-name": true    // 启用插件
  },
  "alwaysThinkingEnabled": false,
  "model": "haiku"
}
```

**危险陷阱**:
- ❌ hooks 指向不存在的文件会导致屏幕闪烁
- ❌ 已禁用的插件如果缓存未清除，仍会显示

### 4. 插件注册表 (v1)

**位置**: `~/.claude/plugins/installed_plugins.json`

**结构**:
```json
{
  "version": 1,
  "plugins": {
    "plugin-name@marketplace": {
      "version": "1.0.0",
      "installedAt": "2025-12-10T...",
      "lastUpdated": "2025-12-10T...",
      "installPath": "/path/to/plugin",
      "gitCommitSha": "...",
      "isLocal": true
    }
  }
}
```

### 5. 插件注册表 (v2)

**位置**: `~/.claude/plugins/installed_plugins_v2.json`

**结构** (数组格式):
```json
{
  "version": 2,
  "plugins": {
    "plugin-name@marketplace": [
      {
        "scope": "user",
        "installPath": "/path/to/plugin",
        "version": "1.0.0",
        ...
      }
    ]
  }
}
```

### 6. 插件缓存

**位置**: `~/.claude/plugins/cache/`

**结构**:
```
cache/
├── claude-code-workflows/
│   ├── python-development/
│   ├── javascript-typescript/
│   └── ...
├── claude-code-marketplace/
├── every-marketplace/
└── ...
```

**注意**: 即使禁用了插件，缓存仍存在，可能导致agents继续显示！

---

## 清理与管理策略

### 完整清理流程

#### 第一步：删除项目级占位符代理文件

```bash
# 检查项目级代理
ls /opt/claude/mystocks_spec/.claude/agents/

# 删除所有占位符（如果有）
rm /opt/claude/mystocks_spec/.claude/agents/*.md
```

**检查清单**:
- [ ] 列出项目级agents目录
- [ ] 确认所有文件都是占位符（无实现内容）
- [ ] 删除所有占位符文件

#### 第二步：禁用 settings.json 中的插件

```bash
# 编辑 ~/.claude/settings.json
# 将所有 enabledPlugins 改为 false
```

**示例**:
```json
"enabledPlugins": {
  "python-development@claude-code-workflows": false,
  "javascript-typescript@claude-code-workflows": false,
  "backend-development@claude-code-workflows": false,
  // ... 其他插件都设为 false
}
```

**原因**: 这会阻止Claude Code激活这些插件的agents

#### 第三步：清空插件注册表 (v1)

```bash
# 编辑 ~/.claude/plugins/installed_plugins.json
# 清空所有插件记录
```

**结果**:
```json
{
  "version": 1,
  "plugins": {}
}
```

#### 第四步：清空插件注册表 (v2)

```bash
# 编辑 ~/.claude/plugins/installed_plugins_v2.json
# 清空所有插件记录
```

**结果**:
```json
{
  "version": 2,
  "plugins": {}
}
```

#### 第五步：清除插件缓存

```bash
# 删除所有缓存文件
rm -rf ~/.claude/plugins/cache/*
```

**警告**: 即使禁用了插件，缓存仍可能导致agents显示！

#### 第六步：检查并移除有问题的Hooks

```bash
# 检查 settings.json 中的 hooks
# 确保所有hooks命令指向存在的文件

# 如果有不存在的命令，删除整个hooks配置：
"hooks": {}
```

**危险信号**:
- ❌ Hooks指向 `todo-hook-manager.js` 等不存在的文件
- ❌ Hooks指向相对路径（可能找不到）
- ❌ 命令执行失败导致重复重试

---

## 常见问题与解决方案

### 问题1：屏幕狂闪

**原因**:
1. Hooks指向不存在的文件，导致重复失败
2. 插件缓存未清除，agents不断重新加载
3. 后台find进程扫描agents文件

**解决方案**:
```bash
# 1. 清除hooks
编辑 ~/.claude/settings.json，设置 "hooks": {}

# 2. 清除插件缓存
rm -rf ~/.claude/plugins/cache/*

# 3. 杀死后台find进程
kill -9 $(pgrep -f "find.*agents")

# 4. 重启Claude Code
# （退出并重新启动）
```

### 问题2：删除了agents但仍显示

**原因**:
- 插件缓存仍存在agents定义
- 注册表未清空
- 需要重启Claude Code才能生效

**解决方案**:
```bash
# 1. 确认删除了文件
ls -la ~/.claude/agents/
ls -la /project/.claude/agents/

# 2. 清空注册表
# 编辑 ~/.claude/plugins/installed_plugins.json
# 编辑 ~/.claude/plugins/installed_plugins_v2.json

# 3. 清除缓存
rm -rf ~/.claude/plugins/cache/

# 4. 重启Claude Code
```

### 问题3：Plugins自动重新启用

**原因**: Claude Code可能会自动恢复已禁用的插件配置

**解决方案**:
```bash
# 方案 A: 定期检查settings.json
# 方案 B: 卸载不需要的插件（完全删除）
# 方案 C: 使用只读权限保护settings.json
chmod 444 ~/.claude/settings.json
```

### 问题4：无法完全卸载插件

**原因**: 仅删除缓存可能不够彻底

**完全卸载步骤**:
```bash
# 1. 禁用插件
编辑 settings.json，设置为 false

# 2. 清空注册表
清空 installed_plugins.json 和 installed_plugins_v2.json

# 3. 删除缓存
rm -rf ~/.claude/plugins/cache/plugin-name/

# 4. 删除marketplace
rm -rf ~/.claude/plugins/marketplaces/marketplace-name/

# 5. 更新known_marketplaces（如果需要）
编辑 ~/.claude/plugins/known_marketplaces.json
```

---

## 最佳实践

### 1. 用户级Agents管理

**推荐做法**:
- ✅ 保留6-8个通用、高质量的代理
- ✅ 定期审查和更新代理
- ✅ 为每个代理添加明确的描述
- ✅ 限制工具访问（最小权限原则）

**示例**:
```markdown
---
name: code-reviewer
description: 专家代码审查专家。在代码变更后主动使用。
tools: Read, Grep, Glob, Bash, Edit
model: inherit
---

You are a senior code review expert...
```

### 2. 项目级Agents管理

**推荐做法**:
- ✅ 仅创建项目特定的高价值代理
- ✅ 检入版本控制
- ✅ 文档化存在理由
- ✅ 定期清理未使用的代理

**示例用途**:
```
mystocks_spec/.claude/agents/
├── mystocks-api-tester.md    # API测试
├── mystocks-db-auditor.md    # 数据库审计
└── README.md                  # 说明文档
```

### 3. 插件管理

**推荐做法**:
- ✅ 最小化启用的插件数量
- ✅ 定期审计已安装的插件
- ✅ 定期清除缓存
- ✅ 记录禁用原因

**配置模板**:
```json
"enabledPlugins": {
  // ✅ 使用的插件
  "useful-plugin@marketplace": true,

  // ❌ 不使用的插件
  "unused-plugin@marketplace": false
}
```

### 4. 配置文件维护

**定期检查清单**:
- [ ] Settings.json 中的hooks指向有效文件
- [ ] EnabledPlugins 配置与实际需求一致
- [ ] 注册表与已启用的插件同步
- [ ] 缓存定期清除

### 5. Hooks配置安全

**安全实践**:
```json
// ❌ 危险：指向不存在的文件
"hooks": {
  "PostToolUse": [{
    "command": "node agents/todo-hook-manager.js"  // 文件不存在！
  }]
}

// ✅ 安全：要么使用有效文件，要么清空
"hooks": {}  // 或指向绝对路径的有效命令
```

---

## 检查清单

### 初始设置检查

- [ ] 审查所有用户级agents（~/.claude/agents/）
- [ ] 审查所有项目级agents（project/.claude/agents/）
- [ ] 验证settings.json有效性
- [ ] 检查hooks配置的有效性
- [ ] 列出所有启用的插件
- [ ] 记录禁用原因

### 定期维护检查

- [ ] 审查代理描述是否清晰
- [ ] 确认所有代理仍在使用
- [ ] 验证工具权限是否合理
- [ ] 检查hooks是否工作正常
- [ ] 清理未使用的代理
- [ ] 更新文档

### 清理后验证

- [ ] 运行 `/agents` 命令无屏幕闪烁
- [ ] 仅显示预期的user agents
- [ ] 没有项目级占位符
- [ ] 没有plugin agents显示
- [ ] 所有settings.json配置有效
- [ ] 注册表为空或仅包含启用的插件

### 故障排除检查

- [ ] 确认hooks指向有效文件
- [ ] 清除插件缓存
- [ ] 验证注册表同步
- [ ] 检查后台进程
- [ ] 重启Claude Code
- [ ] 查看错误日志

---

## 实践案例：MyStocks_spec 项目

### 清理前状态

```
总Agents数: 26
├── User Agents: 6 ✅ (保留)
├── Project Agents: 7 ❌ (占位符)
└── Plugin Agents: 13 ❌ (未使用)

症状: 运行 /agents 命令屏幕狂闪
```

### 清理步骤

1. **删除项目级占位符** → 7个文件
2. **禁用所有插件** → settings.json
3. **清空注册表v1** → installed_plugins.json
4. **清空注册表v2** → installed_plugins_v2.json
5. **删除插件缓存** → cache目录
6. **清空hooks配置** → settings.json
7. **重启Claude Code** → 生效

### 清理后状态

```
总Agents数: 6
├── User Agents: 6 ✅ (完美)
├── Project Agents: 0 ✅ (已清空)
└── Plugin Agents: 0 ✅ (已禁用)

结果: 清洁界面，零屏幕闪烁
```

### 关键经验

1. **三层都要同步更新** - 仅删除文件不够
2. **缓存是隐藏的杀手** - 必须清除
3. **Hooks会导致严重问题** - 定期检查
4. **需要重启才能生效** - 改动后重启Claude Code
5. **定期审计很重要** - 防止配置漂移

---

## 参考资源

### 官方文档
- **主文档**: `/opt/mydoc/Anthropic/Claude-code/sub-agents.md`
- **设置指南**: `/opt/mydoc/Anthropic/Claude-code/settings.md`
- **Hooks指南**: `/opt/mydoc/Anthropic/Claude-code/hooks.md`

### 项目文档
- **快速参考**: `docs/api/AGENTS_QUICK_REFERENCE.md`
- **完整审查**: `docs/api/AGENTS_AUDIT_REPORT.md`
- **清理报告**: `docs/api/FINAL_AGENTS_CLEANUP_REPORT.md`

### CLI命令
```bash
# 查看所有agents
/agents

# 创建新agent
/agents create

# 编辑agent
/agents edit agent-name

# 删除agent
/agents delete agent-name
```

---

## 常见命令速查

```bash
# 文件操作
ls ~/.claude/agents/                          # 列出用户agents
ls /project/.claude/agents/                   # 列出项目agents
rm ~/.claude/agents/agent-name.md             # 删除用户agent

# 配置检查
cat ~/.claude/settings.json | python3 -m json.tool  # 验证JSON
grep enabledPlugins ~/.claude/settings.json   # 检查插件配置
grep hooks ~/.claude/settings.json            # 检查hooks

# 缓存清理
rm -rf ~/.claude/plugins/cache/*              # 清除所有缓存
rm -rf ~/.claude/plugins/cache/plugin-name/   # 清除特定插件缓存

# 注册表管理
cat ~/.claude/plugins/installed_plugins.json      # 查看v1注册表
cat ~/.claude/plugins/installed_plugins_v2.json   # 查看v2注册表

# 进程管理
ps aux | grep claude                          # 查看Claude进程
kill -9 $(pgrep -f "find.*agents")           # 杀死find进程
```

---

**文档完成**

此文档整合了官方标准、实践经验和最佳实践，可作为Claude Code Agents管理的权威参考。

---

*最后更新: 2025-12-10*
*来源: MyStocks_spec 项目实践总结*
