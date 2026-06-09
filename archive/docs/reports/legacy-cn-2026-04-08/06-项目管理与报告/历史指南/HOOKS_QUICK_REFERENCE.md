# Hooks系统快速参考卡片

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


**版本**: 2.0 | **创建**: 2025-11-11

---

## 📋 Hooks清单 (7个)

| Hook | 文件 | 事件 | Matcher | Timeout | 阻塞? |
|------|------|------|---------|---------|-------|
| **Skill激活器** | `user-prompt-submit-skill-activation.sh` | UserPromptSubmit | - | 5s | ❌ |
| **编辑追踪** | `post-tool-use-file-edit-tracker.sh` | PostToolUse | Edit\|Write | 3s | ❌ |
| **数据库验证** | `post-tool-use-database-schema-validator.sh` | PostToolUse | Edit\|Write | 5s | ❌ |
| **文档组织** | `post-tool-use-document-organizer.sh` | PostToolUse | Write | 5s | ❌ |
| **质量门禁** | `stop-python-quality-gate.sh` | Stop | - | 120s | ✅ |
| **上下文注入** | `session-start-task-master-injector.sh` | SessionStart | - | 5s | ❌ |
| **会话清理** | `session-end-cleanup.sh` | SessionEnd | - | 5s | ❌ |

---

## 📁 文件结构

```
.claude/
├── settings.json                                     # ⭐ 主配置
├── skill-rules.json                                  # ⭐ Skill规则
├── build-checker-python.json                         # ⭐ 质量检查配置
├── edit_log.jsonl                                    # 运行时生成
└── hooks/
    ├── user-prompt-submit-skill-activation.sh        # ⭐ Hook 1
    ├── post-tool-use-file-edit-tracker.sh           # ⭐ Hook 2
    ├── post-tool-use-database-schema-validator.sh   # ⭐ Hook 3
    ├── post-tool-use-document-organizer.sh          # ⭐ Hook 4
    ├── stop-python-quality-gate.sh                  # ⭐ Hook 5
    ├── session-start-task-master-injector.sh        # ⭐ Hook 6
    ├── session-end-cleanup.sh                       # ⭐ Hook 7
    ├── README.md                                     # 📖 文档
    ├── FILE_ORGANIZATION_GUIDE.md                    # 📖 文档
    └── HOOKS_IMPROVEMENT_COMPLETION_REPORT.md        # 📖 文档
```

⭐ = 必需文件 | 📖 = 可选文档

---

## 🚀 快速迁移步骤

### 1️⃣ 复制文件 (5分钟)

```bash
# 在新项目中执行
cd /path/to/new-project
mkdir -p .claude/hooks

# 复制所有必需文件
cp -r /path/to/mystocks/.claude/settings.json .claude/
cp -r /path/to/mystocks/.claude/skill-rules.json .claude/
cp -r /path/to/mystocks/.claude/build-checker-python.json .claude/
cp /path/to/mystocks/.claude/hooks/*.sh .claude/hooks/

# 添加执行权限
chmod +x .claude/hooks/*.sh
```

### 2️⃣ 适配配置 (10分钟)

**修改 `build-checker-python.json`**:
```json
{
  "repos": {
    "/new/project/path": {  // ← 改为新项目路径
      "qualityChecks": [...]
    }
  }
}
```

**修改 `skill-rules.json`**:
```json
{
  "skills": {
    "backend-dev-guidelines": {
      "fileTriggers": {
        "pathPatterns": [
          "src/**/*.py"  // ← 改为新项目路径
        ]
      }
    }
  }
}
```

### 3️⃣ 测试运行 (2分钟)

```bash
claude  # 启动Claude Code
# 测试: 输入包含关键词的提示,检查skill激活
# 测试: 编辑文件,检查日志记录
# 测试: 停止会话,检查质量门禁
```

---

## 🔧 常见自定义

### 禁用某个Hook

**删除Database Validator** (不需要数据库验证):
```json
// settings.json - PostToolUse数组中删除:
{
  "matcher": "Edit|Write",
  "hooks": [{
    "command": "...database-schema-validator.sh"  // ← 删除此项
  }]
}
```

### 调整质量门禁阈值

**放宽Stop Hook** (允许更多错误):
```json
// build-checker-python.json
{
  "errorThreshold": 20  // ← 默认10,改为20
}
```

### 修改允许的根文件

**Document Organizer Hook**:
```bash
# 编辑 post-tool-use-document-organizer.sh
ALLOWED_ROOT_FILES=(
    "README.md"
    "LICENSE"      # ← 添加新的允许文件
    "package.json"
)
```

