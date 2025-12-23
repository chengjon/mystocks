# Claude Code CLI - Python LSP 功能指南

> **创建日期**: 2025-12-23
> **适用场景**: 使用 Claude Code CLI (命令行界面)

---

## 核心区别

| 特性 | VSCode + Claude | Claude Code CLI |
|------|-----------------|-----------------|
| **LSP 支持** | ✅ 内置 Pylance | ❌ 无内置 LSP |
| **配置文件** | `.vscode/settings.json` | `~/.claude/settings.json` |
| **代码补全** | ✅ 实时自动补全 | ❌ 需手动请求 |
| **语法检查** | ✅ 实时显示 | ⚠️ 通过 hooks |
| **跳转定义** | ✅ 支持 | ❌ 不支持 |
| **主要用途** | 代码编辑 | 对话式编程 |

---

## Claude Code CLI 中获得 LSP 功能的方法

### 方法 1: 使用独立的 Python LSP Server (推荐)

#### 安装 python-lsp-server

```bash
pip install python-lsp-server
```

#### 配置外部编辑器集成

**与 Vim/Neovim 集成**:
```bash
# 安装 nvim-lspconfig
# 在 Neovim 中配置 python-lsp-server
# 这样可以边写代码边与 Claude Code CLI 对话
```

**与 Helix 编辑器集成**:
```bash
# Helix 内置 LSP 支持
# 配置 language-server.toml
```

### 方法 2: 使用 Pre-commit Hooks (已配置)

**你的项目已经配置了**:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        args: [--fix]  # 自动修复

  - repo: https://github.com/psf/black
    hooks:
      - id: black
        args: [--line-length=120]  # 格式化

  - repo: https://github.com/pre-commit/mirrors-mypy
    hooks:
      - id: mypy  # 类型检查
```

**使用方式**:
```bash
# 手动运行所有检查
pre-commit run --all-files

# Git commit 时自动运行
git commit -m "your message"  # hooks 自动执行
```

### 方法 3: 请求 Claude 进行代码检查

**在 Claude Code CLI 中**:

```bash
# 示例对话
你: "检查 src/core.py 的语法错误和类型问题"
Claude: [运行 mypy 和 pylint，返回结果]

你: "优化这个函数的性能"
Claude: [分析代码，提供优化建议]
```

---

## 推荐工作流程

### 选项 A: VSCode + Claude 插件 (完整体验)

**适合**: 需要实时 LSP 功能的用户

**步骤**:
1. 安装 VSCode
2. 安装 Python 扩展 + Pylance
3. 安装 Claude 插件
4. 在 VSCode 中工作：
   - 实时代码补全 ✅
   - 实时错误提示 ✅
   - Claude Chat 助手 ✅

**配置文件**: `.vscode/settings.json`

### 选项 B: Claude Code CLI + 外部编辑器 (灵活组合)

**适合**: 喜欢命令行 + 独立编辑器的用户

**步骤**:
1. 使用支持 LSP 的编辑器 (Vim/Neovim/Helix)
2. 配置 python-lsp-server
3. 同时运行 Claude Code CLI
4. 工作流程：
   - 在编辑器中写代码 (LSP 功能)
   - 在 Claude Code CLI 中对话 (AI 助手)

**编辑器 LSP 配置**: `~/.config/nvim/` 或 `~/.config/helix/`

### 选项 C: 纯 Claude Code CLI (极简模式)

**适合**: 只需要 AI 助手的用户

**步骤**:
1. 使用任何简单编辑器
2. 依赖 Claude 进行代码检查：
   - "检查这个文件"
   - "修复类型错误"
   - "格式化代码"

**配置**: `.claude/settings.json` (hooks 配置)

---

## 你的项目当前状态

### ✅ 已配置的功能

1. **Pre-commit Hooks**:
   - Ruff (linting + formatting)
   - Black (代码格式化)
   - MyPy (类型检查)
   - Bandit (安全检查)

2. **Claude Code Hooks**:
   - PostToolUse hooks (自动文件追踪)
   - UserPromptSubmit hooks (技能激活)

### 📝 建议配置

#### 如果你想在 VSCode 中使用：

创建 `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.languageServer": "Pylance",
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.extraPaths": ["${workspaceFolder}/src"],
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black"
}
```

#### 如果你想在 Claude Code CLI 中获得更好的体验：

保持当前配置即可，依赖：
- Pre-commit hooks (自动代码检查)
- 请求 Claude 进行代码审查

---

## 常见问题

### Q1: `.vscode/settings.json` 会让 Claude Code CLI 更聪明吗？

**A**: ❌ 不会。Claude Code CLI 不读取这个文件。

### Q2: 如何让 Claude Code CLI 提供代码补全？

**A**: Claude Code CLI 本身不提供代码补全。你需要：
- 使用 VSCode + Claude 插件，或
- 使用支持 LSP 的编辑器 + Claude Code CLI

### Q3: 我应该选择哪种方式？

**A**:
- **重度和代码编写** → VSCode + Claude 插件
- **喜欢命令行** → Claude Code CLI + Neovim/Helix
- **只需要 AI 助手** → 纯 Claude Code CLI

---

## 总结

| 工具组合 | LSP 功能 | Claude AI | 适用场景 |
|---------|---------|-----------|---------|
| **VSCode + Claude** | ✅ 完整 | ✅ 集成 | 日常开发 |
| **Neovim + Claude CLI** | ✅ 完整 | ✅ 独立 | 高级用户 |
| **纯 Claude CLI** | ❌ 无 | ✅ 完整 | 快速原型 |

**推荐**: 根据你的工作习惯选择，不必强求统一。
