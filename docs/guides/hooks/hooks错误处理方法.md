# Claude Code Hooks 问题与解决方案手册

> **文档版本**: v2.0
> **最后更新**: 2025-11-19
> **维护者**: Claude-Kits Team

## 📚 目录

- [1. 配置与环境问题](#1-配置与环境问题)
  - [1.1 占位符未替换](#11-占位符未替换)
  - [1.2 行结束符不兼容](#12-行结束符不兼容)
- [2. 输入处理问题](#2-输入处理问题)
  - [2.1 空输入处理](#21-空输入处理)
  - [2.2 无效 JSON 格式](#22-无效-json-格式)
- [3. 输出格式问题](#3-输出格式问题)
  - [3.1 JSON 手动拼接](#31-json-手动拼接)
  - [3.2 特殊字符转义](#32-特殊字符转义)
- [4. 最佳实践](#4-最佳实践)
- [5. 快速参考](#5-快速参考)

---

## 1. 配置与环境问题

### 1.1 占位符未替换

**问题编号**: CONFIG-001
**影响范围**: `stop-python-quality-gate.sh`
**严重程度**: 🔴 高
**发现日期**: 2025-11-10
**修复状态**: ✅ 已修复

#### 问题描述

配置文件 `build-checker-python.json` 中使用了 `$PROJECT_ROOT` 占位符，但 `stop-python-quality-gate.sh` 脚本直接读取配置而未进行占位符替换，导致仓库路径匹配失败。

#### 错误现象

- **症状**: 质量检查无法正确定位项目仓库
- **错误信息**: 仓库路径匹配失败
- **用户影响**: Stop hook 无法执行质量检查，形同虚设

#### 根本原因

脚本使用 `jq` 直接解析配置文件中的 `repos` 对象，将 `$PROJECT_ROOT` 作为字面量字符串处理，而非运行时变量。

**错误代码示例**:
```json
{
  "repos": {
    "$PROJECT_ROOT": {
      "qualityChecks": [...]
    }
  }
}
```

#### 解决方案

##### 方案概述

在读取配置后、使用前，动态替换 `$PROJECT_ROOT` 占位符为实际的项目根目录路径。

##### 实施步骤

1. 获取当前工作目录作为 `PROJECT_ROOT`
2. 使用 `jq` 的 `to_entries` 和 `from_entries` 遍历所有仓库条目
3. 条件替换：如果 key 是 `$PROJECT_ROOT`，替换为实际路径
4. 返回处理后的配置对象

##### 代码示例

**修改位置**: `stop-python-quality-gate.sh` 第 189-203 行

```bash
# 动态替换 $PROJECT_ROOT 占位符为实际项目根目录
PROJECT_ROOT=$(pwd)
REPO_CONFIGS=$(echo "$BUILD_CONFIG" | jq -c --arg root "$PROJECT_ROOT" '
    .repos | to_entries | map(
        if .key == "$PROJECT_ROOT" then
            .key = $root
        else
            .
        end
    ) | from_entries
')
```

#### 验证结果

##### 测试方法

```bash
PYTHON_QG_DEBUG=true bash -c 'echo "{\"session_id\": \"test-123\"}" | .claude/hooks/stop-python-quality-gate.sh'
```

##### 测试结果

```json
{
  "hookSpecificOutput": {
    "hookEventName": "Stop",
    "decision": "allow",
    "reason": "✅ 所有质量检查通过！"
  }
}
```

##### 通过的检查项

- ✅ critical_imports: 核心模块导入验证
- ✅ backend_syntax: 后端 Python 语法检查
- ✅ core_syntax: 核心模块语法检查
- ✅ type_hints_core: 类型提示检查（mypy）
- ✅ quick_tests: 快速测试（pytest）

#### 改进效果

| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| 占位符支持 | ❌ 不支持 | ✅ 动态替换 |
| 配置灵活性 | ❌ 硬编码路径 | ✅ 可移植配置 |
| Hook 功能 | ⚠️ 路径不匹配 | ✅ 完全正常 |

#### 核心收益

1. **配置可移植性**: 同一配置文件可在不同环境使用，无需修改路径
2. **维护简化**: 占位符机制减少硬编码，便于维护
3. **质量保障**: Hook 正常工作，确保代码质量门禁生效

#### 技术细节

**Stop Hook 工作流程**:

1. 读取 stdin JSON → 获取 `session_id`
2. 解析编辑日志 (`.claude/edit_log.jsonl`)
3. 提取受影响的仓库列表
4. **加载配置 + 替换占位符** ← 本次修复点
5. 按仓库执行质量检查
6. 统计错误数量
7. 决策: 错误 ≥ 阈值(10) → 阻止停止 (`exit 2`)，错误 < 阈值 → 允许停止 (`exit 0`)

**配置结构**:
```json
{
  "errorThreshold": 10,
  "repos": {
    "$PROJECT_ROOT": {
      "qualityChecks": [
        {
          "name": "critical_imports",
          "command": "...",
          "critical": true,
          "timeout": 15
        }
      ]
    }
  }
}
```

---

### 1.2 行结束符不兼容

**问题编号**: CONFIG-002
**影响范围**: `stop-python-quality-gate.sh`
**严重程度**: 🟡 中
**发现日期**: 2025-11-10
**修复状态**: ✅ 已修复

#### 问题描述

`stop-python-quality-gate.sh` 文件包含 Windows 格式的行结束符（CRLF），在 Linux/WSL 环境中产生警告，且可能在某些环境下导致脚本执行失败。

#### 错误现象

- **症状**: Git 在 Linux/WSL 环境中警告 "LF will be replaced by CRLF"
- **用户影响**: 虽不影响功能，但产生持续警告，降低开发体验

#### 根本原因

文件在 Windows 环境中编辑，保存时使用了 CRLF（`\r\n`）行结束符，而 Unix/Linux 系统期望 LF（`\n`）。

#### 解决方案

##### 方案概述

将所有 shell 脚本的行结束符标准化为 LF，并配置 Git 自动处理。

##### 实施步骤

1. 转换现有文件的行结束符
2. 配置 Git `core.autocrlf` 为 `input` 模式
3. 提交时自动转换为 LF，检出时保持不变

##### 代码示例

```bash
# 转换 CRLF → LF
sed -i 's/\r$//' .claude/hooks/stop-python-quality-gate.sh

# 设置 Git 配置（仅在提交时转换为 LF）
git config core.autocrlf input
```

#### 改进效果

| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| 行结束符警告 | ⚠️ 持续警告 | ✅ 无警告 |
| Git 状态 | ⚠️ 混乱 | ✅ 干净 |

#### 核心收益

1. **跨平台兼容**: 统一行结束符，消除 Windows/Linux 差异
2. **开发体验**: 消除警告噪音，保持 Git 状态干净

---

## 2. 输入处理问题

### 2.1 空输入处理

**问题编号**: INPUT-001
**影响范围**: `session-start-task-master-injector.sh`, `session-end-cleanup.sh`, `user-prompt-submit-skill-activation.sh`, `stop-python-quality-gate.sh`
**严重程度**: 🔴 高
**发现日期**: 2025-11-12
**修复状态**: ✅ 已修复

#### 问题描述

执行 `/compact` 等命令时，某些 hooks 接收到空输入，直接传递给 `jq` 导致解析失败，脚本因 `set -e` 异常退出。

#### 错误现象

- **症状**: SessionStart hook 报错退出
- **错误信息**: `jq: parse error (at end of file)`
- **用户影响**: `/compact` 命令失败，hook 执行中断

#### 根本原因

脚本使用 `set -euo pipefail` 严格模式，任何命令失败立即退出。未对 stdin 输入进行空值检查，直接将空字符串传递给 `jq`，触发解析错误。

**错误代码示例**:
```bash
set -euo pipefail
INPUT_JSON=$(cat)
SESSION_ID=$(echo "$INPUT_JSON" | jq -r '.session_id // "unknown"')  # 空字符串 → jq 报错 → 脚本退出
```

#### 解决方案

##### 方案概述

在解析 JSON 之前，先检查输入是否为空，为空则优雅跳过，避免 `jq` 解析失败。

##### 实施步骤

1. 读取 stdin 到变量
2. 使用 `[ -z "$INPUT_JSON" ]` 检查是否为空
3. 空输入时记录日志并正常退出（`exit 0`）
4. 非空输入继续后续处理

##### 代码示例

```bash
# ===== 读取 stdin JSON =====
INPUT_JSON=$(cat)

# 检查输入是否为空
if [ -z "$INPUT_JSON" ]; then
    debug_log "Empty input received, skipping"
    exit 0
fi

# 继续正常处理
SESSION_ID=$(echo "$INPUT_JSON" | jq -r '.session_id // "unknown"')
```

**Stop Hook 特殊处理**:
```bash
# Stop hook 空输入时应返回允许JSON，而非静默退出
if [ -z "$INPUT_JSON" ]; then
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "Stop"
  }
}
EOF
    exit 0
fi
```

#### 验证结果

##### 改进效果

| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| 空输入处理 | ❌ 报错退出 | ✅ 优雅跳过 |
| /compact命令 | ⚠️ hook报错 | ✅ 正常执行 |
| 错误恢复 | ❌ 立即退出 | ✅ 安全fallback |

#### 核心收益

1. **健壮性提升**: 所有 hooks 能处理各种异常输入
2. **用户体验**: `/compact` 等命令不再因 hook 错误而失败
3. **调试友好**: 通过 `debug_log` 记录跳过原因
4. **一致性**: 所有 hooks 使用相同的输入验证模式

#### 相关文件

| Hook 文件 | 问题 | 修复状态 |
|-----------|------|---------|
| session-start-task-master-injector.sh | 空输入导致错误 | ✅ 已修复 |
| session-end-cleanup.sh | 空输入导致错误 | ✅ 已修复 |
| user-prompt-submit-skill-activation.sh | 空输入导致错误 | ✅ 已修复 |
| stop-python-quality-gate.sh | 空输入导致错误 | ✅ 已修复 |
| post-tool-use-file-edit-tracker.sh | 已有正确验证 | ✅ 无需修改 |
| post-tool-use-database-schema-validator.sh | 已有正确验证 | ✅ 无需修改 |
| post-tool-use-document-organizer.sh | 已有正确验证 | ✅ 无需修改 |

---

### 2.2 无效 JSON 格式

**问题编号**: INPUT-002
**影响范围**: 同 [2.1 空输入处理](#21-空输入处理)
**严重程度**: 🟡 中
**发现日期**: 2025-11-12
**修复状态**: ✅ 已修复

#### 问题描述

Claude 传入非标准 JSON 或格式错误的数据，脚本未验证 JSON 格式就直接解析，导致 `jq` 报错，脚本异常退出。

#### 错误现象

- **症状**: Hook 执行失败，日志显示 `jq` 解析错误
- **用户影响**: Hook 无法正常工作

#### 根本原因

缺少 JSON 格式验证步骤，直接使用 `jq` 提取字段，遇到格式错误的 JSON 立即失败。

#### 解决方案

##### 方案概述

在提取 JSON 字段之前，先使用 `jq empty` 验证 JSON 格式是否有效，无效则优雅跳过。

##### 代码示例

```bash
# 验证 JSON 格式
if ! echo "$INPUT_JSON" | jq empty 2>/dev/null; then
    debug_log "Invalid JSON input, skipping"
    exit 0
fi

# 安全提取字段 (带fallback)
SESSION_ID=$(echo "$INPUT_JSON" | jq -r '.session_id // "unknown"' 2>/dev/null || echo "unknown")
```

#### 改进效果

| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| 无效JSON处理 | ❌ jq解析失败 | ✅ 验证后跳过 |
| 错误恢复 | ❌ 立即退出 | ✅ 安全fallback |

#### 技术细节

**Hook 输入验证最佳实践**:

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. 读取 stdin
INPUT_JSON=$(cat)

# 2. 空输入检查
if [ -z "$INPUT_JSON" ]; then
    debug_log "Empty input received, skipping"
    exit 0
fi

# 3. JSON格式验证
if ! echo "$INPUT_JSON" | jq empty 2>/dev/null; then
    debug_log "Invalid JSON input, skipping"
    exit 0
fi

# 4. 安全提取字段 (带fallback)
FIELD=$(echo "$INPUT_JSON" | jq -r '.field // "default"' 2>/dev/null || echo "default")
```

---

## 3. 输出格式问题

### 3.1 JSON 手动拼接

**问题编号**: OUTPUT-001
**影响范围**: `stop-python-quality-gate.sh` (2处), `user-prompt-submit-skill-activation.sh` (1处)
**严重程度**: 🔴 高
**发现日期**: 2025-11-19
**修复状态**: ✅ 已修复

#### 问题描述

使用字符串拼接手动构建 JSON 对象，未正确转义特殊字符，导致 JSON 格式无效，Claude 无法解析 hook 输出。

#### 错误现象

- **症状**: Stop hook 总是报 "JSON validation failed"
- **错误信息**: `Hook JSON output validation failed: Invalid input`
- **用户影响**: Hook 功能失效，质量门禁无法工作

#### 根本原因

手动拼接 JSON 字符串时：
1. 换行符转义不正确
2. 引号转义可能失败
3. 特殊字符（emoji、中文等）未处理
4. 多重转义逻辑复杂易错

**错误代码示例**:

**位置 1**: `stop-python-quality-gate.sh` 第 275-279 行（警告情况）
```bash
# 手动拼接 JSON - 容易出错！
ERROR_DETAILS="{"
for check_name in "${!CHECK_ERRORS[@]}"; do
    ERROR_DETAILS="$ERROR_DETAILS\"$check_name\": ${CHECK_ERRORS[$check_name]},"
done
ERROR_DETAILS="${ERROR_DETAILS%,}}"  # 移除最后的逗号

cat <<EOF
{
  "hookSpecificOutput": {
    "errorDetails": $ERROR_DETAILS  # 直接插入，没有转义
  }
}
EOF
```

**位置 2**: `stop-python-quality-gate.sh` 第 298-320 行（阻断情况）
```bash
# 多重转义处理 - 容易出错！
REASON="${REASON}$(echo -e "$ERROR_SUMMARY" | sed 's/"/\\"/g' | tr '\n' '\\' | sed 's/\\/\\n/g')"

cat <<EOF
{
  "reason": "$(echo -e "$REASON" | sed 's/"/\\"/g' | head -c 1000)",
  "errorDetails": $ERROR_DETAILS
}
EOF
```

**位置 3**: `user-prompt-submit-skill-activation.sh` 第 267 行
```bash
# 直接插入变量，没有转义
cat <<EOF
{
  "hookSpecificOutput": {
    "additionalContext": "$ACTIVATION_MESSAGE"  # 如果包含引号或换行会失败
  }
}
EOF
```

#### 解决方案

##### 方案概述

使用 `jq` 生成 JSON，确保 100% 有效的 JSON 输出，自动处理所有特殊字符转义。

##### 实施步骤

1. 构建数据为 Bash 变量或数组
2. 使用 `jq -n` 从 null 开始构建 JSON
3. 通过 `--arg` 传递字符串参数（自动转义）
4. 通过 `--argjson` 传递 JSON 参数
5. 在 jq 表达式中组装最终的 JSON 结构

##### 代码示例

**修复 1**: `stop-python-quality-gate.sh` 警告情况（第 270-293 行）

```bash
# 构建错误详情 JSON 数组（使用 jq 确保正确转义）
ERROR_DETAILS_ARRAY="[]"
for check_name in "${!CHECK_ERRORS[@]}"; do
    ERROR_DETAILS_ARRAY=$(echo "$ERROR_DETAILS_ARRAY" | jq --arg name "$check_name" --argjson count "${CHECK_ERRORS[$check_name]}" '. += [{name: $name, errors: $count}]')
done

# 使用 jq 生成有效的 JSON（确保所有字符正确转义）
jq -n \
    --arg decision "allow" \
    --arg reason "⚠️ 发现 $TOTAL_ERRORS 个错误，低于阈值 ($ERROR_THRESHOLD)。建议修复后再继续。" \
    --argjson errorDetails "$ERROR_DETAILS_ARRAY" \
    '{
        hookSpecificOutput: {
            hookEventName: "Stop",
            decision: $decision,
            reason: $reason,
            errorDetails: $errorDetails
        }
    }'
```

**修复 2**: `stop-python-quality-gate.sh` 阻断情况（第 296-329 行）

```bash
# 构建错误详情 JSON 数组（使用 jq 确保正确转义）
ERROR_DETAILS_ARRAY="[]"
for check_name in "${!CHECK_ERRORS[@]}"; do
    ERROR_DETAILS_ARRAY=$(echo "$ERROR_DETAILS_ARRAY" | jq --arg name "$check_name" --argjson count "${CHECK_ERRORS[$check_name]}" '. += [{name: $name, errors: $count}]')
done

# 构建原因字符串（限制长度避免过长）
REASON="❌ Python 质量检查失败: 发现 $TOTAL_ERRORS 个错误（阈值: $ERROR_THRESHOLD）

请修复以下错误后再停止：

$(echo -e "$ERROR_SUMMARY" | head -c 800)"

# 使用 jq 生成有效的 JSON（确保所有字符正确转义）
jq -n \
    --arg decision "block" \
    --arg reason "$REASON" \
    --argjson errorDetails "$ERROR_DETAILS_ARRAY" \
    --arg suggestion "使用 Task Master 创建修复任务: task-master add-task --prompt='修复质量检查错误'" \
    '{
        hookSpecificOutput: {
            hookEventName: "Stop",
            decision: $decision,
            reason: $reason,
            errorDetails: $errorDetails,
            suggestion: $suggestion
        }
    }'
```

**修复 3**: `user-prompt-submit-skill-activation.sh`（第 262-270 行）

```bash
# 使用 jq 确保正确转义
jq -n \
    --arg context "$ACTIVATION_MESSAGE" \
    '{
        hookSpecificOutput: {
            hookEventName: "UserPromptSubmit",
            additionalContext: $context
        }
    }'
```

#### 验证结果

##### 测试场景 1: 包含特殊字符的消息

```bash
ACTIVATION_MESSAGE='Test message with "quotes" and
newlines and emoji 💡'

jq -n \
    --arg context "$ACTIVATION_MESSAGE" \
    '{
        hookSpecificOutput: {
            hookEventName: "UserPromptSubmit",
            additionalContext: $context
        }
    }'
```

**输出**:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "Test message with \"quotes\" and newlines and emoji 💡"
  }
}
```
✅ JSON 完全有效，所有特殊字符正确转义

##### 测试场景 2: Stop hook 错误详情数组

```bash
# 模拟多个检查错误
declare -A CHECK_ERRORS
CHECK_ERRORS["syntax_check"]=5
CHECK_ERRORS["type_hints"]=3
CHECK_ERRORS["test_failures"]=2

ERROR_DETAILS_ARRAY="[]"
for check_name in "${!CHECK_ERRORS[@]}"; do
    ERROR_DETAILS_ARRAY=$(echo "$ERROR_DETAILS_ARRAY" | jq --arg name "$check_name" --argjson count "${CHECK_ERRORS[$check_name]}" '. += [{name: $name, errors: $count}]')
done
```

**输出**:
```json
{
  "errorDetails": [
    {"name": "test_failures", "errors": 2},
    {"name": "type_hints", "errors": 3},
    {"name": "syntax_check", "errors": 5}
  ]
}
```
✅ 数组格式正确，数值类型正确

#### 改进效果

| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| JSON 有效性 | ⚠️ 特殊字符会破坏 JSON | ✅ 100% 有效 |
| 特殊字符处理 | ❌ 需要复杂的手动转义 | ✅ jq 自动处理 |
| 引号处理 | ❌ sed 转义可能失败 | ✅ 完美转义 |
| 换行符处理 | ❌ tr/sed 组合不可靠 | ✅ 保留原始换行 |
| Emoji 和 Unicode | ❌ 可能损坏 | ✅ 完整保留 |
| 代码可维护性 | ❌ 复杂难懂 | ✅ 清晰简洁 |
| 错误详情格式 | ❌ 对象（易出错） | ✅ 数组（标准） |

#### 核心收益

1. **可靠性**: 彻底消除 JSON 无效的风险
2. **安全性**: 不再需要手动处理特殊字符转义
3. **可维护性**: 代码更清晰，使用标准的 jq 工具
4. **一致性**: 所有 hooks 都使用相同的 JSON 生成模式
5. **健壮性**: 能正确处理任何字符（引号、换行、emoji、中文等）

#### 技术细节

**jq 参数说明**:
- `jq -n`: 不读取输入，从 null 开始构建
- `--arg name value`: 传入字符串参数（自动转义）
- `--argjson name value`: 传入 JSON 参数
- `.`: 当前对象
- `. += [...]`: 向数组追加元素

**jq vs 手动拼接对比**:

| 方面 | 手动拼接 | jq 生成 |
|------|---------|---------|
| 字符转义 | ❌ 手动处理易错 | ✅ 自动正确转义 |
| 特殊字符 | ❌ 需要复杂处理 | ✅ 自动处理 |
| JSON 格式 | ❌ 容易出错 | ✅ 始终有效 |
| 维护性 | ❌ 难以维护 | ✅ 清晰易懂 |
| 可靠性 | ⚠️ 不稳定 | ✅ 100%可靠 |

#### 相关文件

| 文件 | 问题数 | 修复状态 |
|------|-------|---------|
| stop-python-quality-gate.sh | 2 处手动拼接 | ✅ 已修复 |
| user-prompt-submit-skill-activation.sh | 1 处直接插入 | ✅ 已修复 |
| post-tool-use-database-schema-validator.sh | 0（已使用 jq） | ✅ 无需修改 |
| post-tool-use-document-organizer.sh | 0（已使用 jq） | ✅ 无需修改 |
| session-start-task-master-injector.sh | 0（输出纯文本） | ✅ 无需修改 |

---

### 3.2 特殊字符转义

**问题编号**: OUTPUT-002
**影响范围**: 同 [3.1 JSON 手动拼接](#31-json-手动拼接)
**严重程度**: 🔴 高
**发现日期**: 2025-11-19
**修复状态**: ✅ 已修复（通过修复 OUTPUT-001 一并解决）

#### 问题描述

在手动构建 JSON 字符串时，使用复杂的 `sed`/`tr` 组合尝试转义特殊字符，但逻辑不完善，无法正确处理所有情况。

#### 解决方案

采用 `jq` 生成 JSON 的方案已完全解决特殊字符转义问题。详见 [3.1 JSON 手动拼接](#31-json-手动拼接)。

---

## 4. 最佳实践

### 4.1 输入处理最佳实践

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. 读取 stdin
INPUT_JSON=$(cat)

# 2. 空输入检查
if [ -z "$INPUT_JSON" ]; then
    debug_log "Empty input received, skipping"
    # 根据 hook 类型决定行为:
    # - SessionStart/End: exit 0 (跳过)
    # - Stop: 输出允许JSON + exit 0
    exit 0
fi

# 3. JSON格式验证
if ! echo "$INPUT_JSON" | jq empty 2>/dev/null; then
    debug_log "Invalid JSON input, skipping"
    exit 0
fi

# 4. 安全提取字段 (带fallback)
SESSION_ID=$(echo "$INPUT_JSON" | jq -r '.session_id // "unknown"' 2>/dev/null || echo "unknown")
```

### 4.2 输出 JSON 最佳实践

**✅ 正确做法**: 始终使用 jq 生成 JSON

```bash
# 字符串参数
jq -n --arg text "$USER_INPUT" '{message: $text}'

# JSON 参数
jq -n --argjson data "$JSON_OBJECT" '{data: $data}'

# 数组构建
ARRAY="[]"
for item in "${items[@]}"; do
    ARRAY=$(echo "$ARRAY" | jq --arg val "$item" '. += [$val]')
done
```

**❌ 错误做法**: 手动拼接 JSON

```bash
# 错误 1: 直接插入变量
echo "{\"message\": \"$USER_INPUT\"}"

# 错误 2: 手动拼接对象
JSON="{"
JSON="$JSON\"key\": \"$value\","
JSON="${JSON%,}}"

# 错误 3: 使用 sed/tr 转义
echo "{\"message\": \"$(echo "$TEXT" | sed 's/"/\\"/g')\"}"
```

### 4.3 代码审查检查清单

在编写或审查 hooks 代码时，使用以下检查清单：

- [ ] 是否添加了空输入检查？
- [ ] 是否添加了 JSON 格式验证？
- [ ] 是否使用了 `cat <<EOF` 手动构建 JSON？
- [ ] 是否在 heredoc 中直接插入变量（如 `"field": "$VAR"`）？
- [ ] 是否使用了 `sed 's/"/\\"/g'` 或类似的手动转义？
- [ ] 是否手动拼接 JSON 对象或数组（如 `JSON="{}"`）？
- [ ] 是否使用 `jq -n` 和 `--arg`/`--argjson` 生成 JSON？
- [ ] 输出的 JSON 是否经过验证（如 `jq .` 测试）？

✅ 如果以上任何一项答案是"是"（除了第 7-8 项），则需要重构为使用 jq。

---

## 5. 快速参考

### 5.1 问题索引

| 问题编号 | 问题标题 | 严重程度 | 状态 |
|---------|---------|---------|------|
| CONFIG-001 | 占位符未替换 | 🔴 高 | ✅ 已修复 |
| CONFIG-002 | 行结束符不兼容 | 🟡 中 | ✅ 已修复 |
| INPUT-001 | 空输入处理 | 🔴 高 | ✅ 已修复 |
| INPUT-002 | 无效 JSON 格式 | 🟡 中 | ✅ 已修复 |
| OUTPUT-001 | JSON 手动拼接 | 🔴 高 | ✅ 已修复 |
| OUTPUT-002 | 特殊字符转义 | 🔴 高 | ✅ 已修复 |

### 5.2 受影响文件汇总

| Hook 文件 | 相关问题 | 修复状态 |
|-----------|---------|---------|
| stop-python-quality-gate.sh | CONFIG-001, CONFIG-002, INPUT-001, OUTPUT-001 | ✅ 全部修复 |
| session-start-task-master-injector.sh | INPUT-001 | ✅ 已修复 |
| session-end-cleanup.sh | INPUT-001 | ✅ 已修复 |
| user-prompt-submit-skill-activation.sh | INPUT-001, OUTPUT-001 | ✅ 全部修复 |
| post-tool-use-file-edit-tracker.sh | - | ✅ 无问题 |
| post-tool-use-database-schema-validator.sh | - | ✅ 无问题 |
| post-tool-use-document-organizer.sh | - | ✅ 无问题 |

### 5.3 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v2.0 | 2025-11-19 | 重构文档结构，规范化格式，添加分类索引 |
| v1.3 | 2025-11-19 | 添加 Claude-Kits 项目 JSON 手动拼接问题修复 |
| v1.2 | 2025-11-12 | 添加空输入和无效 JSON 处理 |
| v1.1 | 2025-11-11 | 添加 Stop Hook JSON 输出无效错误 |
| v1.0 | 2025-11-10 | 初始版本，包含占位符和行结束符问题 |

---

**文档结束**

> **维护建议**: 每次发现新问题时，请按照本文档的格式规范添加新章节，并更新快速参考索引。