---

## 🎯 Hook功能速查

### UserPromptSubmit - Skill激活器
**何时触发**: 用户输入提示词时
**作用**: 根据关键词自动加载skill文档
**配置**: `skill-rules.json`

### PostToolUse #1 - 编辑追踪器
**何时触发**: 使用Edit或Write工具时
**作用**: 记录编辑的文件到 `edit_log.jsonl`
**用途**: 为Stop hook提供批量检查输入

### PostToolUse #2 - 数据库验证器
**何时触发**: 编辑数据库相关文件时
**作用**: 检查数据库架构违规 (MyStocks特定: TDengine vs PostgreSQL)
**自定义**: 修改 `DANGEROUS_PATTERNS` 数组

### PostToolUse #3 - 文档组织器
**何时触发**: 创建新文档文件时
**作用**: 验证文档位置,建议正确的 `docs/` 子目录
**自定义**: 修改 `ALLOWED_ROOT_FILES` 和分类规则

### Stop - 质量门禁
**何时触发**: 停止Claude会话时
**作用**: 批量检查Python文件,错误≥阈值时阻止
**配置**: `build-checker-python.json`
**阻塞**: ✅ 是唯一阻塞型hook (exit 2)

### SessionStart - 上下文注入
**何时触发**: 启动Claude会话时
**作用**: 注入Task Master任务上下文 (或其他项目上下文)
**自定义**: 可改为注入Git信息、最近文档等

### SessionEnd - 会话清理
**何时触发**: 结束Claude会话时
**作用**: 清理当前会话的编辑日志,截断到5000行
**配置**: 修改 `MAX_LOG_LINES` 变量

---

## 🐛 故障排查

| 问题 | 检查 | 解决 |
|------|------|------|
| Hook不执行 | `ls -la .claude/hooks/*.sh` | `chmod +x .claude/hooks/*.sh` |
| Stop太严格 | `jq .errorThreshold .claude/build-checker-python.json` | 增加阈值或临时禁用 |
| Skill不激活 | `cat .claude/skill-rules.json` | 检查关键词和路径模式 |
| 日志太大 | `wc -l .claude/edit_log.jsonl` | 手动清理或调整 `MAX_LOG_LINES` |

### 调试命令

```bash
# 检查hook语法
bash -n .claude/hooks/hook-name.sh

# 手动运行hook测试
echo '{"user_message":"test"}' | .claude/hooks/user-prompt-submit-skill-activation.sh

# 启用调试模式
export HOOK_NAME_DEBUG=true
```

---

## 📊 性能指标

| Hook | 平均耗时 | 最大耗时 (Timeout) |
|------|----------|-------------------|
| Skill激活器 | <1s | 5s |
| 编辑追踪器 | <0.5s | 3s |
| 数据库验证器 | <1s | 5s |
| 文档组织器 | <1s | 5s |
| 质量门禁 | 10-60s | 120s |
| 上下文注入 | <2s | 5s |
| 会话清理 | <1s | 5s |

**总PostToolUse耗时**: 最多13秒 (3+5+5)

---

## 🔗 相关文档

- **完整迁移指南**: `docs/guides/HOOKS_MIGRATION_GUIDE.md`
- **Hooks用户手册**: `.claude/hooks/README.md`
- **文件组织指南**: `.claude/hooks/FILE_ORGANIZATION_GUIDE.md`
- **实施报告**: `.claude/hooks/HOOKS_IMPROVEMENT_COMPLETION_REPORT.md`
- **Claude官方文档**: https://docs.claude.com/en/docs/claude-code/hooks

---

## 📝 迁移检查清单

- [ ] 复制所有 `.sh` 文件到 `.claude/hooks/`
- [ ] 复制3个配置文件到 `.claude/`
- [ ] 运行 `chmod +x .claude/hooks/*.sh`
- [ ] 修改 `build-checker-python.json` 路径
- [ ] 修改 `skill-rules.json` 文件路径模式
- [ ] 测试UserPromptSubmit hook (输入关键词)
- [ ] 测试PostToolUse hook (编辑文件)
- [ ] 测试Stop hook (停止会话)
- [ ] 删除不需要的hooks (可选)
- [ ] 根据新项目调整配置 (可选)

---

**💡 提示**: 最小迁移只需10个文件 + 5分钟配置即可运行!

**📧 问题反馈**: 参考 `HOOKS_MIGRATION_GUIDE.md` 的故障排查章节

**版本**: 2.0 | **最后更新**: 2025-11-11
