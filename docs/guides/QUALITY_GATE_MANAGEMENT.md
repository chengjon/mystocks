# 质量门禁管理参考文档

本文档记录 MyStocks 项目的质量门禁系统配置、使用方法和常见问题。

---

## 目录

1. [系统概述](#系统概述)
2. [Python 质量门禁](#python-质量门禁)
3. [Web 质量门禁](#web-质量门禁)
4. [配置说明](#配置说明)
5. [常见问题](#常见问题)
6. [故障排除](#故障排除)
7. [最佳实践](#最佳实践)

---

## 系统概述

### 架构设计

质量门禁系统基于 Claude Code Hook 机制实现，在会话停止前自动检查代码质量：

```
┌─────────────────────────────────────────────────────────────────┐
│                    Claude Code 会话流程                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PostToolUse (文件编辑)                                          │
│       ↓                                                         │
│  post-tool-use-file-edit-tracker.sh (非阻塞记录)                  │
│       ↓                                                         │
│  ... 多次编辑 ...                                                │
│       ↓                                                         │
│  Stop (会话停止)                                                 │
│       ↓                                                         │
│  ┌─────────────────┐  ┌─────────────────┐                       │
│  │ Python Quality  │  │  Web Quality    │                       │
│  │ Gate            │  │  Gate           │                       │
│  │ (stop-python)   │  │  (stop-web)     │                       │
│  └────────┬────────┘  └────────┬────────┘                       │
│           │                    │                                 │
│           └─────────┬──────────┘                                 │
│                     ↓                                           │
│           错误 ≥ 阈值?                                           │
│              ↓                                                   │
│        是 → 阻断停止，要求修复                                     │
│        否 → 允许停止                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 核心文件

| 文件 | 用途 |
|------|------|
| `.claude/hooks/stop-python-quality-gate.sh` | Python 质量门禁脚本 |
| `.claude/hooks/stop-web-dev-quality-gate.sh` | Web/TypeScript 质量门禁脚本 |
| `.claude/build-checker-python.json` | Python 质量门禁配置 |
| `.claude/settings.json` | Hook 注册配置 |

---

## Python 质量门禁

### 文件位置

```
.claude/hooks/stop-python-quality-gate.sh
```

### 检查项目

| 检查项 | 命令 | 关键 | 说明 |
|--------|------|------|------|
| critical_imports | 核心模块导入验证 | ✅ | 验证 ConfigDrivenTableManager 和后端 app 可导入 |
| backend_syntax | 后端语法检查 | ✅ | `find web/backend/app -name '*.py' -exec py_compile` |
| core_syntax | 核心模块语法检查 | ✅ | `find src/core src/adapters src/data_access -name '*.py' -exec py_compile` |
| type_hints_core | mypy 类型检查 | ❌ | 非强制，仅记录 |
| quick_tests | pytest 快速测试 | ❌ | 非强制，最多 3 个失败后停止 |

### 退出码

| 退出码 | 含义 |
|--------|------|
| 0 | 质量检查通过，允许停止 |
| 2 | 错误 ≥ 阈值，阻断停止 |

### 错误阈值

默认阈值: **10 个错误**

```json
// build-checker-python.json
{
  "errorThreshold": 10
}
```

---

## Web 质量门禁

### 文件位置

```
.claude/hooks/stop-web-dev-quality-gate.sh
```

### 检查命令

```bash
npx vue-tsc --noEmit
```

### 错误阈值

默认阈值: **40 个错误**

```bash
QUALITY_GATE_THRESHOLD=40
```

### 忽略模式配置

Web 质量门禁通过 `IGNORED_PATTERNS` 数组过滤误报，主要包括：

| 类别 | 示例 |
|------|------|
| Vue/Element Plus 类型 | `ComponentInternalInstance`, `Cannot find name '$slots'` |
| 第三方库类型 | KLineCharts, technicalindicators 不完整类型定义 |
| 自动生成类型 | `generated-types.ts` 相关错误 |
| 视图组件类型 | `views/*.vue` 类型推断问题 |

#### 添加忽略模式

```bash
# 在 stop-web-dev-quality-gate.sh 中添加
IGNORED_PATTERNS=(
    # 新模式
    "Your custom error pattern"
)
```

---

## 配置说明

### settings.json Hook 注册

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-python-quality-gate.sh"
          }
        ],
        "timeout": 120
      },
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-web-dev-quality-gate.sh"
          }
        ],
        "timeout": 120
      }
    ]
  }
}
```

### build-checker-python.json 完整配置

```json
{
  "version": "2.0",
  "errorThreshold": 10,
  "repos": {
    "$PROJECT_ROOT": {
      "qualityChecks": [
        {
          "name": "检查名称",
          "description": "检查描述",
          "command": "执行的 bash 命令",
          "critical": true,
          "timeout": 30,
          "errorPatterns": ["Pattern1", "Pattern2"]
        }
      ]
    }
  }
}
```

#### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 检查名称，用于错误报告 |
| description | string | 检查描述 |
| command | string | 执行的 bash 命令 |
| critical | boolean | 是否关键检查，失败则阻断 |
| timeout | number | 超时时间（秒） |
| errorPatterns | array | 错误匹配正则表达式数组 |

---

## 常见问题

### Q1: Python 质量门禁报 "IndentationError"

**问题**: Python 文件缩进错误

**原因**: 文件缺少必要的导入或 docstring，导致函数体缩进异常

**解决**:
```bash
# 1. 检查文件
cat -A /path/to/file.py | head -5

# 2. 验证语法
python -m py_compile /path/to/file.py

# 3. 修复文件
# 确保文件开头有:
# - docstring 或 # 注释
# - import 语句
# - 函数定义不使用额外缩进
```

**示例修复**:
```python
# 修复前 (错误)
    def get_data(self):
        ...

# 修复后 (正确)
"""
Module docstring
"""
import logging

def get_data(self):
    ...
```

---

### Q2: Web 质量门禁报 "Module has already exported"

**问题**: TypeScript 重复导出类型

**原因**: 多个文件导出同名类型

**解决**:
```typescript
// 方案1: 移除重复导出
// index.ts
// export * from './strategy';  // 注释掉，因为 common.ts 已导出

// 方案2: 使用显式重导出
// index.ts
export type { TypeName } from './source';
```

---

### Q3: 错误阈值设置多少合适

**建议**:

| 项目规模 | 初始阈值 | 稳定后阈值 |
|---------|---------|-----------|
| 小型 (< 100 文件) | 5 | 3 |
| 中型 (100-500 文件) | 10 | 5 |
| 大型 (> 500 文件) | 15 | 10 |

---

### Q4: 如何跳过质量检查

**临时跳过**: 在 settings.json 中注释掉 hook

**永久跳过**: 删除或重命名 hook 脚本

---

### Q5: 误报太多怎么办

**Web 质量门禁**: 添加到 `IGNORED_PATTERNS`

```bash
IGNORED_PATTERNS=(
    # 现有模式...
    "Your false positive pattern"
)
```

**Python 质量门禁**: 添加 `errorPatterns` 白名单

```json
{
  "errorPatterns": [
    "ModuleNotFoundError",
    "ImportError",
    "SyntaxError",
    "Traceback",
    "Your custom pattern"
  ]
}
```

---

## 故障排除

### 检查 Hook 是否生效

```bash
# 1. 确认 settings.json 配置正确
cat .claude/settings.json | jq '.hooks.Stop'

# 2. 手动运行 Hook
bash .claude/hooks/stop-python-quality-gate.sh
bash .claude/hooks/stop-web-dev-quality-gate.sh

# 3. 查看编辑日志
cat .claude/edit_log.jsonl | head -10
```

### 调试模式

```bash
# Python 质量门禁调试
export PYTHON_QG_DEBUG=true
bash .claude/hooks/stop-python-quality-gate.sh
```

### 超时问题

**症状**: Hook 超时退出

**解决**: 增加 `settings.json` 中的 timeout

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [...],
        "timeout": 180  // 增加为 180 或 240
      }
    ]
  }
}
```

同时增加 `build-checker-python.json` 中的 timeout:

```json
{
  "timeout": 180
}
```

---

## 最佳实践

### 1. 渐进式阈值调整

- **初期**: 宽松阈值 (10-15)，允许开发继续
- **稳定期**: 严格阈值 (3-5)，要求代码质量
- **发布前**: 零容忍 (0)，所有错误必须修复

### 2. 关键检查 vs 非关键检查

| 检查类型 | critical | 用途 |
|---------|----------|------|
| 语法检查 | ✅ | 必须通过，防止低级错误 |
| 导入检查 | ✅ | 必须通过，确保模块可运行 |
| 类型检查 | ❌ | 建议修复，不阻断开发 |
| 测试 | ❌ | 建议通过，不阻断开发 |

### 3. 定期清理误报模式

每季度审查 `IGNORED_PATTERNS`，移除已修复的误报：

```bash
# 定期执行
npx vue-tsc --noEmit 2>&1 | grep -v "Pattern1\|Pattern2\|..."
```

### 4. 文档同步更新

当添加新的检查规则时，同步更新本文档。

---

## 快速参考

### 常用命令

```bash
# 运行 Python 质量门禁
bash .claude/hooks/stop-python-quality-gate.sh

# 运行 Web 质量门禁
bash .claude/hooks/stop-web-dev-quality-gate.sh

# 手动验证核心导入
python -c 'from src.core import ConfigDrivenTableManager'
python -c 'from web.backend.app.main import app'

# TypeScript 类型检查
cd web/frontend && npx vue-tsc --noEmit

# Python 语法检查
python -m py_compile src/adapters/akshare/financial_data.py
```

### 文件路径速查

```
.claude/
├── hooks/
│   ├── stop-python-quality-gate.sh    # Python 质量门禁
│   ├── stop-web-dev-quality-gate.sh   # Web 质量门禁
│   └── parse_edit_log.py              # 编辑日志解析
├── build-checker-python.json          # Python 配置
└── settings.json                      # Hook 注册
```

---

## 变更日志

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-01-18 | 初始文档 |

---

**文档维护**: 主 CLI (Claude Code)
**最后更新**: 2026-01-18
